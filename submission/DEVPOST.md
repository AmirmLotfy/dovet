# Dovet — Devpost submission draft

Status: **BLOCKED — do not publish until the live Strands recovery, public source release, final
video, and owner attestations pass.**

## Project

**Dovet**

**Tagline:** Keep the work. Change the agent.

**Track:** Agents for Humans — Professional Agents

**Website:** https://dovet.site

## Inspiration

Coding agents reduce typing, but interrupted sessions can create a different kind of work. The
developer has to reconstruct the objective, inspect unfinished edits, remember failed approaches,
and decide whether another worker can safely continue.

Dovet starts from a narrower promise than perfect memory: preserve enough observable, verifiable
state to make the next action useful. It keeps the human in control of scope, spend, and permissions
without making the human rewrite the handoff.

## What it does

Dovet supervises coding runs that it explicitly starts and owns. It can interrupt an owned Codex
turn, confirm termination, seal selected working files into content-addressed checkpoint artifacts,
and restore them into an isolated destination. Credential-like files, build outputs, symlinks, path
escapes, and oversized files are excluded or rejected.

A Strands supervisor is implemented to inspect bounded evidence and return a typed recovery
recommendation. Deterministic code separately checks the snapshot, current policy, one-use approval,
budget reservation, and single-writer lease before execution. A worker's completion statement is
never enough: protected acceptance tests decide whether the candidate result passes.

The product interface is organized around Work, Needs you, and History. It reads supported Codex
usage through the authenticated app-server and treats missing or stale readings as unknown. It
never rotates subscriptions, copies authentication files, or claims control over arbitrary existing
Codex Desktop sessions.

## How we built it

The durable local service uses Python 3.12, FastAPI, SQLite in WAL mode, Pydantic contracts, and an
owner-only content-addressed artifact store. The Codex integration uses the installed supported SDK
for managed thread start and interruption. A short-lived stdio MCP plugin bridges Codex to the
independent launchd service.

The recovery supervisor uses Strands Agents with a typed Pydantic result and bounded evidence
tools. AWS infrastructure defines separate least-privilege roles for AgentCore Runtime and Code
Interpreter, a private encrypted S3 artifact bucket, DynamoDB state, and retained logs. The
CloudFormation template validates, but the live runtime is not claimed until one authorized Bedrock
request succeeds.

The local console uses React and Vite. The documentation and marketing site use Next.js and deploy
on Vercel. The public site is isolated from local-machine control and serves only public
documentation and synthetic evidence.

## Challenges

The hardest boundary is deciding which state can be trusted after a worker stops. A lease timeout
does not stop a process. A file watcher does not prove a consistent checkpoint. A polished model
answer does not prove the protected tests passed.

The real managed Codex probe also exposed a host-lifetime issue: the interactive process could read
Codex usage, while the launchd daemon initially could not find the Codex executable. Dovet now pins
the resolved executable path into the LaunchAgent and the restarted daemon returns the authenticated
usage state without storing the account identifier.

AWS discovery returned an active Nova inference profile, while both Strands ConverseStream and
direct Converse calls returned “Operation not allowed.” Dovet records zero successful provider
requests and keeps the live recovery gate blocked instead of replacing it with a mock.

## Accomplishments

- A real Dovet-managed Codex turn was intentionally interrupted through the installed SDK.
- The resulting checkpoint restored byte-for-byte from an immutable SHA-256 snapshot.
- Fifty-one local unit, integration, and tooling tests pass, alongside six desktop and mobile
  browser checks.
- Tests cover corrupt blobs, secret exclusion, stale approvals, replay, unknown cost, and
  competing writers.
- The plugin validates and the independent launchd daemon survives bridge exit.
- A fresh Python 3.12 environment installs the built wheel, runs the packaged database migration,
  and imports the Strands supervisor and worker.
- The authenticated evidence view accepts only a validated PASS receipt, and the 1920x1080
  recorder refuses to start without one.
- The public site works signed out at https://dovet.site on desktop and narrow screens.
- Deployable AWS infrastructure validates without provisioning under the authenticated root user.

## What we learned

Useful autonomy needs a small number of clear state transitions. Strands is valuable for the
ambiguous recovery recommendation. Software rules remain responsible for permissions, money,
process ownership, and verification. The most useful output is a defensible next action tied to
evidence, not a summary that sounds confident.

## What is next

The authenticated AWS account currently reports the Nova Micro agreement, entitlement, and region
as available, but model authorization as `NOT_AUTHORIZED`. The owner must first review and submit
the access terms shown by the Bedrock console. One bounded successful invocation then unblocks the
actual Strands recovery and protected importer verification. After that evidence exists, the team
can review the least-privilege deployment change set, record the evidence-linked demo, add the
locked Higgsfield narration, publish the source tag, and complete the submission. Future adapters will be advertised
only after their conformance tests pass.

## Built with

Python, TypeScript, React, Vite, Next.js, SQLite, Pydantic, FastAPI, Strands Agents, Amazon Bedrock,
Amazon Bedrock AgentCore, boto3, Codex supported APIs, Playwright, FFmpeg, and Vercel.

## Disclosure

OpenAI Codex assisted with implementation, research, testing, documentation, and submission
preparation. Standard open-source frameworks and SDKs are pinned in repository lockfiles. Emergit,
a separate pre-existing recovery project, informed four independently implemented safety
behaviors described in the repository disclosure. The owner must confirm eligibility, dates,
authorship, contributors, and legal terms before submission.
