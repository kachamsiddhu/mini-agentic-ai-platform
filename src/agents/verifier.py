import time
import os
import yaml
import uuid
from src.state import AgentState
from src.schemas import AgentMessage, WorkflowState
from src.tracing import log_trace, TraceLog
from src.tools.actions import simulate_restart, simulate_scale
from src.tools.schema import SimulateRestartInput, SimulateScaleInput
from src.knowledge.graph import DependencyGraph

BLAST_RADIUS_LIMIT = int(os.getenv("BLAST_RADIUS_LIMIT", "3"))

def load_policies():
    policy_path = "policies/safety_rules.yaml"
    if os.path.exists(policy_path):
        with open(policy_path, "r") as f:
            return yaml.safe_load(f)
    return {"allowed_actions": [], "blocked_actions": [], "autonomy_tiers": {}}

def verifier_node(state: AgentState):
    start_time = time.time()
    policies = load_policies()
    dep_graph = DependencyGraph()
    proposed_actions = state.get("proposed_actions", [])
    tier_env = os.getenv("AUTONOMY_TIER", "MEDIUM")
    tier_policy = policies.get("autonomy_tiers", {}).get(tier_env, "simulate_actions")
    safety_decisions = []
    action_results = []
    rejected_options = []
    for action_req in proposed_actions:
        action_name = action_req.get("action")
        service = action_req.get("service")
        if action_name in policies.get("blocked_actions", []):
            decision = f"REJECTED: {action_name} is explicitly blocked."
            safety_decisions.append({"action": action_req, "decision": decision})
            rejected_options.append(action_name)
            continue
        if action_name not in policies.get("allowed_actions", []):
            decision = f"REJECTED: {action_name} is not in the allowed list."
            safety_decisions.append({"action": action_req, "decision": decision})
            rejected_options.append(action_name)
            continue
        blast_radius = dep_graph.get_blast_radius(service)
        if len(blast_radius) > BLAST_RADIUS_LIMIT:
            decision = (
                f"REJECTED: blast radius for {service} is {len(blast_radius)} services "
                f"({', '.join(blast_radius)}) which exceeds limit of {BLAST_RADIUS_LIMIT}."
            )
            safety_decisions.append({"action": action_req, "decision": decision, "blast_radius": blast_radius})
            rejected_options.append(action_name)
            continue
        incident_env = state.get("incident_details", {}).get("environment", "production")
        if not dep_graph.check_cross_env_action(service, incident_env):
            service_env = dep_graph.graph.nodes.get(service, {}).get("environment", "unknown")
            decision = (
                f"REJECTED: cross-environment action blocked. "
                f"Incident env={incident_env}, service env={service_env}."
            )
            safety_decisions.append({"action": action_req, "decision": decision})
            rejected_options.append(action_name)
            continue
        if tier_policy == "recommend_only":
            decision = f"RECOMMEND_ONLY: {action_name} approved for recommendation, but not execution. Blast radius: {blast_radius}."
            safety_decisions.append({"action": action_req, "decision": decision, "blast_radius": blast_radius})
            action_results.append({"action": action_name, "status": "recommended_only"})
            continue
        decision = f"APPROVED: {action_name} passes all policy checks. Blast radius: {blast_radius}."
        safety_decisions.append({"action": action_req, "decision": decision, "blast_radius": blast_radius})
        if action_name == "restart_service":
            res = simulate_restart(SimulateRestartInput(service=service))
            action_results.append({"action": action_name, "status": res.status, "result": res.data or res.error})
        elif action_name == "scale_service":
            res = simulate_scale(SimulateScaleInput(service=service, replicas=action_req.get("replicas", 3)))
            action_results.append({"action": action_name, "status": res.status, "result": res.data or res.error})
        elif action_name == "clear_cache":
            action_results.append({"action": action_name, "status": "ok",
                                   "result": f"Simulated clear_cache successful for {service}"})
    msg = AgentMessage(
        sender="verifier",
        receiver="user",
        task_id=str(uuid.uuid4()),
        message_type="report",
        payload={"action_results": action_results, "safety_decisions": safety_decisions}
    )
    latency = (time.time() - start_time) * 1000
    log_trace(TraceLog(
        run_id=state["run_id"],
        workflow_state=WorkflowState.VERIFICATION.value,
        agent="verifier",
        input_data={"proposed_actions": proposed_actions},
        output_data={"action_results": action_results, "safety_decisions": safety_decisions},
        rejected_options=rejected_options,
        latency_ms=latency,
        cost_usd=0.0,
        tokens=0
    ))
    return {
        "workflow_state": WorkflowState.COMPLETE,
        "safety_decisions": safety_decisions,
        "action_results": action_results,
        "messages": [msg]
    }
