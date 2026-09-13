# Dovet blockers

| Area | Status | Evidence | Required owner action |
|---|---|---|---|
| AWS credentials | PASS | `aws login` completed; SDK CRT support is pinned | None for read-only work; use a least-privilege role before deployment |
| Bedrock model | BLOCKED | Discovery passes, but Nova Micro `ConverseStream` and `Converse` both return `Operation not allowed` | Grant an IAM role `bedrock:InvokeModel` for one approved model/profile or enable model invocation for this account |
| AgentCore deployment | BLOCKED | Current identity is account root and model invocation is denied | Provide or approve a least-privilege deployment role after reviewing the concrete resource plan |
| Polly narration | BLOCKED | Voice discovery passed and synthesis tooling is ready; live recovery scenes are not yet evidence-backed | None until the live recovery and picture edit exist |
| Production website | PASS | `dovet-site.vercel.app` returns HTTP 200 | None |
| Domain DNS | PASS | Vercel nameservers are authoritative; apex is HTTP 200 and `www` redirects to apex; signed-out browser title verified | None |
| Public source/video/Devpost | BLOCKED | Publication content does not exist yet | Review finished content and perform legal attestations/publication approval |
