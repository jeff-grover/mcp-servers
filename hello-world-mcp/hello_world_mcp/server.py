#!/usr/bin/env python3
"""
A simple hello world MCP server that demonstrates basic MCP functionality.
Runs as an HTTP server on localhost using SSE transport.
"""

import asyncio
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn


# Create the server instance
server = Server("hello-world-mcp")


@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="say_hello",
            description="Returns a friendly hello message",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to greet (optional)",
                    }
                },
                "additionalProperties": False,
            },
        ),
        Tool(
            name="get_random_fact",
            description="Returns a random fun fact",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    if name == "say_hello":
        name_arg = arguments.get("name", "World")
        message = f"Hello, {name_arg}! 👋 Welcome to the MCP Hello World server!"
        return [TextContent(type="text", text=message)]
    
    elif name == "get_random_fact":
        facts = [
            "Honey never spoils! Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
            "A group of flamingos is called a 'flamboyance'.",
            "Octopuses have three hearts and blue blood.",
            "The shortest war in history lasted only 38-45 minutes between Britain and Zanzibar in 1896.",
            "Bananas are berries, but strawberries aren't!",
        ]
        import random
        fact = random.choice(facts)
        return [TextContent(type="text", text=f"🎲 Random fact: {fact}")]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


def run():
    """Entry point for console script."""
    # Create SSE transport and get the ASGI app
    sse_transport = SseServerTransport("/messages")
    
    # Create ASGI app
    async def app(scope, receive, send):
        if scope["type"] == "http":
            if scope["path"] == "/messages":
                if scope["method"] == "GET":
                    async with sse_transport.connect_sse(scope, receive, send) as streams:
                        await server.run(streams[0], streams[1], server.create_initialization_options())
                    return
                elif scope["method"] == "POST":
                    await sse_transport.handle_post_message(scope, receive, send)
                    return
        
        # 404 for other paths
        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [[b"content-type", b"text/plain"]],
        })
        await send({
            "type": "http.response.body",
            "body": b"Not Found",
        })
    
    # Run the server
    uvicorn.run(app, host="localhost", port=8000)


if __name__ == "__main__":
    run()