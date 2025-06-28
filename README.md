# MCP Servers

A collection of Model Context Protocol (MCP) servers that provide Claude Code with specialized functionality for various development and analytics tasks.

## Current Servers

### calcs-api
MCP server that provides access to the Calcs API for retail analytics calculations and test management. Acts as a bridge between Claude and the Calcs API, offering comprehensive tools for managing A/B tests, analyses, and retrieving retail analytics data.

**Location**: `calcs-api/`
**Documentation**: See individual server README in `calcs-api/README.md`

## Quick Start

### Prerequisites
- Node.js 18 or higher
- npm

### Installation
```bash
# Install all dependencies for all servers
npm run install:all

# Or install individually
npm install              # Root dependencies
cd calcs-api && npm install  # calcs-api dependencies
```

### Building
```bash
# Build all servers
npm run build

# Build specific server
npm run build:calcs-api
```

### Development
```bash
# Run calcs-api in development mode
npm run dev:calcs-api

# Type check all servers
npm run type-check

# Type check specific server
npm run type-check:calcs-api
```

## Available Commands

| Command | Description |
|---------|-------------|
| `npm run build` | Build all MCP servers |
| `npm run build:calcs-api` | Build only the calcs-api server |
| `npm run dev:calcs-api` | Run calcs-api in development mode |
| `npm run start:calcs-api` | Start calcs-api production build |
| `npm run type-check` | Type check all servers |
| `npm run type-check:calcs-api` | Type check calcs-api only |
| `npm run install:all` | Install dependencies for all servers |

## Repository Structure

```
mcp-servers/
├── README.md              # This file
├── CLAUDE.md             # Claude Code guidance
├── package.json          # Root package.json with workspace management
├── calcs-api/            # Calcs API MCP server
│   ├── README.md
│   ├── package.json
│   ├── src/
│   ├── dist/
│   └── examples/
└── [future-server]/      # Additional servers go here
```

## Adding New Servers

To add a new MCP server to this repository:

1. **Create a new directory** for your server (e.g., `my-new-server/`)

2. **Initialize the server** with its own `package.json`:
   ```bash
   mkdir my-new-server
   cd my-new-server
   npm init -y
   ```

3. **Update root package.json** to include your server:
   ```json
   {
     "workspaces": [
       "calcs-api",
       "my-new-server"
     ],
     "scripts": {
       "build": "npm run build:calcs-api && npm run build:my-new-server",
       "build:my-new-server": "cd my-new-server && npm run build",
       "dev:my-new-server": "cd my-new-server && npm run dev"
     }
   }
   ```

4. **Follow MCP server conventions**:
   - Use `"type": "module"` in package.json
   - Entry point should be `dist/index.js` after build
   - Include `build`, `dev`, `start`, and `type-check` scripts
   - Use Node.js 18+ compatible code

5. **Update this README** to document your new server

6. **Add configuration examples** in a `examples/` directory within your server

## Configuration

Each server includes example configuration files for Claude Code integration. See individual server directories for specific setup instructions.

For calcs-api, see `calcs-api/examples/claude-code-config.json` for configuration examples.

## Development Guidelines

- Each server should be self-contained in its own directory
- Follow the existing patterns for package.json scripts
- Include comprehensive documentation in each server's README
- Add configuration examples for easy setup
- Use TypeScript for type safety
- Follow MCP protocol specifications

## License

MIT
