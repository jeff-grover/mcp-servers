# MCP Servers

A collection of Model Context Protocol (MCP) servers that provide Claude Code and Cursor with specialized functionality for various development and analytics tasks.

## Current Servers

### hello-world-mcp
A simple demonstration MCP server in Python that showcases basic MCP functionality with two tools:
- `say_hello` - Returns a friendly greeting message
- `get_random_fact` - Returns random fun facts

**Location**: `hello-world-mcp/`
**Port**: 8000
**Documentation**: See individual server README in `hello-world-mcp/README.md`

### calcs-api
MCP server that provides access to the Calcs API for retail analytics calculations and test management. Acts as a bridge between Claude and the Calcs API, offering comprehensive tools for managing A/B tests, analyses, and retrieving retail analytics data.

**Location**: `calcs-api/`
**Port**: 8001
**Documentation**: See individual server README in `calcs-api/README.md`

## Quick Start

### Prerequisites
- Python 3.10 or higher
- UV package manager (recommended) or pip
- Claude Code CLI

### Installation

Each server can be installed and run independently:

```bash
# Install hello-world-mcp
cd hello-world-mcp
uv sync

# Install calcs-api
cd ../calcs-api
uv sync
```

### Running Servers

Start each server in its own terminal:

```bash
# Terminal 1: Start hello-world server (port 8000)
cd hello-world-mcp
uv run hello-world-mcp

# Terminal 2: Start calcs-api server (port 8001)
cd calcs-api
uv run calcs-api
```

### Connecting to Claude Code

Add servers using Claude Code CLI commands:

```bash
# Add hello-world-mcp server
claude mcp add --transport sse hello-world-mcp http://localhost:8000/messages

# Add calcs-api server (requires environment variables)
claude mcp add --transport sse calcs-api http://localhost:8001/messages

# Start Claude Code with MCP servers
claude
```

### Connecting to Cursor

Add servers to your Cursor settings by opening Cursor settings (Cmd/Ctrl + ,) and adding:

```json
{
  "mcp": {
    "servers": {
      "hello-world-mcp": {
        "transport": {
          "type": "sse",
          "url": "http://localhost:8000/messages"
        }
      },
      "calcs-api": {
        "transport": {
          "type": "sse", 
          "url": "http://localhost:8001/messages"
        }
      }
    }
  }
}
```

## Repository Structure

```
mcp-servers/
├── README.md                    # This file
├── CLAUDE.md                   # Claude Code guidance
├── package.json                # Root package.json (legacy Node.js structure)
├── hello-world-mcp/            # Simple demo MCP server (Python/UV)
│   ├── README.md
│   ├── pyproject.toml
│   ├── hello_world_mcp/
│   └── claude-code-config.json
├── calcs-api/                  # Calcs API MCP server (Python/UV)
│   ├── README.md
│   ├── pyproject.toml
│   ├── calcs_api/
│   ├── claude-code-config.json
│   └── examples/
└── [future-server]/            # Additional servers go here
```

## Adding New Servers

To add a new MCP server to this repository:

1. **Create a new directory** for your server (e.g., `my-new-server/`)

2. **Initialize the server** with UV and pyproject.toml:
   ```bash
   mkdir my-new-server
   cd my-new-server
   uv init --package
   ```

3. **Set up MCP dependencies** in `pyproject.toml`:
   ```toml
   [project]
   name = "my-new-server"
   version = "0.1.0"
   requires-python = ">=3.10"
   dependencies = [
       "mcp>=1.0.0",
       "fastapi>=0.100.0",
       "uvicorn>=0.20.0",
   ]

   [project.scripts]
   my-new-server = "my_new_server.server:run"
   ```

4. **Follow MCP server conventions**:
   - Use SSE transport for HTTP connectivity
   - Entry point should expose a `run()` function
   - Use Python 3.10+ compatible code
   - Choose a unique port number

5. **Create configuration examples**:
   ```bash
   # Create claude-code-config.json
   echo '{
     "mcpServers": {
       "my-new-server": {
         "transport": {
           "type": "sse",
           "url": "http://localhost:PORT/messages"
         }
       }
     }
   }' > claude-code-config.json
   ```

6. **Update this README** to document your new server

## Managing MCP Servers

### List configured servers:
```bash
claude mcp list
```

### Remove a server:
```bash
claude mcp remove hello-world-mcp
```

### Check server status:
Check if servers are running by visiting their health endpoints:
- hello-world-mcp: http://localhost:8000/messages
- calcs-api: http://localhost:8001/messages

## Environment Configuration

### calcs-api Environment Setup
The calcs-api server requires environment variables:

```bash
cd calcs-api
cp .env.example .env  # If available
# Edit .env with your actual API tokens:
# CALCS_API_TOKEN=your_token_here
# CALCS_API_BASE_URL=https://your-api-url.com
# CALCS_DEFAULT_CLIENT=your_client_id
```

### hello-world-mcp
No environment configuration required - runs out of the box.

## Development Guidelines

- Each server should be self-contained in its own directory
- Use Python with UV for dependency management
- Use HTTP/SSE transport for Claude Code/Cursor compatibility
- Include comprehensive documentation in each server's README
- Add configuration examples for easy setup
- Follow MCP protocol specifications
- Choose unique port numbers to avoid conflicts

## Troubleshooting

### Server won't start
- Check if the port is already in use: `lsof -i :8000`
- Verify dependencies are installed: `uv sync`
- Check environment variables for calcs-api

### Claude Code can't connect
- Verify server is running and accessible
- Check port numbers match configuration
- Use `claude mcp list` to see configured servers

### Cursor can't connect
- Ensure absolute URLs in configuration
- Check that Cursor has MCP support enabled
- Verify server URLs are accessible

## License

MIT