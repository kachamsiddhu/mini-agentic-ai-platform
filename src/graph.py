import time
import functools
from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.schemas import WorkflowState
from src.agents.planner import planner_node
from src.agents.investigator import investigator_node
from src.agents.infra import infra_node
from src.agents.verifier import verifier_node

MAX_RETRIES = 3
RETRY_DELAY_S = 1.0
NODE_TIMEOUT_S = 30.0

def with_retry(node_fn, max_retries: int = MAX_RETRIES, timeout_s: float = NODE_TIMEOUT_S):
    @functools.wraps(node_fn)
    def wrapper(state: AgentState):
        last_exc = None
        for attempt in range(1, max_retries + 1):
            start = time.time()
            try:
                result = node_fn(state)
                elapsed = time.time() - start
                if elapsed > timeout_s:
                    print(f"[WARN] {node_fn.__name__} completed but exceeded timeout "
                          f"({elapsed:.1f}s > {timeout_s}s)")
                return result
            except Exception as exc:
                last_exc = exc
                print(f"[RETRY] {node_fn.__name__} attempt {attempt}/{max_retries} failed: {exc}")
                if attempt < max_retries:
                    time.sleep(RETRY_DELAY_S)
        raise RuntimeError(f"{node_fn.__name__} failed after {max_retries} attempts") from last_exc
    return wrapper

def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("planner",      with_retry(planner_node))
    builder.add_node("investigator", with_retry(investigator_node))
    builder.add_node("infra",        with_retry(infra_node))
    builder.add_node("verifier",     with_retry(verifier_node))
    builder.set_entry_point("planner")
    builder.add_edge("planner", "investigator")
    builder.add_edge("investigator", "infra")
    builder.add_edge("infra", "verifier")
    builder.add_edge("verifier", END)
    return builder.compile()
