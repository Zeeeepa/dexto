"""Research Agent - Specialized agent for web research and data collection."""

from typing import Any, Dict, List
from datetime import datetime

from openai import AsyncOpenAI
from chatkit.agents import AgentContext
from agents import Agent, function_tool

from app.constants import SUB_AGENT_MODEL


class ResearchAgent:
    """Sub-agent specialized in web research and information gathering."""

    def __init__(self, openai_client: AsyncOpenAI):
        """Initialize research agent."""
        self.client = openai_client
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the research agent with tools."""

        @function_tool(description="Search the web for information")
        async def web_search(
            ctx: AgentContext, query: str, max_results: int = 5
        ) -> Dict[str, Any]:
            """
            Search the web for information.

            Args:
                query: Search query
                max_results: Maximum number of results to return

            Returns:
                Search results with titles, URLs, and snippets
            """
            # This would integrate with MCP browser/search tools
            return {
                "query": query,
                "results": [
                    {
                        "title": f"Result {i+1} for: {query}",
                        "url": f"https://example.com/result{i+1}",
                        "snippet": f"Snippet about {query}...",
                    }
                    for i in range(max_results)
                ],
                "searched_at": datetime.now().isoformat(),
            }

        @function_tool(description="Extract data from a webpage")
        async def extract_webpage_data(
            ctx: AgentContext, url: str, selectors: List[str]
        ) -> Dict[str, Any]:
            """
            Extract specific data from a webpage.

            Args:
                url: URL to extract from
                selectors: CSS selectors for data extraction

            Returns:
                Extracted data
            """
            # This would integrate with MCP browser tools
            return {
                "url": url,
                "extracted_data": {
                    selector: f"Data from {selector} at {url}"
                    for selector in selectors
                },
                "extracted_at": datetime.now().isoformat(),
            }

        @function_tool(description="Analyze and synthesize research findings")
        async def synthesize_research(
            ctx: AgentContext, sources: List[Dict[str, str]]
        ) -> Dict[str, Any]:
            """
            Analyze and synthesize information from multiple sources.

            Args:
                sources: List of sources with titles and content

            Returns:
                Synthesized insights and summary
            """
            return {
                "source_count": len(sources),
                "key_themes": [
                    "Theme 1: Common pattern across sources",
                    "Theme 2: Emerging trend identified",
                    "Theme 3: Key insight synthesized",
                ],
                "summary": f"Analyzed {len(sources)} sources and identified key patterns...",
                "synthesized_at": datetime.now().isoformat(),
            }

        # Create agent with tools
        agent = Agent[AgentContext](
            model=SUB_AGENT_MODEL,
            name="ResearchAgent",
            instructions="""You are a research specialist agent focused on:

1. **Web Research**: Finding relevant and authoritative sources
2. **Data Extraction**: Gathering specific information from sources
3. **Information Synthesis**: Combining insights from multiple sources
4. **Fact Verification**: Ensuring accuracy and reliability

Your workflow:
1. Understand the research question
2. Identify relevant sources using web_search
3. Extract detailed information using extract_webpage_data
4. Synthesize findings using synthesize_research
5. Present clear, organized results

Always cite sources and provide context for your findings.""",
            tools=[web_search, extract_webpage_data, synthesize_research],
        )

        return agent

    def get_agent(self) -> Agent:
        """Get the research agent instance."""
        return self.agent

