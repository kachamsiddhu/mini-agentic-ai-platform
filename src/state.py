from typing import TypedDict, List, Dict, Any, Annotated
import operator
from .schemas import AgentMessage, WorkflowState

def merge_messages(old: List[AgentMessage], new: List[AgentMessage]) -> List[AgentMessage]:
    return old + new

class AgentState(TypedDict):
    run_id: str
    incident_details: Dict[str, Any]
    workflow_state: WorkflowState
    messages: Annotated[List[AgentMessage], merge_messages]
    investigation_results: Dict[str, Any]
    proposed_actions: List[Dict[str, Any]]
    action_results: List[Dict[str, Any]]
    safety_decisions: List[Dict[str, Any]]
