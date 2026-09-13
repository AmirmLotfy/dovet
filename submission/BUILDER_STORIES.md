# Builder.aws story drafts

These drafts are ready for editorial review and publication after each story links the public tagged
source. Story two preserves the AWS blocker instead of presenting the missing invocation as a pass.

## Agents for Humans: What Survives When a Coding Agent Stops?

A coding session is not a reliable storage boundary. Source files may survive while the developer
still loses track of what changed, which checks ran, and which attempt should come next.

Dovet uses a narrower recovery contract. A checkpoint identifies the managed run, task and policy
versions, base commit, selected file modes, sizes, and SHA-256 content identifiers. The overall
snapshot digest binds the manifest. Restoration revalidates the manifest and every blob before
writing into a separate destination.

The uncomfortable cases shaped the design. Credential-like names such as environment files and
private keys are omitted. Common VCS, dependency, and build directories are omitted. Paths that
escape the approved root, resolve through symlinks, or collide after case and Unicode normalization
are rejected. A file is read between two metadata observations and hashed again after the scan.

The latest capture is not automatically the best checkpoint. Dovet tests a failed capture while an
older checkpoint remains available, and tests a corrupted newest blob falling back to the earlier
valid state. This matters because replacing the only good recovery point with a partial scan would
turn preservation into data loss.

The current test report records 54 passing local checks, including binary and Unicode restoration,
corrupt-object rejection, sensitive-file omission, and previous-checkpoint retention. Six desktop
and mobile browser checks cover the evidence UI. A separate real managed Codex probe records an
intentional interruption and byte-identical restore, and an isolated Python 3.12 environment proves
the built wheel includes its database migration and recovery modules.

The lesson is practical: preserve early, label omissions, and keep the last state you can still
prove. Recovery should be based on durable facts rather than a summary that no longer has a source.

## Agents for Humans: Let Strands Recommend, Then Make Policy Decide

After an interruption, starting a replacement agent is only one possible answer. The work may
already be ready for verification. The original worker may still be alive. The proposed provider
may be outside policy, or the next request may have an unknown cost.

Dovet gives a Strands supervisor four bounded evidence tools and asks for a typed recovery result.
The result contains an action, checkpoint, target worker, evidence identifiers, short explanation,
uncertainties, and preconditions. It deliberately excludes hidden reasoning.

That response is advisory. Deterministic local code checks the current policy and snapshot again.
An approval is tied to the action digest and snapshot, expires, and can be consumed once. A budget
reservation rejects unknown amounts and reservations above the approved ceiling. A workspace lease
can change generations only after the old writer's termination is confirmed. An expired lease alone
does not authorize another writer.

Those boundaries now have passing adversarial tests. The cloud implementation uses Strands Agents
1.55.1 and defines separate least-privilege AgentCore roles. CloudFormation validation and Bedrock
model discovery pass.

The live evidence is still incomplete. The authenticated account reports the Nova Micro agreement,
entitlement, and region as available while authorization remains `NOT_AUTHORIZED`. The owner
completed the console's first-use action, but the listed Nova profile rejected both Strands
streaming and direct boto3 invocation with “Operation not allowed,” so Dovet records zero successful
requests. Checks across four documented Nova regions and every discovered callable Nova text model
found no authorized fallback. The account root reproduces the denial, and AWS Support has the exact
request and zero-quota evidence. The submitted build therefore describes the Strands recovery as
implemented but not live-proven. A bounded request and the protected fixture must pass before Dovet
advertises the provider adapter as working. A reviewed least-privilege role is required before
hosted deployment.

That blocked result is part of the architecture, not something to polish away. Agentic judgment and
reliable control complement each other only when the integration itself is proven.

## Agents for Humans: Why “Done” Is Not a Verification Result

Coding agents are useful narrators of what they believe they changed. That statement is evidence,
but it should not decide whether the task is complete.

Dovet treats an agent result as a candidate. A separate verifier executes fixed argv templates
against an exact source snapshot. The acceptance suite and command configuration live outside the
worker's writable scope. Their digests are included in the verification record, along with the
actual exit status and bounded output.

The submission fixture makes this visible. It is a small Python CSV importer with rules for quoted
fields, leading-zero IDs, BOM handling, decimal prices, duplicate IDs, formula-like text, and
structured row errors. Thirteen protected acceptance cases currently fail because the incomplete
fixture has not been recovered. Dovet labels that as a pre-recovery failure instead of committing a
handwritten answer or changing the tests.

The worker tool tests cover the other side of the boundary. File writes are bound to the expected
source hash and approved path. Every tool call rejects a stale lease. Commands come only from
trusted argv templates. Policy tests reject a changed snapshot, replayed state, and an active prior
writer.

Once the authorized Strands recovery runs, the same protected suite will decide the outcome. If any
case remains red, the task remains open. The disclosed submission film keeps that cloud-dependent
sequence visibly blocked.

The result is a more precise promise. Dovet cannot make generated code universally safe, and it does
not claim that it can. It can show exactly which version was checked, what the independent process
returned, and why the product displayed success or kept the work open.
