# Mode Comparison Guide

Dexto offers 6 different operational modes, each optimized for specific use cases. This guide helps you choose the right mode for your needs.

## Quick Comparison

| Mode | Use Case | Interface | Multi-User | Setup Complexity |
|------|----------|-----------|------------|------------------|
| **web** | Development, demos | Browser UI | ❌ Single | ⭐ Easy |
| **cli** | Terminal work, automation | Terminal REPL | ❌ Single | ⭐ Easy |
| **server** | Custom integrations | REST API + WebSocket | ✅ Multi | ⭐⭐ Medium |
| **discord** | Team collaboration | Discord chat | ✅ Multi | ⭐⭐ Medium |
| **telegram** | Mobile-first, personal | Telegram chat | ✅ Multi | ⭐⭐ Medium |
| **mcp** | IDE integration | MCP protocol | ❌ Single | ⭐⭐⭐ Advanced |

## Mode Details

### Web Mode (Default)

```bash
dexto
dexto --mode web --web-port 8080
```

**Best for:**
- 🎨 Development and testing
- 👥 Demos and presentations
- 🏠 Personal use
- ⚙️ Visual agent configuration
- 🔧 MCP playground

**Features:**
- **Visual Chat Interface**: Rich, interactive chat UI
- **Session Management**: Browse and resume past conversations
- **Agent Configuration**: Visual editor for agent settings
- **Tool Approval**: UI for reviewing and approving tool executions
- **MCP Playground**: Test and configure MCP servers visually
- **Settings Panel**: Manage API keys, preferences, and more
- **Starter Prompts**: Quick-access buttons for common tasks

**Architecture:**
- Web UI: Next.js standalone server on port 3000
- API: Express server on port 3001
- Both processes managed by main dexto process

**Startup:**
```bash
$ dexto
✓ Starting web UI on http://localhost:3000
✓ Starting API server on http://localhost:3001
✓ MCP servers initialized
→ Open http://localhost:3000 in your browser
```

**Pros:**
- ✅ Most intuitive for new users
- ✅ Visual feedback for all operations
- ✅ Easy to configure and test agents
- ✅ Best debugging experience

**Cons:**
- ❌ Single user only
- ❌ Requires browser
- ❌ Higher resource usage (2 processes)

**When to use:**
- First-time setup and configuration
- Developing and testing new agents
- Giving demos or presentations
- Learning Dexto's capabilities
- Visual MCP server management

**When NOT to use:**
- Production multi-user deployments
- Headless/server environments
- CI/CD pipelines
- Mobile-only access

---

### CLI Mode

```bash
dexto --mode cli
dexto --mode cli "create a snake game"
```

**Best for:**
- 💻 Terminal-only environments
- 🔁 SSH sessions
- 📜 Scripting and automation
- ⚡ Quick one-off tasks

**Features:**
- **Interactive REPL**: Persistent chat session in terminal
- **Markdown Rendering**: Formatted responses with syntax highlighting
- **Session Continuity**: Resume with `-c` or `-r` flags
- **Command History**: Up/down arrows to navigate history
- **Terminal Integration**: Direct tool output in terminal
- **REPL Commands**:
  - `/exit` - Exit the REPL
  - `/model <model>` - Switch LLM model mid-session
  - `/session` - Show current session info
  - `/help` - Show available commands

**Architecture:**
- Single process
- Direct terminal I/O
- No web UI or server

**Startup:**
```bash
$ dexto --mode cli
╭─────────────────────────────────────────────╮
│ Dexto AI Assistant                          │
│ Model: gpt-4-turbo                          │
│ Type your message or '/help' for commands  │
╰─────────────────────────────────────────────╯

> create a snake game

[Assistant]: I'll create a snake game...
```

**Pros:**
- ✅ Lightweight (single process)
- ✅ Fast startup
- ✅ Works over SSH
- ✅ Great for automation
- ✅ Terminal-native workflows

**Cons:**
- ❌ No visual interface
- ❌ Limited markdown rendering
- ❌ Single user
- ❌ No tool approval UI (auto-approve or reject)

**When to use:**
- Working on remote servers via SSH
- Automating tasks with shell scripts
- Terminal-only development environments
- Quick queries without UI overhead
- Integration with terminal-based workflows

**When NOT to use:**
- Need visual feedback
- Complex tool approval workflows
- Multiple concurrent users
- Rich media interactions

**Pro Tips:**
```bash
# One-shot execution
dexto --mode cli "your prompt here" && exit

# Continue previous work
dexto --mode cli -c

# Auto-approve tools for automation
dexto --mode cli --auto-approve "analyze logs"

# Resume specific session
dexto --mode cli -r sess-abc123
```

---

### Server Mode

