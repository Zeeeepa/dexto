"""Error handling and recovery utilities."""

import logging
import traceback
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories."""
    AGENT_ERROR = "agent_error"
    TOOL_ERROR = "tool_error"
    API_ERROR = "api_error"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"


class AppError(Exception):
    """Base application error."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM_ERROR,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = True,
    ):
        """
        Initialize application error.

        Args:
            message: Error message
            category: Error category
            severity: Error severity
            details: Additional error details
            recoverable: Whether error is recoverable
        """
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.recoverable = recoverable
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "error": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp,
        }


class AgentError(AppError):
    """Agent-specific error."""

    def __init__(self, message: str, agent_name: str, **kwargs):
        """Initialize agent error."""
        super().__init__(
            message,
            category=ErrorCategory.AGENT_ERROR,
            details={"agent": agent_name},
            **kwargs
        )


class ToolError(AppError):
    """Tool execution error."""

    def __init__(self, message: str, tool_name: str, **kwargs):
        """Initialize tool error."""
        super().__init__(
            message,
            category=ErrorCategory.TOOL_ERROR,
            details={"tool": tool_name},
            **kwargs
        )


class ValidationError(AppError):
    """Validation error."""

    def __init__(self, message: str, field: str, **kwargs):
        """Initialize validation error."""
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.LOW,
            details={"field": field},
            **kwargs
        )


class ErrorHandler:
    """Centralized error handling."""

    def __init__(self):
        """Initialize error handler."""
        self.error_history = []
        self.error_counts = {}

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle an error with logging and tracking.

        Args:
            error: Exception to handle
            context: Additional context

        Returns:
            Error response dictionary
        """
        # Log error
        logger.error(
            f"Error occurred: {str(error)}",
            exc_info=True,
            extra={"context": context}
        )

        # Track error
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # Store in history
        error_entry = {
            "type": error_type,
            "message": str(error),
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
            "traceback": traceback.format_exc(),
        }
        self.error_history.append(error_entry)

        # Keep only recent errors
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]

        # Return error response
        if isinstance(error, AppError):
            return error.to_dict()
        else:
            return {
                "error": str(error),
                "category": ErrorCategory.SYSTEM_ERROR.value,
                "severity": ErrorSeverity.HIGH.value,
                "recoverable": False,
                "timestamp": datetime.now().isoformat(),
            }

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "total_errors": len(self.error_history),
            "by_type": dict(self.error_counts),
            "recent_errors": self.error_history[-10:] if self.error_history else [],
        }


class RetryHandler:
    """Handle operation retries with exponential backoff."""

    @staticmethod
    async def retry_with_backoff(
        func: Callable,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        exceptions: tuple = (Exception,)
    ):
        """
        Retry function with exponential backoff.

        Args:
            func: Async function to retry
            max_attempts: Maximum retry attempts
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            exceptions: Exceptions to catch and retry

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        import asyncio

        for attempt in range(max_attempts):
            try:
                return await func()
            except exceptions as e:
                if attempt == max_attempts - 1:
                    raise

                delay = min(base_delay * (2 ** attempt), max_delay)
                logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds before attempting to close circuit
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open

    def call(self, func: Callable, *args, **kwargs):
        """
        Call function through circuit breaker.

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception if circuit is open
        """
        import time

        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise AppError(
                    "Circuit breaker is open",
                    category=ErrorCategory.SYSTEM_ERROR,
                    severity=ErrorSeverity.HIGH,
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        """Handle failed call."""
        import time

        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )


# Global error handler
error_handler = ErrorHandler()

