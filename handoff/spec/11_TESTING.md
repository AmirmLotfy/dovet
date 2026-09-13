# 11 - Verification plan and evidence-driven demo

## 1. Test philosophy

A typed schema is not a working product. A successful model response is not a passing test. A replay is not a live run. Use deterministic unit tests for mechanics and separate opt-in live tests for provider behavior. Record which class each result belongs to.

Every release test captures build commit, test-command version, fixture/suite digest, timestamp, outcome and sanitized artifact paths. Tests must fail closed when evidence cannot be read. The pack-validation script supplied with this handoff validates its starting contracts only; it cannot validate future application code.

## 2. Synthetic demonstration repository

Use a small Python package called `parcel_import`, not a real user/company repository. Its task is to implement a CSV order importer. Public fixtures contain invented identifiers and addresses only.

Public task contract:

```text
Implement parse_orders(csv_text: str) -> ImportResult.
Use Python's standard CSV parsing semantics, preserve IDs as strings,
return accepted typed records plus structured row errors, and never
execute or evaluate CSV content. Do not add dependencies.
```

`Order` has `order_id`, `customer_name`, `quantity` and `unit_price` as Decimal. `RowError` has source line, stable code and field. Define source-line handling for multiline CSV fields explicitly and test it. `ImportResult` has ordered accepted records and ordered errors. Supply a fixed header contract, deterministic duplicate-ID behavior (first valid occurrence wins), a UTF-8 BOM rule and no locale-guessing for prices.

Acceptance cases stored in a protected suite outside the worker-write scope:

1. A valid single record produces the expected typed values.
2. Quoted commas and escaped quotes are parsed correctly.
3. Leading zeros in `order_id` are preserved.
4. A leading BOM is accepted and blank lines are ignored.
5. Missing required headers fail with a structured file-level error.
6. Non-integer and nonpositive quantities produce row errors.
7. Decimal price arithmetic does not use binary float conversion.
8. A malformed/negative price is rejected by the documented rule.
9. Duplicate IDs follow the first-valid-occurrence rule.
10. A bad row does not discard unrelated valid rows.
11. Spreadsheet-like formulas are returned as inert text, never executed.
12. Extra headers are ignored or rejected consistently with the published contract.

The worker can read the contract and public sample tests. It cannot modify the canonical acceptance suite or verifier command configuration. Report this as protected testing, not a perfect defense against malicious software.

## 3. A reliable but honest demo sequence

Start a real managed worker on the incomplete fixture. Wait for an actual meaningful event or source modification. The demonstration operator then intentionally interrupts that owned worker through Dovet's fault-injection control. Mark the event `demonstration_fault`; do not claim it was an actual service outage or exhausted subscription.

Validate and seal the remaining snapshot. Run verification on the incomplete snapshot to show actual failed criteria. Let the Strands supervisor inspect it and recommend a permitted recovery. Start the real replacement worker, then independently verify its result.

An LLM may finish faster or slower than expected. The recording harness must wait for real events with a timeout and preserve the actual result. It must not insert fake errors or replace a failed final check with a success. When the first worker completes before interruption, reset a fresh fixture run and record again; do not rewrite its history.

To demonstrate a human approval boundary, use a genuine recovery request whose additional cost allowance is not authorized, or a proposal to write outside the approved source scope. Show that it remains paused until an explicit decision. Never execute a real production migration for a demo.

## 4. Required test matrix

