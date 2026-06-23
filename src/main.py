import argparse
import json
import uuid
import sys
from src.graph import build_graph
from src.schemas import WorkflowState
from src.tracing import get_traces

def print_trace(traces):
    print("\n" + "="*60)
    print("FULL AUDIT TRACE (Workflow -> Agent -> Step -> Tool Call)")
    print("="*60)
    for t in traces:
        print(f"\n[{t['workflow_state'].upper()}] Agent: {t['agent']}")
        print(f"  Latency : {t['latency_ms']:.1f} ms | Cost: ${t['cost_usd']:.4f} | Tokens: {t['tokens']}")
        inp = json.loads(t['input_data']) if isinstance(t['input_data'], str) else t['input_data']
        out = json.loads(t['output_data']) if isinstance(t['output_data'], str) else t['output_data']
        rej = json.loads(t['rejected_options']) if isinstance(t['rejected_options'], str) else t['rejected_options']
        print(f"  Input   : {json.dumps(inp, indent=4)[:400]}")
        print(f"  Output  : {json.dumps(out, indent=4)[:600]}")
        if rej:
            print(f"  Rejected: {rej}")
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description="Mini Agentic AI Platform CLI")
    parser.add_argument("--incident-file", type=str, required=True, help="Path to the JSON incident file")
    args = parser.parse_args()
    try:
        with open(args.incident_file, "r") as f:
            incident_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find file {args.incident_file}")
        sys.exit(1)
    run_id = str(uuid.uuid4())
    print(f"\nStarting run: {run_id}")
    print(f"Incident : {incident_data.get('title')} [{incident_data.get('severity')}]")
    print(f"Services : {incident_data.get('affected_services')}")
    print(f"Env      : {incident_data.get('environment')}")
    print("-"*60)
    initial_state = {
        "run_id": run_id,
        "incident_details": incident_data,
        "workflow_state": WorkflowState.INCIDENT_RECEIVED,
        "messages": [],
        "investigation_results": {},
        "proposed_actions": [],
        "action_results": [],
        "safety_decisions": []
    }
    graph = build_graph()
    print("Executing graph (Planner -> Investigator -> Infra -> Verifier)...")
    final_state = graph.invoke(initial_state)
    print("\n--- SAFETY DECISIONS ---")
    print(json.dumps(final_state.get("safety_decisions", []), indent=2))
    print("\n--- ACTION RESULTS ---")
    print(json.dumps(final_state.get("action_results", []), indent=2))
    traces = get_traces(run_id)
    print_trace(traces)
    print(f"\nRun ID: {run_id}  (traces persisted to traces.db)")

if __name__ == "__main__":
    main()
