"""Voice Automation ChatKit Server implementation."""

from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from openai import AsyncOpenAI

from chatkit.server import ChatKitServer
from chatkit.types import (
    AgentMessageItem,
    MessageItemContent,
    TextContent,
    Thread,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageInput,
    WidgetItem,
)
from chatkit.widgets import Card, Col, Row, Text, Title

from app.constants import OPENAI_API_KEY
from app.memory_store import MemoryStore
from app.agents.orchestrator import OrchestratorAgent

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


class VoiceAutomationServer(ChatKitServer[dict[str, Any]]):
    """ChatKit server for voice automation platform."""

    def __init__(self):
        """Initialize server with memory store and agents."""
        super().__init__(store=MemoryStore())
        self.orchestrator = OrchestratorAgent(openai_client)
        self.active_workflows: dict[str, dict] = {}

    async def generate(
        self,
        context: dict[str, Any],
        thread: ThreadMetadata,
        user_input: UserMessageInput | None = None,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Generate streaming response from orchestrator agent."""

        # Get thread history
        thread_items = await self.store.list_thread_items(
            {"thread_id": thread.id, "limit": 50}, context
        )

        # Build message history
        messages = []
        for item in thread_items.data:
            if hasattr(item, "content"):
                role = "assistant" if isinstance(item, AgentMessageItem) else "user"
                content_text = ""
                if isinstance(item.content, list):
                    for content_item in item.content:
                        if isinstance(content_item, TextContent):
                            content_text += content_item.text
                        elif isinstance(content_item, dict) and "text" in content_item:
                            content_text += content_item["text"]
                
                if content_text:
                    messages.append({"role": role, "content": content_text})

        # Add current user input
        if user_input and hasattr(user_input, "text"):
            messages.append({"role": "user", "content": user_input.text})

        # Generate agent ID
        agent_id = self.generate_item_id("agent", thread, context)

        try:
            # Call OpenAI directly for simplicity
            response = await openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                stream=True,
            )

            # Stream response
            full_response = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    
                    # Create streaming event
                    from chatkit.types import ThreadItemDeltaEvent
                    yield ThreadItemDeltaEvent(
                        item_id=agent_id,
                        delta=content,
                    )

            # Save complete message
            content_list: list[MessageItemContent] = [
                TextContent(type="text", text=full_response)
            ]

            message = AgentMessageItem(
                id=agent_id,
                thread_id=thread.id,
                created_at=datetime.now(),
                content=content_list,
            )

            await self.store.add_thread_item(thread.id, message, context)

            # Signal completion
            from chatkit.types import ThreadItemDoneEvent
            yield ThreadItemDoneEvent(item_id=agent_id)

        except Exception as e:
            # Error handling
            error_msg = f"Error generating response: {str(e)}"
            content_list: list[MessageItemContent] = [
                TextContent(type="text", text=error_msg)
            ]

            message = AgentMessageItem(
                id=agent_id,
                thread_id=thread.id,
                created_at=datetime.now(),
                content=content_list,
            )

            await self.store.add_thread_item(thread.id, message, context)
            
            from chatkit.types import ThreadItemDoneEvent
            yield ThreadItemDoneEvent(item_id=agent_id)

    async def render_widget(
        self, thread: ThreadMetadata, context: dict[str, Any]
    ) -> WidgetItem | None:
        """Render workflow status widget."""

        # Check if there are active workflows for this thread
        thread_workflows = [
            wf
            for wf in self.active_workflows.values()
            if wf.get("thread_id") == thread.id
        ]

        if not thread_workflows:
            return None

        # Create workflow status widget
        widget_id = self.generate_item_id("widget", thread, context)

        workflow_cards = []
        for workflow in thread_workflows:
            card = Card(
                children=[
                    Row(
                        children=[
                            Col(
                                children=[
                                    Title(value=f"Workflow: {workflow['id']}"),
                                    Text(value=f"Task: {workflow.get('task', 'N/A')}"),
                                    Text(
                                        value=f"Status: {workflow.get('status', 'unknown')}",
                                        color="success"
                                        if workflow.get("status") == "completed"
                                        else "info",
                                    ),
                                    Text(
                                        value=f"Progress: {workflow.get('progress', 0)}%"
                                    ),
                                ]
                            )
                        ]
                    )
                ]
            )
            workflow_cards.append(card)

        # Combine into widget
        widget_root = Col(children=workflow_cards)

        return WidgetItem(
            id=widget_id,
            thread_id=thread.id,
            created_at=datetime.now(),
            root=widget_root,
        )

    def generate_item_id(
        self, item_type: str, thread: ThreadMetadata, context: dict[str, Any]
    ) -> str:
        """Generate unique item ID."""
        return self.store.generate_item_id(item_type, thread, context)

