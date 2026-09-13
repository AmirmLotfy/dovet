# Build and AI-use disclosure

OpenAI Codex assisted with repository implementation, tests, documentation, research, browser QA,
and submission preparation. Higgsfield produced the opening visual and neutral American synthetic
narration used in the disclosed submission film. FFmpeg and ImageMagick assembled and verified the
local edit. No voice was cloned.

Emergit is a separate pre-existing recovery project. It informed four independently implemented
safety behaviors: resumable run state, explicit recovery eligibility, durable recovery artifacts,
and verified completion. No Emergit source code, tests, copy, layout, or artwork was copied into
Dovet. Full dependency and model-use details are in `docs/AI_AND_DEPENDENCY_DISCLOSURE.md`.

The submission's deterministic mocks exercise local policy and failure handling. They are not
reported as live provider passes. AWS account provisioning blocked every Bedrock text-model
invocation, so the release records zero successful provider requests and no AgentCore deployment.
