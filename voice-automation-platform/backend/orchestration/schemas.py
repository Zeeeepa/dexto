"""Core schemas for orchestration system."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentState(str, Enum):
    """Agent lifecycle states."""
    CREATING = "creating"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowState(str, Enum):
    """Workflow execution states."""
    CREATING = "creating"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WebhookTrigger(str, Enum):
    """Webhook trigger events."""
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    QUALITY_GATE_PASSED = "quality_gate.passed"
    QUALITY_GATE_FAILED = "quality_gate.failed"


class QualityGateType(str, Enum):
    """Quality gate validation types."""
    JSON_SCHEMA = "json_schema"
    REGEX_MATCH = "regex_match"
    LLM_VALIDATION = "llm_validation"
    CUSTOM_FUNCTION = "custom_function"


class WebhookConfig(BaseModel):
    """Webhook configuration for inter-agent communication."""
    
    url: str = Field(..., description="Webhook endpoint URL")
    trigger: WebhookTrigger = Field(..., description="Event that triggers this webhook")
    target_agent: Optional[str] = Field(None, description="Target agent role")
    headers: Dict[str, str] = Field(default_factory=dict)
    retry_count: int = Field(default=3, ge=0, le=10)
    timeout_seconds: int = Field(default=30, ge=1, le=300)


class QualityGate(BaseModel):
    """Quality gate for output validation."""
    
    gate_id: str = Field(..., description="Unique gate identifier")
    gate_type: QualityGateType = Field(..., description="Type of validation")
    validation_config: Dict[str, Any] = Field(..., description="Type-specific config")
    retry_on_fail: bool = Field(default=True)
    max_retries: int = Field(default=2, ge=0, le=5)
    escalate_on_fail: bool = Field(default=False)
    escalation_target: Optional[str] = Field(None, description="Agent to escalate to")


class AgentConfig(BaseModel):
    """Configuration for a single agent in the workflow."""
    
    role: str = Field(..., description="Agent role/identifier")
    system_prompt: str = Field(..., description="Agent's system instructions")
    model: str = Field(default="gpt-4o-mini", description="LLM model to use")
    tools: List[str] = Field(default_factory=list, description="MCP tools available")
    depends_on: List[str] = Field(default_factory=list, description="Parent agent roles")
    webhooks: List[WebhookConfig] = Field(default_factory=list)
    quality_gates: List[QualityGate] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OrchestrationConfig(BaseModel):
    """Complete orchestration configuration from voice command."""
    
    workflow_id: str = Field(..., description="Unique workflow identifier")
    parent_role: str = Field(..., description="Orchestrator agent role")
    parent_prompt: str = Field(..., description="Orchestrator system prompt")
    children: List[AgentConfig] = Field(..., description="Child agent configs")
    webhooks: List[WebhookConfig] = Field(default_factory=list)
    quality_gates: List[QualityGate] = Field(default_factory=list)
    max_parallel_agents: int = Field(default=5, ge=1, le=20)
    timeout_seconds: int = Field(default=600, ge=60, le=3600)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentInstance(BaseModel):
    """Runtime instance of an agent."""
    
    id: str = Field(..., description="Unique agent instance ID")
    role: str = Field(..., description="Agent role")
    config: AgentConfig = Field(..., description="Agent configuration")
    state: AgentState = Field(default=AgentState.CREATING)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = Field(default=0, ge=0)
    
    class Config:
        arbitrary_types_allowed = True


class WorkflowContext(BaseModel):
    """Runtime context for workflow execution."""
    
    workflow_id: str = Field(..., description="Unique workflow ID")
    config: OrchestrationConfig = Field(..., description="Workflow config")
    state: WorkflowState = Field(default=WorkflowState.CREATING)
    parent_agent: Optional[AgentInstance] = None
    child_agents: Dict[str, AgentInstance] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class VoiceCommandIntent(BaseModel):
    """Parsed voice command with orchestration plan."""
    
    original_command: str = Field(..., description="Original voice input")
    intent: str = Field(..., description="Classified intent")
    orchestration: OrchestrationConfig = Field(..., description="Generated workflow")
    confidence: float = Field(..., ge=0.0, le=1.0)
    alternative_intents: List[str] = Field(default_factory=list)


class QualityGateResult(BaseModel):
    """Result of quality gate validation."""
    
    gate_id: str
    passed: bool
    agent_id: str
    output: Any
    error: Optional[str] = None
    retry_attempted: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


class WebhookEvent(BaseModel):
    """Webhook event payload."""
    
    event_id: str
    trigger: WebhookTrigger
    workflow_id: str
    agent_id: Optional[str] = None
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)

