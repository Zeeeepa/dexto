"""Advanced agent collaboration system."""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class CollaborationMode(str, Enum):
    """Agent collaboration modes."""
    
    SEQUENTIAL = "sequential"  # Agents work one after another
    PARALLEL = "parallel"  # Agents work simultaneously
    CONSENSUS = "consensus"  # Agents vote on decisions
    LEADER_FOLLOWER = "leader_follower"  # One agent leads, others assist
    DEBATE = "debate"  # Agents discuss to reach conclusion


class AgentMessage:
    """Message between agents."""

    def __init__(
        self,
        from_agent: str,
        to_agent: Optional[str],
        content: str,
        message_type: str = "info",
        metadata: Optional[Dict] = None,
    ):
        """
        Initialize agent message.

        Args:
            from_agent: Sender agent name
            to_agent: Recipient agent name (None for broadcast)
            content: Message content
            message_type: Message type
            metadata: Optional metadata
        """
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.content = content
        self.message_type = message_type
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()


class CollaborationSession:
    """Agent collaboration session."""

    def __init__(
        self,
        session_id: str,
        mode: CollaborationMode,
        participants: List[str],
    ):
        """
        Initialize collaboration session.

        Args:
            session_id: Session identifier
            mode: Collaboration mode
            participants: List of agent names
        """
        self.session_id = session_id
        self.mode = mode
        self.participants = participants
        self.messages: List[AgentMessage] = []
        self.decisions: List[Dict[str, Any]] = []
        self.status = "active"
        self.created_at = datetime.now().isoformat()

    def add_message(self, message: AgentMessage):
        """Add message to session."""
        self.messages.append(message)
        logger.info(
            f"Session {self.session_id}: "
            f"{message.from_agent} -> {message.to_agent or 'all'}: "
            f"{message.content[:50]}..."
        )

    def add_decision(self, agent: str, decision: Any, reasoning: str):
        """Add agent decision."""
        self.decisions.append({
            "agent": agent,
            "decision": decision,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat(),
        })

    def get_consensus(self) -> Optional[Any]:
        """Get consensus decision from all agents."""
        if not self.decisions:
            return None

        # Simple majority voting
        from collections import Counter
        
        decisions = [d["decision"] for d in self.decisions]
        counter = Counter(str(d) for d in decisions)
        
        if counter:
            most_common = counter.most_common(1)[0]
            return most_common[0]
        
        return None


