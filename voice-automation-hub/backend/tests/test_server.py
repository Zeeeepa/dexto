"""Tests for Voice Automation Server."""

import pytest
from datetime import datetime


def test_imports():
    """Test that all required modules can be imported."""
    try:
        from app.server import VoiceAutomationServer
        from app.memory_store import MemoryStore
        from app.constants import BACKEND_PORT
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_constants():
    """Test constants are loaded."""
    from app.constants import BACKEND_PORT, ORCHESTRATOR_MODEL
    
    assert isinstance(BACKEND_PORT, int)
    assert BACKEND_PORT > 0
    assert isinstance(ORCHESTRATOR_MODEL, str)
    assert len(ORCHESTRATOR_MODEL) > 0
