#!/usr/bin/env node

import 'dotenv/config';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import { CalcsApiClient } from './api-client.js';
import { createTools, handleToolCall } from './tools.js';
import { CalcsApiConfig } from './types.js';

// Environment variable validation
function getRequiredEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

function getOptionalEnv(name: string, defaultValue: string): string {
  return process.env[name] || defaultValue;
}

async function main() {
  try {
    // Load configuration from environment variables
    const config: CalcsApiConfig = {
      baseUrl: getOptionalEnv('CALCS_API_BASE_URL', 'https://staging-app.marketdial.dev/calcs'),
      bearerToken: getRequiredEnv('CALCS_API_TOKEN'),
      defaultClient: getOptionalEnv('CALCS_DEFAULT_CLIENT', '')
    };

    // Validate bearer token
    if (!config.bearerToken) {
      throw new Error('CALCS_API_TOKEN environment variable is required');
    }

    // Initialize API client
    const apiClient = new CalcsApiClient(config);

    // Test connection
    console.error('Testing API connection...');
    const healthResult = await apiClient.healthCheck();
    if (healthResult.error) {
      console.error(`API health check failed: ${healthResult.error}`);
      process.exit(1);
    }
    console.error('API connection successful');

    // Create MCP server
    const server = new Server(
      {
        name: 'calcs-api-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Get tools
    const tools = createTools(apiClient);

    // Handle list tools request
    server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools,
      };
    });

    // Handle tool calls
    server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      console.error(`Handling tool call: ${name} with args:`, JSON.stringify(args, null, 2));
      
      try {
        const result = await handleToolCall(name, args || {}, apiClient);
        
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        console.error(`Tool execution error:`, errorMessage);
        
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ error: errorMessage }, null, 2),
            },
          ],
          isError: true,
        };
      }
    });

    // Start server
    const transport = new StdioServerTransport();
    await server.connect(transport);
    
    console.error('Calcs API MCP Server started successfully');
    console.error(`Base URL: ${config.baseUrl}`);
    console.error(`Default client: ${config.defaultClient || 'None (must be specified per request)'}`);
    
  } catch (error) {
    console.error('Failed to start server:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

// Handle process termination
process.on('SIGINT', async () => {
  console.error('Received SIGINT, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.error('Received SIGTERM, shutting down gracefully...');
  process.exit(0);
});

// Start the server
main().catch((error) => {
  console.error('Unhandled error:', error);
  process.exit(1);
});