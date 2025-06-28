# Calcs API MCP Server

A Model Context Protocol (MCP) server that provides Claude Code and Cursor with access to the Calcs API for retail analytics calculations and test management. This server runs as an HTTP service using Server-Sent Events (SSE) transport for compatibility with modern MCP clients.

## Features

This MCP server provides comprehensive access to the Calcs API endpoints, including:

### Test Management (6 tools)
- `health_check` - Check API connectivity and health status
- `get_tests` - Get all tests for a client
- `get_test_status` - Get detailed status and information for a specific test
- `get_active_clients` - Get list of all active clients
- `get_site_tests` - Get all tests where a site has treatment or control role
- `describe_transactions` - Get descriptive overview of the fact_transactions table

### Results & Analytics (8 tools)
- `get_test_results` - Get test results with advanced filtering (OVERALL, CUSTOMER_COHORT, CUSTOMER_SEGMENT, SITE_COHORT, SITE_PAIR, FINISHED_COHORT, SITE_TAG)
- `get_lift_explorer_results` - Get lift explorer results (JSON equivalent of .avro file contents)
- `get_lift_explorer_ids` - Get list of valid lift explorer IDs for client
- `get_site_pair_lift_manifest` - Get site pair lift manifest data
- `get_prediction_table` - Get prediction table data
- `get_customer_cross` - Get customer cross data
- `download_all_test_data` - Download comprehensive chart data for a test
- `get_clients_jobs_summary` - Get job information for all active clients

### Analysis Management (7 tools)
- `list_analyses` - List all analyses for the current client
- `create_analysis` - Create a new rollout analysis
- `get_analysis` - Get a specific analysis by ID
- `update_analysis` - Update an existing analysis
- `delete_analysis` - Delete an analysis
- `run_analysis` - Run rollout analysis synchronously
- `start_analysis` - Start analysis asynchronously with progress tracking
- `get_analysis_results` - Get results of a completed analysis

### Job & System Monitoring (4 tools)
- `get_jobs_summary` - Get count of running jobs and compute hours for date range
- `get_oldest_job_date` - Get the date of the oldest job for client
- `get_newest_job_date` - Get the date of the newest job for client

**Total: 25 comprehensive tools** covering the complete Calcs API surface area for retail analytics, A/B testing, and rollout analysis.

## Smart Response Management

This MCP server includes intelligent response size management to prevent context overflow when working with large datasets:

### Safe-by-Default Design
- **Automatic size detection**: Responses are checked against a 40,000 token limit
- **Smart error handling**: Large responses return helpful error messages with filtering suggestions
- **Seamless small responses**: Data under the limit passes through unchanged

### Keyword Filtering System
For endpoints that may return large datasets, filtered variants are available:
- `get_tests_filtered` - Filter test data by field keywords
- `get_test_results_filtered` - Filter comprehensive test results
- `download_all_test_data_filtered` - Filter complete test data packages  
- `get_lift_explorer_results_filtered` - Filter large analytics datasets
- `list_analyses_filtered` - Filter analysis lists

### Example Usage
```
User: "What's the average lift percent across all tests for RetailCorp?"

1. Claude calls get_tests(client="RetailCorp")
2. If response too large → Error: "Use get_tests_filtered with keywords: ['lift_percent']"
3. Claude calls get_tests_filtered(client="RetailCorp", keywords=["lift_percent"])
4. Receives manageable filtered data with only lift percentage fields
5. Computes average from filtered results
```

This approach enables complex analytical queries across arbitrarily large datasets while maintaining optimal performance and context efficiency.

## Prerequisites

- Python 3.10 or higher
- UV package manager
- A valid Calcs API bearer token
- Access to the Calcs API (default: `https://staging-app.marketdial.dev/calcs`)
- Claude Code CLI or Cursor IDE (for MCP integration)

## Installation

1. Navigate to the calcs-api-mcp directory:
   ```bash
   cd calcs-api-mcp
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

Create a `.env` file in the calcs-api-mcp directory:

```env
CALCS_API_TOKEN=your_bearer_token_here
CALCS_DEFAULT_CLIENT=your_client_name
CALCS_API_BASE_URL=https://staging-app.marketdial.dev/calcs
```

## Usage

### Starting the Server

Run the MCP server (starts on http://localhost:8001):

```bash
uv run calcs-api-mcp
```

The server will start and listen on port 8001 with the endpoint `/messages` for MCP communication.

### Connecting to Claude Code

After starting the server, add it to Claude Code:

```bash
# Add the server to Claude Code
claude mcp add --transport sse calcs-api-mcp http://localhost:8001/messages

