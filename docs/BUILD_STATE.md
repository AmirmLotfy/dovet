# Dovet build state

Last updated: 2026-09-13

## Active gate

**G3 — BLOCKED (OWNER LEGAL ACTION):** the real Strands recovery vertical slice awaits the owner's first Nova Micro playground invocation after reviewing the model EULA.

## Completed evidence

- **PASS:** repository initialized without deleting the immutable handoff.
- **PASS:** Codex CLI `0.154.0-alpha.6.2` app-server schema generation.
- **PASS:** authenticated Codex account and rate-limit read; global configuration hash unchanged.
- **PASS:** Python 3.12.12, Node 24.19.0, pnpm 11.19.0, Playwright Chrome at 1920x1080, FFmpeg H.264/AAC.
- **PASS:** compatible imports for Strands 1.55.1, openai-codex 0.154.0, boto3 1.43.93, AgentCore 1.23.0 and MCP 2.1.1.
- **PASS:** G1 migration, WAL/foreign keys, rollback, event ordering/deduplication and content-addressed artifact tests.
- **PASS:** G2 confirmed owned-process termination, stable checkpoint capture, corrupt/missing blob rejection and isolated restore tests.
- **PASS:** real managed Codex turn `01a0980a-3634-7dc1-821e-ccde0bf26bd1` interrupted through the installed SDK; restored snapshot `37825aa7bdff1bb8885c153a6680cac4331eb7bb22e962bde3e0deab69eac205` matched.
- **PASS:** Python lint/types, generated OpenAPI TypeScript contracts, and console plus 12-route site production builds.
- **PASS:** Codex plugin and skill validators; launchd install/start/status; stdio bridge exit leaves the supervisor daemon healthy.
- **PASS:** anonymous Vercel preview and stable production alias return HTTP 200; 1920x1080 and 390x844 browser checks show no horizontal overflow or serious/critical axe findings.
- **PASS:** `dovet.site` now delegates to `ns1.vercel-dns.com` and `ns2.vercel-dns.com`; HTTPS apex returns 200 and a signed-out browser loaded the expected Dovet title.
- **PASS:** G4 mechanics reject stale/replayed approvals, unconfirmed writer takeover, unknown/over-cap costs, credential-like checkpoint paths, corrupt newest checkpoints and stale/unknown Codex usage.
- **PASS:** launchd daemon restart plus authenticated loopback usage read; install-time Codex path fixes the restricted launchd PATH.
- **PASS:** 51 Python unit/integration/tooling tests; the explicit live test is deselected offline and skips with a precise authorization message when invoked without its paid-run flag.
- **PASS:** deterministic owner-only `.dovet` checkpoint export, whole-archive validation, idempotent content import, and separate-directory restore. Traversal, unexpected members, prohibited paths, and corrupt objects are rejected before any local store mutation.
- **PASS:** an end-to-end `dovet bundle verify` and `dovet bundle restore` CLI proof restored a Unicode payload byte-identically in an isolated temporary home.
- **PASS:** six desktop/mobile console browser checks, including the validated evidence rail, have no serious or critical axe findings; the recording project stays skipped until a live receipt exists.
- **PASS:** the daemon now exposes only validated PASS receipts through an authenticated run route; failed, mismatched, oversized, symlinked, or chain-of-thought-marked receipts cannot receive a verified UI state.
- **PASS:** `pnpm demo:record` builds the console, pairs with the independent service without printing its credential, records at 1920x1080, and writes a checksum-bound manifest only after a real PASS receipt. Its current preflight correctly returns BLOCKED before recording.
- **PASS:** the built `dovet-0.1.0` wheel installs in a fresh Python 3.12 environment; its CLI, packaged SQLite migration, supervisor import, and restricted worker import pass outside the checkout.
- **PASS:** the live vertical runner stops before provider invocation when Nova is unauthorized, enforces a current official price card and run cap, keeps capability tokens out of model-visible schemas, and binds protected verification to the recovered candidate root.
- **PASS:** full Apache-2.0 text, security policy, AI/dependency disclosure, architecture diagram and fail-closed release/video scripts.
- **PASS:** Devpost and Builder.aws drafts now match the 51-test report, isolated-install evidence,
  validated receipt UI, recording gate, and exact Nova authorization blocker; owner-only actions are
  ordered in `submission/OWNER_ACTIONS.md`.
- **PASS:** the generated deadline clock confirms the build window and records the eight-hour media
  reserve boundary without hard-coding a stale remaining-time claim in submission copy.
- **PASS:** Higgsfield produced one restrained 1920x1080 opening insert and an accepted timing-gated Dylan narration audition; IDs, hashes, cost and rejection evidence are recorded without claiming an accent review.
- **PASS:** the updated marketing site now presents the evidence UI, daemon durability, portable recovery, isolated install, and exact cloud blocker. Local 1920x1080 and 390x844 QA passed; the updated build remains intentionally undeployed for owner publication.
- **PASS:** an 8.6-second Higgsfield production look test combines the accepted opening, Dylan audition, actual site footage, restrained motion, and an original deterministic music bed. It is labelled `NOT RECOVERY EVIDENCE`, probes as 1920x1080 H.264 with 48 kHz stereo AAC, and remains local.
- **FAIL (pre-recovery baseline):** 13 protected importer acceptance cases cannot import `parcel_import`; these remain red until the authorized recovery worker produces and independently verifies the fixture.
- **BLOCKED:** Bedrock's current console says the Model access page is retired and serverless models activate on first invocation. Nova Micro availability reports agreement, entitlement, and region available but account authorization `NOT_AUTHORIZED`; Strands `ConverseStream`, direct `Converse`, and a documented one-token first-use probe return `ValidationException: Operation not allowed`. The Nova catalog states that using it agrees to its EULA, so the authenticated playground is prepared for the owner to perform that legal acceptance. No working model invocation is claimed.

## Current commands

```text
codex app-server generate-json-schema --out <temporary-directory>
aws sts get-caller-identity --output json
uv run pytest tests/unit tests/integration -q
uv run python scripts/probe_managed_codex.py --output artifacts/managed-codex-interruption.json
pnpm contracts
pnpm check
pnpm test
pnpm test:integration
pnpm build
pnpm test:e2e
pnpm demo:record
pnpm video:sound
pnpm video:preview
uv run python scripts/deadline_status.py
curl -I https://dovet.site
```

## Next actions

1. In the already-open authenticated `us-east-1` Nova Micro playground, the owner reviews the linked EULA, enters a harmless prompt, and chooses **Run** once. This first use is the console's activation path and constitutes acceptance of the displayed model EULA.
2. Rerun the bounded live vertical: managed Codex interruption, Strands recommendation, deterministic authorization, restricted recovery worker, and independent protected verification.
3. Review a least-privilege CloudFormation change set, record and render the evidence-linked demo,
   then prepare the final source, website and submission package for owner-controlled publication.

## Working commit evidence

The exact current SHA is generated after each commit in `artifacts/release-evidence.json`; verify
it with `git rev-parse HEAD`. This file is updated at each verified gate.
