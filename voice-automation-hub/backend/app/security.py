"""Security utilities and middleware."""

import hashlib
import secrets
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiting to prevent abuse."""

    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed.

        Args:
            identifier: Unique identifier (IP, user ID, etc.)

        Returns:
            Whether request is allowed
        """
        now = datetime.now().timestamp()
        cutoff = now - self.window_seconds

        # Clean old requests
        self.requests[identifier] = [
            ts for ts in self.requests[identifier]
            if ts > cutoff
        ]

        # Check limit
        if len(self.requests[identifier]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False

        # Add new request
        self.requests[identifier].append(now)
        return True

    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier."""
        now = datetime.now().timestamp()
        cutoff = now - self.window_seconds

        recent = [
            ts for ts in self.requests.get(identifier, [])
            if ts > cutoff
        ]

        return max(0, self.max_requests - len(recent))


class APIKeyManager:
    """Manage API keys for authentication."""

    def __init__(self):
        """Initialize API key manager."""
        self.keys: Dict[str, Dict[str, Any]] = {}

    def generate_key(
        self,
        name: str,
        permissions: list = None
    ) -> str:
        """
        Generate new API key.

        Args:
            name: Key name/description
            permissions: List of permissions

        Returns:
            Generated API key
        """
        key = f"vh_{secrets.token_urlsafe(32)}"
        
        self.keys[key] = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "permissions": permissions or ["read", "write"],
            "last_used": None,
            "usage_count": 0,
        }

        logger.info(f"Generated API key: {name}")
        return key

    def validate_key(self, key: str) -> bool:
        """
        Validate API key.

        Args:
            key: API key to validate

        Returns:
            Whether key is valid
        """
        if key not in self.keys:
            return False

        # Update usage
        self.keys[key]["last_used"] = datetime.now().isoformat()
        self.keys[key]["usage_count"] += 1

        return True

    def revoke_key(self, key: str) -> bool:
        """
        Revoke API key.

        Args:
            key: API key to revoke

        Returns:
            Whether key was revoked
        """
        if key in self.keys:
            del self.keys[key]
            logger.info(f"Revoked API key: {key[:10]}...")
            return True
        return False

    def list_keys(self) -> list:
        """List all API keys (masked)."""
        return [
            {
                "key": f"{key[:10]}...{key[-4:]}",
                "name": data["name"],
                "created_at": data["created_at"],
                "last_used": data["last_used"],
                "usage_count": data["usage_count"],
            }
            for key, data in self.keys.items()
        ]


class InputValidator:
    """Validate and sanitize inputs."""

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input.

        Args:
            value: Input string
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            raise ValueError("Input must be string")

        # Trim whitespace
        value = value.strip()

        # Check length
        if len(value) > max_length:
            raise ValueError(f"Input too long (max {max_length} characters)")

        # Remove null bytes
        value = value.replace("\x00", "")

        return value

    @staticmethod
    def validate_workflow_name(name: str) -> str:
        """Validate workflow name."""
        name = InputValidator.sanitize_string(name, max_length=100)

        if not name:
            raise ValueError("Workflow name cannot be empty")

        # Only allow alphanumeric, spaces, hyphens, underscores
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
            raise ValueError(
                "Workflow name can only contain letters, numbers, "
                "spaces, hyphens, and underscores"
            )

        return name

    @staticmethod
    def validate_task_description(description: str) -> str:
        """Validate task description."""
        description = InputValidator.sanitize_string(description, max_length=5000)

        if not description:
            raise ValueError("Task description cannot be empty")

        return description

    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email address."""
        import re
        
        email = email.strip().lower()
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email address")

        return email


class ContentSecurityPolicy:
    """Content Security Policy utilities."""

    @staticmethod
    def get_csp_header() -> str:
        """Get Content Security Policy header value."""
        directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self' ws: wss:",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        return "; ".join(directives)

    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": ContentSecurityPolicy.get_csp_header(),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }


class AuditLogger:
    """Audit logging for security events."""

    def __init__(self):
        """Initialize audit logger."""
        self.audit_log = []

    def log_event(
        self,
        event_type: str,
        actor: str,
        action: str,
        resource: str,
        result: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log audit event.

        Args:
            event_type: Type of event
            actor: Who performed the action
            action: What action was performed
            resource: What resource was affected
            result: Outcome (success/failure)
            details: Additional details
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "actor": actor,
            "action": action,
            "resource": resource,
            "result": result,
            "details": details or {},
        }

        self.audit_log.append(entry)
        logger.info(f"Audit: {event_type} - {actor} {action} {resource}: {result}")

        # Keep only recent entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

    def get_recent_events(self, limit: int = 100) -> list:
        """Get recent audit events."""
        return self.audit_log[-limit:]


# Global instances
rate_limiter = RateLimiter()
api_key_manager = APIKeyManager()
audit_logger = AuditLogger()

