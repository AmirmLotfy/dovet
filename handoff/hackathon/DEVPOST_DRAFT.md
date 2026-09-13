# Dovet - Devpost draft and field map

**Not a submission receipt.** This is prepared copy. Codex must reconcile every implementation statement with the actual release manifest before generating `submission/devpost-final.md`. Delete or qualify any capability not proven. All URLs below are fields to fill, not existing public assets.

## Project name

Dovet

## Tagline

Keep the work. Change the agent. Evidence-based recovery for interrupted coding tasks.

## Track

Professional Agents

## Inspiration

Using a coding agent can replace typing with a different kind of work: coordination. When a session stops, the developer often has to reconstruct the objective, inspect unfinished edits, remember unsuccessful approaches and explain the task again.

We wanted to preserve useful working facts rather than promise perfect memory. The question behind Dovet is simple: can an interrupted task recover without making the human become the handoff mechanism?

## What it does

Dovet supervises supported managed coding runs. It records observable progress, creates validated checkpoints and detects interruptions. A Strands supervisor examines the available evidence and recommends whether to resume, restart, hand off, verify or ask the developer.

The coordinator enforces permissions, spending rules and one-writer ownership before acting. A replacement worker receives the permitted checkpoint, while independent acceptance checks determine whether the result is complete.

The interface focuses on work in progress, decisions that need a human and the evidence behind each outcome. It is not a subscription-account rotator or a promise to control every existing coding session.

## How we built it

[Use past tense only after these components actually work.]

The local service uses Python, SQLite and immutable file artifacts. A Codex adapter uses supported owned-session interfaces; a thin plugin exposes the local tools without making the plugin process responsible for durability. The recovery supervisor uses the Strands Agents SDK, with a Bedrock coding worker and an AgentCore deployment for the cloud decision path.

React interfaces share a restrained design system. The public website provides installation guidance, integration boundaries and a synthetic judge demo. The hosted fixture is separated from real developer repositories and labelled with its actual worker adapters.

The checkpoint format is documented as DovetCheckpoint/1. It stores task facts, source hashes and evidence references, not hidden model reasoning or unrestricted credentials.

## Challenges

The difficult part is not writing another summary. It is identifying which state is safe to trust after a process stops.

A filesystem notification does not guarantee a complete snapshot. An expired lease does not prove a writer is dead. A model's recommendation is not an approval. A successful-looking log is not independent verification.

[Insert one or two actual implementation incidents with links to the corresponding sanitized tests/commits. Do not invent a debugging history.]

## Accomplishments

[Generate this section from proven release evidence only.]

The core demonstration follows one genuine task across an intentional interruption, a validated checkpoint, a Strands recovery decision, an authorized replacement and an independently checked result. The original and replacement attempts remain visible, and a material permission request pauses for the human rather than being approved by the model.

## What we learned

[Confirm this reflects the build.]

Useful autonomy needs fewer ambiguous boundaries, not more model calls. A small number of deliberate agent decisions works better here than making an LLM responsible for every state transition. The most important product output is a defensible next action with enough evidence to trust it.

## What's next

Expand adapter compatibility only after conformance tests exist. Add stronger multi-machine execution isolation, team approvals and measured recovery benchmarks. Keep the core local-first workflow inspectable and open source. Do not announce unbuilt integrations as currently supported.

## Built with

Select only technologies actually used in the tagged release: Strands Agents, Amazon Bedrock, Amazon Bedrock AgentCore, Python, TypeScript, React, SQLite, Codex supported APIs, Vercel; add DynamoDB, S3 and AgentCore Code Interpreter only when deployed paths use them.

## AI/pre-existing work disclosure

Draft for owner review:

"We used OpenAI Codex as an AI coding assistant during implementation and used standard open-source frameworks/SDKs. The project-specific product, recovery workflow and submission work were developed during the hackathon period. Incorporated pre-existing code, templates and third-party assets are listed in the repository's dependency/license disclosure."

Adjust the statement to the actual history. Do not claim all code was manually written or conceal reused project work. The owner confirms authorship/rights and actual dates.

## Final field checklist

| Field | Source of truth |
|---|---|
| Project/website URL | Verified deployment, not intended domain |
| Source URL | Public tagged repository/release |
| Video URL | Public signed-out playback on YouTube/Vimeo |
| Architecture | Diagram exported from actual component map |
| Screenshots | Actual reviewed build captures |
| Testing instructions | Working fixture path, platform assumptions, judge credentials if required |
| AWS Builder ID | Actual owner-provided account information |
| Team | Owner-confirmed contributors and roles |
| Bonus posts | Actual public Builder.aws URLs |
| Submission | Receipt after final successful submission |

## Testing-instruction draft

Open the verified `/judges` URL. Start the synthetic importer demonstration. Observe a real managed worker, trigger the labelled demonstration interruption, inspect its checkpoint and follow the permitted recovery to the verification result. The page identifies the workers actually used; a recorded run is marked as recorded.

For the local Codex integration, use the source release's tested installation guide and supported operating-system instructions. The judge demo does not require connecting a private repository. Include a free owner-funded judge access route and any credentials in the appropriate private testing field, never in a public code file.

Before submission, test these instructions from a signed-out clean browser and a fresh source checkout. Remove steps referring to a feature that was not shipped.
