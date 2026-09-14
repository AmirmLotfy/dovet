# Dovet build state

Last updated: 2026-09-14

## Active gate

**Submission freeze — READY WITH DISCLOSED AWS BLOCKER:** the owner can submit the tested local
product and a visibly disclosed 2:57 film now. The evidence-gated live Strands/Bedrock release stays
BLOCKED because AWS still denies inference and exposes zero, non-adjustable on-demand quotas.

## Final three-minute film gate

- **PASS:** four Playwright recordings capture the actual local console and site at explicit 1920x1080 without network route mocks.
- **PASS:** the final 2:57.255 edit uses the user-approved Higgsfield narration, an original OpenAI-generated editorial opener/close, and real product footage throughout its evidence body.
- **PASS:** H.264 1920x1080 video, 48 kHz stereo AAC, end-to-end decode, generated 3840x2160 YouTube thumbnail with a 1280x720 fallback, generated 1800x1200 Devpost cover below 5 MB, SRT/VTT sidecars, scene source hashes, and AWS-blocker labels are verified.
- **PASS:** the rejected Higgsfield motion opener and rejected 4:40 edit are not used in the final film.
- **BLOCKED:** the film makes no live Strands/Bedrock or AgentCore claim; AWS authorization still records zero successful provider requests.

Verification: `pnpm check` PASS; `pnpm test` PASS with 54 Python tests; `pnpm build` PASS with 16 site routes; normal `pnpm test:e2e` PASS with six browser checks and five explicitly gated recording skips; four real story-recording checks passed during capture; FFmpeg end-to-end decode PASS.

Changed files include `video/render_story.py`, `apps/console/tests/record-local-story.spec.ts`, `apps/site/app/judges/page.tsx`, `apps/site/app/site.css`, `submission/video/final-film-manifest.json`, and the submission delivery documents. Commands: `pnpm video:story`, FFmpeg full decode/probe, Playwright story recording at 1920x1080, and the full release suite. Next action: owner publishes the tagged source, uploads the supplied media, completes legal fields, and submits using the supplied copy.

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
- **PASS:** 54 Python unit/integration/tooling tests; the explicit live test is deselected offline and skips with a precise authorization message when invoked without its paid-run flag.
- **PASS:** deterministic owner-only `.dovet` checkpoint export, whole-archive validation, idempotent content import, and separate-directory restore. Traversal, unexpected members, prohibited paths, and corrupt objects are rejected before any local store mutation.
- **PASS:** an end-to-end `dovet bundle verify` and `dovet bundle restore` CLI proof restored a Unicode payload byte-identically in an isolated temporary home.
- **PASS:** six desktop/mobile console browser checks, including the validated evidence rail, have no serious or critical axe findings; the recording project stays skipped until a live receipt exists.
- **PASS:** the daemon now exposes only validated PASS receipts through an authenticated run route; failed, mismatched, oversized, symlinked, or chain-of-thought-marked receipts cannot receive a verified UI state.
- **PASS:** `pnpm demo:record` builds the console, pairs with the independent service without printing its credential, records at 1920x1080, and writes a checksum-bound manifest only after a real PASS receipt. Its current preflight correctly returns BLOCKED before recording.
- **PASS:** the built `dovet-0.1.0` wheel installs in a fresh Python 3.12 environment; its CLI, packaged SQLite migration, supervisor import, and restricted worker import pass outside the checkout.
- **PASS:** the live vertical runner stops before provider invocation when Nova is unauthorized, enforces a current official price card and run cap, keeps capability tokens out of model-visible schemas, and binds protected verification to the recovered candidate root.
- **PASS:** full Apache-2.0 text, security policy, AI/dependency disclosure, architecture diagram and fail-closed release/video scripts.
- **PASS:** Devpost and Builder.aws drafts now match the 54-test report, isolated-install evidence,
  validated receipt UI, recording gate, and exact Nova authorization blocker; owner-only actions are
  ordered in `submission/OWNER_ACTIONS.md`.
- **PASS:** the generated deadline clock confirms the build window and records the eight-hour media
  reserve boundary without hard-coding a stale remaining-time claim in submission copy.
