"""Test Agent - Specialized agent for test automation and validation."""

from typing import Any, Dict, List
from datetime import datetime

from openai import AsyncOpenAI
from chatkit.agents import AgentContext
from agents import Agent, function_tool

from app.constants import SUB_AGENT_MODEL


class TestAgent:
    """Sub-agent specialized in test automation and quality validation."""

    def __init__(self, openai_client: AsyncOpenAI):
        """Initialize test agent."""
        self.client = openai_client
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the test agent with tools."""

        @function_tool(description="Run unit tests")
        async def run_unit_tests(
            ctx: AgentContext,
            test_files: List[str],
            coverage: bool = True,
        ) -> Dict[str, Any]:
            """
            Run unit tests on specified files.

            Args:
                test_files: List of test files to run
                coverage: Whether to collect coverage data

            Returns:
                Test results with pass/fail status
            """
            return {
                "test_framework": "pytest",
                "files_tested": test_files,
                "total_tests": 45,
                "passed": 43,
                "failed": 2,
                "skipped": 0,
                "duration": "2.34s",
                "coverage": {
                    "enabled": coverage,
                    "percentage": 87.5,
                    "uncovered_lines": [15, 23, 45],
                },
                "failed_tests": [
                    {
                        "name": "test_authentication_edge_case",
                        "file": "test_auth.py",
                        "error": "AssertionError: Expected True but got False",
                    }
                ],
                "run_at": datetime.now().isoformat(),
            }

        @function_tool(description="Run integration tests")
        async def run_integration_tests(
            ctx: AgentContext, test_suite: str
        ) -> Dict[str, Any]:
            """
            Run integration tests for a test suite.

            Args:
                test_suite: Name of test suite to run

            Returns:
                Integration test results
            """
            return {
                "test_suite": test_suite,
                "total_tests": 12,
                "passed": 11,
                "failed": 1,
                "duration": "45.2s",
                "failed_tests": [
                    {
                        "name": "test_api_rate_limiting",
                        "error": "Timeout: API did not respond within 30 seconds",
                    }
                ],
                "run_at": datetime.now().isoformat(),
            }

        @function_tool(description="Run end-to-end tests")
        async def run_e2e_tests(
            ctx: AgentContext,
            scenarios: List[str],
            browser: str = "chromium",
        ) -> Dict[str, Any]:
            """
            Run end-to-end tests with browser automation.

            Args:
                scenarios: List of test scenarios
                browser: Browser to use (chromium, firefox, webkit)

            Returns:
                E2E test results
            """
            return {
                "browser": browser,
                "scenarios": scenarios,
                "total_tests": len(scenarios),
                "passed": len(scenarios) - 1,
                "failed": 1,
                "duration": "2m 15s",
                "failed_scenarios": [
                    {
                        "name": scenarios[0] if scenarios else "unknown",
                        "step": "Click login button",
                        "error": "Element not found: #login-btn",
                    }
                ],
                "run_at": datetime.now().isoformat(),
            }

        @function_tool(description="Analyze test results and suggest fixes")
        async def analyze_test_failures(
            ctx: AgentContext, test_results: Dict[str, Any]
        ) -> Dict[str, Any]:
            """
            Analyze test failures and suggest fixes.

            Args:
                test_results: Test results from previous runs

            Returns:
                Analysis with suggested fixes
            """
            return {
                "failures_analyzed": test_results.get("failed", 0),
                "root_causes": [
                    {
                        "category": "timing_issue",
                        "description": "Test timeout due to slow API response",
                        "affected_tests": 1,
                    },
                    {
                        "category": "assertion_error",
                        "description": "Unexpected return value in edge case",
                        "affected_tests": 1,
                    },
                ],
                "suggestions": [
                    "Increase timeout for API tests to 60 seconds",
                    "Add better error handling for edge cases",
                    "Update test assertions to match new behavior",
                ],
                "priority": "high",
                "analyzed_at": datetime.now().isoformat(),
            }

        # Create agent with tools
        agent = Agent[AgentContext](
            model=SUB_AGENT_MODEL,
            name="TestAgent",
            instructions="""You are a test automation specialist focused on:

1. **Unit Testing**: Running and analyzing unit tests
2. **Integration Testing**: Testing component interactions
3. **E2E Testing**: Full user flow validation with browsers
4. **Test Analysis**: Identifying root causes of failures

Your workflow:
1. Understand what needs to be tested
2. Select appropriate test types and tools
3. Execute tests systematically
4. Analyze results and failures
5. Suggest fixes and improvements

Testing best practices:
- Test happy paths and edge cases
- Isolate failures to specific components
- Provide clear error messages
- Suggest actionable fixes
- Recommend test coverage improvements
- Consider performance impacts""",
            tools=[
                run_unit_tests,
                run_integration_tests,
                run_e2e_tests,
                analyze_test_failures,
            ],
        )

        return agent

    def get_agent(self) -> Agent:
        """Get the test agent instance."""
        return self.agent

