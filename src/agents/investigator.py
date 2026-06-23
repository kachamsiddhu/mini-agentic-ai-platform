import time
import uuid
from src.state import AgentState
from src.schemas import AgentMessage, WorkflowState
from src.tracing import log_trace, TraceLog
from src.knowledge.rag import KnowledgeBase
from src.tools.actions import get_logs, get_metrics
from src.tools.schema import GetLogsInput, GetMetricsInput

kb = KnowledgeBase()

def investigator_node(state: AgentState):
    start_time = time.time()
    msg = [m for m in state.get("messages", []) if m.receiver == "investigator"][-1]
    service = msg.payload.get("service")
    logs_resp = get_logs(GetLogsInput(service=service, timeframe="recent"))
    metrics_resp = get_metrics(GetMetricsInput(service=service))
    logs_data = logs_resp.data if logs_resp.status == "ok" else f"ERROR: {logs_resp.error}"
    metrics_data = metrics_resp.data if metrics_resp.status == "ok" else f"ERROR: {metrics_resp.error}"
    rag_results = kb.search(f"high latency or timeout or OOM in {service}", top_k=2,
                            filters={"service": service})
    investigation_results = {
        "service": service,
        "logs": logs_data,
        "metrics": metrics_data,
        "runbook_hints": [res["content"] for res in rag_results]
    }
    out_msg = AgentMessage(
        sender="investigator",
        receiver="infra",
        task_id=str(uuid.uuid4()),
        message_type="propose_action",
        payload={"investigation_results": investigation_results}
    )
    latency = (time.time() - start_time) * 1000
    log_trace(TraceLog(
        run_id=state["run_id"],
        workflow_state=WorkflowState.INVESTIGATION.value,
        agent="investigator",
        input_data={"service": service},
        output_data={"investigation_results": investigation_results},
        latency_ms=latency,
        cost_usd=0.0,
        tokens=0
    ))
    return {
        "workflow_state": WorkflowState.ACTION,
        "investigation_results": investigation_results,
        "messages": [out_msg]
    }
