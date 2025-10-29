"""Monitoring and observability utilities."""

import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict, deque
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and track application metrics."""

    def __init__(self, max_history: int = 1000):
        """
        Initialize metrics collector.

        Args:
            max_history: Maximum number of metric entries to keep
        """
        self.max_history = max_history
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.timers: Dict[str, List[float]] = defaultdict(list)

    def increment(self, metric: str, value: int = 1) -> None:
        """Increment a counter metric."""
        self.counters[metric] += value

    def set_gauge(self, metric: str, value: float) -> None:
        """Set a gauge metric."""
        self.gauges[metric] = value

    def record_value(self, metric: str, value: float) -> None:
        """Record a value in histogram."""
        self.histograms[metric].append(value)

    def record_time(self, metric: str, duration: float) -> None:
        """Record timing information."""
        self.timers[metric].append(duration)
        # Keep only recent timings
        if len(self.timers[metric]) > self.max_history:
            self.timers[metric] = self.timers[metric][-self.max_history:]

    @contextmanager
    def timer(self, metric: str):
        """Context manager for timing operations."""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.record_time(metric, duration)

    def get_stats(self, metric: str) -> Optional[Dict[str, float]]:
        """Get statistics for a metric."""
        if metric in self.timers and self.timers[metric]:
            values = self.timers[metric]
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "p50": sorted(values)[len(values) // 2],
                "p95": sorted(values)[int(len(values) * 0.95)],
                "p99": sorted(values)[int(len(values) * 0.99)],
            }
        return None

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "timers": {
                metric: self.get_stats(metric)
                for metric in self.timers
                if self.get_stats(metric)
            },
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.timers.clear()


# Global metrics collector
metrics = MetricsCollector()


class RequestLogger:
    """Log and track request information."""

    def __init__(self):
        """Initialize request logger."""
        self.requests: deque = deque(maxlen=1000)

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        error: Optional[str] = None,
    ) -> None:
        """
        Log a request.

        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration: Request duration in seconds
            error: Optional error message
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration": duration,
            "error": error,
        }
        self.requests.append(entry)

        # Update metrics
        metrics.increment(f"requests.{method.lower()}")
        metrics.increment(f"responses.{status_code}")
        metrics.record_time(f"request_duration.{path}", duration)

        if error:
            metrics.increment("errors.total")

    def get_recent_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent requests."""
        return list(self.requests)[-limit:]

    def get_error_rate(self, window_minutes: int = 5) -> float:
        """
        Calculate error rate over time window.

        Args:
            window_minutes: Time window in minutes

        Returns:
            Error rate (0-1)
        """
        cutoff = datetime.now().timestamp() - (window_minutes * 60)
        recent_requests = [
            r for r in self.requests
            if datetime.fromisoformat(r["timestamp"]).timestamp() > cutoff
        ]

        if not recent_requests:
            return 0.0

        error_count = sum(
            1 for r in recent_requests
            if r["status_code"] >= 400 or r["error"]
        )

        return error_count / len(recent_requests)


# Global request logger
request_logger = RequestLogger()


class HealthCheck:
    """System health check utilities."""

    @staticmethod
    def check_system_health() -> Dict[str, Any]:
        """
        Check overall system health.

        Returns:
            Health status dictionary
        """
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {},
        }

        # Check error rate
        error_rate = request_logger.get_error_rate()
        health["checks"]["error_rate"] = {
            "status": "healthy" if error_rate < 0.1 else "degraded",
            "value": error_rate,
            "threshold": 0.1,
        }

        # Check request volume
        recent_requests = len(request_logger.get_recent_requests(limit=100))
        health["checks"]["request_volume"] = {
            "status": "healthy",
            "value": recent_requests,
        }

        # Overall status
        if any(
            check["status"] == "degraded"
            for check in health["checks"].values()
        ):
            health["status"] = "degraded"

        return health


# Global health checker
health_checker = HealthCheck()

