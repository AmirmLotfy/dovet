# 09 - API and event contracts

## 1. Contract authority

Pydantic domain/request models are the source of truth. Generate OpenAPI and TypeScript types from them; validate breaking changes in CI. The handoff specifies behavior and required endpoints, not an already-running API.

Local API prefix: `/api/v1`. Bind to loopback with authenticated session, Origin/Host validation and CSRF for mutations. Every response has request ID; every async mutation returns an operation/action ID and actual queued state. Use RFC3339 UTC instants, opaque IDs and cursor pagination. Error responses never contain raw exceptions, environment variables or credentials.

## 2. Local endpoints

| Method/path | Input and output | Important behavior |
|---|---|---|
| GET `/health` | version, readiness, capability digest | No secrets/account IDs |
| POST `/session/pair` | one-use nonce -> local session | Owner-triggered, short expiry, exact origin |
| GET `/projects` | paginated project summaries | Registered paths only |
| POST `/projects` | name, approved absolute root, requested mode | Inspect first; no auto execution |
| GET `/projects/{id}` | project, effective policy, active tasks | Authorized local owner |
| POST `/projects/{id}/policies` | new policy version, approval | Immutable prior policies |
| POST `/projects/{id}/tasks` | objective, criteria, scope, profile, policy version | Validate full task before ready |
| POST `/tasks/{id}/runs` | provider profile, task version, idempotency key | Budget/lease check; returns queued run |
| GET `/runs/{id}` | state, lineage, checks, cost basis | No invented progress percentage |
| GET `/runs/{id}/events` | after sequence, limit | Persisted order; SSE optional Accept header |
| POST `/runs/{id}/pause` | operator intent, version | Own workers only; no surprise auto recovery |
| POST `/runs/{id}/checkpoint` | reason, idempotency key | Quiescent capture; async |
| POST `/runs/{id}/recovery` | incident/checkpoint IDs, expected state | Proposes, does not self-approve |
| POST `/runs/{id}/verify` | snapshot/checkpoint/profile digests | Immutable protected tests |
| GET `/checkpoints/{id}` | manifest summary and completeness | Paths/blobs constrained by project |
| POST `/checkpoints/{id}/export` | redaction/selection review | Returns bounded local export operation |
| GET `/approvals` | pending/expired decisions | No hidden automatic approval |
| POST `/approvals/{id}/decision` | approve/deny, bound digest, nonce, actor | Single-use, expiry and CAS |
| GET `/connections` | profiles and capabilities | Credential refs only |
| POST `/connections` | provider kind, config, secure credential reference | Disabled until tested/approved |
| PATCH `/connections/{id}` | config/version/enabled | Reject unsafe changes while active |
| POST `/connections/{id}/probe` | explicit permission to small test | Report actual probe/cost |
| DELETE `/connections/{id}` | expected version | Drain/deny when in use |
| GET `/connections/{id}/usage` | windows and data freshness | Known/unknown/stale, not zero fill |
| GET `/history` | status/project/cursor | Stable paging |

## 3. Mutation envelope

All state-changing requests include an idempotency key and relevant `expected_version` or source digest. Duplicate same-key/same-body returns the existing operation. Same key with a different body returns conflict. Do not accept action parameters from unsigned query strings.

Example proposal response:

```json
{
  "request_id": "req_example",
  "operation_id": "op_example",
  "status": "awaiting_approval",
  "action_id": "action_example",
  "message": "A new worker would exceed the current approved budget."
}
```

Examples are contract illustrations, not test evidence.

## 4. Error codes

`AUTH_REQUIRED`, `PROJECT_NOT_TRUSTED`, `CAPABILITY_UNAVAILABLE`, `USAGE_UNKNOWN`, `WORKER_STILL_ACTIVE`, `SNAPSHOT_INCOMPLETE`, `HASH_MISMATCH`, `POLICY_DENIED`, `BUDGET_UNKNOWN`, `BUDGET_EXHAUSTED`, `APPROVAL_REQUIRED`, `APPROVAL_EXPIRED`, `APPROVAL_MISMATCH`, `IDEMPOTENCY_CONFLICT`, `PROTECTED_TEST_CHANGED`, `PROVIDER_UNAVAILABLE`, `TIMEOUT`, `VALIDATION_ERROR`.

Return appropriate HTTP status plus a safe message, retryable boolean and suggested permitted action. 409 handles stale versions; 422 invalid inputs; 403 policy denial; 503 temporarily unavailable capability. Not every failure is retryable. UI preserves the diagnostic request ID.

## 5. Event envelope

Required: `id`, `run_id`, `seq`, `type`, `source_kind`, `knowledge_kind`, `observed_at`, `payload`, optional `trace_id`. Run events append; they do not rewrite old observations. Knowledge kinds: observed, reported, inferred, verified.

Event names include run.created, worker.started, worker.interrupted, worker.exit_confirmed, checkpoint.started, checkpoint.ready, checkpoint.incomplete, recovery.proposed, policy.denied, approval.requested, approval.decided, recovery.dispatched, verification.started, verification.check_finished, verification.failed, task.verified, task.paused and cost.updated.

Do not overload a progress event to imply success. SSE supports reconnection using the last seen sequence and a retention boundary; if the cursor expired, fetch the run snapshot and new cursor. Cloud polling returns only events after the last sequence.

## 6. Cloud decision endpoint

Use the authenticated AgentCore invocation API, not an unauthenticated public endpoint. Input is the incident envelope, expected policy/task/snapshot digests and idempotency token. Output must validate against `contracts/recovery.schema.json`.

The caller validates signature/authentication, schema, evidence lineage and current local policy. The returned decision is advisory until the local guard authorizes it. A replay from an old snapshot is rejected even when the JSON is well-formed.

## 7. Hosted demo endpoints

`POST /demo/sessions`, `POST /demo/sessions/{id}/runs`, `GET /demo/sessions/{id}/runs/{run}`, `GET .../events`, `POST .../interrupt`, `GET .../artifacts/{id}`. Only fixed fixture/scenario IDs are valid. The actor's session token binds every request. There is no arbitrary prompt/command/repository field.

A demo interrupt targets only the current owned child worker. A recorded replay is served from a different immutable manifest route. No endpoint can invoke the local user's daemon or reuse their credentials. Guard request sizes, session expiry, concurrency, artifact scope and operator-approved budget.

## 8. CLI contract to implement

```text
dovet doctor
dovet setup
dovet service install|start|stop|status|uninstall
dovet project add <path>
dovet open
dovet run --project <id> --task <id>
dovet status [--json]
dovet checkpoint <run-id>
dovet recover <run-id>
dovet export <checkpoint-id> --output <path>
dovet demo --scenario interrupted-import
dovet verify <run-id>
```

All destructive/publishing/spend actions have a preview and an explicit approval path. The CLI exits nonzero for failures and blocked prerequisites. `--json` mode is machine-readable and never prints status decoration around JSON.
