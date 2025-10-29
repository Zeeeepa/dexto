"""Memory Store for thread persistence."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os


class MemoryStore:
    """Simple in-memory store for thread data with optional persistence."""

    def __init__(self, persist_path: Optional[str] = None):
        """
        Initialize memory store.

        Args:
            persist_path: Optional path for persistence to disk
        """
        self.threads: Dict[str, Dict[str, Any]] = {}
        self.persist_path = persist_path

        # Load from disk if path provided
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    def create_thread(self, thread_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new thread.

        Args:
            thread_id: Unique thread identifier
            metadata: Optional thread metadata

        Returns:
            Created thread data
        """
        thread_data = {
            "id": thread_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "messages": [],
            "context": {},
        }

        self.threads[thread_id] = thread_data
        self._persist()

        return thread_data

    def get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Get thread by ID.

        Args:
            thread_id: Thread identifier

        Returns:
            Thread data or None if not found
        """
        return self.threads.get(thread_id)

    def update_thread(self, thread_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update thread data.

        Args:
            thread_id: Thread identifier
            updates: Updates to apply

        Returns:
            Updated thread data or None if not found
        """
        if thread_id not in self.threads:
            return None

        thread = self.threads[thread_id]
        thread.update(updates)
        thread["updated_at"] = datetime.now().isoformat()

        self._persist()
        return thread

    def add_message(self, thread_id: str, message: Dict[str, Any]) -> bool:
        """
        Add message to thread.

        Args:
            thread_id: Thread identifier
            message: Message data

        Returns:
            Success status
        """
        if thread_id not in self.threads:
            return False

        message_data = {
            **message,
            "timestamp": datetime.now().isoformat(),
        }

        self.threads[thread_id]["messages"].append(message_data)
        self.threads[thread_id]["updated_at"] = datetime.now().isoformat()

        self._persist()
        return True

    def get_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages for a thread.

        Args:
            thread_id: Thread identifier

        Returns:
            List of messages
        """
        thread = self.threads.get(thread_id)
        return thread["messages"] if thread else []

    def set_context(self, thread_id: str, key: str, value: Any) -> bool:
        """
        Set context value for thread.

        Args:
            thread_id: Thread identifier
            key: Context key
            value: Context value

        Returns:
            Success status
        """
        if thread_id not in self.threads:
            return False

        self.threads[thread_id]["context"][key] = value
        self.threads[thread_id]["updated_at"] = datetime.now().isoformat()

        self._persist()
        return True

    def get_context(self, thread_id: str, key: str, default: Any = None) -> Any:
        """
        Get context value for thread.

        Args:
            thread_id: Thread identifier
            key: Context key
            default: Default value if not found

        Returns:
            Context value or default
        """
        thread = self.threads.get(thread_id)
        if not thread:
            return default

        return thread["context"].get(key, default)

    def list_threads(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all threads.

        Args:
            limit: Maximum number to return
            offset: Offset for pagination

        Returns:
            List of thread data
        """
        all_threads = list(self.threads.values())
        # Sort by updated_at desc
        all_threads.sort(key=lambda x: x["updated_at"], reverse=True)

        return all_threads[offset : offset + limit]

    def delete_thread(self, thread_id: str) -> bool:
        """
        Delete a thread.

        Args:
            thread_id: Thread identifier

        Returns:
            Success status
        """
        if thread_id in self.threads:
            del self.threads[thread_id]
            self._persist()
            return True
        return False

    def clear_all(self) -> None:
        """Clear all threads."""
        self.threads.clear()
        self._persist()

    def _persist(self) -> None:
        """Persist to disk if path is set."""
        if not self.persist_path:
            return

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)

            # Write to disk
            with open(self.persist_path, "w") as f:
                json.dump(self.threads, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to persist memory store: {e}")

    def _load_from_disk(self) -> None:
        """Load from disk."""
        try:
            with open(self.persist_path, "r") as f:
                self.threads = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load memory store: {e}")
            self.threads = {}

