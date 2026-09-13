# Dovet - Codex build handoff

**Product:** Dovet. **Intended domain:** `dovet.site`. **Tagline:** Keep the work. Change the agent.
**Prepared:** 2026-09-13. **Status:** implementation specification, not an already-built application.
**Primary submission:** Agents for Humans / Professional Agents.

Dovet is a local-first recovery supervisor for AI-assisted development. It preserves verifiable working state, detects an interrupted managed coding run, asks a Strands agent to recommend a recovery, enforces deterministic policy, starts an authorized replacement worker, and independently checks the result. A Codex plugin is its convenient entry point; an independently running local service is the component that survives the coding host stopping.

## Start building

1. Put this entire directory inside a new repository as `handoff/`.
2. Copy `AGENTS.md` to the repository root, unless a root file already exists; then merge without deleting existing instructions.
3. Open the repository in Codex Desktop and paste `CODEX_MASTER_PROMPT.md`.
4. Codex reads the index, PRD, architecture, and implementation plan first, then only the documents needed for the current phase.
5. Keep the handoff files immutable. Record implementation decisions and evidence under the application's `docs/` and `artifacts/` directories.

There is no need to paste the entire pack into one model message. That wastes context and makes changes harder to track.

## What is included

| File | Purpose |
|---|---|
| `CODEX_MASTER_PROMPT.md` | Execution brief to paste into Codex |
| `AGENTS.md` | Repository working rules |
| `spec/01_PRD.md` | Product, requirements, supported scope, acceptance |
| `spec/02_ARCHITECTURE.md` | Components, trust boundaries, recovery algorithm, decisions |
| `spec/03_ERD.md` + `contracts/schema.sql` | Data model and executable SQLite starting migration |
| `spec/04_CODEX_PLUGIN.md` | Codex adapter, usage observation, plugin packaging |
| `spec/05_AGENTS_AND_CONTRACTS.md` | Strands supervisor, worker tools, decision contracts |
| `spec/06_SECURITY.md` | Credentials, approvals, isolation, prompt injection, privacy |
| `spec/07_UI_UX.md` + `design/tokens.css` | Screen-by-screen visual and interaction specification |
| `spec/08_MARKETING_WEBSITE.md` | Routes, publishable copy, conversion, SEO, accessibility |
| `spec/09_API.md` | Local and hosted API behavior |
| `spec/10_BUILD_PLAN.md` | Ordered implementation gates and deadline protection |
| `spec/11_TESTING.md` | Functional, adversarial, recovery, design and release tests |
| `spec/12_DEPLOYMENT.md` | Local install, AWS, Vercel, domain, release and rollback |
| `hackathon/REQUIREMENTS.md` | Verified competition requirements and evidence mapping |
| `hackathon/VIDEO_PRODUCTION.md` | Real recording, narration, rendering and YouTube publication |
| `hackathon/NARRATION.md` | English demo narration, tied to evidence |
| `hackathon/DEVPOST_DRAFT.md` | Submission content with claims gated on implementation |
| `hackathon/BUILDER_POSTS.md` | Three evidence-led build-story drafts |
| `config/` | Example local policy and environment configuration |
| `contracts/` | Checkpoint and recovery schemas, example payloads |
| `spec/13_SOURCES.md` | Primary sources and researched design references |
| `scripts/validate_pack.py` | Validates the supplied handoff contracts, not the application |
| `diagrams/` | Editable Mermaid architecture/ERD source |
| `evidence/PACK_VALIDATION.json` | Actual handoff-validation results |

## Fixed decisions

- Mac-first; Linux is a secondary CLI target. No Electron or mobile app in the submission path.
- Python for the local service, Strands supervisor and restricted fallback worker. TypeScript/React for the web interfaces.
- Codex-supported session APIs, not UI injection or reading undocumented authentication stores.
- One configured Codex identity plus independently authorized Bedrock workers; no subscription-account rotation.
- SQLite is local operational truth. Optional cloud demo metadata uses DynamoDB; selected artifacts use private S3.
- Strands runs recovery judgment. Deterministic code owns permissions, budget checks, leases, mutation and verification.
- No automatic commit, push, merge, production deployment or database migration by coding workers.
- Full product architecture is specified, but submission-critical gates come first. Never label an unfinished feature complete.

## Important boundaries

The intended domain is a naming choice, not proof it is available or owned. A limited web screen is not a trademark clearance. Verify with a registrar; do not purchase without the user's price approval.

The live application, website and video must be built before they can be deployed, recorded or uploaded. Codex can automate much of this with an authenticated terminal/browser, but account logins, domain purchase, spending approval, legal attestations, CAPTCHA/MFA and final public publication can require the owner. Never claim these steps happened without checking the resulting public URL and receipt.

The competition deadline is 2026-09-14 17:00 America/Los_Angeles, equivalent to 2026-09-15 03:00 Africa/Cairo. Recheck the official page before final submission. Freeze a working submission before spending time on optional extensions.

## Definition of a truthful release

A stranger can install the tagged source, run the documented demo, inspect real checkpoint/test evidence, and understand which integrations are implemented. The marketing site describes those capabilities accurately. The public video depicts the same tagged build. Every external dependency, required credential and known limitation is disclosed.
