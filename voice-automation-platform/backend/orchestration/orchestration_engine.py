"""Main orchestration engine coordinating all components."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from .agent_factory import AgentFactory
from .quality_gates import QualityGateSystem
from .schemas import (
    AgentConfig,
    AgentInstance,
    OrchestrationConfig,
    WebhookTrigger,
    WorkflowContext,
)
from .voice_parser import VoiceCommandParser
from .webhook_adapter import WebhookEventAdapter
from .workflow_coordinator import WorkflowCoordinator


class OrchestrationEngine:
    """Main engine coordinating voice-driven multi-agent workflows."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize orchestration engine.
        
        Args:
            api_key: OpenAI API key for voice parsing and quality gates
        """
        self.voice_parser = VoiceCommandParser(api_key=api_key)
        self.factory = AgentFactory()
        self.coordinator = WorkflowCoordinator(self.factory)
        self.quality_gates = QualityGateSystem(api_key=api_key)
        self.webhook_adapter = WebhookEventAdapter()
    
    async def start(self) -> None:
        """Start the orchestration engine."""
        await self.webhook_adapter.start()
        
        # Register webhook handlers for workflow events
        self.webhook_adapter.add_handler(
            WebhookTrigger.AGENT_COMPLETED,
            self._handle_agent_completed
        )
        self.webhook_adapter.add_handler(
            WebhookTrigger.AGENT_FAILED,
            self._handle_agent_failed
        )
    
    async def stop(self) -> None:
        """Stop the orchestration engine."""
        await self.webhook_adapter.stop()
    
    async def process_voice_command(self, command: str, metadata: Optional[Dict[str, Any]] = None) -> WorkflowContext:
        """Process voice command and create workflow.
        
        Args:
            command: Natural language voice command
            metadata: Additional context (e.g., thread_id, user_id)
            
        Returns:
            Created WorkflowContext
        """
        # Parse voice command
        intent = await self.voice_parser.parse(command)
        
        # Create workflow
        workflow = await self.create_workflow(
            intent.orchestration,
            metadata=metadata
        )
        
        # Emit workflow started event
        await self.webhook_adapter.create_event(
            trigger=WebhookTrigger.WORKFLOW_STARTED,
            workflow_id=workflow.workflow_id,
            payload={"intent": intent.intent, "confidence": intent.confidence}
        )
        
        return workflow
    
    async def create_workflow(
        self,
        config: OrchestrationConfig,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowContext:
        """Create a new workflow.
        
        Args:
            config: Orchestration configuration
            metadata: Additional workflow metadata
            
        Returns:
            Created WorkflowContext
        """
        # Create workflow with parent agent
        workflow = await self.factory.create_workflow(config, metadata)
        
        # Register workflow-level webhooks
        for webhook in config.webhooks:
            self.webhook_adapter.add_webhook(webhook)
        
        return workflow
    
    async def spawn_children(self, workflow: WorkflowContext) -> None:
        """Spawn all child agents in the workflow.
        
        Args:
            workflow: Workflow context
        """
        # Calculate execution order
        execution_levels = VoiceCommandParser.calculate_execution_order(workflow.config)
        
        # Spawn all agents (they'll wait for dependencies)
        for level in execution_levels:
            for agent_role in level:
                agent_config = next(
                    c for c in workflow.config.children
                    if c.role == agent_role
                )
                
                agent = await self.factory.spawn_child_agent(workflow, agent_config)
                
                # Emit agent created event
                await self.webhook_adapter.create_event(
                    trigger=WebhookTrigger.AGENT_STARTED,
                    workflow_id=workflow.workflow_id,
                    agent_id=agent.id,
                    payload={"role": agent.role, "tools": agent.config.tools}
                )
    
    async def execute_workflow(self, workflow: WorkflowContext) -> None:
        """Execute a workflow asynchronously.
        
        Args:
            workflow: Workflow to execute
        """
        try:
            await self.coordinator.execute_workflow(workflow)
            
            # Emit workflow completed event
            await self.webhook_adapter.create_event(
                trigger=WebhookTrigger.WORKFLOW_COMPLETED,
                workflow_id=workflow.workflow_id,
                payload={
                    "duration_seconds": (
                        workflow.completed_at - workflow.started_at
                    ).total_seconds() if workflow.completed_at and workflow.started_at else 0
                }
            )
            
        except Exception as e:
            # Emit workflow failed event
            await self.webhook_adapter.create_event(
                trigger=WebhookTrigger.WORKFLOW_FAILED,
                workflow_id=workflow.workflow_id,
                payload={"error": str(e)}
            )
            raise
    
    async def execute_agent(
        self,
        agent: AgentInstance,
        workflow: WorkflowContext
    ) -> Any:
        """Execute a single agent with quality gates.
        
        Args:
            agent: Agent instance to execute
            workflow: Parent workflow
            
        Returns:
            Agent output (after quality gate validation)
        """
        try:
            # Execute agent
            result = await self.coordinator._execute_agent(workflow, agent)
            
            # Apply quality gates
            if agent.config.quality_gates:
                for gate in agent.config.quality_gates:
                    gate_result = await self.quality_gates.validate_with_retry(
                        gate=gate,
                        output=result,
                        agent=agent,
                        retry_func=lambda: self.coordinator._execute_agent(workflow, agent)
                    )
                    
                    if gate_result.passed:
                        await self.webhook_adapter.create_event(
                            trigger=WebhookTrigger.QUALITY_GATE_PASSED,
                            workflow_id=workflow.workflow_id,
                            agent_id=agent.id,
                            payload={"gate_id": gate.gate_id}
                        )
                    else:
                        await self.webhook_adapter.create_event(
                            trigger=WebhookTrigger.QUALITY_GATE_FAILED,
                            workflow_id=workflow.workflow_id,
                            agent_id=agent.id,
                            payload={
                                "gate_id": gate.gate_id,
                                "error": gate_result.error
                            }
                        )
                        
                        if not gate.retry_on_fail:
                            raise ValueError(f"Quality gate {gate.gate_id} failed")
            
            # Emit agent completed event
            await self.webhook_adapter.create_event(
                trigger=WebhookTrigger.AGENT_COMPLETED,
                workflow_id=workflow.workflow_id,
                agent_id=agent.id,
                payload={"output": result}
            )
            
            return result
            
        except Exception as e:
            # Emit agent failed event
            await self.webhook_adapter.create_event(
                trigger=WebhookTrigger.AGENT_FAILED,
                workflow_id=workflow.workflow_id,
                agent_id=agent.id,
                payload={"error": str(e)}
            )
            raise
    
    async def cancel_workflow(self, workflow_id: str) -> None:
        """Cancel a running workflow.
        
        Args:
            workflow_id: Workflow to cancel
        """
        await self.coordinator.cancel_workflow(workflow_id)
    
    async def _handle_agent_completed(self, event) -> None:
        """Handle agent completion event."""
        # Log or process completion
        pass
    
    async def _handle_agent_failed(self, event) -> None:
        """Handle agent failure event."""
        # Log or trigger escalation
        pass
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowContext]:
        """Get workflow by ID."""
        return self.factory.get_workflow(workflow_id)
    
    def get_agent(self, agent_id: str) -> Optional[AgentInstance]:
        """Get agent by ID."""
        return self.factory.get_agent(agent_id)

