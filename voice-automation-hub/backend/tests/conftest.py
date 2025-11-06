"""Pytest configuration and fixtures."""

import pytest
import os
from typing import AsyncGenerator

# Mock OpenAI for testing
os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing"


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    from unittest.mock import AsyncMock, MagicMock
    
    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="Test response",
                        tool_calls=None,
                    )
                )
            ]
        )
    )
    
    return mock_client


@pytest.fixture
async def test_client():
    """Create test FastAPI client."""
    from httpx import AsyncClient
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_workflow():
    """Sample workflow data for testing."""
    return {
        "id": "wf_test_123",
        "task": "Test task description",
        "status": "pending",
        "agents": [],
        "progress": 0,
    }


@pytest.fixture
def sample_thread():
    """Sample thread data for testing."""
    return {
        "id": "thread_test_123",
        "messages": [],
        "context": {},
        "metadata": {"test": True},
    }


@pytest.fixture
def memory_store():
    """Create test memory store."""
    from app.memory_store import MemoryStore
    
    # Use in-memory only (no persistence) for tests
    store = MemoryStore(persist_path=None)
    yield store
    store.clear_all()

