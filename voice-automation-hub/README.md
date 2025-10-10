# Voice Automation Hub

> A comprehensive voice-to-voice AI automation platform powered by ChatKit, enabling natural language control of complex multi-agent workflows with MCP tool integration.

## 🎯 Overview

Voice Automation Hub is a production-grade platform that transforms voice commands into sophisticated multi-agent workflows. Built on OpenAI's ChatKit framework and integrated with Model Context Protocol (MCP), it provides a complete solution for voice-controlled automation.

### Key Features

- **🎤 Voice-to-Voice Interface** - Natural conversation using Web Speech API
- **🤖 Multi-Agent Orchestration** - Dynamic sub-agent spawning with workflow DAG
- **🔧 MCP Tool Integration** - Extensible tool ecosystem for automation
- **📊 Real-Time Visualization** - Live workflow progress and task tracking
- **⚡ Streaming Architecture** - Server-Sent Events for instant updates
- **🎨 Rich UI Components** - Custom ChatKit widgets for immersive experience

### Architecture

```
Voice Command (Web Speech API)
    ↓
Orchestrator Agent (Main Controller)
    ├── spawn_sub_agents(task, tools)
    ├── create_workflow_dag(agents, deps)
    ├── validate_quality_gates(output)
    └── emit_progress_events(status)
    ↓
Sub-Agent System (Dynamic)
    ├── ResearchAgent (browser, search, scraper)
    ├── CodeAgent (fs, git, linter)
    ├── TestAgent (pytest, playwright)
    └── ValidationAgent (quality_checker)
    ↓
Event Streaming (Webhooks + SSE)
    ├── ThreadStreamEvent → Progress updates
    ├── WidgetItem → Task visualization
    └── HiddenContextItem → Inter-agent comms
    ↓
Visual Interface
    ├── Voice Chat Panel
    ├── Workflow DAG Viewer
    ├── Task Manager (concurrent)
    └── MCP Dashboard
```

## 📦 Project Structure

```
voice-automation-hub/
├── backend/                 # Python FastAPI + ChatKit server
│   ├── app/
│   │   ├── main.py         # FastAPI application + ChatKit endpoint
│   │   ├── server.py       # VoiceAutomationServer (ChatKitServer)
│   │   ├── agents/         # Agent system
│   │   │   ├── orchestrator.py  # Main orchestration agent
│   │   │   ├── research.py      # Research sub-agent
│   │   │   ├── code.py          # Code generation/analysis
│   │   │   └── test.py          # Testing automation
│   │   ├── tools/          # Function tools
│   │   │   ├── mcp_manager.py   # MCP server management
│   │   │   ├── cli.py           # CLI execution
│   │   │   ├── browser.py       # Browser automation
│   │   │   └── workflow.py      # Workflow DAG builder
│   │   ├── widgets/        # Custom ChatKit widgets
│   │   │   ├── workflow_dag.py  # DAG visualization
│   │   │   ├── task_progress.py # Progress tracking
│   │   │   └── mcp_dashboard.py # MCP monitoring
│   │   ├── memory_store.py # Thread/item persistence
│   │   └── constants.py    # Configuration constants
│   ├── requirements.txt    # Python dependencies
│   └── pyproject.toml      # Project metadata
│
├── frontend/               # React + ChatKit Web Component
│   ├── src/
│   │   ├── App.tsx        # Main application
│   │   ├── components/
│   │   │   ├── VoiceChatPanel.tsx    # Voice interface
│   │   │   ├── WorkflowViewer.tsx    # Task progression
│   │   │   ├── TaskManager.tsx       # Concurrent tasks
│   │   │   └── MCPDashboard.tsx      # MCP management
│   │   ├── hooks/
│   │   │   ├── useVoiceRecognition.ts # Web Speech API
│   │   │   ├── useWorkflows.ts        # Workflow state
│   │   │   └── useMCPServers.ts       # MCP state
│   │   └── lib/
│   │       └── config.ts   # Frontend configuration
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── deployment/             # Deployment scripts
│   ├── windows/
│   │   ├── install.ps1    # PowerShell installation
│   │   ├── start.bat      # Quick start script
│   │   └── stop.bat       # Shutdown script
│   ├── docker/
│   │   ├── Dockerfile.backend
│   │   ├── Dockerfile.frontend
│   │   └── docker-compose.yml
│   └── .env.example       # Environment template
│
├── examples/               # Example workflows
│   ├── research_workflow.py      # Web research → report
│   ├── testing_automation.py     # Unit → Integration → E2E
│   ├── content_pipeline.py       # Writer → Editor → Publisher
│   ├── code_review.py            # Auto code review workflow
│   └── data_processing.py        # ETL pipeline automation
│
└── docs/                   # Documentation
    ├── ARCHITECTURE.md     # System architecture
    ├── API.md             # API reference
    ├── WIDGETS.md         # Widget development guide
    ├── MCP_INTEGRATION.md # MCP tool guide
    └── TROUBLESHOOTING.md # Common issues

```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with `uv` or `pip`
- **Node.js 20+** with `npm`
- **OpenAI API Key** - Export as `OPENAI_API_KEY`
- **Windows** (for PowerShell scripts) or **Linux/Mac** (Docker)

### Installation (Windows)

```powershell
# 1. Run installation script
cd deployment/windows
.\install.ps1

# 2. Configure environment
cp ../.env.example ../.env
# Edit .env with your API keys

# 3. Start services
.\start.bat

# 4. Open browser
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

### Installation (Docker)

```bash
# 1. Build and start
cd deployment/docker
docker-compose up -d

# 2. Access services
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

### Manual Installation

#### Backend

