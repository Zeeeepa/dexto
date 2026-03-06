"""MCP Dashboard Widget - Monitor MCP tool usage and performance."""

from typing import Any, Dict, List
from datetime import datetime


class MCPDashboardWidget:
    """Widget for monitoring MCP tool usage."""

    @staticmethod
    def render(
        tool_usage: List[Dict[str, Any]], time_window: str = "1h"
    ) -> Dict[str, Any]:
        """
        Render MCP dashboard widget.

        Args:
            tool_usage: List of recent tool usage records
            time_window: Time window for statistics (1h, 24h, 7d)

        Returns:
            Dashboard widget configuration
        """
        # Calculate statistics
        total_calls = len(tool_usage)
        successful_calls = sum(1 for u in tool_usage if u.get("success", False))
        failed_calls = total_calls - successful_calls

        # Group by tool
        tool_stats = {}
        for usage in tool_usage:
            tool_name = usage.get("tool_name", "unknown")
            if tool_name not in tool_stats:
                tool_stats[tool_name] = {
                    "calls": 0,
                    "successes": 0,
                    "failures": 0,
                    "avg_duration": 0,
                }

            tool_stats[tool_name]["calls"] += 1
            if usage.get("success", False):
                tool_stats[tool_name]["successes"] += 1
            else:
                tool_stats[tool_name]["failures"] += 1

        # Convert to list for widget
        tools = [
            {
                "name": name,
                "calls": stats["calls"],
                "success_rate": (
                    (stats["successes"] / stats["calls"] * 100)
                    if stats["calls"] > 0
                    else 0
                ),
                "failures": stats["failures"],
            }
            for name, stats in tool_stats.items()
        ]

        return {
            "widget_type": "mcp_dashboard",
            "time_window": time_window,
            "summary": {
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls,
                "success_rate": (
                    (successful_calls / total_calls * 100) if total_calls > 0 else 0
                ),
            },
            "tools": sorted(tools, key=lambda x: x["calls"], reverse=True),
            "recent_activity": tool_usage[-10:] if len(tool_usage) > 10 else tool_usage,
            "generated_at": datetime.now().isoformat(),
        }

