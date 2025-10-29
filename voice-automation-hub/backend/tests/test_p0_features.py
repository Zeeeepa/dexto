"""Comprehensive tests for P0 features implemented in Phase 10."""

import pytest
import asyncio
from datetime import datetime
from pathlib import Path
import sys

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestEnhancedMemoryStore:
    """Test suite for Enhanced Memory Store."""

    def test_memory_store_initialization(self):
        """Test memory store initializes correctly."""
        from app.memory_store_enhanced import EnhancedMemoryStore
        
        store = EnhancedMemoryStore()
        assert store is not None
        assert len(store.threads) == 0
        assert len(store.items) == 0
        assert len(store.attachments) == 0

    def test_thread_creation(self):
        """Test creating threads with metadata."""
        from app.memory_store_enhanced import EnhancedMemoryStore
        
        store = EnhancedMemoryStore()
        thread = store.create_thread("test-thread-1", metadata={"env": "test"})
        
        assert thread.id == "test-thread-1"
        assert thread.metadata["env"] == "test"
        assert thread.status == "active"
        assert len(thread.messages) == 0

    def test_item_creation(self):
        """Test creating items with content."""
        from app.memory_store_enhanced import EnhancedMemoryStore
        
        store = EnhancedMemoryStore()
        item = store.create_item(
            "item-1",
            "test_type",
            {"data": "value"},
            metadata={"priority": "high"}
        )
        
        assert item.id == "item-1"
        assert item.type == "test_type"
        assert item.content["data"] == "value"
        assert item.metadata["priority"] == "high"

    def test_thread_search(self):
        """Test thread search functionality."""
        from app.memory_store_enhanced import EnhancedMemoryStore
        
        store = EnhancedMemoryStore()
        thread1 = store.create_thread("t1", metadata={"env": "prod"})
        thread2 = store.create_thread("t2", metadata={"env": "dev"})
        
        # Search by status
        results = store.search_threads(status="active")
        assert len(results) == 2
        
        # Search by metadata
        results = store.search_threads(metadata={"env": "prod"})
        assert len(results) == 1
        assert results[0].id == "t1"

    def test_item_linking(self):
        """Test linking items to threads."""
        from app.memory_store_enhanced import EnhancedMemoryStore
        
        store = EnhancedMemoryStore()
        thread = store.create_thread("thread-1")
        item = store.create_item("item-1", "test", {})
        
        success = store.link_item_to_thread("thread-1", "item-1")
        assert success is True
        assert "item-1" in thread.items

    def test_statistics(self):
        """Test statistics generation."""
        from app.memory_store_enhanced import EnhancedMemoryStore
        
        store = EnhancedMemoryStore()
        store.create_thread("t1")
        store.create_item("i1", "type1", {})
        
        stats = store.get_statistics()
        assert stats["threads"]["total"] == 1
        assert stats["items"]["total"] == 1


class TestCreatorAgent:
    """Test suite for Creator Agent."""

    def test_creator_initialization(self):
        """Test creator agent initializes."""
        # Import directly to avoid dependency issues
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "creator",
            "backend/app/agents/creator.py"
        )
        creator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(creator_module)
        
        creator = creator_module.CreatorAgent()
        assert creator is not None
        assert len(creator.command_patterns) > 0

    def test_voice_command_parsing(self):
        """Test parsing voice commands."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "creator",
            "backend/app/agents/creator.py"
        )
        creator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(creator_module)
        
        creator = creator_module.CreatorAgent()
        
        # Test deployment command
        parsed = creator.parse_voice_command("deploy the app to production")
        assert parsed["intent"] == "deploy"
        assert "production" in parsed["target"]
        
        # Test code command
        parsed = creator.parse_voice_command("write a test for authentication")
        assert parsed["intent"] == "code"

    def test_sub_agent_determination(self):
        """Test determining required sub-agents."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "creator",
            "backend/app/agents/creator.py"
        )
        creator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(creator_module)
        
        creator = creator_module.CreatorAgent()
        parsed = creator.parse_voice_command("deploy to production")
        agents = creator.determine_required_agents(parsed)
        
        # Deployment should spawn multiple agents
        assert len(agents) >= 2
        agent_types = [a.agent_type for a in agents]
        assert "test" in agent_types  # Should include test agent

    def test_quality_gates(self):
        """Test quality gate creation and validation."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "creator",
            "backend/app/agents/creator.py"
        )
        creator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(creator_module)
        
        creator = creator_module.CreatorAgent()
        QualityGate = creator_module.QualityGate
        
        # Test error threshold gate
        gate = QualityGate("test", "error_threshold", {"max_errors": 0})
        passed, msg = gate.validate({"errors": 0})
        assert passed is True
        
        passed, msg = gate.validate({"errors": 1})
        assert passed is False

    @pytest.mark.asyncio
    async def test_orchestration_plan(self):
        """Test creating orchestration plan."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "creator",
            "backend/app/agents/creator.py"
        )
        creator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(creator_module)
        
        creator = creator_module.CreatorAgent()
        result = await creator.process_voice_command("write a test")
        
        assert result["success"] is True
        assert "plan" in result
        assert len(result["plan"]["agents"]) > 0
        assert len(result["plan"]["quality_gates"]) > 0


