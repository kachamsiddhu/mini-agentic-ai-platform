import time
import uuid
from src.state import AgentState
from src.schemas import AgentMessage, WorkflowState
from src.tracing import log_trace, TraceLog

def infra_node(state: AgentState):
    start_time = time.time()
    investigation = state.get("investigation_results", {})
    service = investigation.get("service")
    logs = investigation.get("logs", "")
    proposed_actions = []
    if "db_connection_pool approaching capacity" in logs or "timeout" in logs.lower():
        proposed_actions.append({"action": "restart_service", "service": service})
        proposed_actions.append({"action": "scale_service", "service": service, "replicas": 5})
    elif "oom" in logs.lower() or "memory" in logs.lower():
        proposed_actions.append({"action": "restart_service", "service": service})
        proposed_actions.append({"action": "clear_cache", "service": service})
    out_msg = AgentMessage(
        sender="infra",
        receiver="verifier",
        task_id=str(uuid.uuid4()),
        message_type="verify_action",
        payload={"proposed_actions": proposed_actions}
    )
    latency = (time.time() - start_time) * 1000
    log_trace(TraceLog(
        run_id=state["run_id"],
        workflow_state=WorkflowState.ACTION.value,
        agent="infra",
        input_data={"investigation_results": investigation},
        output_data={"proposed_actions": proposed_actions},
        latency_ms=latency,
        cost_usd=0.0,
        tokens=0
    ))
    return {
        "proposed_actions": proposed_actions,
        "messages": [out_msg]
    }
