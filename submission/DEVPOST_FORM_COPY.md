# Dovet — exact Devpost form copy

## Project name

Dovet

## Elevator pitch

Dovet preserves verified working state when a managed coding agent stops, then hands it to an authorized replacement without giving up control of files, budgets, or tests.

## Project story — paste the full block below

# Dovet — Keep the work. Change the agent.

## Inspiration

Coding agents reduce typing, but an interrupted session leaves a developer reconstructing the objective, inspecting unfinished edits, remembering failed approaches, and deciding whether another worker can safely continue.

Dovet began with a narrower question: can we preserve the observable facts of the work so the developer does not have to become the handoff mechanism?

## What it does

Dovet supervises coding runs that it explicitly starts and owns. When a managed Codex worker is interrupted, Dovet confirms that the owned process stopped, seals the approved working set into an immutable content-addressed checkpoint, and preserves the task objective, source revision, evidence references, and source hashes.

A Strands supervisor integration reads bounded evidence and produces a typed recovery recommendation. Deterministic policy separately checks the snapshot, one-use approval, known request cost, budget reservation, provider allowlist, and single-writer lease before anything may execute. A model cannot grant itself file or network permissions, increase its budget, or approve its own proposal.

A replacement worker runs in a restricted candidate workspace. Protected acceptance tests live outside its writable scope and decide whether the result passes. An agent saying “done” is evidence, not a successful verification result.

The product interface is organized around Work, Needs you, and History. It reads supported Codex usage through the authenticated app-server and treats missing or stale readings as unknown. Dovet does not rotate subscriptions, copy authentication files, or claim control over arbitrary existing Codex Desktop sessions.

## How we built it

The durable local service uses Python 3.12, FastAPI, SQLite in WAL mode, Pydantic contracts, an append-only event ledger, and an owner-only content-addressed artifact store. A short-lived stdio MCP plugin bridges Codex to the independent launchd daemon, so the durability layer survives when the plugin process exits.

The installed supported Codex SDK handles managed thread start, events, authenticated usage reads, and interruption. Checkpoints bind file paths, modes, sizes, operation state, and SHA-256 objects. Import validates the whole portable bundle before writing anything and restores only into a separate destination.

The recovery supervisor is implemented with Strands Agents 1.55.1, typed Pydantic output, and four bounded evidence tools. Deterministic code remains responsible for authorization, cost, process ownership, leases, and verification.

The local console uses React and Vite. The marketing and documentation website uses Next.js and Vercel. Playwright records the actual product at 1920×1080. AWS CloudFormation defines encrypted S3 artifacts, DynamoDB state, retained logs, and permission-separated AgentCore roles, but the stack was not deployed because live model conformance did not pass.

## Challenges we ran into

The hardest boundary was deciding which state could still be trusted after a worker stopped. A lease timeout does not terminate a process. A filesystem notification does not prove a consistent checkpoint. A polished model answer does not prove protected tests passed.

The managed Codex integration also exposed a host-lifetime issue: the interactive process could read Codex usage while the launchd daemon initially could not find the Codex executable. Dovet now resolves and pins the installed executable path when the service is installed, without copying account credentials.

AWS exposed an active Nova inference profile, agreement, entitlement, and model discovery, but every Strands and direct Bedrock invocation returned `ValidationException: Operation not allowed`. A sweep of 89 discovered text models found zero authorized fallbacks. Dovet records that as BLOCKED instead of replacing the missing integration with fake success.

## Accomplishments that we're proud of

- A real Dovet-managed Codex turn was intentionally interrupted through the installed supported SDK.
- Its immutable checkpoint restored byte-for-byte from a SHA-256-bound snapshot.
- Fifty-four Python unit, integration, and tooling tests pass.
- Six normal desktop/mobile browser checks and four real 1920×1080 recording checks pass.
- Tests cover corrupted objects, secret exclusion, stale approvals, replay, unknown cost, competing writers, traversal, and portable checkpoint validation.
- The independent launchd daemon survives the MCP bridge exiting.
- A fresh Python 3.12 environment installs the built wheel, runs its packaged migration, and imports the Strands supervisor and restricted worker.
- The public evidence interface distinguishes observed, reported, inferred, independently verified, and blocked claims.
- The source, architecture, documentation, disclosure, three-minute film, captions, thumbnails, and reproducible release package are prepared under Apache-2.0.

## What we learned

Useful autonomy needs a small number of explicit state transitions. Strands handles the ambiguous recovery recommendation; deterministic software remains responsible for permissions, cost, process ownership, and verification.

Missing provider evidence must remain visibly missing even when the rest of the product and presentation are ready. Recovery becomes more trustworthy when every conclusion can be traced to an immutable artifact, confirmed process event, or independent test result.

## What's next for Dovet

When AWS enables model invocation, the bounded live runner will execute the real Strands recovery and protected importer verification. The same evidence gate will then produce the live recovery recording.

After that, Dovet can add provider adapters only after each adapter passes its conformance suite, followed by stronger multi-machine isolation, team approvals, and measured recovery benchmarks.

### Current limitation

AWS account provisioning blocked all Bedrock text-model invocations before submission. The Strands recovery integration is implemented, but this build records zero successful provider requests and does not claim a live Bedrock recovery or AgentCore deployment.

## Built with — comma-separated tags

Strands Agents, Amazon Bedrock, Python, FastAPI, Pydantic, SQLite, TypeScript, React, Vite, Next.js, Codex, MCP, Playwright, FFmpeg, ImageMagick, Vercel, AWS CloudFormation, Amazon S3, Amazon DynamoDB, local-first, coding agents, developer tools

## Try it out links

- Product and documentation: https://dovet.site
- Judge evidence page: https://dovet.site/judges
- Public source: REPLACE_WITH_PUBLIC_GITHUB_URL
- Public film: REPLACE_WITH_PUBLIC_YOUTUBE_URL

## Image gallery

1. `submission/gallery/dovet-devpost-cover-3x2.png` — primary 3:2 cover.
2. `submission/screenshots/console-evidence-fixture.png` — evidence-linked recovery receipt.
3. `submission/screenshots/marketing-desktop.png` — public product story.
4. `submission/architecture.png` — system architecture.

## Track

Professional Agents

## Public repository

REPLACE_WITH_PUBLIC_GITHUB_URL

## Architecture diagram

Upload `submission/architecture.png`.

## AWS Builder ID

OWNER ENTERS THEIR OWN AWS BUILDER ID.

## Optional live demo URL

Leave blank. The public `/judges` route is an evidence page and recorded replay, not a live hosted recovery integration.

## Testing instructions

Dovet runs locally on macOS. The public site cannot control the judge's machine. AWS credentials are not required for the local test suite.

Prerequisites: Python 3.12, uv, Node.js 24, pnpm 11, Git, and FFmpeg.

```sh
git clone REPLACE_WITH_PUBLIC_GITHUB_URL
cd dovet
pnpm setup
pnpm doctor
pnpm check
pnpm test
pnpm build
pnpm test:e2e
```

Expected submitted-build evidence: 54 Python tests pass; TypeScript checks and builds pass; six normal desktop/mobile browser checks pass. The live Bedrock test is opt-in and remains blocked on this AWS account. The local daemon binds only to loopback. The release deliberately reports zero successful provider requests and no AgentCore deployment.

## Bonus Builder.aws URL

REPLACE_WITH_PUBLIC_BUILDER_AWS_ARTICLE_URL
