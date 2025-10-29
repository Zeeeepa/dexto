# 🎤 Voice Automation Hub

> AI-Powered Multi-Agent Workflow Orchestration with Voice Control

A production-ready platform for building and executing complex AI workflows through natural language voice commands. Built on ChatKit and OpenAI Agents, featuring multi-agent coordination, MCP tool integration, and real-time workflow visualization.

## ✨ Features

### 🎯 Core Capabilities
- **Voice-First Interface**: Control workflows with natural language commands
- **Multi-Agent System**: Coordinated AI agents working together on complex tasks
- **Real-time Monitoring**: Live workflow status, progress tracking, and agent coordination
- **MCP Integration**: Browser automation, filesystem operations, and extensible tools
- **Custom Widgets**: Visual workflow DAGs, progress tracking, and MCP dashboards

### 🤖 Specialized Agents

#### Orchestrator Agent
Central coordinator that manages workflow execution:
- Creates and manages multi-step workflows
- Spawns and coordinates sub-agents
- Tracks progress and dependencies
- Handles workflow state management

#### Research Agent
Information gathering and synthesis:
- Web search and data extraction
- Multi-source research synthesis
- Structured information retrieval
- Citation and source tracking

#### Code Agent
Software development automation:
- Code generation from requirements
- Code quality analysis and refactoring
- Bug detection and security scanning
- Automated test generation

#### Test Agent
Quality assurance and validation:
- Unit, integration, and E2E testing
- Test failure analysis
- Coverage reporting
- Performance benchmarking

#### Analysis Agent
Data analysis and insights:
- Statistical analysis
- Pattern and trend detection
- Insight generation
- Data visualization

## 🚀 Enterprise Features (Phases 7-8)

### WebSocket Real-Time Communication 🔌
- Bidirectional WebSocket connections at `/ws`
- Connection management with metadata
- User-specific connection tracking
- Real-time workflow updates
- Agent status broadcasting
- Metrics streaming
- Auto-reconnection support

### Authentication & Authorization 🔐
- JWT-based authentication
- User registration and login
- Role-based access control (admin, user, viewer)
- Password hashing with bcrypt
- Bearer token authentication
- Session management
- Permission checking middleware
- Default admin account

### Database Persistence Layer 💾
- SQLite database with complete schema
- Workflow lifecycle tracking
- Agent performance metrics
- Execution logs
- Metrics storage
- Analytics tracking
- Query helpers with pagination
- Audit trail

### Redis Caching 🚀
- Multi-backend caching system
- Redis cache with automatic fallback
- In-memory cache support
- TTL support
- `@cached` decorator
- `get_or_set` pattern
- Key generation with hashing

### Webhook Integrations 🪝
- 8 webhook event types
- HMAC signature verification
- Delivery history tracking
- Success rate statistics
- Automatic retry logic
- Event-driven architecture
- External system integration

### Advanced Agent Collaboration 🤝
- 5 collaboration modes:
  - **Sequential**: Agents work one after another
  - **Parallel**: Simultaneous execution
  - **Consensus**: Democratic voting
  - **Leader-Follower**: Hierarchical coordination
  - **Debate**: Discussion-based decisions
- Inter-agent messaging
- Collaborative decision making
- Session management
- Context sharing

## 🎯 Latest Features

### Testing Infrastructure ✅
- Complete pytest test suite with 100% coverage setup
- Tests for all agents, memory store, and API endpoints
- Mock OpenAI client for testing
- Async test support

### Monitoring & Observability 📊
- Real-time metrics (counters, gauges, timers, histograms)
- Request logging and tracking
- Performance metrics with percentiles (p50, p95, p99)
- Health check system with error rate monitoring
- `/api/metrics` endpoint for metrics
- `/api/health/detailed` for detailed health status

### Error Handling & Recovery 🛡️
- Custom error hierarchy with severity levels
- Automatic error tracking and statistics
- Retry handler with exponential backoff
- Circuit breaker pattern for fault tolerance
- `/api/errors/statistics` endpoint

### Security Features 🔒
- Rate limiting to prevent API abuse
- API key management system
- Input validation and sanitization
- Content Security Policy headers
- Audit logging for security events
- `/api/security/audit-log` endpoint

