# Windows Deployment Guide

Complete guide for deploying Dexto on Windows environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Configuration](#configuration)
- [Deployment Modes](#deployment-modes)
- [Production Deployment](#production-deployment)
- [Storage Configuration](#storage-configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

1. **Node.js** (≥20.0.0)
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify: `node --version`

2. **pnpm** (≥10.12.4)
   ```powershell
   npm install -g pnpm
   pnpm --version
   ```

3. **Git** (for source builds)
   - Download from [git-scm.com](https://git-scm.com/)

### Optional Dependencies

- **Docker Desktop** (for containerized deployment)
- **Redis** (for production caching)
- **PostgreSQL** (for production database)

## Installation Methods

### Method 1: Global NPM Install (Recommended)

**Easiest method for end users:**

```powershell
# Install globally
npm install -g dexto

# Verify installation
dexto --version

# Run setup wizard
dexto
```

### Method 2: Build from Source

**For developers and contributors:**

```powershell
# Clone repository
git clone https://github.com/truffle-ai/dexto.git
cd dexto

# Install dependencies
pnpm install

# Build all packages (takes ~2 minutes)
pnpm run build:all

# Install CLI globally
pnpm run install-cli

# Verify
dexto --version
```

**What `pnpm run build:all` does:**
- Compiles TypeScript to JavaScript for all 7 packages
- Builds Next.js Web UI in production mode
- Creates standalone deployment bundle
- Copies webui distribution to CLI package

## Configuration

### Initial Setup

```powershell
# Run interactive setup
dexto setup
```

This creates `~/.dexto/config/global.yml` with your preferences.

### Environment Variables

Create `.env` file or set system environment variables:

```env
# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Server Ports
FRONTEND_PORT=3000
API_PORT=3001

# Logging
DEXTO_LOG_LEVEL=info
DEXTO_LOG_TO_CONSOLE=true

# Storage (Production)
REDIS_URL=redis://localhost:6379
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost/dexto

# Telemetry
DEXTO_ANALYTICS_DISABLED=1  # Opt-out
```

**Setting Environment Variables in Windows:**

```powershell
# PowerShell (Current Session)
$env:OPENAI_API_KEY = "sk-..."

# PowerShell (Permanent - User)
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")

# PowerShell (Permanent - System)
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "Machine")

# Command Prompt
set OPENAI_API_KEY=sk-...
setx OPENAI_API_KEY "sk-..."  # Permanent
```

### Agent Configuration

Create custom agents in YAML:

```yaml
# agents/my-custom-agent.yml
version: 1.0.0
name: my-custom-agent
description: Custom agent for specific tasks

llm:
  provider: openai
  model: gpt-4-turbo
  temperature: 0.7
  maxTokens: 4096

tools:
  - name: filesystem
    enabled: true
  - name: browser
    enabled: true
  - name: process
    enabled: true

mcpServers:
  - name: github
    type: stdio
    command: npx
    args: ['-y', '@modelcontextprotocol/server-github']
    env:
      GITHUB_TOKEN: ${GITHUB_TOKEN}

sessions:
  maxSessions: 100
  sessionTTL: 3600000  # 1 hour
  messageHistoryLimit: 100

storage:
  cache:
    type: memory
  database:
    type: sqlite
    filename: ./data/agent.db
```

## Deployment Modes

### 1. Web UI Mode (Default)

**Start with default settings:**
```powershell
dexto
```

**Access:** `http://localhost:3000`

**Custom ports:**
```powershell
dexto --web-port 8080 --api-port 8081
```

**With specific agent:**
```powershell
dexto --agent coding-agent
dexto --agent ./my-agent.yml
```

### 2. CLI Mode (Interactive Terminal)

**Start interactive REPL:**
```powershell
dexto --mode cli
```

**One-shot query:**
```powershell
dexto --mode cli "create a snake game"
```

**Continue last session:**
```powershell
dexto -c --mode cli
```

**Auto-approve tools (for trusted environments):**
```powershell
dexto --mode cli --auto-approve "refactor my code"
```

### 3. API Server Mode

**Start HTTP API server:**
```powershell
dexto --mode server --api-port 4000
```

**Available Endpoints:**
- `POST http://localhost:4000/api/chat` - Send chat message
- `GET http://localhost:4000/api/sessions` - List sessions
- `GET http://localhost:4000/api/sessions/:id` - Get session
- `DELETE http://localhost:4000/api/sessions/:id` - Delete session
- `WebSocket: ws://localhost:4000` - Real-time communication

### 4. MCP Server Mode

**Expose as MCP server:**
```powershell
dexto --mode mcp
```

Connect from Claude Desktop, Cursor, or other MCP clients.

### 5. Bot Modes

**Discord Bot:**
```powershell
# Set token in environment
$env:DISCORD_BOT_TOKEN = "your-bot-token"
dexto --mode discord
```

**Telegram Bot:**
```powershell
$env:TELEGRAM_BOT_TOKEN = "your-bot-token"
dexto --mode telegram
```

## Production Deployment

### Option 1: Windows Service (NSSM)

**Install NSSM (Non-Sucking Service Manager):**

1. Download from [nssm.cc](https://nssm.cc/download)
2. Extract to `C:\nssm`

**Create Windows Service:**

```powershell
# Add NSSM to PATH
$env:Path += ";C:\nssm\win64"

# Install service
nssm install Dexto "C:\Program Files\nodejs\node.exe" "C:\Users\YourUser\AppData\Roaming\npm\node_modules\dexto\dist\index.js"

# Configure service
nssm set Dexto AppDirectory "C:\dexto"
nssm set Dexto AppParameters "--mode server --api-port 4000 --skip-setup --no-interactive"
nssm set Dexto AppEnvironmentExtra OPENAI_API_KEY=sk-...
nssm set Dexto AppStdout "C:\dexto\logs\dexto-stdout.log"
nssm set Dexto AppStderr "C:\dexto\logs\dexto-stderr.log"
nssm set Dexto Start SERVICE_AUTO_START

# Start service
nssm start Dexto

# Check status
nssm status Dexto

# Stop service
nssm stop Dexto

# Remove service
nssm remove Dexto confirm
```

### Option 2: PM2 Process Manager

**Install PM2:**
```powershell
npm install -g pm2
pm2 --version
```

**Create ecosystem file:**

```javascript
// ecosystem.config.cjs
module.exports = {
  apps: [{
    name: 'dexto-api',
    script: 'dexto',
    args: '--mode server --api-port 4000 --skip-setup --no-interactive',
    cwd: 'C:\\dexto',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      OPENAI_API_KEY: 'sk-...',
      FRONTEND_PORT: '3000',
      API_PORT: '4000',
      DEXTO_LOG_LEVEL: 'info'
    },
    error_file: 'C:\\dexto\\logs\\pm2-error.log',
    out_file: 'C:\\dexto\\logs\\pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
```

**Manage with PM2:**

```powershell
# Start application
pm2 start ecosystem.config.cjs

# Check status
pm2 status
pm2 logs dexto-api
pm2 monit

# Save configuration
pm2 save

# Setup startup (requires admin)
pm2 startup
# Run the generated command as administrator

# Stop application
pm2 stop dexto-api

# Restart application
pm2 restart dexto-api

# Delete application
pm2 delete dexto-api
```

### Option 3: Docker (Windows Containers/WSL2)

**Build and run:**

```powershell
# Build image
docker build -t dexto:latest .

# Run container
docker run -d `
  --name dexto-server `
  -p 3000:3000 `
  -p 3001:3001 `
  -e OPENAI_API_KEY=sk-... `
  -e DEXTO_LOG_LEVEL=info `
  -v C:\dexto\data:/app/data `
  -v C:\dexto\logs:/root/.dexto/logs `
  --restart unless-stopped `
  dexto:latest

# View logs
docker logs -f dexto-server

# Stop container
docker stop dexto-server

# Remove container
docker rm dexto-server
```

### Option 4: Docker Compose

**Manage with Docker Compose:**

```powershell
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f dexto

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v

# Rebuild and restart
docker-compose up -d --build
```

## Storage Configuration

### Development (In-Memory)

**Fast, ephemeral storage for testing:**

```yaml
storage:
  cache:
    type: memory
  database:
    type: memory
```

**Pros:** Fast, no setup required  
**Cons:** Data lost on restart

### Simple Persistence (SQLite)

**Single-file database:**

```yaml
storage:
  cache:
    type: memory
  database:
    type: sqlite
    filename: C:/dexto/data/dexto.db
```

**Pros:** Simple, portable, no server required  
**Cons:** Limited concurrency, not suitable for high traffic

### Production (Redis + PostgreSQL)

**Scalable, production-ready:**

```yaml
storage:
  cache:
    type: redis
    url: redis://localhost:6379
    maxConnections: 100
    ttl: 3600  # 1 hour
  database:
    type: postgres
    connectionString: postgresql://user:pass@localhost:5432/dexto
    maxConnections: 25
    ssl: false
```

**Setup Redis on Windows:**

1. Enable WSL2: `wsl --install`
2. Install Redis in WSL: `sudo apt install redis-server`
3. Start Redis: `sudo service redis-server start`
4. Connect: `redis://localhost:6379`

**Setup PostgreSQL on Windows:**

1. Download from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Install and start service
3. Create database:
   ```sql
   CREATE DATABASE dexto;
   CREATE USER dexto_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE dexto TO dexto_user;
   ```
4. Connection string: `postgresql://dexto_user:secure_password@localhost:5432/dexto`

## Troubleshooting

### Path Issues

**Symptom:** `dexto: command not found`

**Solution:**
```powershell
# Check npm global path
npm config get prefix

# Add to PATH (User environment)
$npmPath = npm config get prefix
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "User") + ";$npmPath",
    "User"
)

# Restart PowerShell
```

### Permission Errors

**Symptom:** Access denied during installation

**Solution:**
- Run PowerShell as Administrator
- Or change npm prefix:
  ```powershell
  npm config set prefix C:/npm-global
  $env:Path += ";C:\npm-global"
  ```

### Build Errors

**Symptom:** Build fails during `pnpm run build:all`

**Solution:**
```powershell
# Clear cache and rebuild
pnpm run clean
Remove-Item -Recurse -Force node_modules
pnpm install
pnpm run build:all
```

### Port Conflicts

**Symptom:** `EADDRINUSE: address already in use`

**Solution:**
```powershell
# Check what's using the port
netstat -ano | findstr :3000

# Kill process
taskkill /PID <PID> /F

# Or use different ports
dexto --web-port 8080 --api-port 8081
```

### Module Not Found

**Symptom:** `Cannot find module '@dexto/core'`

**Solution:**
```powershell
# Rebuild packages
cd packages/core
pnpm run build

cd ../cli
pnpm run build

# Reinstall CLI
cd ../..
pnpm run install-cli
```

### WebUI Not Loading

**Symptom:** Web UI shows blank page or 404

**Solution:**
```powershell
# Rebuild WebUI
cd packages/webui
pnpm run build

# Re-embed WebUI
cd ../..
pnpm run embed-webui

# Reinstall CLI
pnpm run install-cli
```

### Logs Not Showing

**Symptom:** No console output

**Solution:**
```powershell
# Enable console logging
$env:DEXTO_LOG_TO_CONSOLE = "true"
$env:DEXTO_LOG_LEVEL = "debug"

# Check log files
Get-Content $env:USERPROFILE\.dexto\logs\dexto.log -Tail 50
```

### API Connection Failed

**Symptom:** Web UI can't connect to API

**Solution:**
1. Verify API is running: `curl http://localhost:3001`
2. Check firewall settings
3. Verify ports match in configuration
4. Check browser console for CORS errors

## Common Commands Reference

```powershell
# Installation
npm install -g dexto                    # Install globally
pnpm run install-cli                    # Install from source

# Starting
dexto                                   # Default (Web UI)
dexto --mode cli                        # CLI mode
dexto --mode server                     # API server only
dexto --web-port 8080                   # Custom port

# Agent Management
dexto list-agents                       # List available agents
dexto install coding-agent              # Install agent
dexto uninstall coding-agent            # Remove agent
dexto --agent coding-agent              # Use specific agent

# Session Management
dexto session list                      # List sessions
dexto session history <id>              # View history
dexto session delete <id>               # Delete session
dexto -c                                # Continue last session
dexto -r <session-id>                   # Resume session

# Development
pnpm install                            # Install dependencies
pnpm run build:all                      # Build all packages
pnpm run dev                            # Development mode
pnpm test                               # Run tests
pnpm run lint                           # Lint code
pnpm run typecheck                      # Type checking

# Logs
Get-Content $env:USERPROFILE\.dexto\logs\dexto.log -Tail 50
```

## Next Steps

1. **Quick Start:** Run `dexto` to open Web UI
2. **Configure:** Set API keys via setup or environment variables
3. **Install Agents:** `dexto install coding-agent nano-banana-agent`
4. **Try a Task:** "create a todo app in HTML"
5. **Production:** Set up Redis + PostgreSQL for scaling

## Additional Resources

- [Main Documentation](https://docs.dexto.ai/)
- [Configuration Guide](https://docs.dexto.ai/docs/guides/configuring-dexto)
- [API Reference](https://docs.dexto.ai/api/)
- [Discord Community](https://discord.gg/GFzWFAAZcm)

