"""Analysis Agent - Specialized agent for data analysis and insights."""

from typing import Any, Dict, List
from datetime import datetime

from openai import AsyncOpenAI
from chatkit.agents import AgentContext
from agents import Agent, function_tool

from app.constants import SUB_AGENT_MODEL


class AnalysisAgent:
    """Sub-agent specialized in data analysis and insight generation."""

    def __init__(self, openai_client: AsyncOpenAI):
        """Initialize analysis agent."""
        self.client = openai_client
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the analysis agent with tools."""

        @function_tool(description="Analyze dataset statistics")
        async def analyze_statistics(
            ctx: AgentContext, data_source: str, metrics: List[str]
        ) -> Dict[str, Any]:
            """
            Analyze statistical properties of a dataset.

            Args:
                data_source: Source of data to analyze
                metrics: Metrics to calculate (mean, median, std, etc.)

            Returns:
                Statistical analysis results
            """
            return {
                "data_source": data_source,
                "row_count": 10000,
                "column_count": 15,
                "metrics": {
                    "mean": 45.67,
                    "median": 42.0,
                    "std_dev": 12.34,
                    "min": 10.0,
                    "max": 95.0,
                },
                "missing_values": {
                    "total": 150,
                    "percentage": 1.5,
                    "by_column": {"age": 50, "income": 100},
                },
                "analyzed_at": datetime.now().isoformat(),
            }

        @function_tool(description="Detect patterns and trends")
        async def detect_patterns(
            ctx: AgentContext, data_source: str, pattern_types: List[str]
        ) -> Dict[str, Any]:
            """
            Detect patterns and trends in data.

            Args:
                data_source: Source of data
                pattern_types: Types of patterns to detect (trend, seasonal, anomaly)

            Returns:
                Detected patterns and trends
            """
            return {
                "data_source": data_source,
                "patterns_found": 3,
                "trends": [
                    {
                        "type": "increasing",
                        "metric": "user_engagement",
                        "strength": 0.85,
                        "period": "last_3_months",
                    }
                ],
                "seasonality": [
                    {
                        "pattern": "weekly",
                        "peak_days": ["Monday", "Tuesday"],
                        "confidence": 0.92,
                    }
                ],
                "anomalies": [
                    {
                        "date": "2024-01-15",
                        "value": 150.0,
                        "expected": 45.0,
                        "deviation": 3.5,
                    }
                ],
                "detected_at": datetime.now().isoformat(),
            }

        @function_tool(description="Generate insights from analysis")
        async def generate_insights(
            ctx: AgentContext,
            analysis_results: Dict[str, Any],
            context: str,
        ) -> Dict[str, Any]:
            """
            Generate actionable insights from analysis.

            Args:
                analysis_results: Previous analysis results
                context: Business context for insights

            Returns:
                Generated insights and recommendations
            """
            return {
                "insights": [
                    {
                        "title": "User Engagement Increasing",
                        "description": "User engagement has grown 25% over last quarter",
                        "impact": "high",
                        "confidence": 0.9,
                    },
                    {
                        "title": "Weekly Peak Activity",
                        "description": "Activity peaks on Mondays and Tuesdays",
                        "impact": "medium",
                        "confidence": 0.85,
                    },
                ],
                "recommendations": [
                    "Schedule important updates on high-activity days",
                    "Investigate anomaly on 2024-01-15 for potential issues",
                    "Continue current growth strategies",
                ],
                "next_steps": [
                    "Deep dive into engagement drivers",
                    "Set up monitoring for anomaly detection",
                ],
                "generated_at": datetime.now().isoformat(),
            }

        @function_tool(description="Create visualizations")
        async def create_visualizations(
            ctx: AgentContext,
            data_source: str,
            chart_types: List[str],
        ) -> Dict[str, Any]:
            """
            Create data visualizations.

            Args:
                data_source: Source of data
                chart_types: Types of charts to create (line, bar, scatter, etc.)

            Returns:
                Visualization specifications
            """
            return {
                "data_source": data_source,
                "visualizations": [
                    {
                        "type": "line",
                        "title": "User Engagement Over Time",
                        "x_axis": "date",
                        "y_axis": "engagement_score",
                        "config": {"smooth": True, "show_points": True},
                    },
                    {
                        "type": "bar",
                        "title": "Activity by Day of Week",
                        "x_axis": "day",
                        "y_axis": "activity_count",
                        "config": {"colors": ["#667eea", "#764ba2"]},
                    },
                ],
                "created_at": datetime.now().isoformat(),
            }

        # Create agent with tools
        agent = Agent[AgentContext](
            model=SUB_AGENT_MODEL,
            name="AnalysisAgent",
            instructions="""You are a data analysis specialist focused on:

1. **Statistical Analysis**: Computing metrics and distributions
2. **Pattern Detection**: Finding trends, seasonality, and anomalies
3. **Insight Generation**: Creating actionable recommendations
4. **Data Visualization**: Designing effective charts and graphs

Your workflow:
1. Understand the analysis objective
2. Examine data characteristics
3. Apply appropriate statistical methods
4. Detect meaningful patterns
5. Generate actionable insights
6. Suggest visualizations

Analysis best practices:
- Validate data quality first
- Use appropriate statistical methods
- Consider business context
- Identify both obvious and subtle patterns
- Provide confidence levels
- Make recommendations actionable
- Suggest follow-up analyses""",
            tools=[
                analyze_statistics,
                detect_patterns,
                generate_insights,
                create_visualizations,
            ],
        )

        return agent

    def get_agent(self) -> Agent:
        """Get the analysis agent instance."""
        return self.agent

