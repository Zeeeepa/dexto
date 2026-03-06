# Dexto Deployment Guide - Complete Reference

**Last Updated:** November 8, 2025  
**Version:** 2.0 - Unified Deployment Documentation

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Operations](#operations)
5. [Deployment Infrastructure Analysis](#deployment-infrastructure-analysis)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)

---

# Quick Start

Get Dexto running in just a few steps!

## Prerequisites (5 Minutes)

**Required:**
- Node.js 20+ ([Download](https://nodejs.org/))
- 4 GB RAM minimum
- 2 GB disk space

**Supported Platforms:**
- Windows 10/11
- Linux (Ubuntu, CentOS, Arch)
- macOS 10.15+

## Installation (2 Minutes)

### Option 1: Python Setup (Recommended - Cross-Platform)

```bash
# Clone or download Dexto
cd /path/to/dexto

# Run setup script
python setup.py

# Or with options
python setup.py --advanced    # Advanced mode with retry/rollback
python setup.py --no-setup    # Skip interactive setup
```

### Option 2: Manual Installation

```bash
# Install dependencies
pnpm install

# Build all packages
pnpm run build:all

# Install CLI globally
pnpm run install-cli

# Run setup
dexto setup
```

## Start Dexto (30 Seconds)

```bash
# Start with Python script
python start.py

# Or directly with CLI
dexto

# With specific mode
python start.py --mode web --web-port 3000
python start.py --mode cli
python start.py --mode server --api-port 3001
```

## Common Commands

```bash
# Check status
python start.py --status

# Stop Dexto
python start.py --stop

# Configure
dexto setup

# List agents
dexto list-agents --installed
```

---

# Installation

## System Requirements

### Minimum Requirements
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disk:** 2 GB free space
- **OS:** Windows 10+, Linux (kernel 4.0+), macOS 10.15+
- **Node.js:** 20.0.0 or higher
- **npm:** 10.0.0 or higher
- **pnpm:** 9.0.0 or higher

### Recommended for Production
- **CPU:** 4+ cores
- **RAM:** 8+ GB
- **Disk:** 10+ GB free space (with logs)
- **Network:** Stable internet connection
- **OS:** Latest LTS version

## Prerequisites Installation

### Windows

```powershell
# Install Node.js from official website
# https://nodejs.org/ - Download LTS version

# Install pnpm globally
npm install -g pnpm

# Verify installation
node --version
npm --version
pnpm --version
```

### Linux (Ubuntu/Debian)

```bash
# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install pnpm
npm install -g pnpm

# Verify
node --version
npm --version
pnpm --version
```

### macOS

```bash
# Using Homebrew
brew install node@20
brew install pnpm

# Or using nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
npm install -g pnpm
```

## Installation Methods

### Method 1: Python Setup Script (Recommended)

The unified `setup.py` script provides cross-platform installation with advanced features:

```bash
# Basic installation
python setup.py

# Advanced installation with retry/rollback
python setup.py --advanced

# Skip interactive setup wizard
python setup.py --no-setup

# Specify log directory
python setup.py --log-dir /path/to/logs

# Help
python setup.py --help
```

**Features:**
- ✅ Automatic prerequisite checking
- ✅ Retry logic with exponential backoff (3 attempts)
- ✅ Automatic rollback on failure
- ✅ Detailed timestamped logging
- ✅ API key validation
- ✅ Cross-platform support (Windows, Linux, macOS)
- ✅ Progress indicators
- ✅ Error recovery suggestions

### Method 2: From Source

```bash
# Clone repository
git clone https://github.com/Zeeeepa/dexto.git
cd dexto

# Install and build
pnpm install
pnpm run build:all
pnpm run install-cli

# Verify
dexto --version
```

### Method 3: Docker

```bash
# Build image
docker build -t dexto .

# Run container
docker run -d --name dexto \
  -p 3000:3000 -p 3001:3001 \
  -e OPENAI_API_KEY=your_key \
  dexto
```

## Post-Installation

### Verify Installation

```bash
# Check version
dexto --version

# List available agents
dexto list-agents

# Check health (after starting)
curl http://localhost:3001/health
```

### Configure API Keys

```bash
# Interactive setup
dexto setup

# Or set environment variables
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_GENERATIVE_AI_API_KEY="..."
```

### First Run

```bash
# Start in web mode (default)
dexto

# Access UI
open http://localhost:3000
```

---

# Configuration

## Configuration Files

### Global Configuration

Location: `~/.dexto/config/global.yml`

```yaml
# Global preferences
llm:
  provider: openai
  model: gpt-4
  apiKey: $OPENAI_API_KEY

defaultAgent: default-agent

# Optional settings
telemetry:
  enabled: true
  endpoint: https://telemetry.dexto.ai
```

### Agent Configuration

Location: `~/.dexto/agents/{agent-name}/agent.yml`

```yaml
name: my-agent
description: My custom agent

llm:
  provider: anthropic
  model: claude-sonnet-4-5-20250929
  temperature: 0.7
  maxOutputTokens: 4096

mcp:
  servers:
    filesystem:
      type: stdio
      command: npx
      args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/workspace"]
```

## Environment Variables

### Core Settings

```bash
# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_GENERATIVE_AI_API_KEY=...

# Dexto Configuration
DEXTO_LOG_LEVEL=info          # debug, info, warn, error
NODE_ENV=production            # development, production
PORT=3001                      # API server port

# Advanced
DEXTO_TELEMETRY_ENABLED=true
DEXTO_MAX_RETRIES=3
DEXTO_TIMEOUT_MS=30000
```

### Setting Environment Variables

**Windows:**
```cmd
setx OPENAI_API_KEY "sk-..."
```

**Linux/macOS:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY="sk-..."
```

## Configuration via Setup Script

```bash
# Run interactive setup
python setup.py

# Setup includes:
# 1. API key configuration
# 2. Default agent selection
# 3. LLM provider preferences
# 4. MCP server setup
# 5. Telemetry opt-in/out
```

---

# Operations

## Starting Dexto

### Using Python Script (Recommended)

```bash
# Start in web mode (UI + API)
python start.py

# Start in CLI mode
python start.py --mode cli

# Start API server only
python start.py --mode server

# Start Discord bot
python start.py --mode discord

# Start Telegram bot
python start.py --mode telegram

# Start MCP server
python start.py --mode mcp

# Custom ports
python start.py --web-port 8080 --api-port 8081

# Background mode (daemon)
python start.py --daemon

# With custom agent
python start.py --agent my-custom-agent
```

### Using CLI Directly

```bash
# Web mode
dexto --mode web

# CLI mode
dexto --mode cli

# Server mode
dexto --mode server --api-port 3001
```

## Operational Modes

### 1. Web Mode
- Full web UI on port 3000
- API server on port 3001
- Best for: Interactive development, demos

```bash
python start.py --mode web
# Access: http://localhost:3000
```

### 2. CLI Mode
- Terminal-based interface
- Interactive chat in terminal
- Best for: Quick queries, automation scripts

```bash
python start.py --mode cli
```

### 3. Server Mode
- API-only, no UI
- RESTful endpoints + WebSocket
- Best for: Production deployments, integrations

```bash
python start.py --mode server
```

### 4. Discord Bot Mode
- Connects to Discord
- Responds to mentions and DMs
- Best for: Team collaboration

```bash
# Requires DISCORD_BOT_TOKEN
export DISCORD_BOT_TOKEN=...
python start.py --mode discord
```

### 5. Telegram Bot Mode
- Connects to Telegram
- Private and group chats
- Best for: Mobile access

```bash
# Requires TELEGRAM_BOT_TOKEN
export TELEGRAM_BOT_TOKEN=...
python start.py --mode telegram
```

### 6. MCP Server Mode
- Model Context Protocol server
- For Claude Desktop, IDEs
- Best for: Development tools integration

```bash
python start.py --mode mcp
```

## Monitoring & Status

### Check Status

```bash
# Using start script
python start.py --status

# Output example:
# Status: RUNNING
# Mode: web
# PID: 12345
# Uptime: 2h 15m
# Web UI: http://localhost:3000
# API: http://localhost:3001
```

### Health Checks

```bash
# API health endpoint
curl http://localhost:3001/health

# Response:
# {
#   "status": "healthy",
#   "version": "1.2.4",
#   "uptime": 8145,
#   "llm": "connected",
#   "mcp": "connected"
# }
```

### Logs

```bash
# View logs
tail -f ~/.dexto/logs/dexto.log

# Installation logs
tail -f ~/.dexto/logs/installation_*.log

# With Python script
python start.py --show-logs
```

## Stopping Dexto

```bash
# Graceful shutdown
python start.py --stop

# Force stop
python start.py --stop --force

# Or press Ctrl+C in terminal
```

## Updating Dexto

```bash
# Pull latest changes
git pull origin main

# Rebuild
python setup.py --advanced

# Or manually
pnpm install
pnpm run build:all
```

---

# Deployment Infrastructure Analysis

## Executive Summary

This section documents critical gaps identified in Dexto's deployment infrastructure through comprehensive codebase analysis.

**Overall Risk Level:** 🔴 **HIGH**  
**Total Gaps Identified:** 14 critical infrastructure gaps  
**Priority Distribution:** 3 P0 (Critical) | 4 P1 (High) | 4 P2 (Medium) | 3 P3 (Low)

## AI Provider Resilience

### GAP #1: No Automatic LLM Provider Failover ❌ P0

**Status:** NOT IMPLEMENTED

**Current State:**
- Manual `switchLLM()` method exists
- NO automatic fallback when provider fails
- Single point of failure for OpenAI/Anthropic
- No circuit breaker pattern

**Impact:**
- System becomes unusable if primary provider is down
- Users must manually switch providers
- Cascading failures waste resources

**Evidence:**
```typescript
// packages/core/src/agent/DextoAgent.ts
public async switchLLM(updates: LLMUpdates): Promise<ValidatedLLMConfig> {
    // Manual switch only - no automatic failover
}
```

**Recommended Solution:**
```typescript
interface FailoverConfig {
    enabled: boolean;
    providers: LLMProvider[];  // Ordered list
    maxRetries: number;
    backoffMs: number;
}

class LLMFailoverManager {
    async executeWithFailover<T>(
        operation: () => Promise<T>,
        config: FailoverConfig
    ): Promise<T> {
        // Try primary provider
        // On failure, try fallback providers
        // Implement circuit breaker
    }
}
```

### GAP #2: No Rate Limit Handling ❌ P0

**Status:** NOT IMPLEMENTED

**Current State:**
- `ErrorType.RATE_LIMIT` defined but unused
- No exponential backoff strategy
- No request queuing
- No provider rotation on rate limits

**Impact:**
- Rate-limited requests fail immediately
- No recovery mechanism
- Lost requests, poor UX

**Recommended Solution:**
```typescript
class RateLimitHandler {
    async handleRateLimit(error: Error): Promise<void> {
        // Exponential backoff: 1s, 2s, 4s, 8s, 16s
        // Queue requests if enabled
        // Rotate to alternate provider
    }
}
```

### GAP #3: No Circuit Breaker ⚠️ P1

**Status:** PARTIALLY IMPLEMENTED

**Current State:**
- Error handling exists
- NO circuit breaker to prevent repeated failures
- No health checks before calls

**Recommended Solution:**
```typescript
enum CircuitState { CLOSED, OPEN, HALF_OPEN }

class CircuitBreaker {
    async execute<T>(operation: () => Promise<T>): Promise<T> {
        if (this.state === CircuitState.OPEN) {
            throw new Error('Circuit breaker open');
        }
        // Execute and track failures
    }
}
```

## Error Handling & Recovery

### GAP #4: No Rollback Mechanism ❌ P0 (FIXED in setup.py)

**Status:** ✅ IMPLEMENTED in Python setup script

**Solution Implemented:**
- Automatic backup before installation
- Rollback on failure
- Restore previous working state
- See `setup.py` for implementation

### GAP #5: No Retry Logic ❌ P1 (FIXED in setup.py)

**Status:** ✅ IMPLEMENTED in Python setup script

**Solution Implemented:**
- 3 retry attempts with exponential backoff
- 5s → 10s → 20s delays
- Handles transient network failures
- See `setup.py` for implementation

### GAP #6: Limited Error Logging ⚠️ P2 (FIXED in setup.py)

**Status:** ✅ IMPLEMENTED in Python setup script

**Solution Implemented:**
- Timestamped logging
- Saved to `~/.dexto/logs/`
- Error categorization
- Recovery suggestions

## Infrastructure Gaps

### GAP #7: No Health Checks ❌ P1

**Status:** NOT IMPLEMENTED

**Needed:**
- `/health` endpoint validation
- Readiness probes
- Liveness checks
- Script validation after startup

### GAP #8: No Service Watchdog ❌ P1

**Status:** NOT IMPLEMENTED

**Needed:**
- Auto-restart on crash
- Process monitoring
- Graceful degradation
- Unattended operation support

### GAP #9: No Environment Profiles ❌ P2

**Status:** NOT IMPLEMENTED

**Needed:**
- dev/staging/production separation
- Environment variable validation
- Profile-specific configuration

### GAP #10: No Log Rotation ❌ P2

**Status:** NOT IMPLEMENTED

**Needed:**
- Automatic log rotation (10MB limit)
- Log compression
- Retention policies
- Disk space management

### GAP #11: No Version Management ❌ P2

**Status:** NOT IMPLEMENTED

**Needed:**
- Version tracking
- Rollback to specific versions
- Compatibility checks
- Upgrade path documentation

## Production Readiness

### GAP #12-14: Monitoring, Tracking, Disaster Recovery ❌ P3

**Status:** NOT IMPLEMENTED

**Needed:**
- Performance monitoring
- Deployment analytics
- Backup strategies
- RTO/RPO definitions

## Priority Matrix

| Gap | Severity | Impact | Effort | Priority | Status |
|-----|----------|--------|--------|----------|--------|
| #1: LLM Failover | 🔴 Critical | High | Medium | P0 | ❌ TODO |
| #2: Rate Limiting | 🔴 Critical | High | Low | P0 | ❌ TODO |
| #4: Rollback | 🔴 Critical | High | Low | P0 | ✅ DONE |
| #5: Retry Logic | 🟡 High | Medium | Low | P1 | ✅ DONE |
| #3: Circuit Breaker | 🟡 High | Medium | Medium | P1 | ❌ TODO |
| #7: Health Checks | 🟡 High | Medium | Low | P1 | ❌ TODO |
| #8: Watchdog | 🟡 High | High | Medium | P1 | ❌ TODO |
| #6: Error Logging | 🟢 Medium | Low | Low | P2 | ✅ DONE |
| #9: Env Profiles | 🟢 Medium | Medium | Low | P2 | ❌ TODO |
| #10: Log Rotation | 🟢 Medium | Low | Low | P2 | ❌ TODO |
| #11: Versioning | 🟢 Medium | Low | Low | P2 | ❌ TODO |
| #12-14: Monitoring | 🟢 Low | Medium | High | P3 | ❌ TODO |

## Implementation Roadmap

### Phase 1: Critical Resilience (P0) - Week 1
1. ✅ Rollback mechanism (DONE in setup.py)
2. ❌ LLM provider failover
3. ❌ Rate limit handling

### Phase 2: Error Handling (P1) - Week 2
4. ✅ Retry logic (DONE in setup.py)
5. ❌ Circuit breaker
6. ❌ Health checks
7. ❌ Service watchdog

### Phase 3: Operational Excellence (P2) - Week 3
8. ✅ Error logging (DONE in setup.py)
9. ❌ Environment profiles
10. ❌ Log rotation
11. ❌ Version tracking

### Phase 4: Production Hardening (P3) - Week 4
12. ❌ Performance monitoring
13. ❌ Deployment tracking
14. ❌ Disaster recovery

---

# Advanced Features

## Advanced Installation

The Python `setup.py` script provides enterprise-grade installation features:

### Automatic Retry with Exponential Backoff

Handles transient failures gracefully:

```python
# Retry logic built into setup.py
# Attempt 1: Wait 5s on failure
# Attempt 2: Wait 10s on failure  
# Attempt 3: Wait 20s on failure
```

**Benefits:**
- Network hiccups don't cause permanent failure
- Automatic recovery from temporary issues
- No manual restart required

### Automatic Rollback on Failure

Protects against failed installations:

```python
# Before installation
1. Backup existing node_modules
2. Attempt installation
3. On failure: Remove failed, restore backup
4. On success: Remove backup
```

**Benefits:**
- No broken state after failed install
- Automatic recovery to working state
- No manual cleanup needed

### Detailed Timestamped Logging

Complete audit trail:

```bash
# Log location: ~/.dexto/logs/installation_YYYYMMDD_HHMMSS.log

[2025-11-08 19:45:23] [INFO] Starting installation
[2025-11-08 19:45:24] [1/8] Checking prerequisites
[2025-11-08 19:45:25] [OK] Prerequisites verified
...
```

**Benefits:**
- Debug issues easily
- Track installation history
- Audit trail for compliance

### API Key Validation

Checks configuration before completion:

```python
# Validates presence of:
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- GOOGLE_GENERATIVE_AI_API_KEY

# Warns if none configured
```

### Comprehensive Error Recovery

Actionable suggestions on failure:

```
Installation failed. Check log file: ~/.dexto/logs/installation_...

Common issues and solutions:
  - Network failure: Check internet connection
  - Permission issues: Run with sudo/admin
  - Disk space: Ensure 2+ GB free
  - Antivirus: Temporarily disable
```

## Advanced Operations

### Background Mode (Daemon)

```bash
# Start as background process
python start.py --daemon

# Check if running
python start.py --status

# Stop daemon
python start.py --stop
```

### Custom Configuration

```bash
# Specify custom config file
python start.py --config /path/to/config.yml

# Override settings via CLI
python start.py --llm-provider anthropic --llm-model claude-sonnet-4-5
```

### Health Monitoring

```bash
# Enable health checks
python start.py --health-check-interval 30

# Health check endpoint
curl http://localhost:3001/health
```

---

# Troubleshooting

## Installation Issues

### Node.js Not Found

**Symptoms:**
- "node: command not found"
- "npm: command not found"

**Solution:**
```bash
# Install Node.js 20+
# Windows: https://nodejs.org/
# Linux: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
# macOS: brew install node@20

# Verify
node --version  # Should be >= 20.0.0
```

### pnpm Not Found

**Symptoms:**
- "pnpm: command not found"

**Solution:**
```bash
npm install -g pnpm
pnpm --version
```

### Installation Fails

**Symptoms:**
- Build errors
- Network timeouts
- Permission denied

**Solutions:**
```bash
# Use advanced installer with retry
python setup.py --advanced

# Run with elevated privileges
sudo python setup.py  # Linux/macOS
# Run as Administrator (Windows)

# Check logs
cat ~/.dexto/logs/installation_*.log
```

### Rollback Failed

**Symptoms:**
- Installation failed, rollback didn't restore

**Solution:**
```bash
# Manual rollback
cd /path/to/dexto
rm -rf node_modules
mv node_modules.backup node_modules

# Or reinstall
python setup.py --advanced
```

## Runtime Issues

### Port Already in Use

**Symptoms:**
- "Error: listen EADDRINUSE: address already in use"

**Solutions:**
```bash
# Use different port
python start.py --web-port 8080

# Find and kill process
# Linux/macOS:
lsof -ti:3000 | xargs kill -9

# Windows:
netstat -ano | findstr :3000
taskkill /PID <pid> /F
```

### Command Not Found

**Symptoms:**
- "dexto: command not found" after installation

**Solutions:**
```bash
# Restart terminal
# Or add npm global to PATH

# Linux/macOS:
export PATH="$PATH:$(npm config get prefix)/bin"

# Windows:
set PATH=%PATH%;%APPDATA%\npm
```

### LLM API Errors

**Symptoms:**
- "OpenAI API key not found"
- "Rate limit exceeded"
- "Connection timeout"

**Solutions:**
```bash
# Configure API keys
dexto setup

# Or set environment variables
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Check key validity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## Performance Issues

### High Memory Usage

**Symptoms:**
- Process using > 2GB RAM
- System slowdown

**Solutions:**
```bash
# Reduce max output tokens
# In agent.yml:
llm:
  maxOutputTokens: 2048  # Reduce from 4096

# Enable message compression
messages:
  compression:
    - type: oldest
      minMessagesToKeep: 10
```

### Slow Response Times

**Symptoms:**
- Responses take > 30s
- Timeout errors

**Solutions:**
```bash
# Use faster model
dexto setup
# Select gpt-4o-mini or claude-haiku

# Increase timeout
export DEXTO_TIMEOUT_MS=60000
```

## Common Errors

### "Module not found"

**Solution:**
```bash
pnpm install
pnpm run build:all
```

### "Permission denied"

**Solution:**
```bash
# Linux/macOS
sudo python setup.py

# Windows: Run as Administrator
```

### "ENOSPC: no space left on device"

**Solution:**
```bash
# Free up disk space (need 2+ GB)
df -h  # Check available space

# Clean npm cache
npm cache clean --force
```

## Getting Help

### Log Files

```bash
# Installation logs
~/.dexto/logs/installation_*.log

# Runtime logs
~/.dexto/logs/dexto.log

# View recent errors
tail -n 50 ~/.dexto/logs/dexto.log | grep ERROR
```

### Debug Mode

```bash
# Enable debug logging
export DEXTO_LOG_LEVEL=debug
python start.py

# Or
dexto --log-level debug
```

### Support Channels

- 📖 Documentation: https://docs.dexto.ai
- 💬 Discord: https://discord.gg/dexto
- 🐛 GitHub Issues: https://github.com/Zeeeepa/dexto/issues
- 📧 Email: support@dexto.ai

---

## Appendix

### File Locations

```
~/.dexto/
├── config/
│   ├── global.yml          # Global preferences
│   └── agents/             # Agent configurations
├── logs/
│   ├── installation_*.log  # Setup logs
│   └── dexto.log          # Runtime logs
├── data/
│   └── database.db        # SQLite database
└── cache/                 # Cached data
```

### Configuration Reference

See [Configuration](#configuration) section for complete reference.

### API Reference

**REST API Endpoints:**
- `GET /health` - Health check
- `POST /api/message` - Send message
- `POST /api/reset` - Reset conversation
- `GET /api/mcp/servers` - List MCP servers
- `POST /api/llm/switch` - Switch LLM provider

**WebSocket:**
- `ws://localhost:3001/` - Real-time events

Full API docs: https://docs.dexto.ai/api

---

**End of Deployment Guide** - For updates, see https://github.com/Zeeeepa/dexto

