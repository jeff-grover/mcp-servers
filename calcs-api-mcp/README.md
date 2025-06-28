# Calcs API MCP Server

A Model Context Protocol (MCP) server that provides Claude Code and Cursor with access to the Calcs API for retail analytics calculations and test management. This server runs as an HTTP service using Server-Sent Events (SSE) transport for compatibility with modern MCP clients.

## Features

This MCP server provides comprehensive access to the Calcs API endpoints, including:

### Test Management
- Get all tests for a client
- Get test status and details
- Get treatment and control sites
- Get cohort IDs

### Results & Analytics
- Get test results with filtering options
- Get lift explorer results
- Get site pair lift manifests
- Get prediction tables
- Get customer cross data
- Download comprehensive test data

### Analysis Management
- List, create, update, and delete analyses
- Run analyses (synchronous and asynchronous)
- Get analysis results

### Administrative Functions
- Get active clients
- Get job summaries and date ranges
- Get site test information
- Manage adhoc data files
- Get transaction descriptions

### Utility Functions
- Health checks and API connectivity tests

## Prerequisites

- Python 3.10 or higher
- UV package manager
- A valid Calcs API bearer token
- Access to the Calcs API (default: `https://staging-app.marketdial.dev/calcs`)
- Claude Code CLI or Cursor IDE (for MCP integration)

## Installation

1. Navigate to the calcs-api directory:
   ```bash
   cd calcs-api
   ```

2. Install dependencies using UV:
   ```bash
   uv sync
   ```

## Configuration

The server requires the following environment variables:

### Required
- `CALCS_API_TOKEN`: Your bearer token for the Calcs API

### Optional
- `CALCS_API_BASE_URL`: Base URL for the Calcs API (default: `https://staging-app.marketdial.dev/calcs`)
- `CALCS_DEFAULT_CLIENT`: Default client identifier to use when not specified in tool calls

### Environment Variables Setup

Create a `.env` file in the calcs-api directory:

```env
CALCS_API_TOKEN=your_bearer_token_here
CALCS_DEFAULT_CLIENT=your_client_name
CALCS_API_BASE_URL=https://staging-app.marketdial.dev/calcs
```

## Usage

### Starting the Server

Run the MCP server (starts on http://localhost:8001):

```bash
uv run calcs-api
```

The server will start and listen on port 8001 with the endpoint `/messages` for MCP communication.

#### Legacy stdio mode (backwards compatibility)
```bash
uv run python calcs_api/server.py --stdio
```

### Connecting to Claude Code

After starting the server, add it to Claude Code:

```bash
# Add the server to Claude Code
claude mcp add --transport sse calcs-api http://localhost:8001/messages

# Start Claude Code with MCP servers
claude
```

You can now use the Calcs API tools in Claude Code:
- Ask Claude to "get all tests for client X"
- Ask Claude to "get test status for test ID 123"
- Request analysis creation, execution, and results

### Connecting to Cursor

Add the server to your Cursor settings:

1. Open Cursor settings (Cmd/Ctrl + ,)
2. Search for "MCP" settings
3. Add the following configuration:

```json
{
  "mcp": {
    "servers": {
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

### Alternative Configuration Methods

You can also use the provided configuration file:

```bash
# Using local config file
claude --mcp-config claude-code-config.json
```

Or copy the server configuration to your global Claude Code config.

## Available Tools

### Test Management Tools

#### `health_check`
Check API health status.
- **Parameters**: None

#### `get_tests`
Get all tests for a client.
- **Parameters**: `client` (optional)

#### `get_test_status`
Get the status of a specific test.
- **Parameters**: `test_id` (required), `client` (optional)

## Multi-Tenant Support

The Calcs API supports multi-tenancy through the `client` header. You can:

1. Set a default client using the `CALCS_DEFAULT_CLIENT` environment variable
2. Override the client for specific tool calls by providing the `client` parameter
3. Some administrative tools may require specific client permissions

## Error Handling

The server provides comprehensive error handling:

- **Authentication errors**: Invalid or missing bearer tokens
- **Validation errors**: Invalid parameters or missing required fields
- **API errors**: HTTP errors from the Calcs API
- **Network errors**: Connection failures or timeouts

All errors are returned in a structured format with descriptive messages.

## Development

### Install dependencies:

```bash
uv sync
```

### Run directly with Python:

```bash
# Run the server module directly (HTTP mode)
uv run python -m calcs_api.server

# Run in stdio mode
uv run python calcs_api/server.py --stdio

# Or run the server file directly
uv run python calcs_api/server.py
```

### Testing the Server

Once running, you can test the server endpoints:

```bash
# Check if server is responding (should see SSE connection attempt)
curl http://localhost:8001/messages

# The server provides MCP protocol communication over SSE
```

## Configuration

The server uses these defaults:
- **Host**: localhost
- **Port**: 8001
- **Endpoint**: /messages
- **Transport**: Server-Sent Events (SSE)

Environment variables must be configured for API access.

## Project Structure

```
calcs-api/
├── README.md                    # This file
├── pyproject.toml              # UV project configuration
├── claude-code-config.json     # MCP configuration example
├── examples/                   # Configuration examples
└── calcs_api/
    ├── __init__.py
    └── server.py               # Main server implementation with API client
```

## Troubleshooting

### Server won't start
- Check if port 8001 is already in use: `lsof -i :8001`
- Verify UV installation: `uv --version`
- Check Python version: `python --version` (should be 3.10+)
- Ensure environment variables are set in `.env` file

### Claude Code can't connect
- Verify server is running: check for "Uvicorn running on http://localhost:8001"
- Test server endpoint: `curl http://localhost:8001/messages`
- Check MCP server list: `claude mcp list`

### API Connection Issues

1. **"Missing required environment variable: CALCS_API_TOKEN"**
   - Ensure your bearer token is set in the `.env` file

2. **"API health check failed"**
   - Check your internet connection
   - Verify the API base URL is correct
   - Confirm your bearer token is valid

3. **"Client header required"**
   - Set the `CALCS_DEFAULT_CLIENT` environment variable or provide the `client` parameter in tool calls

4. **Tool validation errors**
   - Check that all required parameters are provided
   - Ensure parameter types match the expected format (e.g., numbers vs strings)

### Common Issues
- **Port conflicts**: Change port in `server.py` if 8001 is in use
- **UV not found**: Install UV following instructions at https://docs.astral.sh/uv/
- **Python version**: Ensure Python 3.10+ is available
- **Environment variables**: Ensure `.env` file exists in calcs-api directory

### Debug Mode

Check server logs in the terminal where you started the server for detailed error information.

## License

MIT License - see LICENSE file for details.

## Support

For issues related to:
- **This MCP server**: Open an issue in this repository
- **The Calcs API**: Contact your Calcs API provider
- **Claude Code integration**: Refer to Claude Code documentation