from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uuid
import json
from src.graph import build_graph
from src.schemas import WorkflowState
from src.tracing import get_traces

app = FastAPI(title="Mini Agentic AI Platform")
graph = build_graph()

class IncidentPayload(BaseModel):
    incident_id: str
    title: str
    description: str
    severity: str
    affected_services: list[str]
    environment: str
    timestamp: str

@app.post("/incident")
def handle_incident(payload: IncidentPayload):
    run_id = str(uuid.uuid4())
    initial_state = {
        "run_id": run_id,
        "incident_details": payload.model_dump(),
        "workflow_state": WorkflowState.INCIDENT_RECEIVED,
        "messages": [],
        "investigation_results": {},
        "proposed_actions": [],
        "action_results": [],
        "safety_decisions": []
    }
    
    final_state = graph.invoke(initial_state)
    
    return {
        "run_id": run_id,
        "status": "completed",
        "action_results": final_state.get("action_results"),
        "safety_decisions": final_state.get("safety_decisions")
    }

@app.get("/trace/{run_id}")
def get_run_traces(run_id: str):
    traces = get_traces(run_id)
    if not traces:
        raise HTTPException(status_code=404, detail="Run ID not found")
    
    for trace in traces:
        trace["input_data"] = json.loads(trace["input_data"])
        trace["output_data"] = json.loads(trace["output_data"])
        trace["rejected_options"] = json.loads(trace["rejected_options"])
        
    return {"run_id": run_id, "traces": traces}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
