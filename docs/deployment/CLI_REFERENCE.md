# CLI Reference Guide

Complete command-line interface reference for Dexto.

## Table of Contents

- [Overview](#overview)
- [Global Options](#global-options)
- [Commands](#commands)
  - [Project Management](#project-management)
  - [Agent Management](#agent-management)
  - [Session Management](#session-management)
  - [Application Modes](#application-modes)
- [Configuration](#configuration)
- [Environment Variables](#environment-variables)

## Overview

The `dexto` CLI provides a comprehensive interface for:
- Creating and initializing AI agent projects
- Managing agent installations
- Running agents in multiple modes
- Managing chat sessions
- Configuring global preferences

## Global Options

These options apply to all commands unless otherwise specified:

### Agent Selection

```bash
-a, --agent <id|path>
```

Specify which agent to use:
- Registry agent ID: `--agent coding-agent`
- Custom YAML file: `--agent ./my-agent.yml`
- Directory with agent.yml: `--agent ./my-agent-dir/`

**Default**: `default-agent` from global preferences or registry

**Examples**:
```bash
# Use registry agent
dexto --agent coding-agent "create a REST API"

# Use custom agent file
dexto --agent ./custom-agent.yml

# Use agent from directory
dexto --agent ./agents/my-agent/
```

### Model Selection

```bash
-m, --model <model>
```

Override the LLM model for this session:
- `gpt-4-turbo`, `gpt-5-mini` (OpenAI)
- `claude-sonnet-4-5-20250929`, `claude-opus-4` (Anthropic)
- `gemini-2.5-pro`, `gemini-2.5-flash` (Google)
- Any model supported by the configured provider

**Examples**:
```bash
# Use specific model
dexto --model gpt-4-turbo "analyze this code"

# Override agent's default model
dexto --agent coding-agent --model claude-sonnet-4-5 "refactor my code"
```

### Router Selection

```bash
--router <router>
```

Specify the LLM routing strategy:
- `vercel` - Use Vercel AI SDK router (multi-provider support)
- `in-built` - Use Dexto's native LLM client (default)

The router determines how Dexto communicates with LLM providers.

**Examples**:
```bash
# Use Vercel router for advanced features
dexto --router vercel "complex task with multiple models"

# Use native router (default)
dexto --router in-built
```

### Execution Control

```bash
-s, --strict
```

Require all MCP server connections to succeed before starting. By default, Dexto continues even if some servers fail to connect.

**Use cases**:
- Production environments where all tools must be available
- Testing that all MCP servers are properly configured
- Debugging connection issues

**Examples**:
```bash
# Fail fast if any server can't connect
dexto --strict

# Continue even if some servers fail (default)
dexto
```

```bash
--auto-approve
```

Automatically approve all tool executions without confirmation prompts.

**⚠️ Use with caution** - only in trusted environments or for non-destructive operations.

**Examples**:
```bash
# Auto-approve for automation
dexto --auto-approve "read all files in this directory"

# Still requires approval for destructive operations if configured
dexto --auto-approve "analyze my code" # Safe
```

### Session Management

```bash
-c, --continue
```

Continue the most recent conversation in the current context.

**Examples**:
```bash
# Continue where you left off
dexto -c

# Continue with additional prompt
dexto -c "also add error handling"
```

```bash
-r, --resume <sessionId>
```

Resume a specific session by ID.

**Examples**:
```bash
# Resume specific session
dexto -r sess-abc123

# Resume and add prompt
dexto -r sess-abc123 "let's continue working on that API"
```

### Output Control

```bash
--no-verbose
```

Disable verbose output (less logging).

```bash
--no-interactive
```

Disable interactive prompts and API key setup. Useful for:
- CI/CD pipelines
- Automated scripts
- MCP server mode
- Headless environments

**Examples**:
```bash
# Run non-interactively
dexto --no-interactive --mode server

# Combine with skip-setup for full automation
dexto --no-interactive --skip-setup --mode mcp
```

```bash
--skip-setup
```

Skip global setup validation. Use when:
- Running in MCP mode
- Automation/CI where setup is pre-configured
- Testing custom agents

### Agent Installation

```bash
--no-auto-install
```

Disable automatic installation of missing agents from registry.

By default, if you reference an agent that isn't installed, Dexto will offer to install it automatically.

**Examples**:
```bash
# Don't auto-install missing agents
dexto --no-auto-install --agent new-agent
```

### One-Shot Execution

```bash
-p, --prompt <text>
```

Run a single prompt and exit. Alternative to providing prompt as positional argument.

**Examples**:
```bash
# Using --prompt flag
dexto --prompt "create a snake game"

# Using positional argument (same result)
dexto "create a snake game"

# With options
dexto --agent coding-agent --prompt "refactor my code"
```

### Application Mode

```bash
--mode <mode>
```

Choose how Dexto runs:
- `web` (default) - Web UI + API server
- `cli` - Interactive terminal REPL
- `server` - API server only
- `discord` - Discord bot
- `telegram` - Telegram bot
- `mcp` - MCP server

See [Application Modes](#application-modes) for details.

### Port Configuration

```bash
--web-port <port>
```

Port for the web UI (default: 3000).

```bash
--api-port <port>
```

Port for the API server (default: web-port + 1).

**Examples**:
```bash
# Custom ports
dexto --web-port 8080 --api-port 8081

# API port auto-calculated
dexto --web-port 8080  # API will be 8081
```

## Commands

### Project Management

#### create-app

Scaffold a new Dexto TypeScript application with all necessary boilerplate.

```bash
dexto create-app
```

**Interactive prompts**:
1. Project directory name
2. LLM provider (openai, anthropic, google, groq, etc.)
3. API key (or set via environment variable)
4. Create example file (yes/no)

**What it creates**:
```
my-dexto-app/
├── package.json          # With dexto dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── .env                  # API keys and configuration
├── agents/
│   └── default-agent.yml # Agent configuration
└── src/
    └── example.ts        # Example code (optional)
```

**Generated scripts**:
- `npm run dev` - Development mode
- `npm run build` - Build for production
- `npm start` - Start the agent

**Examples**:
```bash
# Create new project
dexto create-app

# Follow prompts to set up your project
```

**Next steps after creation**:
```bash
cd my-dexto-app
npm install
npm run dev
```

#### init-app

Initialize an existing project as a Dexto application. Use this when you want to add Dexto to an existing codebase.

```bash
dexto init-app
```

**Interactive prompts**:
1. Source code directory (e.g., `src/`)
2. Create example file (yes/no)
3. LLM provider
4. API key

**What it does**:
- Adds Dexto dependencies to `package.json`
- Creates `agents/` directory with default agent
- Adds Dexto scripts to `package.json`
- Creates `.env` file for configuration
- Optionally creates example file

**Use cases**:
- Adding AI capabilities to existing app
- Migrating from another AI framework
- Setting up Dexto in a monorepo

**Examples**:
```bash
# In existing project directory
cd my-existing-app
dexto init-app

# Follow prompts to configure Dexto
```

#### setup

Configure global Dexto preferences (stored in `~/.dexto/config/global.yml`).

```bash
dexto setup [options]
```

**Options**:
- `--provider <provider>` - LLM provider (openai, anthropic, google, groq)
- `--model <model>` - Default model name
- `--default-agent <agent>` - Default agent to use
- `--no-interactive` - Skip interactive prompts
- `--force` - Overwrite existing setup without confirmation

**Interactive setup**:
1. Choose LLM provider
2. Enter API key (validates the key)
3. Select default model
4. Choose default agent

**What it configures**:
```yaml
# ~/.dexto/config/global.yml
llm:
  provider: openai
  model: gpt-4-turbo
  apiKey: $OPENAI_API_KEY

defaults:
  agent: coding-agent

setup:
  completed: true
  timestamp: 2025-01-15T10:30:00Z
```

**Examples**:
```bash
# Interactive setup
dexto setup

# Non-interactive with options
dexto setup --provider openai --model gpt-4-turbo --no-interactive

# Force reconfigure
dexto setup --force

# Set default agent
dexto setup --default-agent coding-agent
```

### Agent Management

#### install

Install agents from the Dexto agent registry or from custom YAML files/directories.

```bash
dexto install [agents...] [options]
```

**Arguments**:
- `agents...` - One or more agent IDs, YAML files, or directories

**Options**:
- `--all` - Install all available agents from registry
- `--no-inject-preferences` - Don't inject global LLM preferences into installed agents
- `--force` - Force reinstall even if agent is already installed

**Install sources**:
1. **Registry agents**: By agent ID (e.g., `coding-agent`)
2. **YAML files**: Path to `.yml` file (e.g., `./my-agent.yml`)
3. **Directories**: Path to directory containing `agent.yml`

**Examples**:
```bash
# Install single registry agent
dexto install coding-agent

# Install multiple registry agents
dexto install coding-agent nano-banana-agent podcast-agent

# Install all available agents
dexto install --all

# Install from custom YAML file
dexto install ./custom-agent.yml

# Install from directory
dexto install ./my-agent-dir/

# Force reinstall
dexto install coding-agent --force

# Install without injecting global preferences
dexto install coding-agent --no-inject-preferences
```

**Where agents are installed**:
- Registry agents: `~/.dexto/agents/<agent-id>/`
- Custom agents: `~/.dexto/agents/<directory-name>/`

#### uninstall

Uninstall agents from local installation.

```bash
dexto uninstall [agents...] [options]
```

**Arguments**:
- `agents...` - One or more agent IDs to uninstall

**Options**:
- `--all` - Uninstall all installed agents
- `--force` - Force uninstall protected agents (e.g., `default-agent`)

**Examples**:
```bash
# Uninstall single agent
dexto uninstall coding-agent

# Uninstall multiple agents
dexto uninstall coding-agent nano-banana-agent

# Uninstall all agents
dexto uninstall --all

# Force uninstall protected agent
dexto uninstall default-agent --force
```

**Protected agents**:
- `default-agent` - Requires `--force` to uninstall

#### list-agents

List available and installed agents.

```bash
dexto list-agents [options]
```

**Options**:
- `--verbose` - Show detailed agent information
- `--installed` - Show only installed agents
- `--available` - Show only available agents from registry

**Output format**:

**Default view**:
```
Available Agents (from registry):
  ✓ coding-agent - AI coding assistant
  ✓ nano-banana-agent - Image generation agent
    podcast-agent - Podcast creation agent

Installed Agents:
  → default-agent (v1.0.0)
  → coding-agent (v1.2.0)
```

**Verbose view**:
```
coding-agent (installed)
  Version: 1.2.0
  Description: AI coding assistant with file system access
  Tools: filesystem, browser, process
  Location: ~/.dexto/agents/coding-agent/
```

**Examples**:
```bash
# List all agents
dexto list-agents

# Show only installed
dexto list-agents --installed

# Show only available
dexto list-agents --available

# Detailed information
dexto list-agents --verbose

# Installed with details
dexto list-agents --installed --verbose
```

#### which

Show the path to an installed agent.

```bash
dexto which <agent>
```

**Arguments**:
- `agent` - Agent ID to locate

**Examples**:
```bash
# Show agent path
dexto which coding-agent
# Output: /Users/you/.dexto/agents/coding-agent/coding-agent.yml

# Show default agent
dexto which default-agent
# Output: /Users/you/.dexto/agents/default-agent.yml

# Agent not found
dexto which nonexistent-agent
# Error: Agent 'nonexistent-agent' not found
```

**Use cases**:
- Verify agent installation location
- Debug agent resolution issues
- Find agent configuration file for editing

### Session Management

#### session list

List all chat sessions.

```bash
dexto session list
```

**Output format**:
```
Sessions:
  sess-abc123 - "Create REST API" (5 messages) - 2025-01-15
  sess-def456 - "Snake game" (12 messages) - 2025-01-14
  sess-ghi789 - "Code review" (3 messages) - 2025-01-13
```

**Examples**:
```bash
# List all sessions
dexto session list

# With specific agent
dexto --agent coding-agent session list
```

#### session history

Show the message history for a session.

```bash
dexto session history [sessionId]
```

**Arguments**:
- `sessionId` - Session ID to view (optional, defaults to current session)

**Output format**:
```
Session: sess-abc123 "Create REST API"
Created: 2025-01-15 10:30:00

[user]: Create a REST API with Express
[assistant]: I'll create a REST API using Express. Let me start by...
[tool]: filesystem:write_file
  File: server.js
  Status: Success
[assistant]: I've created a basic Express API with the following features...
```

**Examples**:
```bash
# View specific session
dexto session history sess-abc123

# View current session (in resume mode)
dexto -r sess-abc123 session history

# With agent context
dexto --agent coding-agent session history sess-abc123
```

#### session delete

Delete a session and its history.

```bash
dexto session delete <sessionId>
```

**Arguments**:
- `sessionId` - Session ID to delete (required)

**Examples**:
```bash
# Delete specific session
dexto session delete sess-abc123

# Confirmation prompt appears
# Are you sure you want to delete session sess-abc123? (y/N)
```

**⚠️ Warning**: This action is permanent and cannot be undone.

#### search

Search session history across all sessions or within a specific session.

```bash
dexto search <query> [options]
```

**Arguments**:
- `query` - Search query (required)

**Options**:
- `--session <sessionId>` - Search in specific session only
- `--role <role>` - Filter by message role (user, assistant, system, tool)
- `--limit <number>` - Limit number of results (default: 10)

**Output format**:
```
Found 3 results:

Session: sess-abc123 - "Create REST API"
  [user]: Can you create a REST API with Express?
  [assistant]: I'll create a REST API using Express...

Session: sess-def456 - "API documentation"
  [user]: Document the REST API endpoints
  ...
```

**Examples**:
```bash
# Search all sessions
dexto search "REST API"

# Search in specific session
dexto search "error handling" --session sess-abc123

# Filter by role
dexto search "function" --role assistant

# Limit results
dexto search "bug" --limit 5

# Combined filters
dexto search "API" --session sess-abc123 --role user --limit 3
```

**Use cases**:
- Find previous solutions
- Review conversation history
- Debug issues
- Extract information from past sessions

### Application Modes

#### Default Action (No Command)

When no command is specified, Dexto runs in the mode specified by `--mode` option or defaults to `web` mode.

```bash
dexto [prompt] [options]
```

**Arguments**:
- `prompt` - Optional prompt to execute immediately

**Modes**:

##### web (default)

Full-featured web interface with visual configuration.

```bash
dexto
dexto --mode web
dexto --web-port 8080
```

**Features**:
- Visual chat interface at `http://localhost:3000`
- Session management UI
- Agent configuration interface
- MCP playground
- Tool approval interface
- Settings and preferences

**Use cases**:
- Development and testing
- Demos and presentations
- Personal use
- Visual agent configuration

##### cli

Interactive terminal REPL.

```bash
dexto --mode cli
dexto --mode cli "create a snake game"
```

**Features**:
- Markdown rendering
- Session continuity
- Command history
- Tool execution in terminal
- Syntax highlighting

**Commands in CLI mode**:
- `/exit` - Exit the REPL
- `/model <model>` - Switch LLM model
- `/session` - Show current session info
- `/help` - Show available commands

**Use cases**:
- SSH sessions
- Scripting and automation
- Terminal-only environments
- Quick one-off tasks

##### server

API server only (no UI).

```bash
dexto --mode server
dexto --mode server --api-port 4000
```

**Endpoints**:
- `POST /api/chat` - Send messages
- `GET /api/sessions` - List sessions
- `GET /api/sessions/:id` - Get session details
- `DELETE /api/sessions/:id` - Delete session
- `WebSocket /` - Real-time communication

**Use cases**:
- Integration with custom UIs
- Mobile app backends
- Multi-client support
- Programmatic access

##### discord

Discord bot integration.

```bash
export DISCORD_BOT_TOKEN="your-bot-token"
dexto --mode discord
```

**Setup**:
1. Create Discord application at https://discord.com/developers
2. Add bot to your application
3. Copy bot token
4. Set `DISCORD_BOT_TOKEN` environment variable
5. Invite bot to your server
6. Start Dexto in discord mode

**Bot commands**:
- Mention the bot with your message
- Direct messages work automatically

**Use cases**:
- Team collaboration
- Community support
- Shared AI assistant

##### telegram

Telegram bot integration.

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
dexto --mode telegram
```

**Setup**:
1. Create bot via @BotFather on Telegram
2. Copy bot token
3. Set `TELEGRAM_BOT_TOKEN` environment variable
4. Start Dexto in telegram mode

**Bot commands**:
- `/start` - Initialize bot
- `/ask <message>` - Send message to agent
- Direct messages work automatically

**Use cases**:
- Mobile-first interaction
- Personal AI assistant
- Quick queries on the go

##### mcp

Model Context Protocol server mode.

```bash
dexto --mode mcp
```

Exposes Dexto as an MCP server that can be connected to from:
- Claude Desktop
- Cursor IDE
- Other MCP clients

**Configuration for Claude Desktop**:
```json
{
  "mcpServers": {
    "dexto": {
      "command": "dexto",
      "args": ["--mode", "mcp", "--skip-setup", "--no-interactive"]
    }
  }
}
```

**Use cases**:
- Integration with Claude Desktop
- IDE integration
- Tool aggregation
- Multi-client setups

## Configuration

### Agent YAML Schema

Complete agent configuration reference:

```yaml
# Agent card metadata (optional)
agentCard:
  name: my-agent
  description: Description of what this agent does
  version: 1.0.0
  provider:
    organization: Your Organization
    url: https://example.com
  documentationUrl: https://docs.example.com

# Greeting message (optional)
greeting: "Hello! I'm your AI assistant."

# LLM configuration (required)
llm:
  provider: openai              # openai, anthropic, google, groq, etc.
  model: gpt-4-turbo           # Model name
  apiKey: $OPENAI_API_KEY      # API key (use env var)
  
  # Optional LLM parameters
  temperature: 0.7             # 0.0-2.0, controls randomness
  maxTokens: 4096              # Maximum tokens in response
  topP: 1.0                    # Nucleus sampling parameter
  frequencyPenalty: 0.0        # -2.0 to 2.0
  presencePenalty: 0.0         # -2.0 to 2.0
  
  # Optional: Media types to expand for LLM
  allowedMediaTypes:
    - "image/*"                # All images
    - "application/pdf"        # PDFs
    - "audio/*"                # Audio files

# MCP servers (optional)
mcpServers:
  filesystem:
    type: stdio
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "."]
  
  custom:
    type: stdio
    command: node
    args: ["./custom-server.js"]
    env:
      API_KEY: $CUSTOM_API_KEY

# System prompt configuration (optional)
systemPrompt:
  contributors:
    - id: primary
      type: static
      priority: 0
      content: |
        You are a helpful AI assistant.
    
    - id: dateTime
      type: dynamic
      priority: 10
      source: dateTime
      enabled: true
    
    - id: memories
      type: memory
      priority: 40
      enabled: true
      options:
        includeTimestamps: false
        includeTags: true
        limit: 10
        pinnedOnly: false

# Storage configuration (optional)
storage:
  cache:
    type: in-memory             # in-memory, redis
    # Redis options (if type: redis)
    # url: redis://localhost:6379
    # maxConnections: 100
    # ttl: 3600
  
  database:
    type: sqlite                # sqlite, postgres, in-memory
    # SQLite options
    # path: ./data/dexto.db
    # Postgres options (if type: postgres)
    # connectionString: postgresql://user:pass@host/db
    # maxConnections: 25
  
  blob:
    type: local                 # local, s3, gcs, azure (s3/gcs/azure coming soon)
    maxBlobSize: 52428800       # 50MB per blob
    maxTotalSize: 1073741824    # 1GB total
    cleanupAfterDays: 30        # Auto-cleanup threshold
    # storePath: ~/.dexto/blobs # Optional custom path

# Tool confirmation (optional)
toolConfirmation:
  mode: event-based             # event-based, auto-approve, disabled
  timeout: 120000               # Timeout in ms
  allowedToolsStorage: memory   # memory, storage
  
  toolPolicies:
    alwaysAllow:
      - internal--ask_user
      - mcp--read_file
    alwaysDeny:
      - mcp--delete_file

# Elicitation (optional)
elicitation:
  enabled: true                 # Enable ask_user tool
  timeout: 120000               # Timeout for user input

# Internal tools (optional)
internalTools:
  - ask_user                    # Allows agent to ask questions

# Internal resources (optional)
internalResources:
  enabled: true
  resources:
    - type: filesystem
      paths: ["."]
      maxFiles: 50
      maxDepth: 3
      includeHidden: false
      includeExtensions: [".txt", ".md", ".json", ".yaml"]
    
    - type: blob                # Large file storage

# Starter prompts (optional)
starterPrompts:
  - id: quick-start
    title: "📚 Quick Start"
    description: "Get started quickly"
    prompt: "Show me what you can do"
    category: learning
    priority: 9

# Plugins (optional)
plugins:
  contentPolicy:
    priority: 10
    blocking: true
    maxInputChars: 50000
    redactEmails: true
    redactApiKeys: true
    enabled: true
  
  responseSanitizer:
    priority: 900
    blocking: false
    redactEmails: true
    redactApiKeys: true
    maxResponseLength: 100000
    enabled: true

# Telemetry (optional)
telemetry:
  serviceName: my-agent
  enabled: true
  tracerName: my-tracer
  export:
    type: otlp                  # otlp, console
    protocol: http              # http, grpc
    endpoint: http://localhost:4318/v1/traces
    headers:
      Authorization: Bearer token
```

## Environment Variables

### LLM Provider API Keys

```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Google
export GOOGLE_GENERATIVE_AI_API_KEY=...

# Groq
export GROQ_API_KEY=gsk_...
```

### Application Configuration

```bash
# Ports
export FRONTEND_PORT=3000
export API_PORT=3001

# Logging
export DEXTO_LOG_LEVEL=info          # debug, info, warn, error
export DEXTO_LOG_TO_CONSOLE=true     # true, false

# Telemetry
export DEXTO_ANALYTICS_DISABLED=1    # Opt-out of analytics
```

### Storage Configuration

```bash
# Redis
export REDIS_URL=redis://localhost:6379

# PostgreSQL
export POSTGRES_CONNECTION_STRING=postgresql://user:pass@host/db

# S3 (future)
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_REGION=us-east-1
```

### Bot Configuration

```bash
# Discord
export DISCORD_BOT_TOKEN=...

# Telegram
export TELEGRAM_BOT_TOKEN=...
```

## Common Command Patterns

### Development Workflow

```bash
# Create new project
dexto create-app

# Install additional agents
dexto install coding-agent nano-banana-agent

# Run in development mode
dexto --mode cli

# Test with specific agent
dexto --agent coding-agent "create a test API"

# Continue previous work
dexto -c
```

### Production Workflow

```bash
# Setup global configuration
dexto setup --provider openai --no-interactive

# Install required agents
dexto install coding-agent database-agent

# Run API server
dexto --mode server --api-port 4000 --skip-setup --no-interactive

# Or run web UI
dexto --mode web --web-port 8080 --skip-setup
```

### Agent Development

```bash
# Create agent project
dexto create-app

# Edit agent configuration
vim agents/my-agent/my-agent.yml

# Test agent locally
dexto --agent ./agents/my-agent/

# Install to global registry
dexto install ./agents/my-agent/

# Use installed agent
dexto --agent my-agent
```

### Session Management

```bash
# List all sessions
dexto session list

# Review session history
dexto session history sess-abc123

# Search for information
dexto search "error handling" --session sess-abc123

# Resume previous session
dexto -r sess-abc123 "continue the implementation"

# Clean up old sessions
dexto session delete sess-abc123
```

## Tips & Best Practices

### 1. Use Environment Variables for API Keys

Never hardcode API keys in agent YAML files. Always use environment variables:

```yaml
llm:
  apiKey: $OPENAI_API_KEY  # ✅ Good
  # apiKey: sk-abc123...   # ❌ Bad
```

### 2. Create Project-Specific Agents

Use `create-app` or `init-app` to create project-specific agent configurations:

```bash
cd my-project
dexto init-app
# Edit agents/default-agent.yml for project needs
```

### 3. Use Specific Agents for Tasks

Install and use task-specific agents for better results:

```bash
dexto install coding-agent
dexto --agent coding-agent "refactor my code"
```

### 4. Leverage Session Management

Resume previous sessions to maintain context:

```bash
# Start work
dexto "create a REST API"

# Later, continue
dexto -c "add authentication"

# Or resume by ID
dexto -r sess-abc123 "add rate limiting"
```

### 5. Test with --strict

Use `--strict` to ensure all MCP servers connect:

```bash
dexto --strict  # Fail fast if servers don't connect
```

### 6. Automate with --no-interactive

For scripts and CI/CD:

```bash
dexto --no-interactive --skip-setup --auto-approve --mode server
```

## Troubleshooting

### Command Not Found

```bash
# Verify installation
which dexto

# Check npm global path
npm config get prefix

# Add to PATH
export PATH="$PATH:$(npm config get prefix)/bin"
```

### Agent Not Found

```bash
# Check installation
dexto list-agents --installed

# Show agent path
dexto which coding-agent

# Install if missing
dexto install coding-agent
```

### API Key Issues

```bash
# Verify environment variable
echo $OPENAI_API_KEY

# Run setup to configure
dexto setup

# Test with explicit model
dexto --model gpt-4-turbo "test"
```

### Session Issues

```bash
# List sessions
dexto session list

# Delete corrupted session
dexto session delete sess-abc123

# Start fresh session
dexto --no-continue
```

## See Also

- [Quick Start Guide](QUICK_START.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [Windows Deployment](WINDOWS_DEPLOYMENT.md)
- [Configuration Reference](https://docs.dexto.ai/docs/guides/configuring-dexto)
- [API Reference](https://docs.dexto.ai/api/)