### Workflow Templates Library 📚
- 6 pre-built workflow templates:
  - Comprehensive Code Review
  - API Development Workflow
  - ETL Pipeline Generator
  - Data Insights Report
  - Market Research Analysis
  - Complete Test Suite Generator
- Template search and instantiation
- `/api/templates` endpoint to browse templates
- `/api/workflows/from-template` to create from templates

### Git Operations 🔧
- Repository cloning and management
- Commit history retrieval
- Branch creation and management
- Pull request creation
- Diff generation

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- OpenAI API key

### Installation

#### Windows (Recommended)

```powershell
# Clone repository
git clone https://github.com/Zeeeepa/dexto.git
cd dexto/voice-automation-hub

# Run automated installation
.\deployment\windows\install.ps1

# Edit .env and add your OPENAI_API_KEY
notepad .env

# Start services
.\deployment\windows\start.bat
```

#### Docker

```bash
# Clone repository
git clone https://github.com/Zeeeepa/dexto.git
cd dexto/voice-automation-hub

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start with Docker Compose
cd deployment/docker
docker-compose up -d
```

#### Manual Installation

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install

# Configure environment
cp ../.env.example ../.env
# Edit .env and add your OPENAI_API_KEY

# Start backend
cd ../backend
python -m uvicorn app.main:app --reload --port 8000

# Start frontend (in new terminal)
cd ../frontend
npm run dev
```

### Access

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📖 Usage Examples

### Example 1: Research Workflow

```python
python examples/research_workflow.py
```

Creates a research workflow that:
1. Searches for information on a topic
2. Extracts and analyzes data from multiple sources
3. Synthesizes findings into a comprehensive report

### Example 2: Code Review

```python
python examples/code_review_workflow.py
```

Automates code review process:
1. Analyzes code structure and style
2. Identifies potential issues
3. Checks test coverage
4. Provides improvement recommendations

### Example 3: Data Pipeline

```python
python examples/data_pipeline_workflow.py
```

Generates data processing pipeline:
1. Analyzes data requirements
2. Creates ETL code (Extract, Transform, Load)
3. Generates tests
4. Sets up orchestration

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (React)                       │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐     │
│  │ Voice Chat │  │  Workflow    │  │   Agent     │     │
│  │ Interface  │  │ Visualization│  │  Status     │     │
│  └────────────┘  └──────────────┘  └─────────────┘     │
└──────────────────────────────────────────────────────────┘
                           │
                  ┌────────▼────────┐
                  │  FastAPI Server │
                  │  (ChatKit SSE)  │
                  └────────┬────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
    ┌───────▼───────┐ ┌───▼────┐ ┌──────▼──────┐
    │ Orchestrator  │ │  MCP   │ │   Memory    │
    │    Agent      │ │ Tools  │ │    Store    │
    └───────┬───────┘ └────────┘ └─────────────┘
            │
   ┌────────┴────────┐
   │                 │
┌──▼──┐  ┌──▼──┐  ┌─▼──┐  ┌──▼──┐
│Code │  │Test │  │Res │  │Anal │
│Agent│  │Agent│  │Agt │  │Agt  │
└─────┘  └─────┘  └────┘  └─────┘
```

## 🛠️ Development

### Project Structure

```
voice-automation-hub/
├── backend/
│   ├── app/
│   │   ├── agents/        # AI agents
│   │   │   ├── orchestrator.py
│   │   │   ├── research.py
│   │   │   ├── code.py
│   │   │   ├── test.py
│   │   │   └── analysis.py
│   │   ├── tools/         # MCP tools
│   │   │   ├── browser.py
│   │   │   └── filesystem.py
│   │   ├── widgets/       # Custom widgets
│   │   │   ├── workflow_dag.py
│   │   │   ├── task_progress.py
│   │   │   └── mcp_dashboard.py
│   │   ├── server.py      # ChatKit server
│   │   ├── main.py        # FastAPI app
│   │   └── constants.py   # Configuration
│   ├── tests/             # Test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx        # Main React app
│   │   ├── App.css        # Styling
│   │   ├── hooks/
│   │   │   └── useVoiceRecognition.ts
│   │   └── lib/
│   │       └── config.ts
│   └── package.json
├── examples/              # Example workflows
│   ├── research_workflow.py
│   ├── code_review_workflow.py
│   └── data_pipeline_workflow.py
└── deployment/
    ├── windows/           # Windows deployment
    └── docker/            # Docker deployment
```

