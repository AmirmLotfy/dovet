# Dovet blockers

| Area | Status | Evidence | Required owner action |
|---|---|---|---|
| AWS credentials | PASS | `aws login` completed; SDK CRT support is pinned | None for read-only work; use a least-privilege role before deployment |
| Bedrock model | BLOCKED (AWS ACCOUNT PROVISIONING) | The owner completed the Nova Micro first-use attempt. The console and API still return `Operation not allowed`; authorization is `NOT_AUTHORIZED`, while agreement, entitlement, region, model, and inference profile are available. Both non-adjustable Nova Micro on-demand quotas are `0.0`. The account is outside AWS Organizations and the error reproduces with the account root. An existing account-verification support case has been unassigned for 10 days. | Approve sending the prepared evidence-only follow-up to the existing AWS Support case. AWS must provision the account or identify its remaining verification prerequisite. |
| AgentCore deployment | BLOCKED | The least-privilege stack validates, but model conformance and a reviewed change set must pass first | After the Nova recovery passes, approve the concrete CloudFormation change set and its bounded cost before deployment |
| Higgsfield final narration | BLOCKED | Opening insert and one timing-gated Dylan audition exist; the full evidence-bound script and owner listening review do not | Enable the live recovery, then review the locked voice at normal speed before the bounded narration batch |
| Production website | PASS | `dovet-site.vercel.app` returns HTTP 200 | None |
| Domain DNS | PASS | Vercel nameservers are authoritative; apex is HTTP 200 and `www` redirects to apex; signed-out browser title verified | None |
| Public source/video/Devpost | BLOCKED | Draft content exists, but the evidence-linked recording, public repository, release tag, and submission receipts do not | Review the finished public content and personally perform any eligibility/legal attestations |
| Upload and submission | OWNER ACTION | Authenticated YouTube Studio is available; Devpost account state is unknown. Owner explicitly requested that Codex upload nothing | Use the supplied MP4, captions, thumbnail, metadata, source package, and form copy after final QA |
