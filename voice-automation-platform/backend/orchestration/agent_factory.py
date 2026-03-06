"""Agent factory for creating and managing agent instances."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from agents import Agent

from .schemas import (
    AgentConfig,
    AgentInstance,
    AgentState,
    OrchestrationConfig,
    WorkflowContext,
    WorkflowState,
)


class AgentFactory:
    """Factory for creating and managing agent lifecycle."""
    
    def __init__(self):
        """Initialize agent factory."""
        self.workflows: Dict[str, WorkflowContext] = {}
        self.agents: Dict[str, AgentInstance] = {}
    
    async def create_workflow(
        self,
        config: OrchestrationConfig,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowContext:
        """Create a new workflow with parent orchestrator.
        
        Args:
            config: Orchestration configuration
            metadata: Additional workflow metadata
            
        Returns:
            WorkflowContext with parent agent created
        """
        workflow = WorkflowContext(
            workflow_id=config.workflow_id,
            config=config,
            state=WorkflowState.CREATING,
            metadata=metadata or {}
        )
        
        # Create parent orchestrator agent
        parent_instance = await self._create_agent_instance(
            role=config.parent_role,
            system_prompt=config.parent_prompt,
            model="gpt-4o",  # Use powerful model for orchestrator
            tools=[],  # Orchestrator doesn't need tools
            workflow_id=config.workflow_id
        )
        
        workflow.parent_agent = parent_instance
        self.workflows[config.workflow_id] = workflow
        self.agents[parent_instance.id] = parent_instance
        
        return workflow
    
    async def spawn_child_agent(
        self,
        workflow: WorkflowContext,
        agent_config: AgentConfig
    ) -> AgentInstance:
        """Spawn a child agent in the workflow.
        
        Args:
            workflow: Parent workflow context
            agent_config: Child agent configuration
            
        Returns:
            Created AgentInstance
        """
        agent_instance = await self._create_agent_instance(
            role=agent_config.role,
            system_prompt=agent_config.system_prompt,
            model=agent_config.model,
            tools=agent_config.tools,
            workflow_id=workflow.workflow_id,
            config=agent_config
        )
        
        workflow.child_agents[agent_config.role] = agent_instance
        self.agents[agent_instance.id] = agent_instance
        
        return agent_instance
    
    async def _create_agent_instance(
        self,
        role: str,
        system_prompt: str,
        model: str,
        tools: list[str],
        workflow_id: str,
        config: Optional[AgentConfig] = None
    ) -> AgentInstance:
        """Create a new agent instance.
        
        Args:
            role: Agent role identifier
            system_prompt: System instructions
            model: LLM model to use
            tools: List of MCP tool names
            workflow_id: Parent workflow ID
            config: Optional full agent config
            
        Returns:
            AgentInstance ready to run
        """
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        
        # Create Agent SDK instance
        # NOTE: This is a placeholder - actual Agent SDK integration needed
        agent = Agent(
            name=role,
            instructions=system_prompt,
            model=model
        )
        
        # Create instance wrapper
        if config is None:
            config = AgentConfig(
                role=role,
                system_prompt=system_prompt,
                model=model,
                tools=tools
            )
        
        instance = AgentInstance(
            id=agent_id,
            role=role,
            config=config,
            state=AgentState.CREATING,
            created_at=datetime.now()
        )
        
        # Store agent reference (not serialized)
        instance.metadata = {"agent": agent, "workflow_id": workflow_id}
        
        return instance
    
    def update_agent_state(
        self,
        agent_id: str,
        state: AgentState,
        output: Optional[Any] = None,
        error: Optional[str] = None
    ) -> None:
        """Update agent state.
        
        Args:
            agent_id: Agent instance ID
            state: New state
            output: Optional output data
            error: Optional error message
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.agents[agent_id]
        agent.state = state
        
        if state == AgentState.RUNNING and agent.started_at is None:
            agent.started_at = datetime.now()
        
        if state in (AgentState.COMPLETED, AgentState.FAILED):
            agent.completed_at = datetime.now()
        
        if output is not None:
            agent.output = output
        
        if error is not None:
            agent.error = error
    
    def update_workflow_state(
        self,
        workflow_id: str,
        state: WorkflowState
    ) -> None:
        """Update workflow state.
        
        Args:
            workflow_id: Workflow ID
            state: New state
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        workflow.state = state
        
        if state == WorkflowState.RUNNING and workflow.started_at is None:
            workflow.started_at = datetime.now()
        
        if state in (WorkflowState.COMPLETED, WorkflowState.FAILED):
            workflow.completed_at = datetime.now()
    
    def get_agent(self, agent_id: str) -> Optional[AgentInstance]:
        """Get agent instance by ID."""
        return self.agents.get(agent_id)
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowContext]:
        """Get workflow context by ID."""
        return self.workflows.get(workflow_id)
    
    def get_workflow_agents(self, workflow_id: str) -> Dict[str, AgentInstance]:
        """Get all agents in a workflow."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {}
        
        agents = {}
        if workflow.parent_agent:
            agents[workflow.parent_agent.role] = workflow.parent_agent
        agents.update(workflow.child_agents)
        
        return agents