### Running Tests

```bash
cd backend
pytest tests/ -v
```

### Adding New Agents

1. Create agent file in `backend/app/agents/`
2. Define tools with `@function_tool` decorator
3. Implement agent instructions
4. Register in `__init__.py`

Example:

```python
from agents import Agent, function_tool
from chatkit.agents import AgentContext

@function_tool(description="Your tool description")
async def my_tool(ctx: AgentContext, param: str) -> dict:
    return {"result": "data"}

agent = Agent[AgentContext](
    model="gpt-4o",
    name="MyAgent",
    instructions="Your agent instructions...",
    tools=[my_tool],
)
```

## 📊 Widget System

### Workflow DAG Widget
Visualizes workflow execution as a directed acyclic graph.

### Task Progress Widget
Shows real-time progress of individual tasks with step-by-step tracking.

### MCP Dashboard Widget
Monitors MCP tool usage, success rates, and performance metrics.

## 🔧 Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Required
OPENAI_API_KEY=sk-...

# Optional
BACKEND_PORT=8000
ORCHESTRATOR_MODEL=gpt-4o
SUB_AGENT_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
```

### Model Configuration

Edit `backend/app/constants.py`:

```python
ORCHESTRATOR_MODEL = "gpt-4o"  # Main orchestrator
SUB_AGENT_MODEL = "gpt-4o-mini"  # Sub-agents
```

## 🎯 Use Cases

### Software Development
- Automated code generation and review
- Test suite creation
- Documentation generation
- Bug analysis and fixing

### Data Science
- ETL pipeline generation
- Data analysis and visualization
- Pattern detection
- Report generation

### Research
- Literature reviews
- Market research
- Competitive analysis
- Information synthesis

### QA & Testing
- Test automation
- Coverage analysis
- Performance testing
- Failure analysis

## 🚦 API Reference

### REST Endpoints

#### Create Workflow
```http
POST /api/workflows
Content-Type: application/json

{
  "task": "Research latest AI developments"
}
```

#### Get Workflow Status
```http
GET /api/workflows/{workflow_id}
```

#### List Workflows
```http
GET /api/workflows
```

### ChatKit SSE Endpoint

```http
GET /chatkit
```

Streaming Server-Sent Events for real-time workflow updates.

## 🌐 Complete API Reference

### Core Endpoints
- `GET /` - Service information
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health status with error rates

### Workflow Management
- `GET /api/workflows` - List all active workflows
- `POST /api/workflows` - Create new workflow
- `GET /api/workflows/{id}` - Get workflow details
- `DELETE /api/workflows/{id}` - Delete workflow
- `POST /api/workflows/from-template` - Create workflow from template

### Workflow Templates
- `GET /api/templates` - List all workflow templates
- `GET /api/templates?category={category}` - Filter templates by category
- `GET /api/templates/{id}` - Get template details

### Monitoring & Observability
- `GET /api/metrics` - System metrics (counters, gauges, timers)
- `GET /api/errors/statistics` - Error statistics and recent errors

### Security & Auditing
- `GET /api/security/audit-log` - Security audit log entries
- `GET /api/security/audit-log?limit={n}` - Get last N audit entries

## 🔐 Security

### Built-in Security Features
- **Rate Limiting**: Configurable rate limits to prevent API abuse
- **API Key Management**: Secure API key generation and validation
- **Input Validation**: Comprehensive input sanitization
- **Content Security Policy**: Strict CSP headers on all responses
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, etc.
- **Audit Logging**: All security events are logged
- **CORS**: Configured for development (customize for production)
- **Secure Token Handling**: Environment-based configuration

### Security Best Practices
- Never commit `.env` file with real API keys
- Use API key rotation in production
- Configure rate limits based on your needs
- Review audit logs regularly
- Keep dependencies updated

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [OpenAI Agents](https://github.com/openai/openai-agents-python)
- [ChatKit](https://github.com/openai/openai-chatkit-python)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

## 📧 Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/Zeeeepa/dexto/issues)
- Discussions: [GitHub Discussions](https://github.com/Zeeeepa/dexto/discussions)

---

**Made with ❤️ by the dexto team**
