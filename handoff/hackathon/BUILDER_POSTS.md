# Builder.aws - evidence-led build stories

These are drafts to complete during real implementation. Publish only accurate claims, actual screenshots and permitted code. The optional bonus is secondary to a working submission. Use the exact phrase "Agents for Humans" in each title and verify current organizer instructions before publishing. [S02]

Each article should link the public tagged source and the specific evidence it discusses. Codex may prepare the draft and use an authorized browser, but owner login and publication approval may be necessary. Never invent personal feelings, elapsed debugging time, measurements or production incidents.

## Article 1

### Agents for Humans: What Survives When a Coding Agent Stops?

A coding session is not a reliable storage boundary. The source files might survive, but the developer can still lose track of which changes were checked, which approach failed and what the next worker should attempt.

Dovet starts with a narrower promise than perfect memory: preserve enough verifiable working state to make recovery useful. A checkpoint carries an objective, task version, approved scope, source manifest and evidence references. Statements from the worker remain distinct from independently observed results.

The snapshot process matters as much as the content. A file watcher tells us something changed; it does not prove we captured a consistent version. We stage artifacts, validate their hashes and only then make a checkpoint available for recovery. Missing or inconsistent data blocks the handoff instead of being silently ignored.

**Insert actual build evidence:** show one manifest, the source file it references and a real test where a missing blob causes restore rejection. Explain the implementation tradeoff encountered in this build, with a commit or test link.

The broader lesson is practical: agent continuity should be built on durable facts, not a polished summary that no one can verify.

**Suggested original visual:** actual checkpoint detail with observed/reported/verified labels, plus a short staging-to-ready diagram.

## Article 2

### Agents for Humans: Let Strands Recommend, Not Authorize

The interesting decision after an interruption is not always "start another agent." Sometimes the work should be verified as it stands. Sometimes the original session can resume. Sometimes authorization is missing and the correct next step is to pause.

Dovet gives a Strands supervisor a bounded set of evidence tools. It can inspect the incident, read a checkpoint, compare recent attempts and see which workers the current policy permits. It returns a typed recovery proposal with the evidence supporting that choice.

The proposal is deliberately not an execution command. Deterministic code rechecks the exact snapshot, policy version, available budget and writer ownership before any replacement starts. An agent cannot expand its own permissions through a convincing explanation.

**Insert actual build evidence:** include a sanitized supervisor tool trace and the resulting typed proposal. Contrast an authorized handoff with a real test in which a changed policy or stale snapshot invalidates the same-looking request. Identify the actual AWS runtime/model configuration used without exposing account identifiers.

Agentic judgment and reliable control are complementary. Strands handles the ambiguous recovery choice; explicit software rules preserve the user's authority.

**Suggested original visual:** one decision card showing evidence references, then the policy gate result. No hidden reasoning transcript.

## Article 3

### Agents for Humans: Why "Done" Is Not a Verification Result

Coding agents are good at explaining what they believe they changed. That explanation is useful, but it should not decide whether a task is complete.

Dovet treats completion as a candidate state. A separate verifier executes the approved checks against an identified source snapshot. The acceptance suite and verification profile are outside the worker's writable scope, and their digests are attached to the report.

This makes an interrupted task easier to reason about. The replacement does not inherit an unqualified success claim. It inherits actual evidence, including failures. When verification fails, the task stays open or enters a bounded repair attempt rather than becoming a green badge.

**Insert actual build evidence:** show a failed check on the partial importer fixture and the final report from the same recovery run. Publish measured counts only from that report. Include a test showing that modifying the protected suite invalidates verification.

These controls do not make arbitrary generated code universally safe. They do make the product's claim more precise: the outcome is tied to an inspectable check, not to an agent agreeing with itself.

**Suggested original visual:** the real verification panel with source/suite hash references and failed-to-passed lineage.

## Final editorial checks

Remove all "insert evidence" instructions from published copy. Confirm dates, build tag, actual AWS use and model identifiers. Avoid claiming research findings from a single demo. Link each article from Devpost only after public signed-out access works and record its URL in the release manifest.
