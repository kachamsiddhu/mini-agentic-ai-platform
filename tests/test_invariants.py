import pytest
import os
import yaml
from src.agents.verifier import load_policies, verifier_node

def test_blocked_action_rejected():
    state = {
        "run_id": "test_run_1",
        "incident_details": {"environment": "production"},
        "proposed_actions": [
            {"action": "delete_database", "service": "payment-service"}
        ]
    }
    
    result = verifier_node(state)
    
    decisions = result.get("safety_decisions", [])
    assert len(decisions) == 1
    assert "REJECTED" in decisions[0]["decision"]
    assert "delete_database" in decisions[0]["decision"]

def test_allowed_action_autonomy_tier_medium():
    os.environ["AUTONOMY_TIER"] = "MEDIUM"
    state = {
        "run_id": "test_run_2",
        "incident_details": {"environment": "production"},
        "proposed_actions": [
            {"action": "restart_service", "service": "auth-service"}
        ]
    }
    
    result = verifier_node(state)
    
    decisions = result.get("safety_decisions", [])
    assert len(decisions) == 1
    assert "APPROVED" in decisions[0]["decision"]
    
    action_results = result.get("action_results", [])
    assert len(action_results) == 1
    assert action_results[0]["action"] == "restart_service"

def test_allowed_action_autonomy_tier_low():
    os.environ["AUTONOMY_TIER"] = "LOW"
    state = {
        "run_id": "test_run_3",
        "incident_details": {"environment": "production"},
        "proposed_actions": [
            {"action": "restart_service", "service": "auth-service"}
        ]
    }
    
    result = verifier_node(state)
    
    decisions = result.get("safety_decisions", [])
    assert len(decisions) == 1
    assert "RECOMMEND_ONLY" in decisions[0]["decision"]
    
    action_results = result.get("action_results", [])
    assert len(action_results) == 1
    assert action_results[0]["status"] == "recommended_only"
    
    os.environ["AUTONOMY_TIER"] = "MEDIUM"

def test_cross_env_action_rejected():
    """Invariant: Actions must not target a service in a different environment than the incident."""
    os.environ["AUTONOMY_TIER"] = "MEDIUM"
    state = {
        "run_id": "test_run_4",
        "incident_details": {"environment": "staging"},
        "proposed_actions": [
            {"action": "restart_service", "service": "auth-service"}
        ]
    }

    result = verifier_node(state)

    decisions = result.get("safety_decisions", [])
    assert len(decisions) == 1
    assert "REJECTED" in decisions[0]["decision"]
    assert "cross-environment" in decisions[0]["decision"]
    os.environ["AUTONOMY_TIER"] = "MEDIUM"