class TestCLITools:
    """Test suite for CLI Tools."""

    def test_cli_tools_initialization(self):
        """Test CLI tools initialize."""
        from app.tools.cli import CLITools
        
        tools = CLITools()
        assert tools is not None
        assert tools.system in ["Windows", "Linux", "Darwin"]

    def test_command_execution(self):
        """Test executing commands."""
        from app.tools.cli import CLITools
        
        tools = CLITools()
        result = tools.execute_command("echo test", timeout=5)
        
        assert result["success"] is True
        assert "test" in result["stdout"]
        assert result["return_code"] == 0

    def test_system_info(self):
        """Test getting system information."""
        from app.tools.cli import CLITools
        
        tools = CLITools()
        info = tools.get_system_info()
        
        assert "system" in info
        assert "cpu_count" in info
        assert "memory" in info
        assert info["cpu_count"] > 0

    def test_process_listing(self):
        """Test listing processes."""
        from app.tools.cli import CLITools
        
        tools = CLITools()
        processes = tools.list_processes()
        
        assert len(processes) > 0
        assert "pid" in processes[0]
        assert "name" in processes[0]

    def test_environment_variables(self):
        """Test environment variable operations."""
        from app.tools.cli import CLITools
        
        tools = CLITools()
        
        # Set variable
        result = tools.set_environment_variable("TEST_VAR", "test_value")
        assert result["success"] is True
        
        # Get variable
        value = tools.get_environment_variable("TEST_VAR")
        assert value == "test_value"


class TestResearchAgent:
    """Test suite for Research Agent."""

    @pytest.mark.asyncio
    async def test_research_initialization(self):
        """Test research agent initializes."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "research",
            "backend/app/agents/research_enhanced.py"
        )
        research_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(research_module)
        
        agent = research_module.EnhancedResearchAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_web_search(self):
        """Test web search functionality."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "research",
            "backend/app/agents/research_enhanced.py"
        )
        research_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(research_module)
        
        agent = research_module.EnhancedResearchAgent()
        results = await agent.web_search("Python", num_results=3)
        
        assert len(results) > 0
        assert "title" in results[0]
        assert "url" in results[0]

    @pytest.mark.asyncio
    async def test_research_with_caching(self):
        """Test research with caching."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "research",
            "backend/app/agents/research_enhanced.py"
        )
        research_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(research_module)
        
        agent = research_module.EnhancedResearchAgent()
        
        # First call (no cache)
        result1 = await agent.research("FastAPI", depth="quick")
        assert result1["status"] == "completed"
        
        # Second call (should use cache)
        result2 = await agent.research("FastAPI", depth="quick")
        assert result2["status"] == "completed"
        
        # Results should be identical due to caching
        assert result1["topic"] == result2["topic"]


class TestTestRunner:
    """Test suite for Test Runner."""

    def test_test_runner_initialization(self):
        """Test runner initializes."""
        from app.tools.test_runner import TestRunner
        
        runner = TestRunner()
        assert runner is not None
        assert len(runner.test_history) == 0

    def test_result_validation(self):
        """Test validating test results."""
        from app.tools.test_runner import TestRunner
        
        runner = TestRunner()
        
        # Pass scenario
        result = {
            "test_results": {
                "total": 10,
                "passed": 10,
                "failed": 0,
            },
            "duration": 30
        }
        
        validation = runner.validate_test_results(result, min_pass_rate=1.0)
        assert validation["valid"] is True
        assert validation["summary"]["pass_rate"] == 1.0
        
        # Fail scenario
        result["test_results"]["passed"] = 8
        result["test_results"]["failed"] = 2
        
        validation = runner.validate_test_results(result, min_pass_rate=1.0)
        assert validation["valid"] is False

    def test_duration_validation(self):
        """Test validating test duration."""
        from app.tools.test_runner import TestRunner
        
        runner = TestRunner()
        
        result = {
            "test_results": {"total": 5, "passed": 5, "failed": 0},
            "duration": 45
        }
        
        validation = runner.validate_test_results(
            result,
            min_pass_rate=1.0,
            max_duration=60
        )
        
        assert validation["valid"] is True
        assert validation["checks"]["duration"]["passed"] is True


# Integration Tests
class TestIntegration:
    """Integration tests for P0 features."""

    def test_memory_store_with_creator(self):
        """Test memory store integration with creator agent."""
        from app.memory_store_enhanced import EnhancedMemoryStore
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "creator",
            "backend/app/agents/creator.py"
        )
        creator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(creator_module)
        
        store = EnhancedMemoryStore()
        creator = creator_module.CreatorAgent()
        
        # Create thread for workflow
        thread = store.create_thread("workflow-1", metadata={"type": "automation"})
        
        # Parse command
        parsed = creator.parse_voice_command("deploy app")
        
        # Create item for parsed command
        item = store.create_item(
            "command-1",
            "voice_command",
            parsed,
            metadata={"intent": parsed["intent"]}
        )
        
        # Link them
        store.link_item_to_thread(thread.id, item.id)
        
        # Verify integration
        assert len(thread.items) == 1
        assert thread.items[0] == item.id

    def test_cli_with_test_runner(self):
        """Test CLI tools with test runner."""
        from app.tools.cli import CLITools
        from app.tools.test_runner import TestRunner
        
        cli = CLITools()
        runner = TestRunner()
        
        # Use CLI to check if pytest is available
        result = cli.execute_command("which python", timeout=5)
        assert result["success"] is True
        
        # Test runner can use the same system
        assert runner is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

