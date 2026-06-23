# Auth Service Runbook

## Overview
The auth service manages user authentication and JWT token generation. It depends on `redis-session-cache` and `users-db`.

## Known Issues

### Out of Memory (OOM) Kills
If the auth service is experiencing OOM kills, it is likely due to an unbounded cache expansion during sudden login spikes or memory leaks in the session handler.

Remediation Steps:
1. Check the logs for `memory limit exceeded` or `OOM`.
2. Check metrics for `memory_usage_mb` nearing the 2048 MB limit.
3. If memory is exhausted, the safest immediate mitigation is to execute a `restart_service` to clear the local memory leak.
4. Additionally, you may execute `clear_cache` to force redis to flush stale sessions, reducing load.

Safety Limits:
- DO NOT scale the auth service beyond 5 replicas as it will overwhelm the `users-db`.
- Never `delete_database` under any circumstance.
