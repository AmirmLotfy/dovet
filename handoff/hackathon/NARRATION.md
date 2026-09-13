# Dovet - demo narration

**Production draft.** Use these sentences only after the corresponding implementation has passed its release gate. This is not a report that the product already exists. Adapt scene timings to the real footage. Do not manufacture counts, elapsed times or model results to fit this script.

Pronunciation direction: Dovet, "DOH-vet". Speak evenly, with short pauses at scene changes. The final edit should remain comfortably below five minutes.

## Scene 1 - The problem

An interrupted coding agent should not become another task for the developer.

The code may still be there. But what was actually finished? Which tests passed? What did the agent already try? And what should happen next?

Dovet keeps that working state, so a new authorized agent can continue without making you reconstruct the session.

Keep the work. Change the agent.

## Scene 2 - A bounded task

Here, a managed Codex run is implementing a small order importer.

The task has an explicit objective, approved source files, a spending policy and acceptance checks. The original repository stays separate from the managed worktree.

Dovet follows observable events. It does not pretend to read an agent's private reasoning, and it does not turn activity into an invented completion percentage.

## Scene 3 - Interrupt it

The worker has made a real change. Now I am deliberately interrupting it.

This is a demonstration fault, not a claim that the provider failed.

The coding process stops. Dovet's independent local service stays running. It confirms which process stopped before another worker is allowed to write.

## Scene 4 - Preserve evidence

The checkpoint contains the objective, changed files, remaining criteria and useful evidence from the run.

Each artifact is tied to a source snapshot. An agent's statement is labelled as a statement; a verified result needs an actual check.

The partial implementation does not pass yet. That failure is preserved, rather than hidden behind a reassuring summary.

## Scene 5 - Make a recovery decision

This is where Strands Agents does the judgment work.

The supervisor inspects the interruption, reads the checkpoint, checks eligible workers and considers the current policy. It recommends the smallest useful recovery and explains the evidence behind it.

But the model cannot authorize itself. Deterministic guards still check the snapshot, permissions, spending allowance and whether another writer might be active.

## Scene 6 - Continue the task

A new Bedrock worker now receives the permitted handoff.

It can see the current objective and the incomplete checks. It starts from preserved working facts, not an empty conversation or a claim that everything is already done.

The two attempts remain separate in the history. Recovery does not rewrite the interrupted run as a success.

## Scene 7 - Check the result

A worker saying "done" is only a candidate result.

Dovet runs the protected acceptance checks independently and ties their output to the exact source snapshot. A failed check keeps the task open. A changed verification suite blocks the result.

Here, the recorded report determines the final status. The green state comes from evidence, not from another language model agreeing.

## Scene 8 - The human boundary

Autonomy ends where authorization ends.

This request needs a decision because it exceeds the existing permission or spending policy. Dovet keeps the work paused and shows what would change.

An approval applies to this exact action and snapshot. It cannot become a reusable permission for something else.

## Scene 9 - Product and architecture

The Codex plugin is the entry point. The independent local service owns the task state and recovery controls. Strands runs the supervisor, with the deployed path on Amazon Bedrock AgentCore.

The public demo uses synthetic code and clearly identifies its actual workers. Local execution still requires the developer's machine to be awake. Arbitrary existing desktop sessions are not silently taken over.

Dovet is for developers who want less agent coordination, without giving up control.

The source, installation steps and evidence are available with this release.

Keep the work. Change the agent.
