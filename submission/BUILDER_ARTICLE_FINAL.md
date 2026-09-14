# Agents for Humans: What Survives When a Coding Agent Stops?

Published: https://builder.aws.com/content/3JIVnXnvc2pqUUKrSMCzqPep6k7/agents-for-humans-what-survives-when-a-coding-agent-stops

Coding agents reduce typing, but a stopped session can still leave a developer reconstructing the objective, inspecting unfinished edits, remembering failed approaches, and deciding whether another worker can safely continue.

Dovet starts from a narrower question: **what observable evidence survives the agent?**

The result is a local-first recovery supervisor for coding work. It supervises only runs that it explicitly starts and owns. When a managed Codex worker is interrupted, Dovet confirms that the owned process stopped, seals the approved working set into an immutable checkpoint, asks a Strands supervisor for a bounded recovery recommendation, applies deterministic authorization policy, and verifies the candidate result with protected tests outside the worker's writable scope.

Its promise is deliberately small: **Keep the work. Change the agent.**

## The checkpoint is the recovery contract

A source tree by itself is not enough context for a safe handoff. Dovet's checkpoint binds the managed run, task and policy versions, base commit, operation state, selected file paths, file modes, sizes, and SHA-256 content identifiers. A snapshot digest binds the whole manifest.

The checkpoint engine reads each file between two metadata observations and hashes it again after the scan. It excludes credential-like files, version-control internals, dependency trees, and build output. It rejects paths that escape the approved root, symlink traversal, and names that collide after case or Unicode normalization.

Checkpoint artifacts are immutable. Import validates the manifest and every content object before writing into a separate destination. A failed new capture never replaces the last checkpoint Dovet can still prove.

That behavior is covered by tests for binary and Unicode restoration, corrupted objects, sensitive-file omission, previous-checkpoint retention, and portable bundle validation.

## Strands recommends; deterministic policy decides

After an interruption, starting another worker is only one possible action. The task may already be ready for verification. The original worker may still be alive. The requested provider may be outside policy. The next request may have unknown cost.

Dovet gives a Strands supervisor four bounded evidence tools and requires typed Pydantic output. The recommendation contains an action, checkpoint, target worker, evidence identifiers, a short explanation, uncertainties, and preconditions. It does not store hidden reasoning.

That recommendation cannot authorize itself. Deterministic local code checks the current policy and snapshot again. An approval is tied to the action digest and snapshot, expires, and can be consumed once. A budget reservation rejects unknown amounts and requests above the approved ceiling. A workspace lease can change generations only after the old writer's termination is confirmed. Lease expiry alone never proves that a process stopped.

These boundaries are tested against stale approvals, replay, unknown cost, competing writers, and changed snapshots.

## “Done” is evidence, not verification

A replacement worker operates in a restricted candidate workspace. File writes are bound to the approved path and expected source hash. Commands come only from trusted argv templates, and every mutation checks the active lease.

The verifier runs fixed acceptance commands against an exact source snapshot. The acceptance suite and command configuration live outside the worker's writable scope. Their digests, exit status, and bounded output become part of the durable event ledger.

An agent saying it finished can help explain what happened. It cannot turn a failing test into a pass.

## A daemon that outlives the bridge

Dovet's durable service is a Python 3.12 daemon using FastAPI, Pydantic, and SQLite in WAL mode. A short-lived stdio MCP plugin bridges Codex to that service. The bridge is intentionally not the durability layer: the launchd daemon remains alive when the plugin exits.

The installed supported Codex SDK handles managed thread start, events, authenticated usage reads, and interruption. Missing or stale usage is shown as unknown. Dovet never rotates subscriptions, copies account files, or claims control over arbitrary Codex Desktop sessions.

The console is organized around Work, Needs you, and History. Each result distinguishes claimed, observed, inferred, independently verified, and blocked evidence.

## What the evidence currently proves

The submitted build records a real Dovet-managed Codex turn that was intentionally interrupted through the installed supported SDK. Its immutable checkpoint restored byte-for-byte.

The release evidence records:

- 54 passing Python unit, integration, and tooling tests;
- six passing desktop and mobile browser checks;
- four passing real 1920x1080 recording checks;
- a fresh Python 3.12 environment installing the built wheel and importing its packaged migration, Strands supervisor, and restricted worker;
- a three-minute H.264/AAC product film with captions and a reproducible release package.

## The AWS result we would not fake

The recovery worker is implemented with Strands Agents 1.55.1 and typed output. CloudFormation defines encrypted S3 artifacts, DynamoDB state, retained logs, and permission-separated AgentCore roles.

The authenticated AWS account exposed an active Nova inference profile, agreement, entitlement, and model discovery. However, every Strands and direct Bedrock invocation returned `ValidationException: Operation not allowed`. A sweep of 89 discovered text models found zero authorized fallbacks.

Dovet therefore records **zero successful provider requests**. The live Bedrock conformance test is BLOCKED, and AgentCore was not deployed. The provider adapter will remain unadvertised until a bounded request and the protected recovery fixture both pass.

That blocked result is part of the product's argument. Agentic recovery earns trust by preserving uncertainty, not by turning missing integration evidence into a success badge.

## What comes next

Once AWS enables model invocation, the same bounded runner will execute the live Strands recommendation and protected importer verification. After that, new provider adapters can be added one at a time, only after each passes the same conformance suite.

Dovet is built for the Professional Agents track of Agents for Humans. The product, documentation, architecture, and judge evidence are available at [dovet.site](https://dovet.site).

---

**Suggested Builder Center description:** A practical look at immutable checkpoints, confirmed worker termination, and independent verification for interrupted coding-agent work.

**Suggested tags:** `agents-for-humans`, `strands-agents`, `amazon-bedrock`, `developer-tools`, `open-source`

**Cover image:** `submission/video/thumbnail-youtube-1280.png`
