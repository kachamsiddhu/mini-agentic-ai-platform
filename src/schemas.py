import time
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class WorkflowState(str, Enum):
    INCIDENT_RECEIVED = "incident_received"
    PLANNING = "planning"
    INVESTIGATION = "investigation"
    VERIFICATION = "verification"
    ACTION = "action"
    COMPLETE = "complete"

class AgentMessage(BaseModel):
    sender: str
    receiver: str
    task_id: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: str(time.time()))

class ToolResponse(BaseModel):
    """Structured error envelope for all tool calls (MCP-style)."""
    tool: str
    version: str = "1.0"
    status: str 
    data: Optional[Any] = None
    error: Optional[str] = None

class TraceLog(BaseModel):
    run_id: str
    workflow_state: str
    agent: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    rejected_options: List[str] = []
    latency_ms: float
    cost_usd: float = 0.0
    tokens: int = 0