```bash
cd backend
uv sync  # or: pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"
uv run uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

## 📖 Usage

### Voice Commands

The system responds to natural language voice commands:

```
"Research the latest AI developments and create a summary report"
→ Spawns ResearchAgent → Web scraping → Summarization → Report generation

"Run tests for the authentication module and report results"
→ Spawns TestAgent → Unit tests → Integration tests → Report

"Generate a data pipeline that processes CSV files and creates visualizations"
→ Spawns CodeAgent → ETL code → DataVizAgent → Charts
```

### Programmatic API

```python
from voice_automation_hub import VoiceAutomationServer, Orchestrator

# Initialize server
server = VoiceAutomationServer()

# Create workflow
workflow = await orchestrator.create_workflow(
    command="Research AI agent frameworks",
    sub_agents=["research", "summarizer"],
    mcp_tools=["browser", "search"],
    quality_gates=["factual_accuracy", "completeness"]
)

# Execute with streaming
async for event in workflow.execute():
    print(f"Progress: {event.status} - {event.data}")
```

## 🛠️ Development

### Running Tests

```bash
cd backend
pytest tests/ -v

cd ../frontend  
npm test
```

### Adding Custom Agents

```python
# backend/app/agents/custom_agent.py
from agents import Agent, function_tool
from chatkit.agents import AgentContext

@function_tool(description="Custom tool")
async def my_tool(ctx, param: str):
    return {"result": f"Processed: {param}"}

custom_agent = Agent[AgentContext](
    model="gpt-4.1-mini",
    name="CustomAgent",
    instructions="Your custom instructions here",
    tools=[my_tool]
)
```

### Creating Custom Widgets

```python
# backend/app/widgets/custom_widget.py
from chatkit.widgets import Card, Text, Button, ActionConfig

def render_custom_widget(data: dict):
    return Card(
        children=[
            Text(value=data["title"]),
            Button(
                label="Action",
                onClickAction=ActionConfig(
                    type="custom_action",
                    payload=data
                )
            )
        ]
    )
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...           # OpenAI API key

# Optional  
BACKEND_PORT=8000               # Backend server port
FRONTEND_PORT=5173              # Frontend dev server port
CHATKIT_DOMAIN_KEY=key-...      # ChatKit domain key (production)
LOG_LEVEL=INFO                  # Logging level
MCP_CONFIG_PATH=./mcp.json      # MCP servers configuration
```

### MCP Configuration

```json
{
  "mcpServers": {
    "browser": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp-server"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    },
    "search": {
      "command": "mcp-server-search"
    }
  }
}
```

## 📚 Example Workflows

### Research Workflow

```python
# examples/research_workflow.py
workflow = await orchestrator.execute(
    """
    Research the top 5 AI agent frameworks released in 2024.
    For each framework:
    1. Extract key features
    2. Find GitHub stars and community metrics
    3. Analyze pros and cons
    4. Create comparison table
    5. Generate executive summary
    """
)
```

### Testing Automation

```python
# examples/testing_automation.py
workflow = await orchestrator.execute(
    """
    Run comprehensive testing for the user authentication module:
    1. Unit tests for login/logout/register functions
    2. Integration tests with database
    3. E2E tests with browser automation
    4. Generate coverage report
    5. Identify failing tests and suggest fixes
    """
)
```

## 🎨 Widget Showcase

### Workflow DAG Widget
Visualizes agent hierarchy and task dependencies in real-time.

### Task Progress Widget
Shows live execution progress with:
- Progress bar (0-100%)
- Current step description
- Estimated time remaining
- Agent status (running/completed/failed)

### MCP Dashboard Widget
Monitors MCP server health:
- Active servers and tool count
- Recent tool invocations
- Error rates and performance metrics
- Add/remove server controls

## 🔗 Integration

### With Existing Systems

```python
# Integrate with your existing agent
from voice_automation_hub import VoiceOrchestrator

orchestrator = VoiceOrchestrator()
orchestrator.register_agent("my_agent", my_existing_agent)

# Voice command will now use your agent
result = await orchestrator.process_voice_command(
    "Use my_agent to analyze this data"
)
```

### Webhooks for Events

```python
# Register webhook for workflow events
orchestrator.add_webhook(
    event="task_completed",
    url="https://your-system.com/webhooks/task-done",
    headers={"Authorization": "Bearer token"}
)
```

## 📊 Monitoring

### Built-in Dashboards

- **Workflow Dashboard** - Real-time task execution
- **MCP Dashboard** - Tool usage and health
- **Agent Performance** - Success rates and timing
- **System Metrics** - CPU, memory, API usage

### Logging

```python
# Structured logging with context
import logging
logger = logging.getLogger(__name__)

logger.info(f"Workflow started: {workflow.id}")
logger.error(f"Agent failed: {agent.name} - {error}")
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/voice-automation-hub
cd voice-automation-hub

# Backend setup
cd backend
uv sync --dev

# Frontend setup  
cd ../frontend
npm install

# Run in development
# Terminal 1: Backend
cd backend && uv run uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- **OpenAI ChatKit** - Core framework ([chatkit-python](https://github.com/openai/chatkit-python))
- **OpenAI Agents SDK** - Agent orchestration ([openai-agents-python](https://github.com/openai/openai-agents-python))
- **Model Context Protocol** - Tool integration ([MCP](https://modelcontextprotocol.io))
- **FastAPI** - Backend framework
- **React** - Frontend framework

## 📞 Support

- **Documentation**: [/docs](/docs)
- **Issues**: [GitHub Issues](https://github.com/yourusername/voice-automation-hub/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/voice-automation-hub/discussions)

---

Built with ❤️ by the Voice Automation Hub team