class AgentCoordinator:
    """Coordinate agent collaboration."""

    def __init__(self):
        """Initialize agent coordinator."""
        self.sessions: Dict[str, CollaborationSession] = {}
        self.session_counter = 0

    async def create_session(
        self,
        mode: CollaborationMode,
        participants: List[str],
    ) -> CollaborationSession:
        """
        Create collaboration session.

        Args:
            mode: Collaboration mode
            participants: List of agent names

        Returns:
            Created session
        """
        self.session_counter += 1
        session_id = f"collab_{self.session_counter}"
        
        session = CollaborationSession(session_id, mode, participants)
        self.sessions[session_id] = session
        
        logger.info(
            f"Collaboration session created: {session_id} "
            f"(mode: {mode}, participants: {len(participants)})"
        )
        
        return session

    async def sequential_execution(
        self,
        session: CollaborationSession,
        task: str,
        agents: List[Any],  # Agent objects
    ) -> Dict[str, Any]:
        """
        Execute agents sequentially.

        Args:
            session: Collaboration session
            task: Task description
            agents: List of agent objects

        Returns:
            Execution results
        """
        results = []
        context = {"task": task}

        for agent in agents:
            logger.info(f"Sequential: {agent.name} starting")
            
            # Add previous results to context
            if results:
                context["previous_results"] = results

            try:
                # Execute agent (this would be actual agent execution)
                result = await self._execute_agent(agent, context)
                results.append({
                    "agent": agent.name,
                    "result": result,
                    "status": "success",
                })
                
                # Add message
                message = AgentMessage(
                    from_agent=agent.name,
                    to_agent=None,
                    content=f"Completed task: {result}",
                    message_type="result",
                )
                session.add_message(message)

            except Exception as e:
                logger.error(f"Sequential: {agent.name} failed: {e}")
                results.append({
                    "agent": agent.name,
                    "error": str(e),
                    "status": "failed",
                })

        return {
            "mode": "sequential",
            "results": results,
            "session_id": session.session_id,
        }

    async def parallel_execution(
        self,
        session: CollaborationSession,
        task: str,
        agents: List[Any],
    ) -> Dict[str, Any]:
        """
        Execute agents in parallel.

        Args:
            session: Collaboration session
            task: Task description
            agents: List of agent objects

        Returns:
            Execution results
        """
        logger.info(f"Parallel execution: {len(agents)} agents")

        # Execute all agents concurrently
        tasks = [
            self._execute_agent(agent, {"task": task})
            for agent in agents
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        formatted_results = []
        for agent, result in zip(agents, results):
            if isinstance(result, Exception):
                formatted_results.append({
                    "agent": agent.name,
                    "error": str(result),
                    "status": "failed",
                })
            else:
                formatted_results.append({
                    "agent": agent.name,
                    "result": result,
                    "status": "success",
                })

                # Add message
                message = AgentMessage(
                    from_agent=agent.name,
                    to_agent=None,
                    content=f"Completed: {result}",
                    message_type="result",
                )
                session.add_message(message)

        return {
            "mode": "parallel",
            "results": formatted_results,
            "session_id": session.session_id,
        }

    async def consensus_execution(
        self,
        session: CollaborationSession,
        question: str,
        agents: List[Any],
    ) -> Dict[str, Any]:
        """
        Get consensus from agents.

        Args:
            session: Collaboration session
            question: Question to answer
            agents: List of agent objects

        Returns:
            Consensus result
        """
        logger.info(f"Consensus execution: {len(agents)} agents")

        # Get decision from each agent
        for agent in agents:
            try:
                decision = await self._get_agent_decision(agent, question)
                session.add_decision(
                    agent.name,
                    decision["answer"],
                    decision["reasoning"],
                )
            except Exception as e:
                logger.error(f"Consensus: {agent.name} failed: {e}")

        # Get consensus
        consensus = session.get_consensus()

        return {
            "mode": "consensus",
            "question": question,
            "decisions": session.decisions,
            "consensus": consensus,
            "session_id": session.session_id,
        }

    async def leader_follower_execution(
        self,
        session: CollaborationSession,
        task: str,
        leader_agent: Any,
        follower_agents: List[Any],
    ) -> Dict[str, Any]:
        """
        Leader-follower execution pattern.

        Args:
            session: Collaboration session
            task: Task description
            leader_agent: Leader agent
            follower_agents: Follower agents

        Returns:
            Execution results
        """
        logger.info(
            f"Leader-follower: {leader_agent.name} "
            f"with {len(follower_agents)} followers"
        )

        # Leader creates plan
        plan = await self._execute_agent(
            leader_agent,
            {"task": task, "role": "leader"},
        )

        # Add leader message
        session.add_message(AgentMessage(
            from_agent=leader_agent.name,
            to_agent=None,
            content=f"Plan: {plan}",
            message_type="plan",
        ))

        # Followers execute parts
        follower_results = []
        for i, follower in enumerate(follower_agents):
            try:
                result = await self._execute_agent(
                    follower,
                    {
                        "task": task,
                        "plan": plan,
                        "role": "follower",
                        "part": i + 1,
                    },
                )
                follower_results.append({
                    "agent": follower.name,
                    "result": result,
                    "status": "success",
                })
            except Exception as e:
                follower_results.append({
                    "agent": follower.name,
                    "error": str(e),
                    "status": "failed",
                })

        return {
            "mode": "leader_follower",
            "leader": leader_agent.name,
            "plan": plan,
            "follower_results": follower_results,
            "session_id": session.session_id,
        }

    async def _execute_agent(
        self, agent: Any, context: Dict[str, Any]
    ) -> Any:
        """
        Execute agent (placeholder).

        Args:
            agent: Agent object
            context: Execution context

        Returns:
            Agent result
        """
        # This would be actual agent execution
        # For now, return a placeholder
        await asyncio.sleep(0.1)  # Simulate work
        return f"Result from {agent.name}"

    async def _get_agent_decision(
        self, agent: Any, question: str
    ) -> Dict[str, Any]:
        """
        Get agent decision (placeholder).

        Args:
            agent: Agent object
            question: Question to answer

        Returns:
            Decision with reasoning
        """
        # This would be actual agent decision
        await asyncio.sleep(0.1)  # Simulate thinking
        return {
            "answer": "yes",
            "reasoning": f"Decision by {agent.name}",
        }

    def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def list_sessions(self) -> List[CollaborationSession]:
        """List all sessions."""
        return list(self.sessions.values())


# Global coordinator
agent_coordinator = AgentCoordinator()

