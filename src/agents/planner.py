import time
import uuid
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from src.state import AgentState
from src.schemas import AgentMessage, WorkflowState
from src.tracing import log_trace, TraceLog

def planner_node(state: AgentState):
    start_time = time.time()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        task_id = str(uuid.uuid4())
        msg = AgentMessage(
            sender="planner",
            receiver="investigator",
            task_id=task_id,
            message_type="investigate",
            payload={"service": state["incident_details"].get("affected_services", ["unknown"])[0]}
        )
        latency = (time.time() - start_time) * 1000
        log_trace(TraceLog(
            run_id=state["run_id"],
            workflow_state=WorkflowState.PLANNING.value,
            agent="planner",
            input_data={"incident": state["incident_details"]},
            output_data={"messages": [msg.model_dump()]},
            latency_ms=latency,
            cost_usd=0.0,
            tokens=0
        ))
        return {
            "workflow_state": WorkflowState.INVESTIGATION,
            "messages": [msg]
        }
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
    prompt = PromptTemplate.from_template(
        "You are the Planner Agent. Analyze this incident: {incident}. "
        "Which service needs to be investigated? Reply with just the service name."
    )
    chain = prompt | llm
    service_to_investigate = chain.invoke({"incident": state["incident_details"]["description"]}).content.strip()
    task_id = str(uuid.uuid4())
    msg = AgentMessage(
        sender="planner",
        receiver="investigator",
        task_id=task_id,
        message_type="investigate",
        payload={"service": service_to_investigate}
    )
    latency = (time.time() - start_time) * 1000
    log_trace(TraceLog(
        run_id=state["run_id"],
        workflow_state=WorkflowState.PLANNING.value,
        agent="planner",
        input_data={"incident": state["incident_details"]},
        output_data={"messages": [msg.model_dump()]},
        latency_ms=latency,
        cost_usd=0.001,
        tokens=150
    ))
    return {
        "workflow_state": WorkflowState.INVESTIGATION,
        "messages": [msg]
    }
