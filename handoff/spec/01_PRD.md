# 01 - Product requirements

## 1. Product definition

**Dovet** is an evidence-led continuity supervisor for developers who delegate implementation to coding agents. It minimizes the manual work of preserving context, figuring out what survived, choosing an authorized recovery path, and checking that recovered work actually meets the task.

**Promise:** Keep the work. Change the agent.
**Category:** coding-run recovery and verification utility.
**Customer:** an individual developer, technical founder or small studio using agents on trusted local repositories.
**First supported experience:** Codex plugin + managed Codex run + Bedrock recovery worker + local web console.
**Not the promise:** magical state transfer, unlimited usage, a replacement IDE, general remote administration, or a complete cloud software factory.

## 2. User problem and job

When a coding run stops, the person currently reconstructs the objective, inspects the diff, remembers failed approaches, checks which tests ran, supplies context to another worker and verifies the result. Dovet makes those recovery steps explicit and executable.

Job statement: "When an authorized coding run stops, preserve the useful work and help a permitted worker continue from evidence, without making me repeat the brief or trusting an unverified completion claim."

The commercial hypothesis is that developers will value fewer recovery interventions and more trustworthy task completion. Do not represent this as validated demand until interviews and measured trials support it. Competing capabilities include native thread resume, checkpoints, coding-agent supervision and memory tools. Differentiation must be demonstrated through cross-worker recovery and verification, not claimed novelty.

## 3. Success measures

Track observable outcomes, not invented productivity scores:

- Valid interrupted runs recovered to verified completion / eligible interrupted runs.
- Time from confirmed interruption to first useful replacement-worker action.
- Time to independently verified completion, separately from recovery startup.
- Human interventions per eligible recovery.
- Cost incurred by Dovet-supervised calls, with unknown provider costs displayed separately.
- Original worktree changed unexpectedly, duplicate-writer incidents and leaked-secret incidents: zero tolerated in release tests.

Initial engineering targets, not achieved claims: supported-process interruption classified within 5 seconds; UI state updated within 2 seconds of a persisted event; managed recovery dispatch overhead below 10 seconds excluding model/network/tool execution; local idle service below 150 MB RSS excluding coding workers and browsers. Measure and revise; never put targets on the homepage as results.

## 4. Product surfaces

1. **Codex plugin:** protect/register a task, show status, save context, request a checkpoint, launch managed work and open evidence.
2. **Independent local service:** workspace ownership, durable state, approved commands, usage observation, recovery dispatch and test execution.
3. **Local console:** Work, Needs you, History, Connections and project settings. Runs on loopback; not dependent on a cloud login.
4. **Public marketing/docs website:** actual capability explanation, install instructions, demo and architecture.
5. **Hosted demonstration:** fixed synthetic repository; no local computer access and no user repository import.

## 5. Modes and their honest boundaries

| Mode | What Dovet sees | What it may do |
|---|---|---|
| Managed | Events and processes it launches, approved files, task context | Pause/stop its worker, checkpoint, recover, verify within policy |
| Observed | Allowed filesystem state and manually shared summaries | Best-effort checkpoint and handoff proposal; no automatic takeover |
| Disconnected | Persisted previous state only | Preserve/inspect prior checkpoints; queue no mutating action until revalidated |
| Demo live | Real execution in the isolated fixture | Limited preset actions against that fixture only |
| Demo replay | Recorded event/evidence bundle | Playback and inspection only; permanent Recorded label |

A plugin invocation inside an existing Codex Desktop thread does not grant Dovet global control over that desktop application. Users must deliberately start a managed run for automatic recovery. Project context transfer is not a promise to restore the original conversation or hidden reasoning.

## 6. Main user journey

Install the local package; run the setup doctor; choose a repository; inspect current dirty files; approve data sharing and a verification profile; select the existing Codex identity and an authorized Bedrock worker; choose a monetary ceiling; run a small recovery rehearsal; then enable protection for that project.

The user submits a task with acceptance criteria. Dovet creates an isolated worktree and baseline snapshot. The managed worker operates there. Checkpoints are made at safe milestones. When an unexpected interruption occurs, Dovet confirms that the worker stopped, creates or selects a valid snapshot, asks the Strands supervisor for a recovery decision, checks policy, and either dispatches a replacement or asks a precise human question. Final output is a verified patch/report for review, not an automatic merge.

## 7. Functional requirements

### FR-01 Project registration and trust

Register by resolved absolute local path. Display repository root, branch, HEAD, dirty state and excluded file categories. Reject paths that resolve outside the selected root. Require an explicit "I trust this repository's build/test commands" acknowledgement before executing its tooling. Adding a project never runs install scripts automatically.

Acceptance: a dirty repository can be registered without modifying a byte; a repository with no Git history produces a clear unsupported/setup state, not a destructive `git init` or commit.

### FR-02 Worker/provider connections

List, add, edit, disable and remove authorized provider profiles. Initial profiles are one existing Codex identity and one or more named AWS Bedrock configurations with explicit roles/regions/model IDs. Store credential references, never secret values, in the database. Test auth, model invocation and tool-use support separately. Disabling a profile prevents new work; removing an in-use profile requires stopping/draining the run.

The connection page is not a multi-ChatGPT-account quota pool. Provider money budgets and subscription usage windows are distinct units and must not be summed.

### FR-03 Task brief and acceptance criteria

A task contains objective, scope allowlist, constraints, numbered acceptance criteria, verification profile, max attempts and budget. Criteria have statuses not checked, passing, failing or blocked. Edits during a run create a new version and are delivered at a safe boundary. Scope expansion needs approval.