```bash
dexto --mode server --api-port 4000
```

**Best for:**
- 🔌 Custom frontend integrations
- 📱 Mobile app backends
- 🌐 Multi-client support
- 🔄 Programmatic API access

**Features:**
- **REST API**: Full HTTP API for all operations
- **WebSocket**: Real-time bidirectional communication
- **Multi-Client**: Handle concurrent users
- **Stateless Design**: Session management via API
- **Standard Auth**: Bearer tokens, API keys

**API Endpoints:**

**Chat & Sessions:**
- `POST /api/chat` - Send messages
- `POST /api/sessions` - Create session
- `GET /api/sessions` - List sessions
- `GET /api/sessions/:id` - Get session details
- `GET /api/sessions/:id/history` - Get message history
- `DELETE /api/sessions/:id` - Delete session
- `PATCH /api/sessions/:id` - Update session metadata

**Agent Management:**
- `GET /api/agents` - List available agents
- `GET /api/agents/:id` - Get agent details
- `POST /api/agents/install` - Install agent
- `DELETE /api/agents/:id` - Uninstall agent

**MCP Management:**
- `GET /api/mcp/servers` - List MCP servers
- `POST /api/mcp/servers` - Add MCP server
- `DELETE /api/mcp/servers/:id` - Remove server
- `POST /api/mcp/servers/:id/restart` - Restart server
- `GET /api/mcp/servers/:id/tools` - List server tools

**LLM Management:**
- `GET /api/llm/catalog` - List available models
- `GET /api/llm/current` - Get current LLM config
- `POST /api/llm/switch` - Switch model

**WebSocket:**
```javascript
const ws = new WebSocket('ws://localhost:4000');

// Send message
ws.send(JSON.stringify({
  type: 'message',
  sessionId: 'sess-abc123',
  content: 'Hello!'
}));

// Receive responses
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**Architecture:**
- Express HTTP server
- WebSocket server (ws library)
- Session management in-memory or persistent storage
- No UI included

**Startup:**
```bash
$ dexto --mode server --api-port 4000
✓ API server listening on http://localhost:4000
✓ WebSocket server ready at ws://localhost:4000
✓ MCP servers initialized
```

**Pros:**
- ✅ Multi-user support
- ✅ Integrate with any frontend
- ✅ Standard REST/WebSocket APIs
- ✅ Scalable architecture
- ✅ Language-agnostic clients

**Cons:**
- ❌ No built-in UI
- ❌ Requires custom frontend
- ❌ More complex setup
- ❌ Need to handle auth/security

**When to use:**
- Building custom web/mobile apps
- Need multi-user support
- Integrating with existing systems
- API-first architecture
- Microservices deployment

**When NOT to use:**
- Just need a UI (use web mode)
- Single-user terminal access (use cli mode)
- No custom frontend development

**Example Client:**
```javascript
// Simple Node.js client
const axios = require('axios');

const API = 'http://localhost:4000/api';

async function chat(message) {
  const response = await axios.post(`${API}/chat`, {
    message,
    sessionId: 'my-session'
  });
  return response.data;
}

const result = await chat('Hello!');
console.log(result.response);
```

---

### Discord Mode

```bash
export DISCORD_BOT_TOKEN="your-bot-token"
dexto --mode discord
```

**Best for:**
- 👥 Team collaboration
- 💬 Community support
- 🤝 Shared AI assistant
- 📢 Channel-based workflows

**Features:**
- **Server Integration**: Works in Discord servers
- **Direct Messages**: Private 1-on-1 conversations
- **Channel Threads**: Contextual conversations
- **Role-Based Access**: Discord permissions apply
- **Rich Embeds**: Formatted responses with embeds
- **Mentions**: `@DextoBot your question`

**Setup:**

1. **Create Discord Application:**
   - Go to https://discord.com/developers/applications
   - Click "New Application"
   - Name your application

2. **Add Bot:**
   - Go to "Bot" section
   - Click "Add Bot"
   - Copy bot token
   - Enable "Message Content Intent"

3. **Configure Permissions:**
   - Go to "OAuth2" → "URL Generator"
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions:
     - Read Messages/View Channels
     - Send Messages
     - Send Messages in Threads
     - Embed Links
     - Attach Files
     - Read Message History
     - Add Reactions

4. **Invite Bot:**
   - Copy generated URL
   - Open in browser
   - Select your server
   - Authorize

5. **Start Dexto:**
   ```bash
   export DISCORD_BOT_TOKEN="your-bot-token"
   dexto --mode discord
   ```

**Usage:**
```
# In Discord channel
User: @DextoBot create a snake game

DextoBot: I'll create a snake game for you...
[Creates files and shows results]

# Direct message
User: Help me debug this code

