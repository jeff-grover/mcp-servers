# Calcs API MCP Server

A Model Context Protocol (MCP) server that provides Claude Code with access to the Calcs API for retail analytics calculations and test management.

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

- Node.js 18 or higher
- A valid Calcs API bearer token
- Access to the Calcs API (default: `https://staging-app.marketdial.dev/calcs`)

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Build the TypeScript code:
   ```bash
   npm run build
   ```

## Configuration

The server requires the following environment variables:

### Required
- `CALCS_API_TOKEN`: Your bearer token for the Calcs API

### Optional
- `CALCS_API_BASE_URL`: Base URL for the Calcs API (default: `https://staging-app.marketdial.dev/calcs`)
- `CALCS_DEFAULT_CLIENT`: Default client identifier to use when not specified in tool calls

## Usage

### Running the Server

#### Development Mode
```bash
npm run dev
```

#### Production Mode
```bash
npm run build
npm start
```

### Environment Variables Setup

Create a `.env` file in the project root:

```env
CALCS_API_TOKEN=your_bearer_token_here
CALCS_DEFAULT_CLIENT=your_client_name
CALCS_API_BASE_URL=https://staging-app.marketdial.dev/calcs
```

### Integration with Claude Code

Add the server to your Claude Code MCP configuration. The exact method depends on your setup, but typically involves adding it to your MCP configuration file.

Example configuration entry:
```json
{
  "calcs-api": {
    "command": "node",
    "args": ["/path/to/calcs-api-mcp-server/dist/index.js"],
    "env": {
      "CALCS_API_TOKEN": "your_token_here",
      "CALCS_DEFAULT_CLIENT": "your_client_name"
    }
  }
}
```

## Available Tools

### Test Management Tools

#### `get_tests`
Get all tests for a client.
- **Parameters**: `client` (optional)

#### `get_test_status`
Get the status of a specific test.
- **Parameters**: `test_id` (required), `client` (optional)

#### `get_test_sites`
Get treatment and control sites for a test.
- **Parameters**: `test_id` (required), `client` (optional)

#### `get_cohort_id`
Get the hashed cohort ID for a test.
- **Parameters**: `test_id`, `impl_start_date`, `test_start_date` (required), `blockouts_string`, `client` (optional)

### Results Tools

#### `get_test_results`
Get test results with optional filtering.
- **Parameters**: `test_id`, `filter_type` (required), `filter_value`, `client` (optional)
- **Filter Types**: `OVERALL`, `CUSTOMER_COHORT`, `CUSTOMER_SEGMENT`, `SITE_COHORT`, `SITE_PAIR`, `FINISHED_COHORT`, `SITE_TAG`

#### `get_lift_explorer_results`
Get lift explorer results.
- **Parameters**: `lift_explorer_id` (required), `client` (optional)

#### `get_site_pair_lift_manifest`
Get site pair lift manifest for a test.
- **Parameters**: `test_id` (required), `client` (optional)

#### `get_prediction_table`
Get prediction table for a test.
- **Parameters**: `test_id` (required), `client` (optional)

#### `get_customer_cross`
Get customer cross data for a test.
- **Parameters**: `test_id` (required), `client` (optional)

#### `download_all_test_data`
Download all chart data for a test.
- **Parameters**: `test_id` (required), `client` (optional)

### Analysis Management Tools

#### `get_analyses`
Get all analyses for a client.
- **Parameters**: `client` (optional)

#### `get_analysis`
Get a specific analysis by ID.
- **Parameters**: `analysis_id` (required), `client` (optional)

#### `create_analysis`
Create a new analysis.
- **Parameters**: `name`, `description`, `measurementLength`, `startDate`, `hasImplementationPeriod` (required), plus optional parameters

#### `update_analysis`
Update an existing analysis.
- **Parameters**: `analysis_id` (required), plus optional update fields

#### `delete_analysis`
Delete an analysis.
- **Parameters**: `analysis_id` (required), `client` (optional)

#### `run_analysis`
Run an analysis synchronously.
- **Parameters**: `analysis_id` (required), `force_refresh`, `client` (optional)

#### `start_analysis`
Start an analysis asynchronously.
- **Parameters**: `analysis_id` (required), `force_refresh`, `client` (optional)

#### `get_analysis_results`
Get results of a completed analysis.
- **Parameters**: `analysis_id` (required), `client` (optional)

### Administrative Tools

#### `get_active_clients`
Get all active clients.
- **Parameters**: `client` (optional)

#### `get_jobs_summary`
Get summary of jobs in a date range.
- **Parameters**: `start_date`, `end_date` (required), `client` (optional)

#### `get_oldest_job_date` / `get_newest_job_date`
Get the oldest/newest job date for a client.
- **Parameters**: `client` (optional)

### Utility Tools

#### `health_check`
Check API health status.
- **Parameters**: None

#### `ping`
Simple ping test to check API accessibility.
- **Parameters**: `client` (optional)

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

### Scripts

- `npm run build`: Compile TypeScript to JavaScript
- `npm run dev`: Run in development mode with auto-reload
- `npm run type-check`: Check TypeScript types without compilation

### Project Structure

```
src/
├── index.ts          # Main server entry point
├── api-client.ts     # Calcs API client implementation
├── tools.ts          # MCP tool definitions and handlers
└── types.ts          # TypeScript type definitions
```

## Troubleshooting

### Common Issues

1. **"Missing required environment variable: CALCS_API_TOKEN"**
   - Ensure your bearer token is set in the environment variables

2. **"API health check failed"**
   - Check your internet connection
   - Verify the API base URL is correct
   - Confirm your bearer token is valid

3. **"Client header required"**
   - Set the `CALCS_DEFAULT_CLIENT` environment variable or provide the `client` parameter in tool calls

4. **Tool validation errors**
   - Check that all required parameters are provided
   - Ensure parameter types match the expected format (e.g., numbers vs strings)

### Debug Mode

Run with debug output:
```bash
DEBUG=* npm run dev
```

## License

MIT License - see LICENSE file for details.

## Support

For issues related to:
- **This MCP server**: Open an issue in this repository
- **The Calcs API**: Contact your Calcs API provider
- **Claude Code integration**: Refer to Claude Code documentation