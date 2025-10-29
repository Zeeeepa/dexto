# Voice Automation Hub - Quick Start Guide

Get up and running in 5 minutes! 🚀

## Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 20+** ([Download](https://nodejs.org/))
- **OpenAI API Key** ([Get one](https://platform.openai.com/api-keys))

## Installation

### Windows (Recommended)

```powershell
# 1. Clone/download the repository
cd voice-automation-hub

# 2. Run installation script
cd deployment/windows
.\install.ps1

# 3. Configure API key
notepad ..\.env
# Add your OpenAI API key: OPENAI_API_KEY=sk-...

# 4. Start services
.\start.bat

# 5. Open browser to http://localhost:5173
```

### Linux/Mac

```bash
# 1. Backend setup
cd backend
pip install -r requirements.txt

# 2. Frontend setup
cd ../frontend
npm install

# 3. Configure environment
cp ../.env.example ../.env
nano ../.env  # Add your OPENAI_API_KEY

# 4. Start backend (Terminal 1)
cd backend
export OPENAI_API_KEY="your-key-here"
uvicorn app.main:app --reload --port 8000

# 5. Start frontend (Terminal 2)
cd frontend
npm run dev

# 6. Open http://localhost:5173
```

### Docker (Alternative)

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY

# 2. Start with Docker Compose
cd deployment/docker
docker-compose up -d

# 3. Open http://localhost:5173
```

## First Steps

### 1. Test Voice Input

Click the 🎤 microphone button and say:
> "Create a workflow to research AI agent frameworks"

### 2. Try Text Input

Type in the chat:
> "Run tests for the authentication module"

### 3. Run Example Workflow

```bash
cd examples
python research_workflow.py
```

## Usage Examples

### Voice Commands

```
"Research the latest developments in quantum computing"
→ Spawns ResearchAgent → Web scraping → Report generation

"Generate a data pipeline for CSV processing"
→ Spawns CodeAgent → Creates ETL code → Testing

"Create a workflow to automate testing"
→ Spawns TestAgent → Unit tests → Integration tests
```

### Programmatic API

```python
import requests

# Create workflow via API
response = requests.post('http://localhost:8000/api/workflows', json={
    'task': 'Research AI frameworks and create comparison'
})

workflow = response.json()
print(f"Workflow created: {workflow['id']}")
```

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r backend/requirements.txt --force-reinstall

# Check API key
echo $OPENAI_API_KEY  # Should not be empty
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 20+

# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Voice not working
- **Chrome/Edge**: Voice API works by default
- **Firefox**: May need to enable in `about:config`
- **Safari**: Limited support, use text input
- Check microphone permissions in browser settings

### Connection errors
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check if frontend can reach backend
curl http://localhost:5173

# Restart services
# Windows: Close terminals and run start.bat again
# Linux/Mac: Ctrl+C both terminals and restart
```

## Next Steps

1. **Explore Examples** - Run workflows in `/examples` directory
2. **Read Documentation** - Check `/docs` for detailed guides
3. **Customize Agents** - Modify agents in `/backend/app/agents`
4. **Add MCP Tools** - Configure MCP servers in `mcp.json`
5. **Build Workflows** - Create your own automation workflows

## Key Endpoints

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (coming soon)
- **Health Check**: http://localhost:8000/health

## Getting Help

- **Documentation**: See `/docs` folder
- **Examples**: Check `/examples` folder
- **Issues**: Create a GitHub issue
- **Logs**: Check terminal output for errors

## What's Next?

### Phase 2 Features (Coming Soon)
- Multi-agent coordination with DAG
- MCP tool integration (browser, filesystem, search)
- Advanced widgets (WorkflowDAG, TaskProgress, MCPDashboard)
- Quality gates and validation
- Webhook support for events
- Advanced voice synthesis (text-to-speech)

### Phase 3 Features (Roadmap)
- Agent marketplace
- Custom tool creation
- Workflow templates
- Team collaboration
- Cloud deployment
- Analytics dashboard

---

## Quick Reference Card

### Essential Commands

```bash
# Start services (Windows)
deployment\windows\start.bat

# Start backend (Linux/Mac)
cd backend && uvicorn app.main:app --reload

# Start frontend (Linux/Mac)
cd frontend && npm run dev

# Run example
python examples/research_workflow.py

# Check health
curl http://localhost:8000/health
```

### Environment Variables

```bash
OPENAI_API_KEY=sk-...       # Required
BACKEND_PORT=8000           # Optional (default: 8000)
FRONTEND_URL=http://localhost:5173  # Optional
LOG_LEVEL=INFO              # Optional (INFO/DEBUG/ERROR)
```

---

**Ready to automate? Start talking to your AI assistant now!** 🎤✨

