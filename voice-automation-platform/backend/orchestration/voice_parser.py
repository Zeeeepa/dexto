"""Voice command parser using LLM for intent classification and workflow generation."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from .schemas import (
    AgentConfig,
    OrchestrationConfig,
    QualityGate,
    QualityGateType,
    VoiceCommandIntent,
    WebhookConfig,
    WebhookTrigger,
)


class VoiceCommandParser:
    """Parse voice commands and generate orchestration configurations."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize parser with OpenAI client."""
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o"
    
    async def parse(self, command: str) -> VoiceCommandIntent:
        """Parse voice command and generate orchestration config.
        
        Args:
            command: Natural language voice command
            
        Returns:
            VoiceCommandIntent with workflow configuration
        """
        prompt = self._build_parsing_prompt(command)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return self._build_intent(command, result)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for voice command parsing."""
        return """You are an expert AI orchestration planner. Your job is to:

1. Analyze natural language voice commands
2. Classify the user's intent
3. Design a multi-agent workflow to fulfill the request
4. Assign appropriate tools to each agent
5. Define quality gates and webhooks

Return a JSON object with this structure:
{
    "intent": "brief intent description",
    "confidence": 0.95,
    "workflow": {
        "parent_role": "orchestrator",
        "parent_prompt": "You orchestrate...",
        "children": [
            {
                "role": "agent_name",
                "system_prompt": "You are responsible for...",
                "model": "gpt-4o-mini",
                "tools": ["filesystem", "browser"],
                "depends_on": [],
                "webhooks": [],
                "quality_gates": []
            }
        ],
        "max_parallel_agents": 3,
        "timeout_seconds": 300
    }
}

Available MCP tools: filesystem, browser, terminal, search, database, github, slack

Design workflows that:
- Break complex tasks into specialized sub-agents
- Use webhooks for inter-agent communication
- Apply quality gates for validation
- Handle dependencies with depends_on
- Keep workflows modular and maintainable
"""
    
    def _build_parsing_prompt(self, command: str) -> str:
        """Build user prompt for command parsing."""
        return f"""Parse this voice command and design a workflow:

Command: "{command}"

Analyze the command and create a multi-agent orchestration plan. Consider:
- What is the main goal?
- What sub-tasks are needed?
- Which agents should handle each task?
- What tools does each agent need?
- How should agents communicate?
- What validations are necessary?

Return the JSON workflow configuration."""
    
    def _build_intent(self, command: str, result: Dict[str, Any]) -> VoiceCommandIntent:
        """Build VoiceCommandIntent from parsed result."""
        workflow_data = result["workflow"]
        
        # Generate unique workflow ID
        import uuid
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        
        # Build agent configs
        children = []
        for child_data in workflow_data.get("children", []):
            agent_config = AgentConfig(
                role=child_data["role"],
                system_prompt=child_data["system_prompt"],
                model=child_data.get("model", "gpt-4o-mini"),
                tools=child_data.get("tools", []),
                depends_on=child_data.get("depends_on", []),
                webhooks=self._parse_webhooks(child_data.get("webhooks", [])),
                quality_gates=self._parse_quality_gates(child_data.get("quality_gates", []))
            )
            children.append(agent_config)
        
        # Build orchestration config
        orchestration = OrchestrationConfig(
            workflow_id=workflow_id,
            parent_role=workflow_data.get("parent_role", "orchestrator"),
            parent_prompt=workflow_data.get("parent_prompt", "You coordinate agents."),
            children=children,
            max_parallel_agents=workflow_data.get("max_parallel_agents", 5),
            timeout_seconds=workflow_data.get("timeout_seconds", 600)
        )
        
        return VoiceCommandIntent(
            original_command=command,
            intent=result["intent"],
            orchestration=orchestration,
            confidence=result.get("confidence", 0.85),
            alternative_intents=result.get("alternatives", [])
        )
    
    def _parse_webhooks(self, webhooks_data: List[Dict[str, Any]]) -> List[WebhookConfig]:
        """Parse webhook configurations."""
        webhooks = []
        for wh in webhooks_data:
            webhook = WebhookConfig(
                url=wh["url"],
                trigger=WebhookTrigger(wh["trigger"]),
                target_agent=wh.get("target_agent"),
                headers=wh.get("headers", {}),
                retry_count=wh.get("retry_count", 3),
                timeout_seconds=wh.get("timeout_seconds", 30)
            )
            webhooks.append(webhook)
        return webhooks
    
    def _parse_quality_gates(self, gates_data: List[Dict[str, Any]]) -> List[QualityGate]:
        """Parse quality gate configurations."""
        gates = []
        for gate_data in gates_data:
            gate = QualityGate(
                gate_id=gate_data["gate_id"],
                gate_type=QualityGateType(gate_data["gate_type"]),
                validation_config=gate_data.get("validation_config", {}),
                retry_on_fail=gate_data.get("retry_on_fail", True),
                max_retries=gate_data.get("max_retries", 2)
            )
            gates.append(gate)
        return gates
    
    @staticmethod
    def calculate_execution_order(config: OrchestrationConfig) -> List[List[str]]:
        """Calculate agent execution order using topological sort.
        
        Returns list of levels, where each level contains agents that can run in parallel.
        """
        # Build dependency graph
        graph: Dict[str, List[str]] = {agent.role: agent.depends_on for agent in config.children}
        in_degree: Dict[str, int] = {agent.role: len(agent.depends_on) for agent in config.children}
        
        levels: List[List[str]] = []
        remaining = set(graph.keys())
        
        while remaining:
            # Find agents with no dependencies
            current_level = [role for role in remaining if in_degree[role] == 0]
            
            if not current_level:
                raise ValueError("Circular dependency detected in workflow")
            
            levels.append(current_level)
            remaining -= set(current_level)
            
            # Update in-degrees
            for role in current_level:
                for dependent in graph:
                    if role in graph[dependent]:
                        in_degree[dependent] -= 1
        
        return levels

