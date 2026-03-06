"""
API Client for Z.ai GLM-4.5V Model.

Provides integration with Z.ai's Anthropic-compatible API for:
- Text generation
- Command parsing
- Research synthesis
- Code analysis
"""

import os
import logging
from typing import Dict, List, Any, Optional
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ZAIClient:
    """
    Client for Z.ai GLM-4.5V API.
    
    Uses Anthropic-compatible API format.
    """

    def __init__(self):
        """Initialize Z.ai API client."""
        self.model = os.getenv("ANTHROPIC_MODEL", "glm-4.5V")
        self.base_url = os.getenv(
            "ANTHROPIC_BASE_URL",
            "https://api.z.ai/api/anthropic"
        )
        self.auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"

        if not self.auth_token and not self.test_mode:
            logger.warning(
                "ANTHROPIC_AUTH_TOKEN not set. API calls will fail."
            )

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "x-api-key": self.auth_token or "",
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            timeout=30.0,
        )

        logger.info(f"Z.ai client initialized: model={self.model}")

    async def create_message(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a message using Z.ai API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            system: Optional system prompt

        Returns:
            API response dict
        """
        if self.test_mode:
            return self._mock_response(messages)

        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            if system:
                payload["system"] = system

            response = await self.client.post(
                "/v1/messages",
                json=payload,
            )

            response.raise_for_status()
            result = response.json()

            logger.info(
                f"API call successful: {len(messages)} messages, "
                f"{result.get('usage', {}).get('output_tokens', 0)} tokens"
            )

            return result

        except httpx.HTTPError as e:
            logger.error(f"API call failed: {e}")
            # Fallback to mock in case of error
            return self._mock_response(messages)

    def _mock_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate mock response for testing."""
        last_message = messages[-1]["content"] if messages else ""

        return {
            "id": "msg_mock_123",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": f"Mock response to: {last_message[:100]}...",
                }
            ],
            "model": self.model,
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 50,
                "output_tokens": 100,
            },
        }

    async def parse_command(
        self,
        command: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Parse voice command using AI.

        Args:
            command: Voice command to parse
            context: Optional context information

        Returns:
            Parsed command with intent, entities, etc.
        """
        system_prompt = """You are a voice command parser. 
Parse the user's command and return a JSON response with:
- intent: The main action (deploy, test, research, create, update, analyze)
- entities: Relevant entities (environment, service, topic, etc.)
- confidence: Confidence score 0-1
- reasoning: Brief explanation

Return ONLY valid JSON, no markdown or explanation."""

        messages = [
            {
                "role": "user",
                "content": f"Parse this command: {command}\n"
                f"Context: {context or {}}",
            }
        ]

        response = await self.create_message(
            messages,
            max_tokens=1024,
            temperature=0.3,
            system=system_prompt,
        )

        # Extract text from response
        content = response["content"][0]["text"]

        # Parse JSON (handle various formats)
        try:
            import json

            # Remove special tokens from GLM-4.5V
            if "<|begin_of_box|>" in content and "<|end_of_box|>" in content:
                content = content.split("<|begin_of_box|>")[1].split("<|end_of_box|>")[0]

            # Try to extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content.strip())
        except Exception as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            # Return basic parsed result
            return {
                "intent": "unknown",
                "entities": {},
                "confidence": 0.5,
                "reasoning": "Failed to parse AI response",
                "raw": content,
            }

    async def research_synthesis(
        self,
        query: str,
        sources: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Synthesize research findings using AI.

        Args:
            query: Research query
            sources: List of source documents

        Returns:
            Synthesized research with summary, key findings, etc.
        """
        system_prompt = """You are a research analyst. 
Synthesize the provided sources into a comprehensive research summary.
Focus on key findings, patterns, and actionable insights.
Return JSON with:
- summary: Brief overview
- key_findings: List of important points
- recommendations: Actionable suggestions
- confidence: Overall confidence 0-1"""

        sources_text = "\n\n".join(
            [
                f"Source {i + 1} ({s.get('title', 'Unknown')}):\n{s.get('snippet', '')}"
                for i, s in enumerate(sources)
            ]
        )

        messages = [
            {
                "role": "user",
                "content": f"Research Query: {query}\n\n"
                f"Sources:\n{sources_text}\n\n"
                "Synthesize these sources into actionable insights.",
            }
        ]

        response = await self.create_message(
            messages,
            max_tokens=2048,
            temperature=0.5,
            system=system_prompt,
        )

        content = response["content"][0]["text"]

        try:
            import json

            # Remove special tokens from GLM-4.5V
            if "<|begin_of_box|>" in content and "<|end_of_box|>" in content:
                content = content.split("<|begin_of_box|>")[1].split("<|end_of_box|>")[0]

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content.strip())
        except Exception:
            # Return text response if JSON parsing fails
            return {
                "summary": content,
                "key_findings": [],
                "recommendations": [],
                "confidence": 0.7,
            }

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global client instance
_client: Optional[ZAIClient] = None


def get_client() -> ZAIClient:
    """Get or create global Z.ai client instance."""
    global _client
    if _client is None:
        _client = ZAIClient()
    return _client


async def cleanup_client():
    """Cleanup global client."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
