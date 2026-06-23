# Live Demonstration Script

This script provides a step-by-step guide to demonstrating the Mini Agentic AI Platform to stakeholders. It highlights the five key pillars of the architecture: Planning, Retrieval, Verification, Action, and Trace review.

## Preparation Before the Demo
1. Make sure your dependencies are installed: `pip install -r requirements.txt`.
2. Ensure you have copied `.env.example` to `.env` and populated `GOOGLE_API_KEY` with a valid Gemini API key.
3. Open a terminal at the root of the project (`c:\job_project`).

---

## Step 1: The Incident Trigger & Planning
What to show:
Open one of the mock incident JSON files to show the audience what an incoming webhook from Datadog or PagerDuty looks like.
```bash
cat data/incidents/payment_latency_incident.json
```

Action:
Execute the CLI tool to process the incident:
```bash
python src/main.py --incident-file data/incidents/payment_latency_incident.json
```

Talking Point:
> "When the alert fires, it is passed to our Planner Agent. The Planner's job is not to fix the issue, but to comprehend the incident description using an LLM. It extracts the core failing service so that downstream agents know exactly where to focus their investigation, preventing AI hallucinations."

---

## Step 2: Context Retrieval (RAG)
What to show:
As the script runs, refer to the console output as control passes to the Investigator.

Talking Point:
> "Next, the Investigator Agent takes over. To make informed decisions, it performs Retrieval-Augmented Generation (RAG). It queries a FAISS vector database and BM25 text index to pull historical Runbooks. Simultaneously, it uses its tool execution capabilities to fetch the latest logs and metrics for the service. It now has a complete picture of the state of the service."

---

## Step 3: Proposing Action
What to show:
Refer to the transition from Investigator to Infra Agent in the logs.

Talking Point:
> "The context is passed to the Infra Agent. Based on the retrieved logs—for instance, spotting an Out-Of-Memory (OOM) error or a database connection pool limit—the Infra agent proposes concrete, machine-readable actions like `restart_service` or `scale_service`."

---

## Step 4: Verification & Safety Guardrails
What to show:
Point to the `--- SAFETY DECISIONS ---` section printed in the terminal output.

Talking Point:
> "This is where the system becomes production-ready. We don't just blindly execute AI actions. The Verifier Agent intercepts the proposal and runs deterministic checks:
> 1. It checks an explicit allowed/blocked YAML policy.
> 2. It builds a NetworkX Dependency Graph to calculate the Blast Radius. If restarting this service takes down 5 other services, it rejects the action.
> 3. It checks cross-environment boundaries (e.g., stopping a staging incident from touching a production service).
> 4. Depending on our `AUTONOMY_TIER`, it will either simulate the action, or simply flag it as `RECOMMEND_ONLY` for a human to review."

---

## Step 5: Trace Review & Audit Logging
What to show:
Look at the very bottom of the terminal output where the `FULL AUDIT TRACE` is printed. 

Talking Point:
> "For total compliance, every single transition, LLM token used, cost incurred, and decision made is logged to a local SQLite database (`traces.db`)."

Action:
To prove this is accessible for dashboards, start the FastAPI server in a new terminal:
```bash
uvicorn src.api:app --reload
```
Then, copy the `Run ID` from your previous CLI output, and fetch the trace via the API:
```bash
curl http://localhost:8000/trace/<paste-your-run-id-here>
```

Talking Point:
> "By providing this Trace API, we can seamlessly integrate AI audits into standard observability platforms like Jaeger, Datadog, or Honeycomb, ensuring we always know exactly *why* the AI made a decision."
