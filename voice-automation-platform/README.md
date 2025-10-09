# 🎙️ Voice Automation Platform

**Transform voice commands into multi-agent AI workflows with visual monitoring and MCP tool integration.**

---

## 🌟 **What Is This?**

A complete platform for building voice-driven automation using:
- **OpenAI ChatKit** - Battle-tested chat UI and widget framework
- **Multi-Agent Orchestration** - Spawn hierarchical AI agents with dependencies
- **MCP Integration** - Connect to Model Context Protocol tools (filesystem, browser, terminal, etc.)
- **Quality Gates** - Validate outputs with JSON schema, regex, LLM judgment
- **Real-Time Monitoring** - Visual task progression and concurrent workflow management
- **Voice Interface** - Natural language commands → Complex workflows

---

## 🏗️ **Architecture**

```
Voice Command
    ↓
Voice Parser (GPT-4o)
    ↓
Orchestration Engine
    ↓
Agent Factory ──→ Parent Agent
    ↓                   ↓
Child Agents (DAG)  MCP Tools
    ↓                   ↓
Quality Gates ←─────────┘
    ↓
Webhook Events
    ↓
ChatKit UI (SSE Stream)
    ↓
Task Viewer + MCP Dashboard
```

### **Key Components:**

1. **Voice Command Parser** - LLM-based intent classification and workflow generation
2. **Agent Factory** - Dynamic agent spawning with lifecycle management
3. **Workflow Coordinator** - DAG execution with dependency resolution
4. **Quality Gate System** - Output validation (JSON schema, regex, LLM, custom)
5. **Webhook Adapter** - Inter-agent communication with retry logic
6. **MCP Registry** - Tool server management and health checks
7. **ChatKit Server** - Streaming responses with custom widgets
8. **React Frontend** - Voice interface + visual monitoring

---

## 🚀 **Quick Start**

### **Prerequisites:**
- Python 3.11+
- Node.js 18+
- OpenAI API key

### **Installation:**

```bash
# Clone repository
git clone <repo-url>
cd voice-automation-platform

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Set environment variables
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

### **Run:**

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### **Windows Quick Start:**

```powershell
# Run installer
.\install.ps1

# Start services
.\start.bat
```

---

## 💡 **Usage Examples**

### **Example 1: Research Automation**

**Voice Command:**
> "Research recent AI developments in computer vision, summarize the top 5 papers, and create a report"

**Generated Workflow:**
```
Orchestrator
├─ Web Scraper (arxiv, Google Scholar)
├─ Summarizer (parallel processing)
└─ Report Generator (depends on summaries)
```

### **Example 2: Content Creation Pipeline**

**Voice Command:**
> "Write a blog post about Python async patterns, have an editor review it, optimize for SEO, then publish to Medium"

**Generated Workflow:**
```
Orchestrator
├─ Writer (creates draft)
├─ Editor (reviews + quality gate)
├─ SEO Optimizer (keyword analysis)
└─ Publisher (API integration)
```

### **Example 3: Testing Automation**

**Voice Command:**
> "Run unit tests, then integration tests, then E2E tests on the authentication module"

**Generated Workflow:**
```
Orchestrator
├─ Unit Tester (fast, parallel)
├─ Integration Tester (depends on unit)
└─ E2E Tester (depends on integration)
```

---

## 📋 **Features**

### ✅ **Implemented:**
- ✅ Voice command parsing with GPT-4o
- ✅ Multi-agent orchestration with DAG execution
- ✅ Quality gates (4 validation types)
- ✅ Webhook event system with retry logic
- ✅ MCP server registry and tool discovery
- ✅ ChatKit SDK integration
- ✅ Async/await throughout

### 🚧 **In Progress:**
- 🚧 ChatKit server extension with custom actions
- 🚧 Database-backed storage layer
- 🚧 React frontend with voice interface
- 🚧 MCP dashboard widget
- 🚧 Task progression viewer

### ⏸️ **Todo:**
- ⏸️ 5 example workflows
- ⏸️ Windows deployment scripts
- ⏸️ Comprehensive documentation
- ⏸️ End-to-end testing

---

## 🎯 **Core Concepts**

### **1. Orchestration Configs**

Define workflows declaratively:

```python
config = OrchestrationConfig(
    workflow_id="research_workflow",
    parent_role="orchestrator",
    parent_prompt="You coordinate research tasks",
    children=[
        AgentConfig(
            role="scraper",
            system_prompt="You scrape web data",
            tools=["browser", "search"],
            depends_on=[]
        ),
        AgentConfig(
            role="summarizer",
            system_prompt="You summarize content",
            tools=["filesystem"],
            depends_on=["scraper"]  # Waits for scraper
        )
    ]
)
```

### **2. Quality Gates**

Validate outputs before proceeding:

```python
QualityGate(
    gate_id="json_validation",
    gate_type=QualityGateType.JSON_SCHEMA,
    validation_config={
        "schema": {
            "type": "object",
            "properties": {"summary": {"type": "string"}},
            "required": ["summary"]
        }
    },
    retry_on_fail=True,
    max_retries=2
)
```

### **3. Webhooks**

Inter-agent communication:

```python
WebhookConfig(
    url="http://localhost:8000/webhook/agent_complete",
    trigger=WebhookTrigger.AGENT_COMPLETED,
    target_agent="next_agent",
    retry_count=3
)
```

### **4. MCP Tools**

Assign tools to agents:

```python
AgentConfig(
    role="file_processor",
    tools=["filesystem_read", "filesystem_write"]
)
```

---

## 🔧 **Configuration**

### **Environment Variables:**

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
MCP_REGISTRY_PATH=./mcp_servers.json
DATABASE_URL=sqlite:///./voice_automation.db
WEBHOOK_TIMEOUT=30
MAX_PARALLEL_AGENTS=5
```

### **MCP Servers:**

Configure in `mcp_servers.json`:

```json
{
  "servers": [
    {
      "name": "filesystem",
      "url": "http://localhost:3000/mcp/filesystem",
      "tools": ["read", "write", "list"]
    },
    {
      "name": "browser",
      "url": "http://localhost:3001/mcp/browser",
      "tools": ["navigate", "click", "scrape"]
    }
  ]
}
```

---

## 📚 **Documentation**

- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and data flow
- **[API Reference](docs/API.md)** - Complete API documentation
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Windows Deployment](docs/WINDOWS_DEPLOY.md)** - Windows-specific setup
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing and extending

---

## 🤝 **Contributing**

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 **License**

Apache 2.0 - See [LICENSE](LICENSE) for details

---

## 🙏 **Credits**

Built with:
- [OpenAI ChatKit](https://github.com/openai/chatkit-python) - Chat UI framework
- [OpenAI Agents SDK](https://github.com/openai/agents-sdk) - Agent orchestration
- [FastAPI](https://fastapi.tiangolo.com/) - Backend API
- [React](https://react.dev/) + [Next.js](https://nextjs.org/) - Frontend
- [MCP Protocol](https://modelcontextprotocol.org/) - Tool integration

---

## 📊 **Status**

**Current Version:** 0.1.0 (Alpha)  
**Progress:** 35% Complete  
**See:** [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for detailed progress

---

**Made with ❤️ for the AI automation community**

