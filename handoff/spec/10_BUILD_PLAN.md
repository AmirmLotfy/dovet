# 10 - Build plan and Codex execution gates

This is the full product specification. Build the working recovery path first; breadth cannot compensate for a fake handoff. The hackathon deadline is a delivery constraint, not a reason to remove authorization or pretend an unfinished integration works.

## 1. Repository layout

```text
dovet/
  AGENTS.md
  handoff/                       # This immutable specification pack
  apps/
    site/                        # Next.js public marketing, docs, judge experience
    console/                     # Vite/React local console, bundled into daemon
  packages/
    ui/                          # Shared tokens and accessible primitives
    contracts/                   # Generated client types and JSON schemas
  services/
    daemon/src/dovet/             # CLI, local API, state, adapters, process control
    supervisor/src/              # Strands judgment, deployable to AgentCore
    worker/src/                  # Restricted Bedrock coding worker
  plugins/dovet/                 # Current portable Codex plugin + MCP bridge
  infra/                         # Reproducible AWS resources and least-privilege IAM
  examples/importer/             # Synthetic code fixture; no company code
  tests/
    unit/
    integration/
    adversarial/
    acceptance-protected/
    ui/
  video/                         # Recording, narration, editing, publication scripts
  scripts/                       # Doctor, validation, secret scan, release packaging
  docs/
    BUILD_STATE.md
    CAPABILITIES.md
    BLOCKERS.md
    DECISIONS.md
  artifacts/                     # Ignored private build artifacts; sanitized subset public
```

Use a pnpm workspace for TypeScript applications and an explicit uv workspace or well-separated Python projects. Avoid introducing a monorepo orchestration service merely to run a few commands. Pin dependencies in lockfiles after compatibility probes; record the Python, Node, Codex and AWS CLI versions in the build manifest.

## 2. Build state and working method

`BUILD_STATE.md` holds the active gate, last working commit, commands actually run, failing checks, next three actions and blocked external permissions. Update it at every meaningful milestone. `CAPABILITIES.md` records tested, missing and unverified integration features separately.

Read only the relevant specification sections for each gate. Do not repeatedly ingest the entire repository or run a high-cost agent on every file watcher event. Coalesce filesystem notifications and use deterministic parsing. Separate UI work from core state-machine work so parallel development does not edit the same files.

Do not run simultaneous coding workers in one worktree. Parallel Codex build tasks are also isolated by worktree/ownership. Default local development to one worker and one browser instance to stay usable on a modest-memory Mac. Avoid Docker as a mandatory local dependency.

## 3. Ordered gates

### G0 - Capability and authorization audit

Inspect the actual environment, existing repository and installed tools. Verify current official documentation instead of guessing an SDK method or provider model name. Produce the following evidence:

- Codex app-server version and schema generation; owned thread creation, event stream, interruption, and available rate-limit methods.
- One installed Strands invocation with typed output and two real read tools.
- AWS account/region, an accessible model or inference profile, a tiny authorized model probe, and a user-approved spending ceiling.
- AgentCore deployment prerequisites, the current CLI family and permission gaps.
- Node/Python/package tools, browser automation, FFmpeg, GitHub/Vercel authentication and domain ownership state.
- Whether normal browser-based account authentication is available for later YouTube/Devpost publication.

Run read-only inspection freely within granted permissions. Ask for secrets through supported credential flows, not through a committed environment file. Missing cloud access blocks cloud claims, not local schema/testing/UI work.

**Gate:** a written tested capability matrix; no paid deployment without approval. Do not spend more than one focused diagnostic pass on a blocked authentication flow before recording the exact owner action.

### G1 - Persistence and invariants

Apply the supplied SQLite starting schema through versioned migrations. Implement typed repositories, WAL configuration, foreign keys, event sequencing, task/run lineage checks, immutable policies and durable action dispatch records. Implement private filesystem layout and content-addressed artifacts.

**Gate:** migration tests, transactional rollback, bad lineage rejection and event deduplication pass. No web dashboard yet.

### G2 - Managed task and safe checkpoint

Implement trusted-project onboarding, detached worktree creation, scoped manifest snapshots, restore validation, file-state reconciliation, owned-process observation and explicit stop. Add fake adapters only inside automated tests. Implement a real owned Codex adapter as soon as the data path works.

**Gate:** the source worktree remains unchanged; a killed managed process leaves a recoverable valid snapshot; corrupt/missing blobs are rejected; a human stop does not auto-restart.

### G3 - Real Strands recovery vertical slice

Give the supervisor incident evidence and two genuinely different choices. It must call its evidence tools and return a typed proposal. Deterministic policy validates it. Start the actual restricted Bedrock worker from an immutable checkpoint in a safe worktree. Retain provider/request/run identifiers.

**Gate:** an actual Codex-to-Bedrock recovery completes the fixture without manually restating the task. A supported runtime incompatibility is a blocker to resolve, not permission to relabel a mock as Codex.

