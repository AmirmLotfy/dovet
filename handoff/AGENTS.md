# Dovet repository instructions

## Product invariant

Dovet recovers authorized coding work using observable state and independent verification. It does not guarantee reconstruction of private agent state, recovery of unsaved bytes, availability of another provider, or continuous execution while a local machine is asleep.

## Work in small, verified gates

Read `handoff/START_HERE.md` and the current phase in `handoff/spec/10_BUILD_PLAN.md`. Load the narrowest relevant specification. Record progress in `docs/BUILD_STATE.md`. Use explicit PASS / FAIL / BLOCKED statuses; do not turn missing credentials into a mocked integration pass.

Keep a single normal monorepo, Python service package and TypeScript UI workspace. Use pinned dependencies and lockfiles. No unused frameworks, speculative abstractions, Redis/Kubernetes, multiple autonomous supervisors or billing implementation on the submission path.

## Non-negotiable safety

- Never change another application's account identity or copy browser/Codex authentication tokens.
- Never print or commit secrets. No credentials in browser bundles, screenshots, traces or example configs.
- Never auto-run on a project until that project, data-sharing profile, budget and verification command set are approved.
- Never run two writers in one workspace. Lease expiry alone does not prove the old worker stopped.
- Never destroy existing user edits, run `git reset --hard`, auto-stash, force-push or edit protected tests to obtain success.
- Never use shell interpolation with model-supplied arguments. All executable commands are trusted argv templates.
- Never let the model approve its own proposed action, increase its budget, or override a policy denial.
- Never import a remote checkpoint without validating hashes, format, path constraints and trust level.
- Keep explicit Stop controls accessible. An intentional human stop does not trigger automatic recovery.
- No production deployment, money movement, permission changes or migration execution by demo workers.

## Engineering quality

Use typed Pydantic models and generated TypeScript contracts, not hand-maintained duplicate types. Prefer transactions and append-only events over hidden state. UTC for storage; monotonic time for duration. Every mutation has an idempotency key, source version and audit event. Network retries use bounded exponential backoff with jitter. Protect retries around non-idempotent actions.

Do not call unsupported/internal endpoints because a working example exists online. Verify the installed Codex app-server schema, Strands APIs and AWS SDK commands before using them. Treat model list results as discoverability, not proof of invocation permission. Run a small authorized live probe.

No hidden chain-of-thought storage or invented numerical model confidence. Save a short decision explanation, evidence IDs, uncertainty and the policy result.

## UI quality

Use `handoff/design/tokens.css` and `spec/07_UI_UX.md`. Semantic HTML and accessible primitives. Real empty/loading/error/offline states. No artificial percentages. Always distinguish claimed, observed, inferred and independently verified information. No misleading success toasts for queued work. No new icon/color without a semantic reason.

## External actions

Preview and plan are safe defaults. Domain purchase, paid infrastructure, new OAuth grants, public publishing, legal acceptance and changes to unrelated accounts/DNS need owner authorization. Use existing authenticated tooling only within its granted scope. Never bypass MFA, CAPTCHA or account protections.

## Evidence

Keep sanitized evidence under `artifacts/`, not private raw transcripts. Release checks include install, interruption recovery, corrupted checkpoint, stale lease, approval replay, secret exclusion, test tampering, UI accessibility, public URL checks and video duration. Commit an immutable submission tag with the license and setup instructions.

The hackathon build and recording scripts are outputs to implement; the handoff itself is not evidence of a completed app.
