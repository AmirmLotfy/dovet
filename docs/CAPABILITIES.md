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
| Strands live Bedrock invocation | BLOCKED | Nova Micro is region/entitlement/agreement available but account authorization is `NOT_AUTHORIZED`; `ConverseStream` rejects the call |
| Bedrock worker | BLOCKED | Direct Nova Micro `Converse` also rejects invocation; no successful model response or conformance claim |
| AgentCore Runtime and Code Interpreter | BLOCKED | SDK shapes verified; live permissions and isolation pending |
| Local deterministic recovery | PASS | 54 core unit/integration/tooling tests plus real Codex interruption and byte-identical restore; 13 protected fixture checks remain red before recovery |
| Generated browser contracts | PASS | FastAPI OpenAPI generated through openapi-typescript 7.13.0 |
| Local console/public site builds | PASS | Vite 8.3.0 and Next.js 16.3.5 production builds |
| Isolated Python installation | PASS | Built wheel installed into a fresh Python 3.12 environment; CLI, packaged schema, supervisor, and worker imports pass |
| Portable checkpoint bundle | PASS | Deterministic owner-only export; whole-archive validation rejects traversal, unexpected members, prohibited paths, and corrupt objects before separate-directory restore |
| Codex plugin bridge | PASS | Plugin and skill validators pass; exiting the stdio bridge leaves the launchd daemon healthy |
| Public website preview | PASS | Anonymous HTTP 200; desktop and mobile browser passes with no overflow or serious/critical axe findings |
| Vercel production alias | PASS | `https://dovet-site.vercel.app` returns HTTP 200 |
| `dovet.site` routing | PASS | Vercel nameservers authoritative; HTTPS apex 200, `www` 308 to apex, signed-out browser title verified |
| Browser automation | PASS | System Chrome launched at 1920x1080 through Playwright 1.63.0 |
| Evidence receipt UI | PASS | Authenticated API accepts only validated live PASS receipts; desktop/mobile evidence-rail accessibility checks pass |
| Demo recording preflight | BLOCKED | 1920x1080 recorder and manifest pipeline are ready; it refuses to record before the live recovery receipt exists |
| Media encoding | PASS | FFmpeg 9.0.1 exposes libx264 and AAC |
| Thumbnail/title rasterization | PASS | ImageMagick 7.1.2-3; used because the installed FFmpeg build does not expose `drawtext` |
| Higgsfield opening insert | PASS | One restrained 1920x1080 Kling 3.0 Pro insert generated and checksum-bound; 9 credits spent |
| Higgsfield narration | TIMING PASS / OWNER LISTENING PENDING | All 12 Dylan scenes pass duration, pause, and rate gates; owner must listen once at normal speed before upload |
| Higgsfield media | READY WITH DISCLOSURE | 1920x1080 opener, 12-scene narration, original music bed, 4:40 H.264/AAC film, captions, and thumbnail are prepared; live-dependent scenes remain visibly AWS-blocked |
| GitHub authentication | PASS | Authenticated CLI; public repository not created |
| Vercel authentication | PASS | Authenticated CLI; `dovet-site` preview deployed and anonymous access verified |
| `dovet.site` ownership and routing | PASS | Public DNS delegates to Vercel; apex and `www` were verified signed out |
| YouTube delivery path | PASS | Authenticated YouTube Studio dashboard exists; owner requested manual upload, so no media was uploaded |
| Devpost account readiness | UNKNOWN | Correct hackathon page loaded, but the browser accessibility surface did not expose account controls; owner will submit personally |
