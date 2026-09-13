# Tested capability matrix

Statuses describe evidence from this checkout only.

| Capability | Status | Tested version or boundary |
|---|---|---|
| Codex app-server initialize/account read | PASS | CLI 0.154.0-alpha.6.2; authenticated ChatGPT account |
| Codex rate-limit read | PASS | Actual window returned; missing values remain unknown |
| Codex managed start/events/interrupt | PASS | Real synthetic turn started and interrupted through openai-codex 0.154.0 |
| Codex Desktop arbitrary-session takeover | NOT SUPPORTED | Dovet controls only runs it starts or receives through supported APIs |
| Strands structured output imports | PASS | strands-agents 1.55.1 with Pydantic 2.13.5 |
| AWS authenticated identity | PASS | `aws login` completed in `us-east-1`; current principal is account root, so deployments remain withheld pending least-privilege review |
| Strands live Bedrock invocation | BLOCKED | Listed Nova Micro profile rejects `ConverseStream` with `Operation not allowed` |
| Bedrock worker | BLOCKED | Direct Nova Micro `Converse` also rejects invocation; no successful model response |
| AgentCore Runtime and Code Interpreter | BLOCKED | SDK shapes verified; live permissions and isolation pending |
| Local deterministic recovery | PASS | 38 core unit/integration/tooling tests plus real Codex interruption and byte-identical restore; 13 protected fixture checks remain red before recovery |
| Generated browser contracts | PASS | FastAPI OpenAPI generated through openapi-typescript 7.13.0 |
| Local console/public site builds | PASS | Vite 8.3.0 and Next.js 16.3.5 production builds |
| Codex plugin bridge | PASS | Plugin and skill validators pass; exiting the stdio bridge leaves the launchd daemon healthy |
| Public website preview | PASS | Anonymous HTTP 200; desktop and mobile browser passes with no overflow or serious/critical axe findings |
| Vercel production alias | PASS | `https://dovet-site.vercel.app` returns HTTP 200 |
| `dovet.site` routing | PASS | Vercel nameservers authoritative; HTTPS apex 200, `www` 308 to apex, signed-out browser title verified |
| Browser automation | PASS | System Chrome launched at 1920x1080 through Playwright 1.63.0 |
| Media encoding | PASS | FFmpeg 9.0.1 exposes libx264 and AAC |
| Polly voice discovery | PASS | Authorized read-only `DescribeVoices`; selected voice and engine were returned |
| Polly narration synthesis | BLOCKED | Script and timing pipeline implemented; evidence is not yet reconciled, so no paid synthesis request was sent |
| GitHub authentication | PASS | Authenticated CLI; public repository not created |
| Vercel authentication | PASS | Authenticated CLI; `dovet-site` preview deployed and anonymous access verified |
| `dovet.site` ownership | REPORTED | Owner confirmed; registrar/DNS control not yet observed |
