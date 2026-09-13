# Dovet blockers

| Area | Status | Evidence | Required owner action |
|---|---|---|---|
| AWS credentials | PASS | `aws login` completed; SDK CRT support is pinned | None for read-only work; use a least-privilege role before deployment |
| Bedrock model | BLOCKED (OWNER LEGAL ACTION) | The retired Model access page says serverless models activate on first invocation. Nova Micro is present, its inference profile is active, and agreement/entitlement/region are available, but `authorizationStatus` remains `NOT_AUTHORIZED`; `ConverseStream`, `Converse`, and a one-token first-use probe return `Operation not allowed`. The Nova Micro catalog page states that using the model agrees to its EULA. | The authenticated `us-east-1` Nova Micro playground is open and ready. Personally review the linked EULA, enter a harmless prompt, and choose **Run** once. Tell Codex after the response or exact error appears. |
| AgentCore deployment | BLOCKED | The least-privilege stack validates, but model conformance and a reviewed change set must pass first | After the Nova recovery passes, approve the concrete CloudFormation change set and its bounded cost before deployment |
| Higgsfield final narration | BLOCKED | Opening insert and one timing-gated Dylan audition exist; the full evidence-bound script and owner listening review do not | Enable the live recovery, then review the locked voice at normal speed before the bounded narration batch |
| Production website | PASS | `dovet-site.vercel.app` returns HTTP 200 | None |
| Domain DNS | PASS | Vercel nameservers are authoritative; apex is HTTP 200 and `www` redirects to apex; signed-out browser title verified | None |
| Public source/video/Devpost | BLOCKED | Draft content exists, but the evidence-linked recording, public repository, release tag, and submission receipts do not | Review the finished public content and personally perform any eligibility/legal attestations |
| Upload and submission | OWNER ACTION | Authenticated YouTube Studio is available; Devpost account state is unknown. Owner explicitly requested that Codex upload nothing | Use the supplied MP4, captions, thumbnail, metadata, source package, and form copy after final QA |