- **PASS:** Higgsfield produced one restrained 1920x1080 opening insert and an accepted timing-gated Dylan narration audition; IDs, hashes, cost and rejection evidence are recorded without claiming an accent review.
- **PASS:** the updated marketing site now presents the evidence UI, daemon durability, portable recovery, isolated install, and exact cloud blocker. Local 1920x1080 and 390x844 QA passed; the updated build remains intentionally undeployed for owner publication.
- **PASS:** an 8.6-second Higgsfield production look test combines the accepted opening, Dylan audition, actual site footage, restrained motion, and an original deterministic music bed. It is labelled `NOT RECOVERY EVIDENCE`, probes as 1920x1080 H.264 with 48 kHz stereo AAC, and remains local.
- **FAIL (pre-recovery baseline):** 13 protected importer acceptance cases cannot import `parcel_import`; these remain red until the authorized recovery worker produces and independently verifies the fixture.
- **PASS:** the owner completed the Nova Micro first-use action in the authenticated playground after the model EULA gate was surfaced.
- **PASS:** the owner-approved diagnostic follow-up was submitted to the existing AWS account-verification case through the authenticated in-app browser. The newest correspondence visibly contains the Nova authorization, active profile, zero non-adjustable quota, organization, root reproduction, request ID, bounded-use, and deadline evidence. No attachment, credential, or personal identifier was sent.
- **PASS:** a read-only fallback audit checked Nova Micro in `us-east-1`, `us-west-2`, `eu-west-1`, and `ap-southeast-2`; every route remained `NOT_AUTHORIZED` with zero request/token quota. Every discovered callable Amazon Nova text model in `us-east-1` was also unauthorized. A region or Nova-model switch cannot unblock the live proof.
- **PASS:** a broader read-only sweep checked all 89 discovered Bedrock text models in `us-east-1`; zero were authorized across 17 providers. There is no already-authorized Bedrock fallback on this account.
- **PASS:** all 12 Higgsfield Dylan narration scenes pass measured duration, rate, and pause gates. One short scene was rewritten once. The accepted assets, job IDs, hashes, rejection, and estimated 11.7-credit batch cost are recorded; owner normal-speed listening remains pending.
- **SUPERSEDED:** the earlier 4:40 review renderer and disclosed cut remain as local provenance only. The owner rejected that edit, and neither file is in the final upload package.
- **PASS:** `release:finish-after-aws` checks authorization before cost, then runs the real vertical,
  evidence recording, locked narration render, full checks, and release report under an explicit
  microusd ceiling. Its current dry invocation exits BLOCKED before provider use and performs no
  deployment or publication.
- **PASS:** the owner packager checksum-verifies the final 2:57 film, media contract, captions, thumbnail, source archive, and curated submission documents. It excludes the rejected edit and cannot create the evidence-gated `dovet-demo.mp4`.
- **PASS:** owner-ready Devpost copy, YouTube metadata, captions, thumbnail, judge testing
  instructions, disclosure, URL ledger, legal confirmation sheet, and exact submission order now
  form a complete manual-upload package.
- **PASS:** the final raster submission artwork was generated with OpenAI image generation using
  the Dovet editorial illustration and actual console evidence as references. The Devpost cover is
  1800x1200 PNG at 2.97 MB; the YouTube master is 3840x2160 PNG at 8.75 MB with a 1280x720 fallback.
- **PASS:** the exact Devpost form copy and one final Builder Center article are included in the
  owner package. Both preserve the zero-successful-request Bedrock disclosure.
- **PASS:** the source repository is public at `https://github.com/AmirmLotfy/dovet`; anonymous
  HTTP verification returned 200. The final public release target is `v0.1.4`.
- **BLOCKED:** the playground, Strands `ConverseStream`, and a direct one-token `Converse` call all return `ValidationException: Operation not allowed`. Nova Micro authorization remains `NOT_AUTHORIZED`; its on-demand requests-per-minute and tokens-per-minute quotas are both `0.0` and non-adjustable. Agreement, entitlement, region, model discovery, and the active inference profile all pass. The account is outside AWS Organizations and the account root reproduces the error, isolating this to AWS account verification/provisioning. An existing verification case is still unassigned after 10 days. No working model invocation is claimed.

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

1. Tag the public-link update as `v0.1.4`, generate its archive, checksum, and owner upload ZIP.
2. Owner publishes the disclosed video, completes legal fields, submits Devpost, and
   saves the receipt before the deadline.
3. Publish the prepared Builder Center article after the authenticated Builder ID sign-in gate.
4. Continue monitoring the AWS case. If authorization appears before upload, run the bounded live
   vertical and use the evidence-gated film only if every release check passes.

## Working commit evidence

The exact current SHA is generated after each commit in `artifacts/release-evidence.json`; verify
it with `git rev-parse HEAD`. This file is updated at each verified gate.
