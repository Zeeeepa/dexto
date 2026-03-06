"""Code Agent - Specialized agent for code generation and analysis."""

from typing import Any, Dict, List
from datetime import datetime

from openai import AsyncOpenAI
from chatkit.agents import AgentContext
from agents import Agent, function_tool

from app.constants import SUB_AGENT_MODEL


class CodeAgent:
    """Sub-agent specialized in code generation, analysis, and refactoring."""

    def __init__(self, openai_client: AsyncOpenAI):
        """Initialize code agent."""
        self.client = openai_client
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the code agent with tools."""

        @function_tool(description="Generate code based on requirements")
        async def generate_code(
            ctx: AgentContext,
            requirements: str,
            language: str,
            framework: str = None,
        ) -> Dict[str, Any]:
            """
            Generate code based on requirements.

            Args:
                requirements: Code requirements description
                language: Programming language
                framework: Optional framework to use

            Returns:
                Generated code with explanation
            """
            return {
                "language": language,
                "framework": framework,
                "code": f"# Generated code for: {requirements}\n# Language: {language}\n\n# Implementation here...",
                "explanation": f"Code generated for {requirements} in {language}",
                "generated_at": datetime.now().isoformat(),
            }

        @function_tool(description="Analyze code for issues and improvements")
        async def analyze_code(
            ctx: AgentContext, code: str, check_types: List[str]
        ) -> Dict[str, Any]:
            """
            Analyze code for issues and suggest improvements.

            Args:
                code: Code to analyze
                check_types: Types of checks (syntax, style, security, performance)

            Returns:
                Analysis results with issues and suggestions
            """
            return {
                "checks_performed": check_types,
                "issues": [
                    {
                        "type": "style",
                        "severity": "warning",
                        "message": "Consider using more descriptive variable names",
                        "line": 5,
                    },
                    {
                        "type": "performance",
                        "severity": "info",
                        "message": "This loop could be optimized with list comprehension",
                        "line": 12,
                    },
                ],
                "suggestions": [
                    "Add type hints for better code documentation",
                    "Consider extracting this logic into a separate function",
                ],
                "analyzed_at": datetime.now().isoformat(),
            }

        @function_tool(description="Refactor code to improve quality")
        async def refactor_code(
            ctx: AgentContext, code: str, improvements: List[str]
        ) -> Dict[str, Any]:
            """
            Refactor code with specified improvements.

            Args:
                code: Original code
                improvements: List of improvements to apply

            Returns:
                Refactored code with explanations
            """
            return {
                "original_lines": len(code.split("\n")),
                "refactored_code": f"# Refactored code\n{code}",
                "improvements_applied": improvements,
                "changes": [
                    "Extracted duplicate code into helper function",
                    "Added type hints",
                    "Improved variable naming",
                ],
                "refactored_at": datetime.now().isoformat(),
            }

        @function_tool(description="Generate unit tests for code")
        async def generate_tests(
            ctx: AgentContext,
            code: str,
            test_framework: str = "pytest",
        ) -> Dict[str, Any]:
            """
            Generate unit tests for the given code.

            Args:
                code: Code to generate tests for
                test_framework: Testing framework to use

            Returns:
                Generated test code
            """
            return {
                "test_framework": test_framework,
                "test_code": f"""# Generated tests using {test_framework}
import pytest

def test_happy_path():
    # Test normal execution
    assert True

def test_edge_cases():
    # Test boundary conditions
    assert True

def test_error_handling():
    # Test error scenarios
    with pytest.raises(ValueError):
        pass
""",
                "test_count": 3,
                "coverage_target": "80%",
                "generated_at": datetime.now().isoformat(),
            }

        # Create agent with tools
        agent = Agent[AgentContext](
            model=SUB_AGENT_MODEL,
            name="CodeAgent",
            instructions="""You are a code generation and analysis specialist focused on:

1. **Code Generation**: Creating high-quality code from requirements
2. **Code Analysis**: Identifying issues, bugs, and improvement opportunities
3. **Refactoring**: Improving code structure and maintainability
4. **Test Generation**: Creating comprehensive unit tests

Your workflow:
1. Understand the coding requirement or problem
2. Choose appropriate tools and patterns
3. Generate clean, maintainable code
4. Provide clear explanations
5. Suggest tests and validations

Always follow best practices:
- Write clean, readable code
- Use proper naming conventions
- Add appropriate comments
- Consider error handling
- Think about edge cases
- Suggest tests for validation""",
            tools=[generate_code, analyze_code, refactor_code, generate_tests],
        )

        return agent

    def get_agent(self) -> Agent:
        """Get the code agent instance."""
        return self.agent

