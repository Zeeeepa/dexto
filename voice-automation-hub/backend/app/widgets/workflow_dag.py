"""Workflow DAG Widget - Visual representation of workflow execution."""

from typing import Any, Dict, List
from datetime import datetime


class WorkflowDAGWidget:
    """Widget for visualizing workflow execution as a DAG."""

    @staticmethod
    def render(workflow_id: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Render workflow DAG widget.

        Args:
            workflow_id: Workflow identifier
            tasks: List of tasks with dependencies

        Returns:
            Widget configuration for rendering
        """
        # Build nodes from tasks
        nodes = []
        edges = []

        for idx, task in enumerate(tasks):
            node_id = f"task_{idx}"
            nodes.append(
                {
                    "id": node_id,
                    "label": task.get("name", f"Task {idx + 1}"),
                    "status": task.get("status", "pending"),
                    "agent": task.get("agent", "unknown"),
                    "progress": task.get("progress", 0),
                }
            )

            # Add edges for dependencies
            for dep_idx in task.get("depends_on", []):
                edges.append(
                    {"from": f"task_{dep_idx}", "to": node_id, "type": "dependency"}
                )

        return {
            "widget_type": "workflow_dag",
            "workflow_id": workflow_id,
            "nodes": nodes,
            "edges": edges,
            "layout": "hierarchical",
            "metadata": {
                "total_tasks": len(tasks),
                "completed": sum(
                    1 for t in tasks if t.get("status") == "completed"
                ),
                "failed": sum(1 for t in tasks if t.get("status") == "failed"),
                "generated_at": datetime.now().isoformat(),
            },
        }

