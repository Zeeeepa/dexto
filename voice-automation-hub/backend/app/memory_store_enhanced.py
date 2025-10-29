"""Enhanced Memory Store with threads, items, attachments, and indexing."""

from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from collections import defaultdict
import json
import os
import hashlib
import logging

logger = logging.getLogger(__name__)


class Thread:
    """Thread for conversation/workflow context."""

    def __init__(self, thread_id: str, metadata: Optional[Dict[str, Any]] = None):
        """Initialize thread."""
        self.id = thread_id
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.metadata = metadata or {}
        self.messages: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        self.attachments: List[str] = []  # List of attachment IDs
        self.items: List[str] = []  # List of item IDs
        self.status = "active"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "messages": self.messages,
            "context": self.context,
            "attachments": self.attachments,
            "items": self.items,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Thread":
        """Create from dictionary."""
        thread = cls(data["id"], data.get("metadata"))
        thread.created_at = data["created_at"]
        thread.updated_at = data["updated_at"]
        thread.messages = data.get("messages", [])
        thread.context = data.get("context", {})
        thread.attachments = data.get("attachments", [])
        thread.items = data.get("items", [])
        thread.status = data.get("status", "active")
        return thread


class Item:
    """Generic item for workflow data."""

    def __init__(
        self,
        item_id: str,
        item_type: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize item."""
        self.id = item_id
        self.type = item_type
        self.content = content
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.metadata = metadata or {}
        self.relations: List[str] = []  # Related item IDs
        self.tags: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "relations": self.relations,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        """Create from dictionary."""
        item = cls(
            data["id"],
            data["type"],
            data["content"],
            data.get("metadata"),
        )
        item.created_at = data["created_at"]
        item.updated_at = data["updated_at"]
        item.relations = data.get("relations", [])
        item.tags = data.get("tags", [])
        return item


class Attachment:
    """File attachment."""

    def __init__(
        self,
        attachment_id: str,
        file_path: str,
        mime_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize attachment."""
        self.id = attachment_id
        self.file_path = file_path
        self.mime_type = mime_type
        self.created_at = datetime.now().isoformat()
        self.metadata = metadata or {}
        self.size = self._get_file_size()
        self.checksum = self._calculate_checksum()

    def _get_file_size(self) -> int:
        """Get file size in bytes."""
        try:
            return os.path.getsize(self.file_path)
        except:
            return 0

    def _calculate_checksum(self) -> str:
        """Calculate file checksum."""
        try:
            with open(self.file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "file_path": self.file_path,
            "mime_type": self.mime_type,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "size": self.size,
            "checksum": self.checksum,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attachment":
        """Create from dictionary."""
        attachment = cls(
            data["id"],
            data["file_path"],
            data["mime_type"],
            data.get("metadata"),
        )
        attachment.created_at = data["created_at"]
        attachment.size = data.get("size", 0)
        attachment.checksum = data.get("checksum", "")
        return attachment


class IndexManager:
    """Manage indexes for fast lookups."""

    def __init__(self):
        """Initialize index manager."""
        # Thread indexes
        self.thread_by_status: Dict[str, Set[str]] = defaultdict(set)
        self.thread_by_metadata: Dict[str, Set[str]] = defaultdict(set)

        # Item indexes
        self.item_by_type: Dict[str, Set[str]] = defaultdict(set)
        self.item_by_tag: Dict[str, Set[str]] = defaultdict(set)

        # Attachment indexes
        self.attachment_by_type: Dict[str, Set[str]] = defaultdict(set)

        # Full-text search indexes (simple)
        self.thread_text_index: Dict[str, Set[str]] = defaultdict(set)
        self.item_text_index: Dict[str, Set[str]] = defaultdict(set)

    def index_thread(self, thread: Thread):
        """Index a thread."""
        # Status index
        self.thread_by_status[thread.status].add(thread.id)

        # Metadata indexes
        for key, value in thread.metadata.items():
            index_key = f"{key}:{value}"
            self.thread_by_metadata[index_key].add(thread.id)

        # Text index (simple word-based)
        for message in thread.messages:
            content = str(message.get("content", "")).lower()
            words = content.split()
            for word in words:
                if len(word) > 2:  # Skip short words
                    self.thread_text_index[word].add(thread.id)

    def index_item(self, item: Item):
        """Index an item."""
        # Type index
        self.item_by_type[item.type].add(item.id)

        # Tag indexes
        for tag in item.tags:
            self.item_by_tag[tag].add(item.id)

        # Text index
        content = str(item.content).lower()
        words = content.split()
        for word in words:
            if len(word) > 2:
                self.item_text_index[word].add(item.id)

    def index_attachment(self, attachment: Attachment):
        """Index an attachment."""
        self.attachment_by_type[attachment.mime_type].add(attachment.id)

    def search_threads(
        self,
        query: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Set[str]:
        """Search threads."""
        results = None

        # Status filter
        if status:
            status_results = self.thread_by_status.get(status, set())
            results = status_results if results is None else results & status_results

        # Metadata filter
        if metadata:
            for key, value in metadata.items():
                index_key = f"{key}:{value}"
                meta_results = self.thread_by_metadata.get(index_key, set())
                results = meta_results if results is None else results & meta_results

        # Text search
        if query:
            words = query.lower().split()
            text_results = None
            for word in words:
                word_results = self.thread_text_index.get(word, set())
                text_results = (
                    word_results
                    if text_results is None
                    else text_results & word_results
                )
            if text_results:
                results = text_results if results is None else results & text_results

        return results if results is not None else set()

    def search_items(
        self,
        query: Optional[str] = None,
        item_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Set[str]:
        """Search items."""
        results = None

        # Type filter
        if item_type:
            type_results = self.item_by_type.get(item_type, set())
            results = type_results if results is None else results & type_results

        # Tag filter
        if tags:
            for tag in tags:
                tag_results = self.item_by_tag.get(tag, set())
                results = tag_results if results is None else results & tag_results

        # Text search
        if query:
            words = query.lower().split()
            text_results = None
            for word in words:
                word_results = self.item_text_index.get(word, set())
                text_results = (
                    word_results
                    if text_results is None
                    else text_results & word_results
                )
            if text_results:
                results = text_results if results is None else results & text_results

        return results if results is not None else set()


class EnhancedMemoryStore:
    """Enhanced memory store with threads, items, attachments, and indexing."""

    def __init__(self, persist_path: Optional[str] = None):
        """
        Initialize enhanced memory store.

        Args:
            persist_path: Optional path for persistence
        """
        self.threads: Dict[str, Thread] = {}
        self.items: Dict[str, Item] = {}
        self.attachments: Dict[str, Attachment] = {}
        self.indexes = IndexManager()
        self.persist_path = persist_path

        # Load from disk if available
        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    # Thread operations
    def create_thread(
        self, thread_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Thread:
        """Create new thread."""
        thread = Thread(thread_id, metadata)
        self.threads[thread_id] = thread
        self.indexes.index_thread(thread)
        self._persist()
        logger.info(f"Thread created: {thread_id}")
        return thread

    def get_thread(self, thread_id: str) -> Optional[Thread]:
        """Get thread by ID."""
        return self.threads.get(thread_id)

    def update_thread(
        self, thread_id: str, updates: Dict[str, Any]
    ) -> Optional[Thread]:
        """Update thread."""
        thread = self.threads.get(thread_id)
        if not thread:
            return None

        for key, value in updates.items():
            if hasattr(thread, key):
                setattr(thread, key, value)

        thread.updated_at = datetime.now().isoformat()
        self.indexes.index_thread(thread)
        self._persist()
        return thread

    def add_message(
        self, thread_id: str, message: Dict[str, Any]
    ) -> bool:
        """Add message to thread."""
        thread = self.threads.get(thread_id)
        if not thread:
            return False

        message_data = {
            **message,
            "timestamp": datetime.now().isoformat(),
        }
        thread.messages.append(message_data)
        thread.updated_at = datetime.now().isoformat()

        self.indexes.index_thread(thread)
        self._persist()
        return True

    def search_threads(
        self,
        query: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[Thread]:
        """Search threads."""
        thread_ids = self.indexes.search_threads(query, status, metadata)

        threads = [self.threads[tid] for tid in thread_ids if tid in self.threads]

        # Sort by updated_at desc
        threads.sort(key=lambda t: t.updated_at, reverse=True)

        return threads[:limit]

    # Item operations
    def create_item(
        self,
        item_id: str,
        item_type: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Item:
        """Create new item."""
        item = Item(item_id, item_type, content, metadata)
        self.items[item_id] = item
        self.indexes.index_item(item)
        self._persist()
        logger.info(f"Item created: {item_id} ({item_type})")
        return item

    def get_item(self, item_id: str) -> Optional[Item]:
        """Get item by ID."""
        return self.items.get(item_id)

    def update_item(self, item_id: str, updates: Dict[str, Any]) -> Optional[Item]:
        """Update item."""
        item = self.items.get(item_id)
        if not item:
            return None

        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)

        item.updated_at = datetime.now().isoformat()
        self.indexes.index_item(item)
        self._persist()
        return item

    def search_items(
        self,
        query: Optional[str] = None,
        item_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Item]:
        """Search items."""
        item_ids = self.indexes.search_items(query, item_type, tags)

        items = [self.items[iid] for iid in item_ids if iid in self.items]

        # Sort by updated_at desc
        items.sort(key=lambda i: i.updated_at, reverse=True)

        return items[:limit]

    # Attachment operations
    def create_attachment(
        self,
        attachment_id: str,
        file_path: str,
        mime_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Attachment:
        """Create new attachment."""
        attachment = Attachment(attachment_id, file_path, mime_type, metadata)
        self.attachments[attachment_id] = attachment
        self.indexes.index_attachment(attachment)
        self._persist()
        logger.info(f"Attachment created: {attachment_id}")
        return attachment

    def get_attachment(self, attachment_id: str) -> Optional[Attachment]:
        """Get attachment by ID."""
        return self.attachments.get(attachment_id)

    def link_attachment_to_thread(self, thread_id: str, attachment_id: str) -> bool:
        """Link attachment to thread."""
        thread = self.threads.get(thread_id)
        attachment = self.attachments.get(attachment_id)

        if not thread or not attachment:
            return False

        if attachment_id not in thread.attachments:
            thread.attachments.append(attachment_id)
            thread.updated_at = datetime.now().isoformat()
            self._persist()

        return True

    # Relations
    def link_item_to_thread(self, thread_id: str, item_id: str) -> bool:
        """Link item to thread."""
        thread = self.threads.get(thread_id)
        item = self.items.get(item_id)

        if not thread or not item:
            return False

        if item_id not in thread.items:
            thread.items.append(item_id)
            thread.updated_at = datetime.now().isoformat()
            self._persist()

        return True

    def link_items(self, item_id1: str, item_id2: str) -> bool:
        """Create relation between items."""
        item1 = self.items.get(item_id1)
        item2 = self.items.get(item_id2)

        if not item1 or not item2:
            return False

        if item_id2 not in item1.relations:
            item1.relations.append(item_id2)
            item1.updated_at = datetime.now().isoformat()

        if item_id1 not in item2.relations:
            item2.relations.append(item_id1)
            item2.updated_at = datetime.now().isoformat()

        self._persist()
        return True

    # Statistics
    def get_statistics(self) -> Dict[str, Any]:
        """Get store statistics."""
        return {
            "threads": {
                "total": len(self.threads),
                "by_status": {
                    status: len(thread_ids)
                    for status, thread_ids in self.indexes.thread_by_status.items()
                },
            },
            "items": {
                "total": len(self.items),
                "by_type": {
                    item_type: len(item_ids)
                    for item_type, item_ids in self.indexes.item_by_type.items()
                },
            },
            "attachments": {
                "total": len(self.attachments),
                "by_type": {
                    mime_type: len(att_ids)
                    for mime_type, att_ids in self.indexes.attachment_by_type.items()
                },
            },
        }

    # Persistence
    def _persist(self):
        """Persist to disk."""
        if not self.persist_path:
            return

        try:
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)

            data = {
                "threads": {tid: t.to_dict() for tid, t in self.threads.items()},
                "items": {iid: i.to_dict() for iid, i in self.items.items()},
                "attachments": {
                    aid: a.to_dict() for aid, a in self.attachments.items()
                },
            }

            with open(self.persist_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to persist memory store: {e}")

    def _load_from_disk(self):
        """Load from disk."""
        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            # Load threads
            for tid, tdata in data.get("threads", {}).items():
                thread = Thread.from_dict(tdata)
                self.threads[tid] = thread
                self.indexes.index_thread(thread)

            # Load items
            for iid, idata in data.get("items", {}).items():
                item = Item.from_dict(idata)
                self.items[iid] = item
                self.indexes.index_item(item)

            # Load attachments
            for aid, adata in data.get("attachments", {}).items():
                attachment = Attachment.from_dict(adata)
                self.attachments[aid] = attachment
                self.indexes.index_attachment(attachment)

            logger.info(
                f"Loaded memory store: {len(self.threads)} threads, "
                f"{len(self.items)} items, {len(self.attachments)} attachments"
            )

        except Exception as e:
            logger.error(f"Failed to load memory store: {e}")


# Global instance
enhanced_memory_store = EnhancedMemoryStore(
    persist_path="data/enhanced_memory_store.json"
)

