"""Orchestrator Agent - Main controller for multi-agent workflows."""

from typing import Any, Dict, List
from datetime import datetime

from openai import AsyncOpenAI
from chatkit.agents import AgentContext
from agents import Agent, function_tool

from app.constants import ORCHESTRATOR_MODEL


class OrchestratorAgent:
    """Main orchestrator agent that coordinates sub-agents and workflows."""

    def __init__(self, openai_client: AsyncOpenAI):
        """Initialize orchestrator with OpenAI client."""
        self.client = openai_client
        self.active_workflows: Dict[str, Dict] = {}
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the orchestrator agent with tools."""

        @function_tool(description="Create a workflow with multiple sub-agents")
        async def create_workflow(
            ctx: AgentContext,
            task_description: str,
            sub_agents: List[str],
            tools_required: List[str],
        ) -> Dict[str, Any]:
            """
            Create a workflow for a complex task.

            Args:
                task_description: Description of the task to accomplish
                sub_agents: List of sub-agent types needed (research, code, test, etc.)
                tools_required: List of MCP tools needed

            Returns:
                Workflow details including ID and status
            """
            workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            workflow = {
                "id": workflow_id,
                "task": task_description,
                "status": "created",
                "sub_agents": [
                    {
                        "type": agent_type,
                        "status": "pending",
                        "tools": tools_required,
                    }
                    for agent_type in sub_agents
                ],
                "created_at": datetime.now().isoformat(),
                "progress": 0,
            }

            self.active_workflows[workflow_id] = workflow
            return workflow

        @function_tool(description="Get workflow status and progress")
        async def get_workflow_status(
            ctx: AgentContext, workflow_id: str
        ) -> Dict[str, Any]:
            """
            Get the current status of a workflow.

            Args:
                workflow_id: ID of the workflow

            Returns:
                Workflow status details
            """
            if workflow_id not in self.active_workflows:
                return {"error": f"Workflow {workflow_id} not found"}

            return self.active_workflows[workflow_id]

        @function_tool(description="Update workflow progress")
        async def update_workflow_progress(
            ctx: AgentContext,
            workflow_id: str,
            progress: int,
            status: str = None,
        ) -> Dict[str, Any]:
            """
            Update workflow progress.

            Args:
                workflow_id: ID of the workflow
                progress: Progress percentage (0-100)
                status: Optional status update

            Returns:
                Updated workflow details
            """
            if workflow_id not in self.active_workflows:
                return {"error": f"Workflow {workflow_id} not found"}

            workflow = self.active_workflows[workflow_id]
            workflow["progress"] = progress
            if status:
                workflow["status"] = status
            workflow["updated_at"] = datetime.now().isoformat()

            return workflow

        @function_tool(description="Execute a sub-agent task")
        async def execute_sub_agent(
            ctx: AgentContext,
            workflow_id: str,
            agent_type: str,
            task: str,
        ) -> Dict[str, Any]:
            """
            Execute a specific sub-agent task.

            Args:
                workflow_id: ID of the parent workflow
                agent_type: Type of sub-agent (research, code, test, etc.)
                task: Task description for the sub-agent

            Returns:
                Sub-agent execution results
            """
            if workflow_id not in self.active_workflows:
                return {"error": f"Workflow {workflow_id} not found"}

            workflow = self.active_workflows[workflow_id]

            # Find the sub-agent
            sub_agent = next(
                (a for a in workflow["sub_agents"] if a["type"] == agent_type),
                None,
            )

            if not sub_agent:
                return {
                    "error": f"Sub-agent {agent_type} not found in workflow {workflow_id}"
                }

            # Update sub-agent status
            sub_agent["status"] = "running"
            sub_agent["task"] = task
            sub_agent["started_at"] = datetime.now().isoformat()

            # Simulate execution (in real implementation, spawn actual sub-agent)
            result = {
                "agent_type": agent_type,
                "task": task,
                "status": "completed",
                "output": f"Executed {agent_type} for: {task}",
                "completed_at": datetime.now().isoformat(),
            }

            sub_agent["status"] = "completed"
            sub_agent["result"] = result

            return result

        # Create agent with tools
        agent = Agent[AgentContext](
            model=ORCHESTRATOR_MODEL,
            name="VoiceOrchestrator",
            instructions="""You are an expert orchestrator agent that coordinates complex multi-agent workflows.

Your responsibilities:
1. **Understand User Intent**: Parse voice commands and determine the required workflow
2. **Task Decomposition**: Break complex tasks into sub-tasks for specialized agents
3. **Agent Selection**: Choose appropriate sub-agents (research, code, test, analysis)
4. **Tool Assignment**: Assign MCP tools to sub-agents based on their needs
5. **Progress Tracking**: Monitor and report workflow progress
6. **Quality Validation**: Ensure outputs meet quality standards
7. **Clear Communication**: Provide conversational updates to users

Available Sub-Agents:
- **ResearchAgent**: Web research, data collection, information synthesis
- **CodeAgent**: Code generation, analysis, refactoring
- **TestAgent**: Test creation, execution, validation
- **AnalysisAgent**: Data analysis, metrics, insights

When a user gives a command:
1. Acknowledge their request conversationally
2. Create a workflow with appropriate sub-agents
3. Execute sub-agents in logical order
4. Provide progress updates
5. Summarize results clearly

Be conversational, helpful, and proactive. Ask clarifying questions when needed.""",
            tools=[
                create_workflow,
                get_workflow_status,
                update_workflow_progress,
                execute_sub_agent,
            ],
        )

        return agent

    def get_agent(self) -> Agent:
        """Get the orchestrator agent instance."""
        return self.agent

