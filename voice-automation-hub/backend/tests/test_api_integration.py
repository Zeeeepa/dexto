"""
Test real API integration with Z.ai GLM-4.5V.

These tests use the actual API to validate functionality.
Set TEST_MODE=true to use mocks instead.
"""

import pytest
import asyncio
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAPIClient:
    """Test Z.ai API client."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test API client initializes correctly."""
        from app.api_client import ZAIClient

        client = ZAIClient()

        assert client.model == "glm-4.5V"
        assert client.base_url == "https://api.z.ai/api/anthropic"
        assert client.client is not None

        await client.close()

    @pytest.mark.asyncio
    async def test_create_message(self):
        """Test creating a message via API."""
        from app.api_client import ZAIClient

        client = ZAIClient()

        messages = [
            {"role": "user", "content": "What is 2+2? Answer with just the number."}
        ]

        response = await client.create_message(messages, max_tokens=100, temperature=0)
        
        await client.close()

        assert response is not None
        assert "content" in response
        assert len(response["content"]) > 0
        assert response["content"][0]["type"] == "text"

        # Check we got a response
        text = response["content"][0]["text"]
        assert len(text) > 0

        print(f"API Response: {text}")

    @pytest.mark.asyncio
    async def test_parse_command(self):
        """Test command parsing via API."""
        from app.api_client import ZAIClient

        client = ZAIClient()

        command = "deploy the payment service to production"
        parsed = await client.parse_command(command)
        
        await client.close()

        assert parsed is not None
        assert "intent" in parsed
        assert "confidence" in parsed

        # Should recognize deployment intent
        print(f"Parsed: {parsed}")

        # Basic validation
        assert isinstance(parsed["intent"], str)
        assert isinstance(parsed["confidence"], (int, float))

    @pytest.mark.asyncio
    async def test_research_synthesis(self):
        """Test research synthesis via API."""
        from app.api_client import ZAIClient

        client = ZAIClient()

        query = "What are the benefits of async Python?"
        sources = [
            {
                "title": "Async Python Guide",
                "url": "https://example.com/async",
                "snippet": "Async Python allows concurrent I/O operations...",
            },
            {
                "title": "Performance Benefits",
                "url": "https://example.com/perf",
                "snippet": "Async code can handle thousands of connections...",
            },
        ]

        synthesis = await client.research_synthesis(query, sources)
        
        await client.close()

        assert synthesis is not None
        assert "summary" in synthesis

        print(f"Synthesis: {synthesis}")

        # Should have some content
        assert len(synthesis["summary"]) > 0


class TestCreatorAgentWithAI:
    """Test Creator Agent with real AI parsing."""

    def test_voice_command_parsing_with_ai(self):
        """Test voice command parsing using AI."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "creator", "backend/app/agents/creator.py"
        )
        creator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(creator_module)

        creator = creator_module.CreatorAgent()

        # Test with AI enabled
        parsed = creator.parse_voice_command("deploy to production", use_ai=True)

        assert parsed is not None
        assert "intent" in parsed
        assert "original" in parsed
        assert parsed["original"] == "deploy to production"

        print(f"AI Parsed: {parsed}")

    def test_voice_command_fallback(self):
        """Test voice command parsing with fallback."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "creator", "backend/app/agents/creator.py"
        )
        creator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(creator_module)

        creator = creator_module.CreatorAgent()

        # Test with AI disabled (fallback)
        parsed = creator.parse_voice_command("deploy to production", use_ai=False)

        assert parsed is not None
        assert "intent" in parsed
        assert parsed["original"] == "deploy to production"

        print(f"Fallback Parsed: {parsed}")


class TestResearchAgentWithAI:
    """Test Research Agent with real AI synthesis."""

    @pytest.mark.asyncio
    async def test_research_with_ai_synthesis(self):
        """Test research with AI synthesis."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "research", "backend/app/agents/research_enhanced.py"
        )
        research_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(research_module)

        agent = research_module.EnhancedResearchAgent()

        # Perform research
        result = await agent.research("Python async programming", depth="quick")

        assert result is not None
        assert result["status"] == "completed"
        assert "summary" in result
        assert "findings" in result
        assert len(result["sources"]) > 0

        print(f"Research Result: {result['summary'][:200]}...")
        print(f"Findings: {len(result['findings'])} key points")


class TestMockMode:
    """Test that mock mode works when API is unavailable."""

    @pytest.mark.asyncio
    async def test_mock_mode_enabled(self):
        """Test API client in mock mode."""
        import os

        # Temporarily enable mock mode
        original_test_mode = os.getenv("TEST_MODE")
        os.environ["TEST_MODE"] = "true"

        from app.api_client import ZAIClient

        client = ZAIClient()
        assert client.test_mode is True

        messages = [{"role": "user", "content": "Test message"}]
        response = await client.create_message(messages)

        assert response is not None
        assert "content" in response
        assert response["content"][0]["type"] == "text"
        assert "Mock response" in response["content"][0]["text"]

        await client.close()

        # Restore original
        if original_test_mode is not None:
            os.environ["TEST_MODE"] = original_test_mode
        else:
            del os.environ["TEST_MODE"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