DextoBot: Sure! Share your code and I'll help...
```

**Architecture:**
- discord.js library
- Event-driven message handling
- Per-user session management
- Optional shared sessions per channel

**Startup:**
```bash
$ export DISCORD_BOT_TOKEN="..."
$ dexto --mode discord
✓ Discord bot connected
✓ Logged in as DextoBot#1234
✓ Serving 5 servers
```

**Pros:**
- ✅ Natural team collaboration
- ✅ No extra app needed
- ✅ Rich formatting support
- ✅ Persistent chat history
- ✅ Mobile-friendly

**Cons:**
- ❌ Discord account required
- ❌ Rate limits apply
- ❌ Complex permission setup
- ❌ Not suitable for private deployments

**When to use:**
- Team already uses Discord
- Need shared AI assistant
- Community support bot
- Collaborative projects
- Remote team workflows

**When NOT to use:**
- Need strict privacy/compliance
- Don't want external dependencies
- Rate limits are concern
- User base not on Discord

---

### Telegram Mode

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
dexto --mode telegram
```

**Best for:**
- 📱 Mobile-first interaction
- 🏃 Quick queries on the go
- 👤 Personal AI assistant
- 🌍 International users

**Features:**
- **Mobile-Optimized**: Native mobile experience
- **Push Notifications**: Real-time alerts
- **Voice Messages**: Optional voice input
- **File Sharing**: Send/receive files
- **Inline Keyboards**: Interactive buttons
- **Bot Commands**: `/start`, `/ask`, etc.

**Setup:**

1. **Create Bot:**
   - Open Telegram
   - Search for `@BotFather`
   - Send `/newbot`
   - Follow prompts to set name and username

2. **Get Token:**
   - BotFather will provide token
   - Format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

3. **Configure Bot:**
   ```
   /setdescription - Set bot description
   /setabouttext - Set about text
   /setuserpic - Set profile picture
   ```

4. **Start Dexto:**
   ```bash
   export TELEGRAM_BOT_TOKEN="your-bot-token"
   dexto --mode telegram
   ```

**Bot Commands:**
- `/start` - Initialize bot and show welcome message
- `/ask <message>` - Send message to agent (optional, direct messages also work)
- Direct messages work without commands

**Usage:**
```
User: /start

DextoBot: 👋 Hello! I'm Dexto, your AI assistant.
Ask me anything!

User: /ask create a REST API

DextoBot: I'll help you create a REST API...

User: Make it with Express

DextoBot: Sure! Adding Express...
```

**Architecture:**
- grammy library (Telegram Bot API)
- Event-driven updates
- Per-user session management
- Long-polling or webhooks

**Startup:**
```bash
$ export TELEGRAM_BOT_TOKEN="..."
$ dexto --mode telegram
✓ Telegram bot connected
✓ Bot: @DextoBot
✓ Ready to receive messages
```

**Pros:**
- ✅ Excellent mobile experience
- ✅ Fast and lightweight
- ✅ Global availability
- ✅ Built-in file handling
- ✅ Voice message support

**Cons:**
- ❌ Telegram account required
- ❌ API rate limits
- ❌ Limited rich formatting
- ❌ External dependency

**When to use:**
- Mobile-first use case
- Personal AI assistant
- Quick on-the-go queries
- International user base
- Voice interaction desired

**When NOT to use:**
- Desktop-only workflows
- Need rich UI/formatting
- Strict data locality requirements
- Organization doesn't use Telegram

---

### MCP Mode

```bash
dexto --mode mcp --skip-setup --no-interactive
```

**Best for:**
- 🔧 Claude Desktop integration
- 💻 IDE integration (Cursor, etc.)
- 🔗 Tool aggregation
- 🎯 Multi-client MCP setups

**Features:**
- **MCP Protocol**: Standard Model Context Protocol
- **Tool Aggregation**: Combine multiple MCP servers
- **Resource Management**: Expose filesystem and custom resources
- **Prompt Templates**: Reusable prompt patterns
- **Streaming**: Real-time response streaming

**Setup for Claude Desktop:**

1. **Configure Claude Desktop:**
   ```json
   // ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
   // %APPDATA%\Claude\claude_desktop_config.json (Windows)
   {
     "mcpServers": {
       "dexto": {
         "command": "dexto",
         "args": ["--mode", "mcp", "--skip-setup", "--no-interactive"],
         "env": {
           "OPENAI_API_KEY": "sk-...",
           "DEXTO_LOG_LEVEL": "info"
         }
       }
     }
   }
   ```

2. **Restart Claude Desktop**

3. **Verify Connection:**
   - Look for "Dexto" in available tools
   - Tools from configured MCP servers appear in Claude

**MCP Protocol Methods:**

