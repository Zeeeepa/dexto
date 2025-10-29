"""Webhook integration system."""

import httpx
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class WebhookEvent(str, Enum):
    """Webhook event types."""
    
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    AGENT_ACTION = "agent.action"
    AGENT_ERROR = "agent.error"
    METRIC_THRESHOLD = "metric.threshold"
    USER_REGISTERED = "user.registered"
    ERROR_OCCURRED = "error.occurred"


class WebhookDeliveryStatus(str, Enum):
    """Webhook delivery status."""
    
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class Webhook:
    """Webhook configuration."""

    def __init__(
        self,
        id: str,
        url: str,
        events: List[WebhookEvent],
        secret: Optional[str] = None,
        active: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize webhook.

        Args:
            id: Webhook identifier
            url: Target URL
            events: List of events to subscribe to
            secret: Optional secret for signature
            active: Whether webhook is active
            metadata: Optional metadata
        """
        self.id = id
        self.url = url
        self.events = events
        self.secret = secret
        self.active = active
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()


class WebhookManager:
    """Manage webhooks and deliveries."""

    def __init__(self):
        """Initialize webhook manager."""
        self.webhooks: Dict[str, Webhook] = {}
        self.delivery_history: List[Dict[str, Any]] = []
        self.max_history = 1000
        self.retry_attempts = 3
        self.timeout = 10

    def register_webhook(
        self,
        id: str,
        url: str,
        events: List[str],
        secret: Optional[str] = None,
    ) -> Webhook:
        """
        Register new webhook.

        Args:
            id: Webhook identifier
            url: Target URL
            events: List of event types
            secret: Optional secret

        Returns:
            Registered webhook
        """
        webhook = Webhook(
            id=id,
            url=url,
            events=[WebhookEvent(e) for e in events],
            secret=secret,
        )
        
        self.webhooks[id] = webhook
        logger.info(f"Webhook registered: {id} ({url})")
        
        return webhook

    def unregister_webhook(self, id: str) -> bool:
        """
        Unregister webhook.

        Args:
            id: Webhook identifier

        Returns:
            Whether webhook was removed
        """
        if id in self.webhooks:
            del self.webhooks[id]
            logger.info(f"Webhook unregistered: {id}")
            return True
        return False

    def get_webhook(self, id: str) -> Optional[Webhook]:
        """Get webhook by ID."""
        return self.webhooks.get(id)

    def list_webhooks(self) -> List[Webhook]:
        """List all webhooks."""
        return list(self.webhooks.values())

    async def trigger_event(
        self,
        event_type: WebhookEvent,
        data: Dict[str, Any],
    ):
        """
        Trigger webhook event.

        Args:
            event_type: Event type
            data: Event data
        """
        # Find webhooks subscribed to this event
        webhooks = [
            wh for wh in self.webhooks.values()
            if wh.active and event_type in wh.events
        ]

        if not webhooks:
            logger.debug(f"No webhooks for event: {event_type}")
            return

        # Prepare payload
        payload = {
            "event": event_type.value,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }

        # Deliver to all subscribed webhooks
        for webhook in webhooks:
            await self._deliver_webhook(webhook, payload)

    async def _deliver_webhook(
        self, webhook: Webhook, payload: Dict[str, Any]
    ):
        """
        Deliver webhook payload.

        Args:
            webhook: Webhook configuration
            payload: Payload to send
        """
        delivery_id = f"delivery_{len(self.delivery_history) + 1}"
        
        delivery_record = {
            "id": delivery_id,
            "webhook_id": webhook.id,
            "url": webhook.url,
            "event": payload["event"],
            "status": WebhookDeliveryStatus.PENDING.value,
            "attempts": 0,
            "created_at": datetime.now().isoformat(),
        }

        try:
            # Add signature if secret provided
            headers = {"Content-Type": "application/json"}
            
            if webhook.secret:
                import hmac
                import hashlib
                import json
                
                signature = hmac.new(
                    webhook.secret.encode(),
                    json.dumps(payload).encode(),
                    hashlib.sha256,
                ).hexdigest()
                
                headers["X-Webhook-Signature"] = f"sha256={signature}"

            # Send request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    webhook.url,
                    json=payload,
                    headers=headers,
                )
                
                response.raise_for_status()
                
                delivery_record["status"] = WebhookDeliveryStatus.SUCCESS.value
                delivery_record["response_code"] = response.status_code
                delivery_record["completed_at"] = datetime.now().isoformat()
                
                logger.info(
                    f"Webhook delivered: {webhook.id} "
                    f"(event: {payload['event']}, status: {response.status_code})"
                )

        except Exception as e:
            delivery_record["status"] = WebhookDeliveryStatus.FAILED.value
            delivery_record["error"] = str(e)
            delivery_record["completed_at"] = datetime.now().isoformat()
            
            logger.error(
                f"Webhook delivery failed: {webhook.id} "
                f"(event: {payload['event']}, error: {e})"
            )

            # Retry logic could be added here

        finally:
            # Store delivery record
            self.delivery_history.append(delivery_record)
            
            # Limit history size
            if len(self.delivery_history) > self.max_history:
                self.delivery_history = self.delivery_history[-self.max_history:]

    def get_delivery_history(
        self,
        webhook_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get webhook delivery history.

        Args:
            webhook_id: Optional webhook ID to filter
            limit: Maximum number of records

        Returns:
            List of delivery records
        """
        history = self.delivery_history

        if webhook_id:
            history = [
                record for record in history
                if record["webhook_id"] == webhook_id
            ]

        return history[-limit:]

    def get_webhook_stats(self, webhook_id: str) -> Dict[str, Any]:
        """
        Get webhook statistics.

        Args:
            webhook_id: Webhook identifier

        Returns:
            Statistics dictionary
        """
        deliveries = [
            record for record in self.delivery_history
            if record["webhook_id"] == webhook_id
        ]

        total = len(deliveries)
        success = len([d for d in deliveries if d["status"] == "success"])
        failed = len([d for d in deliveries if d["status"] == "failed"])

        return {
            "webhook_id": webhook_id,
            "total_deliveries": total,
            "successful": success,
            "failed": failed,
            "success_rate": (success / total * 100) if total > 0 else 0,
        }


# Global webhook manager
webhook_manager = WebhookManager()


# Webhook helper functions
async def notify_workflow_started(workflow_id: str, task: str):
    """Notify workflow started."""
    await webhook_manager.trigger_event(
        WebhookEvent.WORKFLOW_STARTED,
        {
            "workflow_id": workflow_id,
            "task": task,
        },
    )


async def notify_workflow_completed(
    workflow_id: str, result: Any, duration: float
):
    """Notify workflow completed."""
    await webhook_manager.trigger_event(
        WebhookEvent.WORKFLOW_COMPLETED,
        {
            "workflow_id": workflow_id,
            "result": result,
            "duration": duration,
        },
    )


async def notify_workflow_failed(workflow_id: str, error: str):
    """Notify workflow failed."""
    await webhook_manager.trigger_event(
        WebhookEvent.WORKFLOW_FAILED,
        {
            "workflow_id": workflow_id,
            "error": error,
        },
    )


async def notify_agent_action(agent_name: str, action: str, details: Dict):
    """Notify agent action."""
    await webhook_manager.trigger_event(
        WebhookEvent.AGENT_ACTION,
        {
            "agent": agent_name,
            "action": action,
            "details": details,
        },
    )


async def notify_error(error_type: str, error_message: str, details: Dict):
    """Notify error occurred."""
    await webhook_manager.trigger_event(
        WebhookEvent.ERROR_OCCURRED,
        {
            "error_type": error_type,
            "error_message": error_message,
            "details": details,
        },
    )

