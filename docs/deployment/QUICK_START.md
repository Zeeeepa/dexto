# Quick Start Guide

Get Dexto up and running in 5 minutes.

## Installation

### Option 1: NPM (Fastest)

```bash
npm install -g dexto
dexto
```

### Option 2: From Source

```bash
git clone https://github.com/truffle-ai/dexto.git
cd dexto
pnpm install
pnpm run build:all
pnpm run install-cli
dexto
```

## First Run

### 1. Start Dexto

```bash
dexto
```

This opens the Web UI at `http://localhost:3000` and starts the API server on `http://localhost:3001`.

### 2. Configure API Keys

On first run, Dexto will prompt you to configure:

- **LLM Provider** (OpenAI, Anthropic, Google, etc.)
- **API Key** for your chosen provider
- **Default Model** to use

**Alternatively, set via environment:**

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
dexto
```

### 3. Try Your First Prompt

In the Web UI, try:

```
create a snake game in HTML/CSS/JS, then open it in the browser
```

Dexto will:
1. Use filesystem tools to create the files
2. Write the HTML, CSS, and JavaScript
3. Use browser tools to open the game

## Usage Modes

### Web UI (Default)

```bash
dexto
# Opens http://localhost:3000
```

**Features:**
- Visual chat interface
- Session management
- Agent configuration
- MCP playground
- Tool approval interface

### CLI Mode

```bash
dexto --mode cli
```

**Features:**
- Interactive terminal REPL
- Markdown rendering
- Session continuity
- Tool execution in terminal

**One-shot mode:**
```bash
dexto "create a REST API in Python"
```

### API Server Mode

```bash
dexto --mode server --api-port 4000
```

**Endpoints:**
- `POST /api/chat` - Send messages
- `GET /api/sessions` - List sessions
- `WebSocket /` - Real-time communication

### MCP Server Mode

```bash
dexto --mode mcp
```

Connect from Claude Desktop, Cursor, or other MCP clients.

## Common Tasks

### Use Different Models

```bash
# Via CLI flag
dexto --model gpt-4-turbo

# Switch in session
> /model gpt-4-turbo
> /model claude-sonnet-4-5
```

### Install Pre-built Agents

```bash
# List available agents
dexto list-agents

# Install agents
dexto install coding-agent nano-banana-agent

# Use installed agent
dexto --agent coding-agent
```

### Continue Previous Session

```bash
# Continue most recent
dexto -c

# Resume specific session
dexto -r <session-id>

# List sessions
dexto session list
```

### Auto-approve Tools

```bash
# Skip confirmation prompts
dexto --auto-approve "refactor my codebase"
```

⚠️ **Use with caution** - only in trusted environments

### Custom Ports

```bash
dexto --web-port 8080 --api-port 8081
```

## Configuration Files

### Global Config

Located at `~/.dexto/config/global.yml`:

```yaml
version: 1.0.0
llm:
  provider: openai
  model: gpt-4-turbo
  apiKey: ${OPENAI_API_KEY}

telemetry:
  enabled: false
```

### Custom Agents

Create in `~/.dexto/agents/` or project directory:

```yaml
# my-agent.yml
version: 1.0.0
name: my-agent
description: Custom agent

llm:
  provider: openai
  model: gpt-4-turbo

tools:
  - name: filesystem
    enabled: true
  - name: browser
    enabled: true

mcpServers:
  - name: github
    type: stdio
    command: npx
    args: ['-y', '@modelcontextprotocol/server-github']
```

Use it:
```bash
dexto --agent ./my-agent.yml
```

## Environment Variables

```bash
# LLM API Keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GOOGLE_API_KEY=...

# Ports
export FRONTEND_PORT=3000
export API_PORT=3001

# Logging
export DEXTO_LOG_LEVEL=debug
export DEXTO_LOG_TO_CONSOLE=true

# Telemetry
export DEXTO_ANALYTICS_DISABLED=1
```

## Project Structure

```
~/.dexto/                    # User data directory
├── config/
│   └── global.yml          # Global configuration
├── agents/                 # Installed agents
├── logs/
│   └── dexto.log          # Application logs
└── storage/               # Session data
```

## Tips & Tricks

### 1. Pipe Input to Dexto

```bash
cat README.md | dexto "summarize this file"
```

### 2. Use Agents for Specific Tasks

```bash
# Image generation
dexto --agent nano-banana-agent "create a sunset scene"

# Podcast creation
dexto --agent podcast-agent "create intro about AI"

# Code development
dexto --agent coding-agent "build a REST API"
```

### 3. Session Management

```bash
# Search history
dexto search "bug fix" --role assistant

# View session history
dexto session history <session-id>

# Delete old sessions
dexto session delete <session-id>
```

### 4. Development Mode

```bash
# Build and watch for changes
pnpm run dev

# Run with debug logs
DEXTO_LOG_LEVEL=debug dexto
```

### 5. Custom MCP Servers

Add to your agent YAML:

```yaml
mcpServers:
  - name: custom-server
    type: stdio
    command: node
    args: ['/path/to/server.js']
  
  - name: http-server
    type: http
    url: http://localhost:8080/mcp
```

## Troubleshooting

### "Command not found: dexto"

```bash
# Check npm global path
npm config get prefix

# Add to PATH
export PATH="$PATH:$(npm config get prefix)/bin"
```

### "Port already in use"

```bash
# Use different port
dexto --web-port 8080

# Or kill process using port 3000
lsof -ti:3000 | xargs kill -9
```

### "Module not found"

```bash
# Rebuild from source
cd dexto
pnpm run clean
pnpm install
pnpm run build:all
pnpm run install-cli
```

### "API connection failed"

1. Verify API is running: `curl http://localhost:3001`
2. Check firewall settings
3. Try different port: `dexto --api-port 8081`

## Next Steps

- **[Full Documentation](https://docs.dexto.ai/)** - Comprehensive guides
- **[Configuration Guide](https://docs.dexto.ai/docs/guides/configuring-dexto)** - Advanced setup
- **[Agent Registry](https://docs.dexto.ai/docs/guides/agent-registry)** - Pre-built agents
- **[API Reference](https://docs.dexto.ai/api/)** - SDK documentation
- **[Discord Community](https://discord.gg/GFzWFAAZcm)** - Get help & share projects

## Common Commands Cheat Sheet

```bash
# Starting
dexto                                  # Web UI
dexto --mode cli                       # CLI mode
dexto --mode server                    # API only

# Agents
dexto list-agents                      # List available
dexto install coding-agent             # Install
dexto --agent coding-agent             # Use

# Sessions
dexto -c                               # Continue last
dexto session list                     # List all
dexto session delete <id>              # Delete

# Configuration
dexto setup                            # Re-run setup
dexto --model gpt-4-turbo             # Use specific model
dexto --auto-approve                   # Skip prompts

# Development
pnpm run dev                           # Dev mode
pnpm test                              # Run tests
pnpm run lint                          # Lint code
```

---

**Need help?** Join our [Discord](https://discord.gg/GFzWFAAZcm) or check the [docs](https://docs.dexto.ai/)!

