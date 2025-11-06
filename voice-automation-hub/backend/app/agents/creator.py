"""Creator Agent - Orchestrates sub-agents based on voice commands."""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
import re
import json

logger = logging.getLogger(__name__)


class QualityGate:
    """Quality gate for validating workflow results."""

    def __init__(
        self,
        name: str,
        check_type: str,
        criteria: Dict[str, Any],
    ):
        """
        Initialize quality gate.

        Args:
            name: Gate name
            check_type: Type of check (error_threshold, completion_time, etc.)
            criteria: Validation criteria
        """
        self.name = name
        self.check_type = check_type
        self.criteria = criteria

    def validate(self, result: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate result against gate criteria.

        Args:
            result: Workflow result

        Returns:
            (passed, message)
        """
        if self.check_type == "error_threshold":
            error_count = result.get("errors", 0)
            threshold = self.criteria.get("max_errors", 0)
            passed = error_count <= threshold
            message = (
                f"Error count: {error_count} (threshold: {threshold})"
                if passed
                else f"Too many errors: {error_count} > {threshold}"
            )
            return passed, message

        elif self.check_type == "completion_time":
            duration = result.get("duration", 0)
            max_time = self.criteria.get("max_seconds", float("inf"))
            passed = duration <= max_time
            message = (
                f"Duration: {duration}s (max: {max_time}s)"
                if passed
                else f"Timeout: {duration}s > {max_time}s"
            )
            return passed, message

        elif self.check_type == "required_fields":
            required = self.criteria.get("fields", [])
            missing = [f for f in required if f not in result]
            passed = len(missing) == 0
            message = (
                "All required fields present"
                if passed
                else f"Missing fields: {missing}"
            )
            return passed, message

        elif self.check_type == "success_status":
            status = result.get("status", "")
            expected = self.criteria.get("expected_status", "success")
            passed = status == expected
            message = (
                f"Status: {status}"
                if passed
                else f"Expected {expected}, got {status}"
            )
            return passed, message

        else:
            return True, f"Unknown check type: {self.check_type}"


class SubAgentSpec:
    """Specification for a sub-agent."""

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        mcp_tools: List[str],
        task: str,
        dependencies: Optional[List[str]] = None,
    ):
        """
        Initialize sub-agent specification.

        Args:
            agent_id: Unique agent identifier
            agent_type: Type (code, research, test, browser, cli)
            mcp_tools: List of MCP tool names to assign
            task: Task description
            dependencies: List of agent IDs this depends on
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.mcp_tools = mcp_tools
        self.task = task
        self.dependencies = dependencies or []
        self.status = "pending"
        self.result: Optional[Dict[str, Any]] = None


class CreatorAgent:
    """Creator agent that spawns and orchestrates sub-agents."""

    def __init__(self):
        """Initialize creator agent."""
        self.command_patterns = self._initialize_patterns()
        self.mcp_tool_registry = self._initialize_tool_registry()

    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize voice command patterns."""
        return {
            "code": re.compile(
                r"(write|create|generate|code|implement|build|develop)\s+(.*)",
                re.IGNORECASE,
            ),
            "research": re.compile(
                r"(research|find|search|look up|investigate)\s+(.*)",
                re.IGNORECASE,
            ),
            "test": re.compile(
                r"(test|verify|validate|check)\s+(.*)",
                re.IGNORECASE,
            ),
            "deploy": re.compile(
                r"(deploy|release|publish|launch)\s+(.*)",
                re.IGNORECASE,
            ),
            "analyze": re.compile(
                r"(analyze|examine|review|inspect)\s+(.*)",
                re.IGNORECASE,
            ),
            "automate": re.compile(
                r"(automate|schedule|run)\s+(.*)",
                re.IGNORECASE,
            ),
        }

    def _initialize_tool_registry(self) -> Dict[str, List[str]]:
        """Initialize MCP tool registry by agent type."""
        return {
            "code": [
                "read_file",
                "write_file",
                "list_directory",
                "git_status",
                "git_commit",
                "git_push",
            ],
            "research": [
                "web_search",
                "read_file",
                "web_scrape",
            ],
            "test": [
                "execute_command",
                "read_file",
                "write_file",
                "run_tests",
            ],
            "browser": [
                "browser_navigate",
                "browser_click",
                "browser_fill",
                "browser_screenshot",
                "browser_extract",
            ],
            "cli": [
                "execute_command",
                "execute_script",
                "list_processes",
                "get_system_info",
            ],
            "analysis": [
                "read_file",
                "analyze_data",
                "generate_insights",
            ],
        }

    def parse_voice_command(
        self, command: str, use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Parse voice command to determine intent and parameters.

        Args:
            command: Voice command text
            use_ai: Whether to use AI parsing (default: True)

        Returns:
            Parsed command info
        """
        if use_ai:
            # Try AI parsing first
            try:
                import asyncio
                from app.api_client import get_client

                client = get_client()
                loop = asyncio.get_event_loop()
                parsed = loop.run_until_complete(client.parse_command(command))

                # Map AI response to our format
                return {
                    "intent": parsed.get("intent", "unknown"),
                    "action": parsed.get("entities", {}).get("action", ""),
                    "target": parsed.get("entities", {}).get("target", command),
                    "original": command,
                    "confidence": parsed.get("confidence", 0.5),
                    "ai_reasoning": parsed.get("reasoning", ""),
                }
            except Exception as e:
                logger.warning(f"AI parsing failed: {e}, using pattern matching")

        # Fallback to pattern matching
        command_lower = command.lower()

        # Match against patterns
        for intent, pattern in self.command_patterns.items():
            match = pattern.match(command_lower)
            if match:
                action = match.group(1)
                target = match.group(2) if match.lastindex >= 2 else ""

                return {
                    "intent": intent,
                    "action": action,
                    "target": target,
                    "original": command,
                }

        # Default fallback
        return {
            "intent": "unknown",
            "action": "",
            "target": command,
            "original": command,
        }

    def determine_required_agents(
        self, parsed_command: Dict[str, Any]
    ) -> List[SubAgentSpec]:
        """
        Determine which sub-agents are needed for the task.

        Args:
            parsed_command: Parsed command info

        Returns:
            List of sub-agent specifications
        """
        intent = parsed_command["intent"]
        target = parsed_command["target"]

        agents = []

        if intent == "code":
            # Need code agent
            agents.append(
                SubAgentSpec(
                    agent_id="code-agent-1",
                    agent_type="code",
                    mcp_tools=self.mcp_tool_registry["code"],
                    task=f"Implement: {target}",
                )
            )

            # Add test agent as dependency
            agents.append(
                SubAgentSpec(
                    agent_id="test-agent-1",
                    agent_type="test",
                    mcp_tools=self.mcp_tool_registry["test"],
                    task=f"Test implementation: {target}",
                    dependencies=["code-agent-1"],
                )
            )

        elif intent == "research":
            agents.append(
                SubAgentSpec(
                    agent_id="research-agent-1",
                    agent_type="research",
                    mcp_tools=self.mcp_tool_registry["research"],
                    task=f"Research: {target}",
                )
            )

        elif intent == "test":
            agents.append(
                SubAgentSpec(
                    agent_id="test-agent-1",
                    agent_type="test",
                    mcp_tools=self.mcp_tool_registry["test"],
                    task=f"Test: {target}",
                )
            )

        elif intent == "deploy":
            # Multi-agent deployment workflow
            agents.extend(
                [
                    SubAgentSpec(
                        agent_id="test-agent-1",
                        agent_type="test",
                        mcp_tools=self.mcp_tool_registry["test"],
                        task=f"Pre-deployment tests: {target}",
                    ),
                    SubAgentSpec(
                        agent_id="cli-agent-1",
                        agent_type="cli",
                        mcp_tools=self.mcp_tool_registry["cli"],
                        task=f"Deploy: {target}",
                        dependencies=["test-agent-1"],
                    ),
                    SubAgentSpec(
                        agent_id="test-agent-2",
                        agent_type="test",
                        mcp_tools=self.mcp_tool_registry["test"],
                        task=f"Post-deployment validation: {target}",
                        dependencies=["cli-agent-1"],
                    ),
                ]
            )

        elif intent == "analyze":
            agents.extend(
                [
                    SubAgentSpec(
                        agent_id="research-agent-1",
                        agent_type="research",
                        mcp_tools=self.mcp_tool_registry["research"],
                        task=f"Gather data: {target}",
                    ),
                    SubAgentSpec(
                        agent_id="analysis-agent-1",
                        agent_type="analysis",
                        mcp_tools=self.mcp_tool_registry["analysis"],
                        task=f"Analyze data: {target}",
                        dependencies=["research-agent-1"],
                    ),
                ]
            )

        elif intent == "automate":
            # Browser + CLI automation
            agents.extend(
                [
                    SubAgentSpec(
                        agent_id="browser-agent-1",
                        agent_type="browser",
                        mcp_tools=self.mcp_tool_registry["browser"],
                        task=f"Automate browser: {target}",
                    ),
                    SubAgentSpec(
                        agent_id="cli-agent-1",
                        agent_type="cli",
                        mcp_tools=self.mcp_tool_registry["cli"],
                        task=f"Automate CLI: {target}",
                    ),
                ]
            )

        else:
            # Default: single generic agent
            agents.append(
                SubAgentSpec(
                    agent_id="generic-agent-1",
                    agent_type="code",
                    mcp_tools=["read_file", "write_file"],
                    task=target,
                )
            )

        return agents

    def create_quality_gates(
        self, parsed_command: Dict[str, Any]
    ) -> List[QualityGate]:
        """
        Create quality gates based on command intent.

        Args:
            parsed_command: Parsed command info

        Returns:
            List of quality gates
        """
        intent = parsed_command["intent"]

        gates = [
            # Always check for errors
            QualityGate(
                name="error_threshold",
                check_type="error_threshold",
                criteria={"max_errors": 0},
            ),
            # Always check for required fields
            QualityGate(
                name="required_fields",
                check_type="required_fields",
                criteria={"fields": ["status", "result"]},
            ),
        ]

        # Intent-specific gates
        if intent in ["code", "deploy"]:
            gates.append(
                QualityGate(
                    name="success_status",
                    check_type="success_status",
                    criteria={"expected_status": "success"},
                )
            )

        if intent == "deploy":
            gates.append(
                QualityGate(
                    name="deployment_time",
                    check_type="completion_time",
                    criteria={"max_seconds": 300},  # 5 minutes max
                )
            )

        return gates

    async def setup_webhook_flow(
        self,
        agents: List[SubAgentSpec],
        webhook_manager: Any,
    ) -> Dict[str, str]:
        """
        Setup webhook coordination between agents.

        Args:
            agents: List of sub-agents
            webhook_manager: Webhook manager instance

        Returns:
            Mapping of agent_id to webhook_id
        """
        webhook_mapping = {}

        for agent in agents:
            # Create webhook for agent completion
            webhook_id = f"webhook-{agent.agent_id}"

            # Register webhook (placeholder - actual implementation would use webhook_manager)
            webhook_mapping[agent.agent_id] = webhook_id

            logger.info(
                f"Webhook registered: {webhook_id} for agent {agent.agent_id}"
            )

        return webhook_mapping

    async def process_voice_command(
        self, command: str
    ) -> Dict[str, Any]:
        """
        Process voice command and create orchestration plan.

        Args:
            command: Voice command text

        Returns:
            Orchestration plan
        """
        start_time = datetime.now()

        # 1. Parse command
        parsed = self.parse_voice_command(command)
        logger.info(f"Parsed command: {parsed['intent']} - {parsed['target']}")

        # 2. Determine required agents
        agents = self.determine_required_agents(parsed)
        logger.info(f"Spawning {len(agents)} sub-agents")

        # 3. Create quality gates
        quality_gates = self.create_quality_gates(parsed)
        logger.info(f"Created {len(quality_gates)} quality gates")

        # 4. Setup webhook coordination
        webhook_mapping = await self.setup_webhook_flow(agents, None)

        # 5. Build execution plan
        plan = {
            "plan_id": f"plan-{int(datetime.now().timestamp())}",
            "command": command,
            "parsed": parsed,
            "agents": [
                {
                    "agent_id": agent.agent_id,
                    "agent_type": agent.agent_type,
                    "mcp_tools": agent.mcp_tools,
                    "task": agent.task,
                    "dependencies": agent.dependencies,
                    "webhook_id": webhook_mapping.get(agent.agent_id),
                }
                for agent in agents
            ],
            "quality_gates": [
                {
                    "name": gate.name,
                    "check_type": gate.check_type,
                    "criteria": gate.criteria,
                }
                for gate in quality_gates
            ],
            "execution_order": self._determine_execution_order(agents),
            "created_at": start_time.isoformat(),
        }

        logger.info(
            f"Orchestration plan created: {len(agents)} agents, "
            f"{len(quality_gates)} gates"
        )

        return {
            "success": True,
            "plan": plan,
        }

    def _determine_execution_order(
        self, agents: List[SubAgentSpec]
    ) -> List[List[str]]:
        """
        Determine execution order based on dependencies.

        Args:
            agents: List of sub-agents

        Returns:
            List of execution stages (each stage can run in parallel)
        """
        # Build dependency graph
        agent_map = {agent.agent_id: agent for agent in agents}
        in_degree = {agent.agent_id: len(agent.dependencies) for agent in agents}

        stages = []
        remaining = set(agent_map.keys())

        while remaining:
            # Find agents with no dependencies
            stage = [
                agent_id
                for agent_id in remaining
                if in_degree[agent_id] == 0
            ]

            if not stage:
                # Circular dependency - break it
                stage = [list(remaining)[0]]

            stages.append(stage)

            # Remove from remaining
            for agent_id in stage:
                remaining.remove(agent_id)

                # Update dependencies
                for other_id in remaining:
                    other_agent = agent_map[other_id]
                    if agent_id in other_agent.dependencies:
                        in_degree[other_id] -= 1

        return stages

    def validate_with_quality_gates(
        self,
        result: Dict[str, Any],
        quality_gates: List[QualityGate],
    ) -> Dict[str, Any]:
        """
        Validate result against quality gates.

        Args:
            result: Workflow result
            quality_gates: List of quality gates

        Returns:
            Validation result
        """
        all_passed = True
        gate_results = []

        for gate in quality_gates:
            passed, message = gate.validate(result)
            gate_results.append(
                {
                    "gate": gate.name,
                    "passed": passed,
                    "message": message,
                }
            )

            if not passed:
                all_passed = False
                logger.warning(f"Quality gate failed: {gate.name} - {message}")

        return {
            "all_passed": all_passed,
            "gates": gate_results,
            "total": len(quality_gates),
            "passed": sum(1 for g in gate_results if g["passed"]),
            "failed": sum(1 for g in gate_results if not g["passed"]),
        }


# Global creator agent instance
creator_agent = CreatorAgent()
