# Dovet blockers

| Area | Status | Evidence | Required owner action |
|---|---|---|---|
| AWS credentials | PASS | `aws login` completed; SDK CRT support is pinned | None for read-only work; use a least-privilege role before deployment |
| Bedrock model | BLOCKED | Nova Micro is present and region/entitlement/agreement are available, but `authorizationStatus` is `NOT_AUTHORIZED`; both `ConverseStream` and `Converse` return `Operation not allowed` | In the AWS console for `us-east-1`, open Bedrock model access, select Amazon Nova Micro, and personally review and submit the displayed access terms |
| AgentCore deployment | BLOCKED | The least-privilege stack validates, but model conformance and a reviewed change set must pass first | After the Nova recovery passes, approve the concrete CloudFormation change set and its bounded cost before deployment |
| Polly narration | BLOCKED | Voice discovery passed and synthesis tooling is ready; live recovery scenes are not yet evidence-backed | None until the live recovery and picture edit exist |
| Production website | PASS | `dovet-site.vercel.app` returns HTTP 200 | None |
| Domain DNS | PASS | Vercel nameservers are authoritative; apex is HTTP 200 and `www` redirects to apex; signed-out browser title verified | None |
| Public source/video/Devpost | BLOCKED | Draft content exists, but the evidence-linked recording, public repository, release tag, and submission receipts do not | Review the finished public content and personally perform any eligibility/legal attestations |