### FR-04 Managed execution

Create an owned isolated worktree from a recorded baseline. Capture selected user dirty state only after consent and preserve its source hashes. Start the worker with a minimal environment and explicit sandbox configuration. Persist actual external thread/run IDs. Track all child process identities. UI distinguishes working, awaiting a tool and waiting for a human.

### FR-05 Usage observation

For supported authenticated Codex app-server versions, read rate limits and subscribe to updates. Normalize each actual window's duration and reset instant. A 5% remaining threshold requests a checkpoint/handoff at the next safe turn boundary. Null means unavailable. Stale data is labelled stale. Threshold routing is optional and cannot change provider spending permission.

### FR-06 Checkpoint creation

Capture an immutable snapshot containing objective version, acceptance criteria, repository base, worker IDs, policy version, selected file manifest, content hashes, relevant evidence references, last verified results, concise public decisions, failed attempts and next proposed steps. Save both JSON and human-readable handoff text. Do not include passwords, full environment dumps, browser state or hidden reasoning.

Acceptance: export/import into a new isolated worktree produces the expected selected file hashes; corruption or exclusions that make recovery incomplete block automatic restoration.

### FR-07 Interruption classification

Classify process exit, explicit provider error, tool timeout, manual pause, host shutdown, stale heartbeat and budget hold separately. Human stop means stopped. Missing activity is not proof of a crash. Repeated errors may trigger a stuck-work proposal, but never a destructive automatic restart of an unowned process.

### FR-08 Recovery decision and routing

A Strands supervisor inspects bounded evidence and proposes resume, restart, handoff, verify-only, pause or ask-human. The local deterministic guard checks policy version, current source hashes, worker availability, budget, lease and approval requirements. Invalid decisions are rejected with one bounded correction attempt; persistent failure leaves work safe and paused.

### FR-09 Single-writer recovery

Request graceful interruption; wait for exit and child termination; obtain a quiescent snapshot; retire the prior lease; acquire a new lease generation; revalidate hashes; dispatch one replacement. A restart during any step can replay the transaction without duplicate dispatch. An unconfirmed old worker prevents takeover.

### FR-10 Independent verification

Run approved verification commands in a clean, credential-minimized environment against the candidate snapshot. Protect the baseline test suite and its digest. Record argv, working directory, environment profile, started/ended timestamps, exit code, timeout and output artifact hashes. A changed test suite is a separate change requiring review, not automatic evidence of success.

"Verified" means the declared checks passed on the displayed snapshot. It does not mean the code is generally secure or correct. Integration checks unavailable without credentials remain blocked.

### FR-11 Human decisions

Queue one decision per incident, containing what happened, evidence, proposed action, exact permission/cost impact, expiry and alternatives. Approval is single-use and bound to action digest, task version, policy, worktree and snapshot. A late approval cannot apply to newer code. Dismiss is not approval. Denial does not enter a retry nag loop.

### FR-12 Result delivery

Show a run receipt: task, workers, recovery chain, changed paths, passed/failed criteria, verified snapshot hash, measured durations, estimated/reported spend and next review action. Export patch and evidence. Apply/push/merge stay explicit owner operations.

### FR-13 History and export

Filter completed, interrupted, paused and failed runs. Search task title/path locally. Export a sanitized checkpoint bundle with a manifest. Delete a project's local history with confirmation and a separate explicit choice for retained worktrees. Never delete the original repository.

### FR-14 Hosted demonstration

Allow a fresh real fixture run, an intentional managed interruption, evidence inspection and a restricted recovery. Accept no arbitrary command, URL, repository or prompt from anonymous users. Show service failures rather than falling back to fake live results. Provide a clearly separated recorded evidence replay when live execution is unavailable.

### FR-15 Installer, doctor and uninstall

Detect missing dependencies, incompatible plugin/schema versions, port conflicts and expired credentials. Provide a dry-run install plan. The independent user service is opt-in, visible and removable. Uninstall removes the service/bridge, not the user's repositories or unseen personal data.

## 8. Release tiers

**Submission release (complete vertical product):** local managed recovery, Codex integration, Bedrock worker, Strands judgment, checkpoint integrity, immutable tests, approval, local UI, marketing/docs site, deployable AgentCore decision service, limited hosted demo, public source and finished demo assets.

**Post-submission extension gates:** conformance-tested additional coding adapters, team synchronization, remote real-repository execution, native menu-bar wrapper, signed installer/notarization, enterprise SSO and hosted billing. These are separately gated; do not show them as delivered features.

The schema supports one user and many local projects without building organizations, invites or payments unnecessarily. Architecture may permit growth without shipping unfinished multi-tenant security.

## 9. Business model hypothesis

Release the local core under Apache-2.0 for reproducibility. Use bring-your-own authorized model access. Investigate paid hosted coordination, managed encrypted history and team controls later. Do not publish invented prices, customer counts or claimed savings. For the hackathon there is no paywall for judging access.

## 10. Non-goals and rejection criteria

Reject subscription quota evasion, universal desktop account switching, background browser-cookie management, secret interception, arbitrary remote shell access, automatic production operations, guaranteed zero data loss, fabricated agent "confidence" percentages, infinite provider retries and an all-in-one project-management suite.

## 11. Release acceptance

The same released build must pass the interruption drill, snapshot-corruption rejection, expired-approval rejection, duplicate-writer prevention, unknown-quota handling, protected-test tamper detection and denied-budget scenario. The primary on-screen demo must use real worker execution, not a state animation. Source, video, website and integration matrix must agree.
