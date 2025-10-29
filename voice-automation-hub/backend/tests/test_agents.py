"""Tests for AI agents."""

import pytest
from unittest.mock import AsyncMock, MagicMock


class TestOrchestratorAgent:
    """Tests for OrchestratorAgent."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, mock_openai_client):
        """Test agent initializes correctly."""
        from app.agents.orchestrator import OrchestratorAgent
        
        agent = OrchestratorAgent(mock_openai_client)
        assert agent is not None
        assert agent.client == mock_openai_client

    @pytest.mark.asyncio
    async def test_agent_has_tools(self, mock_openai_client):
        """Test agent has required tools."""
        from app.agents.orchestrator import OrchestratorAgent
        
        agent = OrchestratorAgent(mock_openai_client)
        agent_obj = agent.get_agent()
        
        assert agent_obj.tools is not None
        assert len(agent_obj.tools) > 0


class TestCodeAgent:
    """Tests for CodeAgent."""

    @pytest.mark.asyncio
    async def test_code_generation_tool(self, mock_openai_client):
        """Test code generation functionality."""
        from app.agents.code import CodeAgent
        
        agent = CodeAgent(mock_openai_client)
        assert agent is not None

    @pytest.mark.asyncio
    async def test_code_analysis_tool(self, mock_openai_client):
        """Test code analysis functionality."""
        from app.agents.code import CodeAgent
        
        agent = CodeAgent(mock_openai_client)
        agent_obj = agent.get_agent()
        
        # Verify tools exist
        assert agent_obj.tools is not None
        tool_names = [tool.name for tool in agent_obj.tools]
        assert "generate_code" in tool_names
        assert "analyze_code" in tool_names


class TestTestAgent:
    """Tests for TestAgent."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, mock_openai_client):
        """Test agent initializes correctly."""
        from app.agents.test import TestAgent
        
        agent = TestAgent(mock_openai_client)
        assert agent is not None

    @pytest.mark.asyncio
    async def test_has_testing_tools(self, mock_openai_client):
        """Test agent has testing tools."""
        from app.agents.test import TestAgent
        
        agent = TestAgent(mock_openai_client)
        agent_obj = agent.get_agent()
        
        tool_names = [tool.name for tool in agent_obj.tools]
        assert "run_unit_tests" in tool_names
        assert "run_integration_tests" in tool_names


class TestAnalysisAgent:
    """Tests for AnalysisAgent."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, mock_openai_client):
        """Test agent initializes correctly."""
        from app.agents.analysis import AnalysisAgent
        
        agent = AnalysisAgent(mock_openai_client)
        assert agent is not None

    @pytest.mark.asyncio
    async def test_has_analysis_tools(self, mock_openai_client):
        """Test agent has analysis tools."""
        from app.agents.analysis import AnalysisAgent
        
        agent = AnalysisAgent(mock_openai_client)
        agent_obj = agent.get_agent()
        
        tool_names = [tool.name for tool in agent_obj.tools]
        assert "analyze_statistics" in tool_names
        assert "detect_patterns" in tool_names


class TestResearchAgent:
    """Tests for ResearchAgent."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, mock_openai_client):
        """Test agent initializes correctly."""
        from app.agents.research import ResearchAgent
        
        agent = ResearchAgent(mock_openai_client)
        assert agent is not None

    @pytest.mark.asyncio
    async def test_has_research_tools(self, mock_openai_client):
        """Test agent has research tools."""
        from app.agents.research import ResearchAgent
        
        agent = ResearchAgent(mock_openai_client)
        agent_obj = agent.get_agent()
        
        tool_names = [tool.name for tool in agent_obj.tools]
        assert "web_search" in tool_names
        assert "extract_data" in tool_names