**Tools:**
- `chat_with_agent` - Send message to Dexto agent
- `list_agent_tools` - List all available tools
- `execute_tool` - Execute specific tool
- Aggregated tools from all connected MCP servers

**Resources:**
- `resource://filesystem/*` - Filesystem access
- `resource://blob/*` - Blob storage
- Custom resources from agent configuration

**Prompts:**
- `prompt://starter/*` - Starter prompt templates
- `prompt://system/*` - System prompt components
- Custom prompts from agent config

**Architecture:**
- stdio transport (stdin/stdout)
- JSON-RPC 2.0 protocol
- Tool aggregation layer
- Session management

**Startup:**
```bash
$ dexto --mode mcp --skip-setup --no-interactive
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {...}
}
```

**Pros:**
- ✅ Standard protocol
- ✅ IDE integration
- ✅ Tool aggregation
- ✅ Claude Desktop native
- ✅ Reusable across clients

**Cons:**
- ❌ Complex setup
- ❌ Limited to MCP clients
- ❌ No standalone UI
- ❌ Requires technical knowledge

**When to use:**
- Using Claude Desktop
- IDE integration (Cursor, etc.)
- Aggregating multiple MCP servers
- Building MCP-compatible tools
- Need standardized protocol

**When NOT to use:**
- Don't use Claude Desktop
- Need standalone application
- Want visual interface
- Simple single-user needs

**Advanced MCP Configuration:**
```yaml
# agent.yml - Configure MCP server behavior
mcpServers:
  # Your MCP servers appear as tools in MCP mode
  filesystem:
    type: stdio
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "."]
  
  github:
    type: stdio
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: $GITHUB_TOKEN
```

---

## Decision Matrix

### By Use Case

**Development & Testing:**
- Primary: **web** mode
- Alternative: **cli** mode for terminal work

**Production Deployment:**
- Multi-user: **server** mode
- Team collaboration: **discord** or **telegram**
- IDE integration: **mcp** mode

**Personal Use:**
- Desktop: **web** or **cli** mode
- Mobile: **telegram** mode
- Claude user: **mcp** mode

**Automation:**
- Scripts: **cli** mode with `--no-interactive`
- API integration: **server** mode
- CI/CD: **cli** mode

### By User Count

**Single User:**
- **web**, **cli**, or **mcp** mode

**Team (2-50 users):**
- **discord** or **telegram** mode

**Large Scale (50+ users):**
- **server** mode with load balancer

### By Interface Preference

**Graphical UI:**
- **web** mode

**Terminal:**
- **cli** mode

**Chat App:**
- **discord** or **telegram** mode

**IDE:**
- **mcp** mode

### By Deployment Environment

**Local Development:**
- **web** or **cli** mode

**Remote Server:**
- **server**, **discord**, or **telegram** mode

**Cloud (AWS/GCP/Azure):**
- **server** mode with container

**Desktop Application (Claude):**
- **mcp** mode

## Combining Modes

You can run multiple instances of Dexto in different modes simultaneously:

```bash
# Terminal 1: Web UI for development
dexto --mode web --web-port 3000

# Terminal 2: API server for integration
dexto --mode server --api-port 4000

# Terminal 3: Discord bot for team
export DISCORD_BOT_TOKEN="..."
dexto --mode discord
```

**Note**: Each instance needs its own configuration and resources.

## Migration Between Modes

Sessions are stored in the same database regardless of mode, so you can:

```bash
# Start in web mode
dexto --mode web

# Resume same session in CLI
dexto --mode cli -r sess-abc123

# Access via API
curl http://localhost:4000/api/sessions/sess-abc123
```

## Recommendations

### For New Users
Start with **web mode**:
```bash
dexto
```

### For Developers
Use **cli mode** during development:
```bash
dexto --mode cli -c
```

Switch to **web mode** for visual debugging:
```bash
dexto --mode web
```

### For Teams
Deploy **server mode**:
```bash
dexto --mode server --api-port 4000
```

Or use **discord/telegram** for chat-based collaboration:
```bash
dexto --mode discord
```

### For Production
Run **server mode** with monitoring:
```bash
dexto --mode server --skip-setup --no-interactive --api-port 4000
```

### For Claude Desktop Users
Configure **mcp mode**:
```json
{
  "mcpServers": {
    "dexto": {
      "command": "dexto",
      "args": ["--mode", "mcp"]
    }
  }
}
```

## See Also

- [CLI Reference](CLI_REFERENCE.md) - Complete command documentation
- [Quick Start Guide](QUICK_START.md) - Get started in 5 minutes
- [Deployment Guide](../DEPLOYMENT.md) - Production deployment strategies
- [API Documentation](https://docs.dexto.ai/api/) - REST API reference

