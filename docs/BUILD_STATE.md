# Dovet build state

Last updated: 2026-09-13

## Active gate

**G3 — IN PROGRESS:** real Strands recovery vertical slice.

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
- **PASS:** 38 Python unit/integration/tooling tests; current sanitized core JUnit report is `artifacts/test-report-core.xml`.
- **PASS:** full Apache-2.0 text, security policy, AI/dependency disclosure, architecture diagram and fail-closed release/video scripts.
- **PASS:** Polly `DescribeVoices` returned the selected English voice/engine; no synthesis request was sent because recovery evidence is incomplete.
- **FAIL (pre-recovery baseline):** 13 protected importer acceptance cases cannot import `parcel_import`; these remain red until the authorized recovery worker produces and independently verifies the fixture.
- **BLOCKED:** AWS authentication and Bedrock discovery pass, but both Strands `ConverseStream` and direct `Converse` probes return `ValidationException: Operation not allowed`; no working model invocation is claimed.

## Current commands

```text
codex app-server generate-json-schema --out <temporary-directory>
aws sts get-caller-identity --output json
uv run pytest tests/unit tests/integration -q
uv run python scripts/probe_managed_codex.py --output artifacts/managed-codex-interruption.json
pnpm contracts
pnpm -r test
pnpm -r build
curl -I https://dovet-site-ahyoqy2rn-mellardoos-projects.vercel.app
```

## Next actions

1. Obtain explicit authorization for a least-privilege Bedrock invocation role, then run the bounded live Strands recovery probe.
2. Execute the recovered fixture with the restricted worker and independent verifier.
3. Record and render the evidence-linked demo, then reconcile public claims and submission materials.

## Last working commit

17c30ab on codex/dovet-build. This file is updated at each verified gate.
