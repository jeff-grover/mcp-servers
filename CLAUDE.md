# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains multiple Model Context Protocol (MCP) servers. Each server is organized in its own subdirectory:

- `calcs-api/` - MCP server that provides access to the Calcs API for retail analytics calculations and test management

The calcs-api server acts as a bridge between Claude and the Calcs API, offering comprehensive tools for managing A/B tests, analyses, and retrieving retail analytics data.

## Development Commands

### Root Level Commands
- `npm run build` - Build all MCP servers
- `npm run build:calcs-api` - Build only the calcs-api server

### Calcs-API Server (in `calcs-api/` directory)
- `npm run build` - Compile TypeScript to JavaScript in `dist/` directory
- `npm run dev` - Run in development mode with auto-reload using tsx
- `npm start` - Run compiled production build from `dist/index.js`
- `npm run type-check` - Check TypeScript types without compilation

### Environment Setup
Required environment variables:
- `CALCS_API_TOKEN` - Bearer token for Calcs API authentication (required)
- `CALCS_API_BASE_URL` - API base URL (optional, defaults to staging)
- `CALCS_DEFAULT_CLIENT` - Default client identifier (optional)

## Architecture

### Core Components

**Entry Point (`calcs-api/src/index.ts`)**
- Initializes MCP server with StdioServerTransport
- Validates environment variables and API connectivity on startup
- Handles tool registration and request routing
- Provides graceful shutdown handling

**API Client (`calcs-api/src/api-client.ts`)**
- Centralized HTTP client for all Calcs API interactions
- Implements flexible client header management (per-request override vs default)
- Comprehensive error handling with structured ApiResponse wrapper
- Supports all API endpoints including test management, results, analysis, and admin functions

**Tool System (`calcs-api/src/tools.ts`)**
- Defines 35+ MCP tools mapped to Calcs API endpoints
- Uses Zod schemas for input validation and type safety
- Consistent error handling and response formatting
- Groups tools by functionality: Test Management, Results, Analysis, Administrative, Utility

**Type Definitions (`calcs-api/src/types.ts`)**
- Complete TypeScript interfaces generated from Calcs API OpenAPI spec
- Enums for status values, filter types, and role definitions
- Generic ApiResponse wrapper for consistent error handling

### Multi-Tenancy Design

The system supports multi-tenant access through a flexible client header system:

1. **Environment Default**: Set `CALCS_DEFAULT_CLIENT` for server-wide default
2. **Per-Request Override**: Any tool can specify `client` parameter to override default
3. **No Client**: If neither provided, no client header sent (may cause API errors)

This allows the same MCP server instance to work with multiple retail clients by specifying the appropriate client parameter in tool calls.

### Error Handling Strategy

- **Validation**: Zod schemas validate all tool inputs before API calls
- **HTTP Errors**: API client wraps HTTP responses in consistent `ApiResponse<T>` format
- **Network Errors**: Fetch errors are caught and returned as structured error responses
- **Tool Errors**: All tool handlers return either data or error objects, never throw

### Data Flow

1. Claude Code calls MCP tool with parameters
2. Tool handler validates input using Zod schema
3. API client makes authenticated HTTP request to Calcs API
4. Response is wrapped in `ApiResponse<T>` format
5. Tool handler returns either data or error to Claude Code

## Key Implementation Details

- Uses ES modules (`"type": "module"`) with `.js` extensions in imports
- Requires Node.js 18+ for modern fetch API support
- All API responses include HTTP status codes for debugging
- Server performs health check on startup to validate configuration
- Supports both synchronous and asynchronous analysis execution
- Comprehensive logging to stderr for debugging (stdout reserved for MCP protocol)