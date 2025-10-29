"""Webhook adapter for inter-agent communication and event routing."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import aiohttp

from .schemas import WebhookConfig, WebhookEvent, WebhookTrigger


class WebhookEventAdapter:
    """Adapter for webhook-based event communication between agents."""
    
    def __init__(self):
        """Initialize webhook adapter."""
        self.webhooks: Dict[WebhookTrigger, List[WebhookConfig]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.handlers: Dict[WebhookTrigger, List[Callable]] = {}
        self.running = False
        self.worker_task: Optional[asyncio.Task] = None
    
    def add_webhook(self, webhook: WebhookConfig) -> None:
        """Register a webhook configuration.
        
        Args:
            webhook: Webhook configuration
        """
        if webhook.trigger not in self.webhooks:
            self.webhooks[webhook.trigger] = []
        
        self.webhooks[webhook.trigger].append(webhook)
    
    def add_handler(self, trigger: WebhookTrigger, handler: Callable) -> None:
        """Register a handler for webhook events.
        
        Args:
            trigger: Event trigger type
            handler: Async callback function(event: WebhookEvent)
        """
        if trigger not in self.handlers:
            self.handlers[trigger] = []
        
        self.handlers[trigger].append(handler)
    
    async def emit(self, event: WebhookEvent) -> None:
        """Emit a webhook event.
        
        Args:
            event: Event to emit
        """
        await self.event_queue.put(event)
    
    async def start(self) -> None:
        """Start webhook event processing."""
        if self.running:
            return
        
        self.running = True
        self.worker_task = asyncio.create_task(self._process_events())
    
    async def stop(self) -> None:
        """Stop webhook event processing."""
        self.running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
    
    async def _process_events(self) -> None:
        """Process events from queue."""
        while self.running:
            try:
                event = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=1.0
                )
                
                # Call registered webhooks
                webhooks = self.webhooks.get(event.trigger, [])
                tasks = [self._call_webhook(webhook, event) for webhook in webhooks]
                
                # Call local handlers
                handlers = self.handlers.get(event.trigger, [])
                tasks.extend([handler(event) for handler in handlers])
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing webhook event: {e}")
    
    async def _call_webhook(self, webhook: WebhookConfig, event: WebhookEvent) -> None:
        """Call a webhook endpoint.
        
        Args:
            webhook: Webhook configuration
            event: Event to send
        """
        payload = {
            "event_id": event.event_id,
            "trigger": event.trigger.value,
            "workflow_id": event.workflow_id,
            "agent_id": event.agent_id,
            "payload": event.payload,
            "timestamp": event.timestamp.isoformat()
        }
        
        for attempt in range(webhook.retry_count + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        webhook.url,
                        json=payload,
                        headers=webhook.headers,
                        timeout=aiohttp.ClientTimeout(total=webhook.timeout_seconds)
                    ) as response:
                        if response.status < 400:
                            return  # Success
                        
                        # Log failure
                        print(f"Webhook call failed: {response.status}")
                
            except Exception as e:
                print(f"Webhook error (attempt {attempt + 1}): {e}")
                
                if attempt < webhook.retry_count:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def create_event(
        self,
        trigger: WebhookTrigger,
        workflow_id: str,
        payload: Dict[str, Any],
        agent_id: Optional[str] = None
    ) -> WebhookEvent:
        """Create and emit a webhook event.
        
        Args:
            trigger: Event trigger type
            workflow_id: Workflow ID
            payload: Event payload data
            agent_id: Optional agent ID
            
        Returns:
            Created WebhookEvent
        """
        import uuid
        
        event = WebhookEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            trigger=trigger,
            workflow_id=workflow_id,
            agent_id=agent_id,
            payload=payload,
            timestamp=datetime.now()
        )
        
        await self.emit(event)
        return event

