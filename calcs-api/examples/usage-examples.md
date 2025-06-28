# Calcs API MCP Server Usage Examples

This document provides examples of how to use the Calcs API MCP server with Claude Code.

## Getting Started

Once the MCP server is configured and running, you can use these tools in your conversations with Claude Code.

## Test Management Examples

### Get All Tests
```
Show me all the tests for our client.
```

### Get Test Details
```
Get the status of test ID 12345.
```

### Get Test Sites
```
Show me the treatment and control sites for test "summer-promotion-2024".
```

## Results and Analytics Examples

### Get Test Results
```
Get the overall results for test ID 12345.
```

### Get Specific Filter Results
```
Get the CUSTOMER_COHORT results for test ID 12345 with filter value 100.
```

### Get Lift Explorer Data
```
Show me the lift explorer results for exploration ID "abc123".
```

### Get Prediction Table
```
Get the prediction table data for test 12345.
```

## Analysis Management Examples

### List All Analyses
```
Show me all the rollout analyses we have.
```

### Create a New Analysis
```
Create a new rollout analysis with the following parameters:
- Name: "Q4 Holiday Campaign Analysis"
- Description: "Analysis of holiday promotions across retail locations"
- Measurement Length: 8 weeks
- Start Date: "2024-11-01"
- Has Implementation Period: true
- Implementation Length: 2 weeks
```

### Run an Analysis
```
Run the analysis with ID "analysis-456" and force a refresh of the data.
```

### Get Analysis Results
```
Get the results for analysis ID "analysis-456".
```

## Administrative Examples

### Get Client Information
```
Show me all active clients in the system.
```

### Get Job Summary
```
Get a summary of all jobs that ran between 2024-01-01 and 2024-01-31.
```

### Check System Health
```
Check if the Calcs API is healthy and responding.
```

## Data Management Examples

### List Uploaded Files
```
Show me all the adhoc files that have been uploaded.
```

### Get File Column Information
```
Show me the column names for the file "sales_data_2024.csv".
```

### Describe Transaction Data
```
Give me an overview of the transaction data available.
```

## Complex Workflow Examples

### Complete Test Analysis Workflow
```
I want to analyze test ID 12345. Please:
1. Get the test status and basic information
2. Get the treatment and control sites
3. Get the overall test results
4. Get the site pair lift manifest
5. Get the prediction table data
```

### Analysis Creation and Execution Workflow
```
Create a new analysis for our Q1 performance review:
- Name: "Q1 Performance Analysis"
- Description: "Quarterly review of all promotional activities"
- 12-week measurement period starting 2024-01-01
- Include implementation period of 2 weeks
- Then run the analysis immediately
```

### Client Health Check Workflow
```
I want to check the health of our Calcs API integration:
1. Run a health check
2. Test the ping endpoint
3. Get the oldest and newest job dates
4. Get a job summary for the last 30 days
```

## Multi-Client Examples

If you're working with multiple clients, you can specify the client in your requests:

### Specify Client in Request
```
Get all tests for client "retailer-abc".
```

### Switch Between Clients
```
Show me the job summary for client "retailer-xyz" from 2024-01-01 to 2024-01-31.
```

## Error Handling Examples

The MCP server provides detailed error messages when things go wrong:

### Invalid Test ID
```
Get the status of test ID 99999.
```
Response: `{"error": "HTTP 404: Not Found"}`

### Missing Required Parameters
```
Create an analysis without specifying the required name field.
```
Response: `{"error": "Validation error: name: Required"}`

### Invalid Date Format
```
Get job summary with invalid date format.
```
Response: `{"error": "Validation error: start_date: Invalid date format"}`

## Best Practices

1. **Always check test status** before trying to get results
2. **Use specific filter types** when getting test results to reduce data size
3. **Specify client explicitly** when working with multiple tenants
4. **Check health endpoints** if you encounter connection issues
5. **Use descriptive analysis names** for better organization

## Tips for Claude Code Users

- The MCP server automatically handles authentication using your configured bearer token
- All responses are returned as JSON for easy processing
- Error messages are designed to be helpful for debugging
- The server supports both synchronous and asynchronous analysis execution