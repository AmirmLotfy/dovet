# Dovet — Devpost submission copy

Status: **OWNER READY — submit with the AWS provisioning disclosure below.**

## Project

**Dovet**

**Tagline:** Keep the work. Change the agent.

**Track:** Agents for Humans — Professional Agents

**Website:** https://dovet.site

## Inspiration

Coding agents reduce typing, but an interrupted session leaves a developer reconstructing the
objective, inspecting unfinished edits, remembering failed approaches, and deciding whether another
worker can safely continue. Dovet preserves observable working facts so the next action begins with
evidence instead of a confident summary with no source.

## What it does

Dovet supervises coding runs that it explicitly starts and owns. It can interrupt an owned Codex
turn, confirm termination, seal selected working files into immutable content-addressed checkpoint
artifacts, and restore them into an isolated destination. Credential-like files, build outputs,
symlinks, path escapes, and oversized files are excluded or rejected.

A Strands supervisor integration inspects bounded evidence and returns a typed recovery
recommendation. Deterministic code separately checks the snapshot, current policy, one-use
approval, budget reservation, and single-writer lease before execution. A worker's completion
statement is never enough: protected acceptance tests decide whether the candidate result passes.

The product interface is organized around Work, Needs you, and History. It reads supported Codex
usage through the authenticated app-server and treats missing or stale readings as unknown. It
does not rotate subscriptions, copy authentication files, or claim control over arbitrary existing
Codex Desktop sessions.

## How we built it

The durable local service uses Python 3.12, FastAPI, SQLite in WAL mode, Pydantic contracts, and an
owner-only content-addressed artifact store. The Codex integration uses the installed supported SDK
for managed thread start and interruption. A short-lived stdio MCP plugin bridges Codex to the
independent launchd service.

The recovery supervisor is implemented with Strands Agents 1.55.1, typed Pydantic output, and four
bounded evidence tools. AWS infrastructure defines separate least-privilege roles for AgentCore
Runtime and Code Interpreter, a private encrypted S3 artifact bucket, DynamoDB state, and retained
logs. The CloudFormation template validates without provisioning.

The local console uses React and Vite. The documentation and marketing site use Next.js on Vercel.
The public site cannot control a local machine and presents only public documentation and synthetic
evidence.

## Challenges

The hardest boundary is deciding which state can be trusted after a worker stops. A lease timeout
does not stop a process. A file watcher does not prove a consistent checkpoint. A polished model
answer does not prove protected tests passed.

The managed Codex probe also exposed a host-lifetime issue: the interactive process could read
Codex usage, while the launchd daemon initially could not find the Codex executable. Dovet now pins
the resolved executable path into the LaunchAgent, and the restarted daemon returns authenticated
usage state without storing the account identifier.

AWS returned an active Nova inference profile, but both Strands `ConverseStream` and direct
`Converse` calls returned `ValidationException: Operation not allowed`. Agreement, entitlement, and
region checks pass, while account authorization remains `NOT_AUTHORIZED` and the exposed
non-adjustable quotas are zero. A sweep of 89 discovered text models found no authorized fallback.
Dovet records zero successful provider requests and keeps the live recovery gate blocked.

## Accomplishments

- A real Dovet-managed Codex turn was intentionally interrupted through the installed SDK.
- Its immutable checkpoint restored byte-for-byte from a SHA-256-bound snapshot.
- Fifty-four local unit, integration, and tooling tests pass, with six desktop and mobile browser
  checks.
- Tests cover corrupt blobs, secret exclusion, stale approvals, replay, unknown cost, competing
  writers, and portable checkpoint validation.
- The plugin validates, and the independent launchd daemon survives bridge exit.
- A fresh Python 3.12 environment installs the built wheel, runs its packaged database migration,
  and imports the Strands supervisor and restricted worker.
- The authenticated evidence view accepts only validated PASS receipts, and the 1920x1080 recorder
  refuses to record a simulated cloud success.
- The public site works signed out at https://dovet.site on desktop and narrow screens.
- Deployable AWS infrastructure validates without provisioning under the authenticated account.

## What we learned

Useful autonomy needs a small number of clear state transitions. Strands handles the ambiguous
recovery recommendation; deterministic software remains responsible for permissions, cost,
process ownership, and verification. Missing provider evidence should stay visibly missing even
when the product and presentation are otherwise ready.

## Current limitation

The submitted build contains the working local supervisor, checkpoint engine, Codex integration,
Strands recovery implementation, policy engine, UI, tests, and deployable AWS template. The AWS
account did not authorize any Bedrock text-model invocation before submission, so the video labels
the cloud-dependent sequence as blocked. There is no successful Bedrock request, AgentCore
deployment, or live hosted recovery claim in this submission. AgentCore deployment and a live demo
are optional hackathon elements; judges can reproduce the local product and tests from source.

## What's next

When AWS provisions model authorization, one bounded command will run the real Strands recovery,
protected importer verification, 1920x1080 evidence recording, and release report. The command is
fail-closed and cannot deploy, upload, publish, alter DNS, or accept legal terms.

## Built with

Python, TypeScript, React, Vite, Next.js, SQLite, Pydantic, FastAPI, Strands Agents, Amazon Bedrock,
Amazon Bedrock AgentCore, boto3, Codex supported APIs, Playwright, FFmpeg, Higgsfield, and Vercel.

## Disclosure

OpenAI Codex assisted with implementation, research, testing, documentation, and submission
preparation. Higgsfield produced the opening visual and synthetic narration. Standard open-source
frameworks and SDKs are pinned in lockfiles. Emergit, a separate pre-existing recovery project,
informed four independently implemented safety behaviors described in the repository disclosure;
no Emergit source code or artwork was copied. The owner must confirm eligibility, dates,
authorship, contributors, third-party rights, and Devpost legal terms.
