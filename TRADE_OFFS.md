# Trade-Offs & Production Hardening

## What was simplified

1. FAISS & Local Files vs Hosted DBs: FAISS and NetworkX are running completely in memory. For production, these would be backed by scalable vector stores (e.g., Pinecone/Milvus/Qdrant) and graph databases (e.g., Neo4j/Amazon Neptune).
2. Simplified Mock Data: The tools currently read static JSON/log files instead of hitting real APIs (Datadog, Kubernetes API, PagerDuty, AWS CloudWatch). Real environments would require robust API error handling and retries.
3. No True LLM Graph Loop: LangGraph edges are strictly sequential in this prototype (Planner -> Investigator -> Infra -> Verifier). In production, conditional edges allowing the verifier to push back to the infra agent to "try another action" (cyclical reasoning loop) would be necessary for true autonomous recovery.
4. LLM Usage: Gemini is mocked via a simple chain in Planner, and the rest is deterministic to ensure testability for this evaluation prototype. In production, we'd use Tool Calling / Function Calling directly from the LLMs across all agents.
5. State Management: LangGraph state is currently kept in-memory for the duration of the request. Production would use Postgres or Redis to persist checkpoints, allowing interrupted graphs to resume.

## Production Hardening

1. Kubernetes Operators: The tools layer should connect to a specialized Kubernetes Operator using least-privilege RBAC rather than giving the main orchestrator cluster admin privileges.
2. Human-in-the-Loop (HITL): Implement a Slack/Teams integration in LangGraph to pause execution at the Verifier node if the autonomy tier is `RECOMMEND_ONLY`. The graph would sleep until a human clicks "Approve" or "Reject".
3. Authentication & Authorization: FastAPI endpoints need OAuth2 + JWT (e.g., Keycloak or Okta) to secure the `POST /incident` and `GET /trace` routes. Only authorized incident managers should trigger workflows.
4. Distributed Tracing: Move SQLite traces to an OpenTelemetry-compatible sink (e.g., Jaeger, Honeycomb) to merge agent traces with standard service spans, allowing us to see LLM spans alongside database queries.
5. Dynamic Policy Updates: Instead of reading from a local `safety_rules.yaml`, policies should be fetched from an Open Policy Agent (OPA) server to allow live compliance updates without redeploying the AI agents.