A second Bedrock-to-Bedrock fixture path may be developed for the hosted demo. It is a separate capability and does not substitute silently for the local integration.

### G4 - Verification, approvals and resilience

Run protected tests independently. A worker's completion statement becomes a candidate, not a pass. Implement failed-verification repair within strict attempt/budget limits. Add immutable approvals, cost reservations, idempotent dispatch, stale-proposal rejection and single-writer reconciliation.

**Gate:** reject a stale approval, replayed action, attempt to change the protected test suite and a competing writer. Unknown costs and stale quotas are shown as unknown. The full recovery trace is visible through a minimal API.

### G5 - Local product UI and plugin

Build the screens in `07_UI_UX.md` using the supplied tokens. Connect every control to real state, including disabled/unavailable/error states. Implement the current plugin manifest using verified documentation or the current official plugin creation workflow. Keep the stdio MCP bridge separate from the opt-in daemon lifecycle.

**Gate:** install the plugin locally, request real status, start a managed task, inspect a checkpoint and stop the task. Closing Codex does not terminate an opted-in independent service. Uninstall stops future monitoring and has an explicit data-retention choice.

### G6 - Cloud supervisor and bounded public demo

Deploy the supervisor to AgentCore and exercise it from the real local coordinator. Implement fixture-only hosted runs with durable cloud status and limited capabilities. The hosted demo cannot access arbitrary visitor repositories or arbitrary shell commands. Isolate generated fixture execution in AgentCore Code Interpreter, not in the credentialed supervisor. Add quotas and an honest replay fallback.

**Gate:** actual deployed request ID, runtime logs, public fixture recovery trace, budget/concurrency limits and a cleanup test. A replay is labelled as a replay. A queue/limit message is not a silent substitution of fake live output.

### G7 - Marketing website and release documentation

Implement the supplied copy and routes. Replace illustrative screenshots with captures of the actual build. Link a tagged source release, installation guide, security/data-flow explanation and judge instructions. Deploy a Vercel preview, then bind the approved domain if owned.

**Gate:** all public claims match the capability matrix; all essential URLs work signed out; keyboard/mobile checks pass; screenshots contain no secrets or real company files.

### G8 - Record and render the submission

Run the genuine fixture once and capture raw footage, event logs and verification artifacts. Generate narration after the timings/results are known. Render the final film, subtitles, thumbnail, description and evidence manifest. Use the detailed video specification.

**Gate:** less than five minutes, actual product behavior, readable text, audio present, no sensitive data, no unsupported claims, architecture explained and source build tag identifiable.

### G9 - Publish and submit

Create the public repository/release, publicly accessible video and final Devpost entry using approved accounts. Ask the owner to confirm eligibility, licenses, public disclosure and paid actions. Verify public URLs in a signed-out browser and record the submission receipt. Publish optional genuine build posts only when they will not jeopardize required assets.

**Gate:** the submission has a verified receipt and no unresolved required fields. A draft or saved local MP4 is not a submitted entry.

## 4. Deadline protection

At the start, calculate remaining time from the official deadline. Reserve the final eight hours for packaging, real recording, upload processing, broken-link fixes and submission. Reserve more time if the upload connection is slow.

Before that reserve begins, stop adding new integrations, telemetry products, billing, onboarding variations, new animation systems or extra models. Remove incomplete advertised capabilities rather than leaving dead controls. Do not cut integrity, authentication, truthful labelling or the independent test path.

If AgentCore deployment is still blocked, a working Strands implementation can still be a valid project; state the missing deployment honestly and remove unsupported scoring claims. If real recovery is not working, do not publish a simulated demonstration as the finished product. The full specification remains the post-submission build backlog, not a certificate of completion.

## 5. Commands the implementation must provide

These are required command contracts to implement, not executables shipped in this specification:

```text
pnpm setup                 # Install pinned JS deps; explain Python setup
pnpm doctor                # Read-only capability report, no secrets
pnpm dev                   # Console/site development, no paid workers by default
pnpm check                 # Formatting, lint, types, Python checks
pnpm test                  # Offline deterministic tests
pnpm test:integration      # Explicit opt-in real-provider tests with budget guard
pnpm test:e2e              # Browser and local service tests
pnpm build                 # Site, console bundle, Python package, plugin bundle
pnpm demo:record           # Real fixture + evidence + browser recording
pnpm video:render          # Narration/audio/subtitles/MP4 assembly
pnpm release:check         # Claims, licenses, secrets, public links, media checks
pnpm release:package       # Tagged distributable artifacts and checksums
```

Use descriptive Python entry points internally instead of opaque shell one-liners. A live command must announce that it consumes credits and enforce a configured ceiling. Make cancellation safe.

## 6. Final Codex report

List actual tested capabilities, exact release commit, actual deployment URLs, reproducible commands, test report paths, video path/public URL, public source URL, Devpost receipt, known limitations and unpaid/unapproved actions. Do not finish with a generic summary of intended features.