| Area | Mandatory checks | Release evidence |
|---|---|---|
| Database | Fresh migration; rollback; FK and enum rejection; cross-task lineage; duplicate event; concurrent reservation | Test report + schema version |
| Snapshots | Add/modify/delete/binary/untracked; atomic staging; missing blob; digest mismatch; interrupted write; inconsistent scan | Manifest and restore checks |
| Paths | `../`; absolute path; symlink escape; Unicode normalization edge; NUL; case collision; huge file | Adversarial tests |
| Process ownership | PID reuse; child survives parent; graceful timeout; no kill of unrelated process; deliberate stop | Process-lifecycle tests |
| Leases | Two simultaneous handoffs; old writer still alive; stale generation; daemon restart mid-dispatch | Fault-injection event traces |
| Provider adapter | Real start/events/interrupt; credential expiry; unavailable model; malformed stream; missing usage window | Capability report |
| Usage | Known/stale/unknown; null window; multiple limits; reset change; percentage bounds; no false 100% | Normalization tests |
| Strands | Tool evidence used; schema valid; invalid output; tool/turn timeout; contradictory evidence | Sanitized model trace |
| Policy | Unauthorized profile; denied path; changed policy; wrong task; scope expansion through prompt injection | Denial events |
| Approvals | Single-use; expiry; modified snapshot; altered action; replay; user cancellation | Approval audit |
| Budget | Atomic reserve; unknown price; in-flight allowance; duplicate billing event; provider failure after dispatch | Reservation/cost ledger |
| Verification | Actual exit codes; timeout; worker false claim; modified suite; stale snapshot; output truncation | Protected report |
| Recovery | Primary -> replacement; replacement failure; bounded retries; intentional stop; incomplete checkpoint | Real end-to-end trace |
| Local web | Invalid Host/Origin; CSRF; missing local token; reconnect; no secret in URL/history | Security integration report |
| Cloud demo | Fixture-only input; concurrency ceiling; duplicate trigger; expired run; session loss; fixed budget | Cloud test/run IDs |
| UI | Keyboard path; focus restore; 200% zoom; small viewport; long paths; empty/error/offline | Browser snapshots/results |
| Release | Clean install; uninstall; public links; video duration; license; secrets; claims consistency | Signed-off manifest |

## 5. Crash-point testing

Inject process termination after each durable boundary: before snapshot seal; after blob writes but before DB ready; after action authorization but before dispatch; after worker start but before acknowledgement; during verification; after approval approval but before consumption; and during daemon shutdown.

After restart, reconcile rather than blindly rerun. The correct outcome is either one confirmed worker or an explicit paused/uncertain state. There must never be two writers operating on the same worktree because the coordinator guessed the old worker died.

Filesystem leases do not revoke another process's OS write permission. A lease expiry is therefore insufficient evidence to reuse a worktree. Confirm process termination or isolate the next attempt and require review before reconciling changes.

## 6. UI acceptance

Use fixed viewports 1440x900, 1280x800, 1024x768, 768x1024 and 390x844. The small layout is for reading status/decisions, not pretending a phone can manage a local Mac daemon remotely.

Run automated accessibility checks plus manual keyboard review. Test light and dark semantic colors, visible focus, non-color status labels, reduced motion and clipped code/path content. Use image diffs for layout regressions, not subjective AI ratings.

A connection that is unavailable remains visibly unavailable. A failed operation has a actionable retry/explanation and preserves user input. No spinner runs forever; timeouts include a diagnostic reference. No loading skeleton resembles verified work.

## 7. Performance and resource targets

Treat these as targets until measured: local status read p95 under 200 ms for a modest fixture; new event visible within one second of daemon receipt; idle daemon average CPU under 1% on the tested Mac; bounded event-store queries; no unbounded transcript kept in memory. Record actual hardware and workload when reporting these metrics.

Do not promise a universal recovery duration. Provider latency, repository size and task complexity vary. Large repositories need scope limits, lazy blob capture and explicit unsupported-file handling rather than a false promise that every file is snapshotted instantly.

## 8. Impact measurement

A valid comparison uses the same fixture/version, interruption point, model settings and authorized budget. Compare manual rebriefing against checkpoint-based recovery across multiple runs; report sample size, failures, medians and spread. Include the context-preservation overhead, not just the best resumed response.

Useful metrics: time from confirmed primary stop to replacement first useful action; bytes/context supplied; retries repeating known unsuccessful changes; human decisions requested; accepted checks at the end; actual reported or estimated cost, clearly separated.

Before measurements exist, marketing and Devpost use qualitative language. Never ship the earlier hypothetical numbers such as fourteen minutes saved, 90% token savings or zero duplicate work as facts.

## 9. Release gates

A release is blocked by any unreviewed secret leak, conflicting writer, falsely passing verification, permission bypass, executable restore injection or replay mislabelled live. Optional integration failure can be documented and removed from advertised scope. Core recovery failure cannot be concealed by a polished website.

Store `artifacts/release-check.json` containing command results and build hashes. Keep private evidence outside the public repository. Publish only scrubbed synthetic fixture traces and provenance required for judge reproducibility.
