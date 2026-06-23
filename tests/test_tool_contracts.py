import pytest
from src.tools.actions import get_logs, get_metrics, simulate_restart, simulate_scale, get_dependency_graph
from src.tools.schema import (
    GetLogsInput, GetMetricsInput, SimulateRestartInput,
    SimulateScaleInput, GetDependencyGraphInput
)
from src.schemas import ToolResponse



def assert_envelope(resp: ToolResponse, expected_tool: str):
    assert isinstance(resp, ToolResponse), "Response must be a ToolResponse"
    assert resp.tool == expected_tool
    assert resp.version, "Version must be set"
    assert resp.status in ("ok", "error"), f"Unexpected status: {resp.status}"
    if resp.status == "ok":
        assert resp.error is None, "ok response must not have an error field"
        assert resp.data is not None, "ok response must have data"
    else:
        assert resp.error is not None, "error response must have an error message"



def test_get_logs_ok():
    resp = get_logs(GetLogsInput(service="auth-service", timeframe="recent"))
    assert_envelope(resp, "get_logs")
    assert resp.status == "ok"
    assert "auth-service" in resp.data or len(resp.data) > 0

def test_get_logs_missing_service():
    resp = get_logs(GetLogsInput(service="nonexistent-service", timeframe="recent"))
    assert_envelope(resp, "get_logs")
    assert resp.status == "error"
    assert "nonexistent-service" in resp.error



def test_get_metrics_ok():
    resp = get_metrics(GetMetricsInput(service="auth-service"))
    assert_envelope(resp, "get_metrics")
    assert resp.status == "ok"
    assert isinstance(resp.data, dict)
    assert "memory_usage_mb" in resp.data

def test_get_metrics_missing_service():
    resp = get_metrics(GetMetricsInput(service="unknown-svc"))
    assert_envelope(resp, "get_metrics")
    assert resp.status == "error"



def test_simulate_restart_ok():
    resp = simulate_restart(SimulateRestartInput(service="auth-service"))
    assert_envelope(resp, "simulate_restart")
    assert resp.status == "ok"
    assert "auth-service" in resp.data



def test_simulate_scale_ok():
    resp = simulate_scale(SimulateScaleInput(service="auth-service", replicas=3))
    assert_envelope(resp, "simulate_scale")
    assert resp.status == "ok"

def test_simulate_scale_over_limit():
    resp = simulate_scale(SimulateScaleInput(service="auth-service", replicas=11))
    assert_envelope(resp, "simulate_scale")
    assert resp.status == "error"
    assert "10" in resp.error 



def test_get_dependency_graph_ok():
    resp = get_dependency_graph(GetDependencyGraphInput(service="auth-service"))
    assert_envelope(resp, "get_dependency_graph")
    assert resp.status == "ok"
    assert "service" in resp.data
    assert "affected_downstream" in resp.data

def test_get_dependency_graph_unknown_service():
    resp = get_dependency_graph(GetDependencyGraphInput(service="ghost-service"))
    assert_envelope(resp, "get_dependency_graph")
    assert resp.status == "ok"
    assert resp.data["affected_downstream"] == []
