import pytest
import uuid
from src.tracing import get_traces
from src.schemas import WorkflowState
from src.graph import build_graph

def test_full_trajectory_and_cost_logging():
    run_id = str(uuid.uuid4())
    initial_state = {
        "run_id": run_id,
        "incident_details": {
            "title": "High Latency in Payment Service",
            "description": "Alert fired for elevated p99 latency in the payment-service.",
            "affected_services": ["payment-service"]
        },
        "workflow_state": WorkflowState.INCIDENT_RECEIVED,
        "messages": [],
        "investigation_results": {},
        "proposed_actions": [],
        "action_results": [],
        "safety_decisions": []
    }
    graph = build_graph()
    final_state = graph.invoke(initial_state)
    assert final_state["workflow_state"] == WorkflowState.COMPLETE
    traces = get_traces(run_id)
    assert len(traces) >= 4
    for t in traces:
        assert "latency_ms" in t
        assert "cost_usd" in t
        assert t["latency_ms"] > 0
