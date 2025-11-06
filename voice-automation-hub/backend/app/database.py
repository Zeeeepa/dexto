"""Database persistence layer."""

import json
import sqlite3
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager."""

    def __init__(self, db_path: str = "data/voicehub.db"):
        """
        Initialize database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Workflows table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    created_by TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    result TEXT,
                    metadata TEXT
                )
            """)

            # Workflow steps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    step_number INTEGER NOT NULL,
                    agent_name TEXT NOT NULL,
                    tool_name TEXT,
                    status TEXT NOT NULL,
                    input TEXT,
                    output TEXT,
                    error TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
                )
            """)

            # Agents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    model TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_active TEXT,
                    total_executions INTEGER DEFAULT 0,
                    total_success INTEGER DEFAULT 0,
                    total_failures INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)

            # Execution logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT,
                    agent_id TEXT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL
                )
            """)

            # Metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    tags TEXT,
                    timestamp TEXT NOT NULL
                )
            """)

            # Analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    user_id TEXT,
                    session_id TEXT,
                    timestamp TEXT NOT NULL
                )
            """)

            conn.commit()
            logger.info("Database initialized successfully")

    def create_workflow(
        self,
        workflow_id: str,
        name: str,
        description: str = "",
        created_by: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create workflow record."""
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO workflows 
                (id, name, description, status, created_by, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    workflow_id,
                    name,
                    description,
                    "pending",
                    created_by,
                    now,
                    now,
                    json.dumps(metadata or {}),
                ),
            )
            conn.commit()

        return self.get_workflow(workflow_id)

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

    def update_workflow(
        self, workflow_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update workflow."""
        updates["updated_at"] = datetime.now().isoformat()

        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [workflow_id]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE workflows SET {set_clause} WHERE id = ?", values
            )
            conn.commit()

        return self.get_workflow(workflow_id)

    def list_workflows(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List workflows."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if status:
                cursor.execute(
                    """
                    SELECT * FROM workflows 
                    WHERE status = ? 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                    """,
                    (status, limit, offset),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM workflows 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset),
                )

            return [dict(row) for row in cursor.fetchall()]

    def create_workflow_step(
        self,
        workflow_id: str,
        step_number: int,
        agent_name: str,
        tool_name: Optional[str] = None,
        input_data: Optional[Dict] = None,
    ) -> int:
        """Create workflow step."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO workflow_steps 
                (workflow_id, step_number, agent_name, tool_name, status, input, started_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    workflow_id,
                    step_number,
                    agent_name,
                    tool_name,
                    "running",
                    json.dumps(input_data or {}),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def update_workflow_step(
        self, step_id: int, updates: Dict[str, Any]
    ):
        """Update workflow step."""
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [step_id]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE workflow_steps SET {set_clause} WHERE id = ?", values
            )
            conn.commit()

    def log_execution(
        self,
        level: str,
        message: str,
        workflow_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        details: Optional[Dict] = None,
    ):
        """Log execution event."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO execution_logs 
                (workflow_id, agent_id, level, message, details, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    workflow_id,
                    agent_id,
                    level,
                    message,
                    json.dumps(details or {}),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()

    def record_metric(
        self, metric_name: str, value: float, tags: Optional[Dict] = None
    ):
        """Record metric."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO metrics (metric_name, metric_value, tags, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (
                    metric_name,
                    value,
                    json.dumps(tags or {}),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()

    def track_analytics(
        self,
        event_type: str,
        event_data: Optional[Dict] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """Track analytics event."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO analytics 
                (event_type, event_data, user_id, session_id, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event_type,
                    json.dumps(event_data or {}),
                    user_id,
                    session_id,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()

    def get_analytics(
        self,
        event_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get analytics data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM analytics WHERE 1=1"
            params = []

            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)

            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)

            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]


# Global database instance
database = Database()

