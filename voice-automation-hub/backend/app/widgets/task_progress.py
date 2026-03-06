"""Task Progress Widget - Real-time task execution progress."""

from typing import Any, Dict, List, Optional
from datetime import datetime


class TaskProgressWidget:
    """Widget for displaying task execution progress."""

    @staticmethod
    def render(
        task_id: str,
        task_name: str,
        status: str,
        progress: int,
        steps: Optional[List[Dict[str, Any]]] = None,
        agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Render task progress widget.

        Args:
            task_id: Task identifier
            task_name: Human-readable task name
            status: Current status (pending, running, completed, failed)
            progress: Progress percentage (0-100)
            steps: Optional list of sub-steps
            agent: Optional agent executing the task

        Returns:
            Widget configuration
        """
        widget_data = {
            "widget_type": "task_progress",
            "task_id": task_id,
            "task_name": task_name,
            "status": status,
            "progress": progress,
            "agent": agent,
        }

        # Add steps if provided
        if steps:
            widget_data["steps"] = [
                {
                    "name": step.get("name", f"Step {idx + 1}"),
                    "status": step.get("status", "pending"),
                    "duration": step.get("duration"),
                    "order": idx,
                }
                for idx, step in enumerate(steps)
            ]

        # Add timing information
        widget_data["timing"] = {
            "started_at": datetime.now().isoformat(),
            "estimated_completion": "2m 30s",
        }

        # Status-specific metadata
        if status == "completed":
            widget_data["timing"]["completed_at"] = datetime.now().isoformat()
            widget_data["timing"]["total_duration"] = "2m 15s"
        elif status == "failed":
            widget_data["error"] = "Task execution failed"
            widget_data["timing"]["failed_at"] = datetime.now().isoformat()

        widget_data["generated_at"] = datetime.now().isoformat()

        return widget_data

