import json
import os
from .schema import (
    GetLogsInput, GetMetricsInput, SimulateRestartInput,
    SimulateScaleInput, GetDependencyGraphInput
)
from src.knowledge.graph import DependencyGraph
from src.schemas import ToolResponse

TOOL_VERSION = "1.0"

def get_logs(args: GetLogsInput) -> ToolResponse:
    log_file = f"data/logs/{args.service.replace('-', '_')}.log"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            return ToolResponse(tool="get_logs", version=TOOL_VERSION, status="ok", data=f.read())
    return ToolResponse(tool="get_logs", version=TOOL_VERSION, status="error",
                        error=f"No logs found for service {args.service}")

def get_metrics(args: GetMetricsInput) -> ToolResponse:
    metrics_file = f"data/metrics/{args.service.replace('-', '_')}.json"
    if os.path.exists(metrics_file):
        with open(metrics_file, "r") as f:
            return ToolResponse(tool="get_metrics", version=TOOL_VERSION, status="ok", data=json.load(f))
    return ToolResponse(tool="get_metrics", version=TOOL_VERSION, status="error",
                        error=f"No metrics found for service {args.service}")

def simulate_restart(args: SimulateRestartInput) -> ToolResponse:
    return ToolResponse(tool="simulate_restart", version=TOOL_VERSION, status="ok",
                        data=f"Simulated restart successful for {args.service}")

def simulate_scale(args: SimulateScaleInput) -> ToolResponse:
    if args.replicas > 10:
        return ToolResponse(tool="simulate_scale", version=TOOL_VERSION, status="error",
                            error=f"Cannot scale {args.service} beyond 10 replicas.")
    return ToolResponse(tool="simulate_scale", version=TOOL_VERSION, status="ok",
                        data=f"Simulated scale to {args.replicas} replicas successful for {args.service}")

def get_dependency_graph(args: GetDependencyGraphInput) -> ToolResponse:
    graph = DependencyGraph()
    blast_radius = graph.get_blast_radius(args.service)
    return ToolResponse(tool="get_dependency_graph", version=TOOL_VERSION, status="ok",
                        data={"service": args.service, "affected_downstream": blast_radius})
