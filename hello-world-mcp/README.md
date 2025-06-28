# Hello World MCP Server

A simple Model Context Protocol (MCP) server that demonstrates basic MCP functionality with Python and UV. This server runs as an HTTP service using Server-Sent Events (SSE) transport for compatibility with Claude Code and Cursor.

## Features

This server provides two demonstration tools:

- **say_hello**: Returns a friendly greeting message with optional name parameter
- **get_random_fact**: Returns a random fun fact from a curated collection

## Prerequisites

- Python 3.10 or higher
- UV package manager
- Claude Code CLI or Cursor IDE (for MCP integration)

## Installation

```bash
cd hello-world-mcp
uv sync
```

## Usage

### Starting the Server

Run the MCP server (starts on http://localhost:8000):

```bash
uv run hello-world-mcp
```

The server will start and listen on port 8000 with the endpoint `/messages` for MCP communication.

### Connecting to Claude Code

After starting the server, add it to Claude Code:

```bash
# Add the server to Claude Code
claude mcp add --transport sse hello-world-mcp http://localhost:8000/messages

# Start Claude Code with MCP servers
claude
```

You can now use the tools in Claude Code:
- Ask Claude to "say hello to [name]" 
- Ask Claude to "give me a random fact"

### Connecting to Cursor

Add the server to your Cursor settings:

1. Open Cursor settings (Cmd/Ctrl + ,)
2. Search for "MCP" settings
3. Add the following configuration:

```json
{
  "mcp": {
    "servers": {
      "hello-world-mcp": {
        "transport": {
          "type": "sse",
          "url": "http://localhost:8000/messages"
        }
      }
    }
  }
}
```

### Alternative Configuration Methods

You can also use the provided configuration file:

```bash
# Using local config file
claude --mcp-config claude-code-config.json
```

Or copy the server configuration to your global Claude Code config.

## Development

### Install dependencies:

```bash
uv sync
```

### Run directly with Python:

```bash
# Run the server module directly
uv run python -m hello_world_mcp.server

# Or run the server file
uv run python hello_world_mcp/server.py
```

### Testing the Server

Once running, you can test the server endpoints:

```bash
# Check if server is responding (should see SSE connection attempt)
curl http://localhost:8000/messages

# The server provides MCP protocol communication over SSE
```

## Configuration

The server uses these defaults:
- **Host**: localhost
- **Port**: 8000
- **Endpoint**: /messages
- **Transport**: Server-Sent Events (SSE)

No environment variables are required for this demonstration server.

## Project Structure

```
hello-world-mcp/
├── README.md                    # This file
├── pyproject.toml              # UV project configuration
├── claude-code-config.json     # MCP configuration example
└── hello_world_mcp/
    ├── __init__.py
    └── server.py               # Main server implementation
```

## API Reference

### Tools

#### say_hello
- **Description**: Returns a friendly greeting message
- **Parameters**:
  - `name` (string, optional): Name to greet
- **Example**: "Hello, Claude! 👋 Welcome to the MCP Hello World server!"

#### get_random_fact
- **Description**: Returns a random fun fact
- **Parameters**: None
- **Example**: "🎲 Random fact: Honey never spoils! Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible."

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Verify UV installation: `uv --version`
- Check Python version: `python --version` (should be 3.10+)

### Claude Code can't connect
- Verify server is running: check for "Uvicorn running on http://localhost:8000"
- Test server endpoint: `curl http://localhost:8000/messages`
- Check MCP server list: `claude mcp list`

### Common Issues
- **Port conflicts**: Change port in `server.py` if 8000 is in use
- **UV not found**: Install UV following instructions at https://docs.astral.sh/uv/
- **Python version**: Ensure Python 3.10+ is available

## License

MIT