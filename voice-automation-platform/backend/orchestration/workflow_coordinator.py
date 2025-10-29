"""Workflow coordinator for managing DAG execution and dependencies."""

from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

from .agent_factory import AgentFactory
from .schemas import AgentConfig, AgentInstance, AgentState, WorkflowContext, WorkflowState
from .voice_parser import VoiceCommandParser


class WorkflowCoordinator:
    """Coordinate workflow execution with dependency management."""
    
    def __init__(self, factory: AgentFactory):
        """Initialize coordinator with agent factory."""
        self.factory = factory
        self.execution_tasks: Dict[str, asyncio.Task] = {}
    
    async def execute_workflow(self, workflow: WorkflowContext) -> None:
        """Execute workflow with proper dependency ordering.
        
        Args:
            workflow: Workflow context to execute
        """
        try:
            self.factory.update_workflow_state(workflow.workflow_id, WorkflowState.RUNNING)
            
            # Calculate execution order (topological sort)
            execution_levels = VoiceCommandParser.calculate_execution_order(workflow.config)
            
            # Execute agents level by level
            for level in execution_levels:
                await self._execute_level(workflow, level)
            
            self.factory.update_workflow_state(workflow.workflow_id, WorkflowState.COMPLETED)
            
        except Exception as e:
            self.factory.update_workflow_state(workflow.workflow_id, WorkflowState.FAILED)
            raise
    
    async def _execute_level(self, workflow: WorkflowContext, agent_roles: List[str]) -> None:
        """Execute a level of agents in parallel.
        
        Args:
            workflow: Workflow context
            agent_roles: List of agent roles to execute in parallel
        """
        tasks = []
        for role in agent_roles:
            agent = workflow.child_agents.get(role)
            if not agent:
                raise ValueError(f"Agent {role} not found in workflow")
            
            task = asyncio.create_task(self._execute_agent(workflow, agent))
            self.execution_tasks[agent.id] = task
            tasks.append(task)
        
        # Wait for all agents in this level to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                role = agent_roles[i]
                agent = workflow.child_agents[role]
                self.factory.update_agent_state(
                    agent.id,
                    AgentState.FAILED,
                    error=str(result)
                )
                raise result
    
    async def _execute_agent(self, workflow: WorkflowContext, agent: AgentInstance) -> Any:
        """Execute a single agent.
        
        Args:
            workflow: Parent workflow
            agent: Agent instance to execute
            
        Returns:
            Agent output
        """
        try:
            self.factory.update_agent_state(agent.id, AgentState.RUNNING)
            
            # Get Agent SDK instance
            agent_sdk = agent.metadata.get("agent")
            if not agent_sdk:
                raise ValueError(f"Agent {agent.id} has no SDK instance")
            
            # Build task prompt from dependencies
            task_prompt = await self._build_task_prompt(workflow, agent)
            
            # Execute agent
            result = await agent_sdk.run(task_prompt)
            
            self.factory.update_agent_state(
                agent.id,
                AgentState.COMPLETED,
                output=result
            )
            
            return result
            
        except Exception as e:
            self.factory.update_agent_state(
                agent.id,
                AgentState.FAILED,
                error=str(e)
            )
            raise
    
    async def _build_task_prompt(self, workflow: WorkflowContext, agent: AgentInstance) -> str:
        """Build task prompt incorporating dependency outputs.
        
        Args:
            workflow: Workflow context
            agent: Agent instance
            
        Returns:
            Task prompt string
        """
        prompt_parts = [f"Your role: {agent.role}"]
        
        # Add dependency outputs
        if agent.config.depends_on:
            prompt_parts.append("\nContext from dependent agents:")
            for dep_role in agent.config.depends_on:
                dep_agent = workflow.child_agents.get(dep_role)
                if dep_agent and dep_agent.output:
                    prompt_parts.append(f"\n{dep_role} output: {dep_agent.output}")
        
        # Add workflow metadata
        if workflow.metadata:
            prompt_parts.append(f"\nWorkflow context: {workflow.metadata}")
        
        return "\n".join(prompt_parts)
    
    async def cancel_workflow(self, workflow_id: str) -> None:
        """Cancel a running workflow.
        
        Args:
            workflow_id: Workflow to cancel
        """
        workflow = self.factory.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Cancel all running agent tasks
        agents = self.factory.get_workflow_agents(workflow_id)
        for agent in agents.values():
            if agent.state == AgentState.RUNNING:
                task = self.execution_tasks.get(agent.id)
                if task and not task.done():
                    task.cancel()
                
                self.factory.update_agent_state(agent.id, AgentState.CANCELLED)
        
        self.factory.update_workflow_state(workflow_id, WorkflowState.CANCELLED)
    
    async def pause_workflow(self, workflow_id: str) -> None:
        """Pause a running workflow."""
        workflow = self.factory.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        self.factory.update_workflow_state(workflow_id, WorkflowState.PAUSED)
    
    async def resume_workflow(self, workflow_id: str) -> None:
        """Resume a paused workflow."""
        workflow = self.factory.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if workflow.state != WorkflowState.PAUSED:
            raise ValueError(f"Workflow {workflow_id} is not paused")
        
        # Continue execution from where it left off
        await self.execute_workflow(workflow)