# Start Claude Code with MCP servers
claude
```

You can now use the Calcs API tools in Claude Code with natural language:
- "Get all tests for client RetailCorp"
- "Show me the test status for test ID 123"
- "Create a new rollout analysis for product launch"
- "Get lift explorer results for ID abc-123"
- "Download all test data for test 456"

### Connecting to Cursor

Add the server to your Cursor settings:

1. Open Cursor settings (Cmd/Ctrl + ,)
2. Search for "MCP" settings
3. Add the following configuration:

```json
{
  "mcp": {
    "servers": {
      "calcs-api-mcp": {
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
Check API connectivity and health status.
- **Parameters**: None
- **Returns**: API health status and connectivity information

#### `get_tests`
Get all tests for a client.
- **Parameters**: `client` (optional)
- **Returns**: List of all tests with metadata

#### `get_test_status`
Get detailed status and information for a specific test.
- **Parameters**: `test_id` (required), `client` (optional)
- **Returns**: Comprehensive test status including configuration and progress

#### `get_active_clients`
Get list of all active clients.
- **Parameters**: `client` (optional)
- **Returns**: List of active client identifiers

#### `get_site_tests`
Get all tests where a site has treatment or control role.
- **Parameters**: `client_site_id` (required), `client` (optional)
- **Returns**: List of tests involving the specified site

#### `describe_transactions`
Get descriptive overview of the fact_transactions table.
- **Parameters**: `client` (optional)
- **Returns**: Schema and metadata about transaction data structure

### Results & Analytics Tools

#### `get_test_results`
Get test results with advanced filtering options.
- **Parameters**: `test_id` (required), `filter_type` (required: OVERALL, CUSTOMER_COHORT, CUSTOMER_SEGMENT, SITE_COHORT, SITE_PAIR, FINISHED_COHORT, SITE_TAG), `filter_value` (optional), `client` (optional)
- **Returns**: Filtered test results and analytics

#### `get_lift_explorer_results`
Get lift explorer results (JSON equivalent of .avro file contents).
- **Parameters**: `lift_explorer_id` (required), `client` (optional)
- **Returns**: Detailed lift analysis data in JSON format

#### `get_lift_explorer_ids`
Get list of valid lift explorer IDs for client.
- **Parameters**: `client` (optional)
- **Returns**: Available lift explorer identifiers

#### `get_site_pair_lift_manifest`
Get site pair lift manifest data.
- **Parameters**: `test_id` (required), `client` (optional)
- **Returns**: Site pairing and lift calculation metadata

#### `get_prediction_table`
Get prediction table data.
- **Parameters**: `test_id` (required), `client` (optional)
- **Returns**: Prediction model results and forecasts

#### `get_customer_cross`
Get customer cross data.
- **Parameters**: `test_id` (required), `client` (optional)
- **Returns**: Customer cross-correlation analysis

#### `download_all_test_data`
Download comprehensive chart data for a test.
- **Parameters**: `test_id` (required), `client` (optional)
- **Returns**: Complete test data package for visualization and analysis

### Analysis Management Tools

#### `list_analyses`
List all analyses for the current client.
- **Parameters**: `client` (optional)
- **Returns**: List of rollout analyses with metadata

#### `create_analysis`
Create a new rollout analysis.
- **Parameters**: `analysis_data` (required object), `client` (optional)
- **Returns**: Created analysis details

#### `get_analysis`
Get a specific analysis by ID.
- **Parameters**: `analysis_id` (required), `client` (optional)
- **Returns**: Detailed analysis configuration and status

#### `update_analysis`
Update an existing analysis.
- **Parameters**: `analysis_id` (required), `analysis_data` (required object), `client` (optional)
- **Returns**: Updated analysis details

#### `delete_analysis`
Delete an analysis.
- **Parameters**: `analysis_id` (required), `client` (optional)
- **Returns**: Deletion confirmation

#### `run_analysis`
Run rollout analysis synchronously.
- **Parameters**: `analysis_id` (required), `force_refresh` (optional), `client` (optional)
- **Returns**: Complete analysis results

#### `start_analysis`
Start analysis asynchronously with progress tracking.
- **Parameters**: `analysis_id` (required), `force_refresh` (optional), `client` (optional)
- **Returns**: Analysis job information with progress tracking details

#### `get_analysis_results`
Get results of a completed analysis.
- **Parameters**: `analysis_id` (required), `client` (optional)
- **Returns**: Final analysis results and recommendations

### Job & System Monitoring Tools

#### `get_jobs_summary`
Get count of running jobs and compute hours for date range.
- **Parameters**: `start_date` (required, YYYY-MM-DD), `end_date` (required, YYYY-MM-DD), `client` (optional)
- **Returns**: Job statistics and resource usage

#### `get_clients_jobs_summary`
Get job information for all active clients.
- **Parameters**: `start_date` (required, YYYY-MM-DD), `end_date` (required, YYYY-MM-DD), `client` (optional)
- **Returns**: Cross-client job summary and resource allocation

#### `get_oldest_job_date`
Get the date of the oldest job for client.
- **Parameters**: `client` (optional)
- **Returns**: Historical job data boundaries

#### `get_newest_job_date`
Get the date of the newest job for client.
- **Parameters**: `client` (optional)
- **Returns**: Most recent job activity timestamp

## Multi-Tenant Support

The Calcs API supports multi-tenancy through the `client` header. You can:

1. Set a default client using the `CALCS_DEFAULT_CLIENT` environment variable
2. Override the client for specific tool calls by providing the `client` parameter
3. Some administrative tools may require specific client permissions

This allows the same MCP server instance to work with multiple retail clients by specifying the appropriate client parameter in tool calls.

## Error Handling

The server provides comprehensive error handling:

- **Authentication errors**: Invalid or missing bearer tokens
- **Validation errors**: Invalid parameters or missing required fields  
- **API errors**: HTTP errors from the Calcs API with detailed messages
- **Network errors**: Connection failures or timeouts
- **Client errors**: Missing or invalid client headers

All errors are returned in a structured format with descriptive messages and HTTP status codes for debugging.

## Development

### Install dependencies:

```bash
uv sync
```

### Run directly with Python:

```bash
# Run the server module directly (HTTP mode)
uv run python -m calcs_api.server

# Run the server file directly
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
calcs-api-mcp/
├── README.md                    # This file
├── pyproject.toml              # UV project configuration
├── claude-code-config.json     # MCP configuration example
└── calcs_api/
    ├── __init__.py
    └── server.py               # Main server implementation with comprehensive API client
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
- Remove and re-add server: `claude mcp remove calcs-api-mcp && claude mcp add --transport sse calcs-api-mcp http://localhost:8001/messages`

### API Connection Issues

1. **"Missing required environment variable: CALCS_API_TOKEN"**
   - Ensure your bearer token is set in the `.env` file

2. **"API health check failed"**
   - Check your internet connection
   - Verify the API base URL is correct
   - Confirm your bearer token is valid

3. **"Client header required" or 422 errors**
   - Set the `CALCS_DEFAULT_CLIENT` environment variable or provide the `client` parameter in tool calls
   - Ensure client name matches exactly what the API expects

4. **Tool validation errors**
   - Check that all required parameters are provided
   - Ensure parameter types match the expected format (e.g., numbers vs strings)
   - Verify date formats are YYYY-MM-DD for date parameters

### Common Issues
- **Port conflicts**: Change port in `server.py` if 8001 is in use
- **UV not found**: Install UV following instructions at https://docs.astral.sh/uv/
- **Python version**: Ensure Python 3.10+ is available
- **Environment variables**: Ensure `.env` file exists in calcs-api-mcp directory
- **Missing tools**: Restart server after any code changes to pick up new tool definitions

### Debug Mode

Check server logs in the terminal where you started the server for detailed error information including:
- HTTP request/response details
- API authentication status
- Tool execution traces
- Error stack traces

## License

MIT License - see LICENSE file for details.

## Support

For issues related to:
- **This MCP server**: Open an issue in this repository
- **The Calcs API**: Contact your Calcs API provider
- **Claude Code integration**: Refer to Claude Code documentation