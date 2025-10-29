"""Tests for MemoryStore."""

import pytest
from datetime import datetime


class TestMemoryStore:
    """Tests for MemoryStore functionality."""

    def test_create_thread(self, memory_store):
        """Test thread creation."""
        thread = memory_store.create_thread("test_123", {"key": "value"})
        
        assert thread["id"] == "test_123"
        assert thread["metadata"]["key"] == "value"
        assert "created_at" in thread
        assert "messages" in thread

    def test_get_thread(self, memory_store):
        """Test retrieving thread."""
        memory_store.create_thread("test_123")
        thread = memory_store.get_thread("test_123")
        
        assert thread is not None
        assert thread["id"] == "test_123"

    def test_get_nonexistent_thread(self, memory_store):
        """Test retrieving non-existent thread."""
        thread = memory_store.get_thread("nonexistent")
        assert thread is None

    def test_update_thread(self, memory_store):
        """Test updating thread."""
        memory_store.create_thread("test_123")
        updated = memory_store.update_thread("test_123", {"status": "active"})
        
        assert updated is not None
        assert updated["status"] == "active"

    def test_add_message(self, memory_store):
        """Test adding message to thread."""
        memory_store.create_thread("test_123")
        success = memory_store.add_message("test_123", {
            "role": "user",
            "content": "Hello"
        })
        
        assert success is True
        messages = memory_store.get_messages("test_123")
        assert len(messages) == 1
        assert messages[0]["content"] == "Hello"

    def test_get_messages(self, memory_store):
        """Test getting messages."""
        memory_store.create_thread("test_123")
        memory_store.add_message("test_123", {"content": "Message 1"})
        memory_store.add_message("test_123", {"content": "Message 2"})
        
        messages = memory_store.get_messages("test_123")
        assert len(messages) == 2

    def test_set_context(self, memory_store):
        """Test setting context."""
        memory_store.create_thread("test_123")
        success = memory_store.set_context("test_123", "workflow_id", "wf_456")
        
        assert success is True
        value = memory_store.get_context("test_123", "workflow_id")
        assert value == "wf_456"

    def test_get_context_with_default(self, memory_store):
        """Test getting context with default."""
        memory_store.create_thread("test_123")
        value = memory_store.get_context("test_123", "nonexistent", "default")
        
        assert value == "default"

    def test_list_threads(self, memory_store):
        """Test listing threads."""
        memory_store.create_thread("test_1")
        memory_store.create_thread("test_2")
        memory_store.create_thread("test_3")
        
        threads = memory_store.list_threads(limit=2)
        assert len(threads) == 2

    def test_delete_thread(self, memory_store):
        """Test deleting thread."""
        memory_store.create_thread("test_123")
        success = memory_store.delete_thread("test_123")
        
        assert success is True
        thread = memory_store.get_thread("test_123")
        assert thread is None

    def test_delete_nonexistent_thread(self, memory_store):
        """Test deleting non-existent thread."""
        success = memory_store.delete_thread("nonexistent")
        assert success is False

    def test_clear_all(self, memory_store):
        """Test clearing all threads."""
        memory_store.create_thread("test_1")
        memory_store.create_thread("test_2")
        
        memory_store.clear_all()
        threads = memory_store.list_threads()
        assert len(threads) == 0

