# 12 - Installation, deployment, domain and release

## 1. Deployment map

| Surface | Target | Must not do |
|---|---|---|
| Marketing/docs | Vercel, intended `dovet.site` | Run persistent coding workers inside short web requests |
| Local console | Loopback HTTP served by the user's daemon | Expose unauthenticated LAN/public control |
| Local worker | User-authorized managed worktree on the developer device | Continue magically while the device sleeps |
| Recovery supervisor | Amazon Bedrock AgentCore Runtime | Treat an LLM proposal as authorization |
| Bounded public demo | AgentCore + short API control plane + DynamoDB + private S3 | Accept arbitrary repositories, prompts or shell input |
| Source | Public tagged GitHub release | Commit credentials, private traces or borrowed unlicensed code |
| Video | Public YouTube/Vimeo | Confuse an unlisted/private upload with a valid public submission |

The domain is intended, not registered by this pack. No AWS/Vercel resources or video have been created by this specification.

## 2. Local installation

Build a Python package with a stable `dovet` executable and bundled local console assets. Provide verified source-install instructions first; publish a registry package only after the package name/ownership is confirmed. Do not display an `npm install` or `uv tool install` command for a package that does not exist.

On macOS, install the independent user service only after a clear consent screen. Use a per-user launchd agent, never a privileged system daemon. Record absolute verified executable paths, a fixed working directory and private stdout/stderr targets. Service plist creation, load/unload commands and login behavior must be tested on the installed macOS release before publication.

Use macOS Keychain for app-owned credential references and existing official provider authentication for Codex. AWS SSO/profile renewal remains the normal provider flow. Keychain failure must not downgrade to a plaintext password file.

The local bootstrap starts with a one-use launch token exchanged for a session credential; do not leave long-lived tokens in query strings. Validate Host and Origin, bind loopback only and apply CSRF protections to writes. A local web app is not automatically safe because it uses localhost.

Uninstall stops the service and removes app-owned executables/plugin entries. Ask whether to preserve checkpoints. Never remove project repositories, external provider credentials or unrelated files.

## 3. AWS authorization and cost preflight

Before deploying, obtain an explicit region, account/profile and maximum authorized build/demo spend. The hackathon resources page says the promotional credit supply is exhausted; do not assume free credits. [S03]

Discover a model or inference profile actually usable in this account/region and verify tool/structured-output compatibility with a minimal paid probe after authorization. A model returned by a catalog is not proof of access. Keep model identifiers/configuration separate from source; no invented future model names. [S11]

Use short-lived role/profile credentials. Deployment and runtime roles are separate. Restrict runtime access to the required Bedrock models, selected artifact prefixes, one demo-state table and logs. Do not attach AdministratorAccess merely to fix a missing permission. Store no AWS secret in client-side JavaScript or public Next.js environment variables.

Configure conservative concurrency, per-run model/tool/time ceilings, max daily new runs, artifact TTL and log retention. AWS budget alerts are advisory, not immediate circuit breakers. Application gates must stop new paid dispatch before the configured limit with an explicit safety margin for in-flight usage.

## 4. AgentCore deployment

Use the current official AgentCore CLI workflow verified during G0. The current getting-started documentation describes the npm `@aws/agentcore` CLI and `agentcore deploy`, with a dry-run option; older examples use a different toolkit. Do not mix incompatible command families. Inspect installed `--help` and pin the successful tool version. [S13]

Keep the Strands supervisor module independent of its local/cloud entry point. Build the runtime for its supported architecture and startup contract. Perform a real deployed invocation, then save the sanitized runtime request/trace identifier and output-schema validation result. A successful container build alone is not a functioning cloud agent.

Persist task/demo status externally. For asynchronous work use AgentCore's documented task lifecycle and health behavior, not an untracked background thread. Rehydrate from durable state after runtime loss. A runtime's temporary filesystem is not the authoritative checkpoint store. [S14]

Provide an infrastructure plan/diff before deploying. Label resources with project, environment and expiry metadata. Avoid a VPC/NAT gateway unless a real requirement justifies its cost. Document teardown and run it on a disposable development environment before relying on it.

## 5. Public demo controls

The only public task is the packaged synthetic importer fixture. Public callers select a supported demo scenario and receive an unguessable run token. They cannot select a repository, change a command, inject a supervisor prompt, enumerate other run IDs or upload files.

Use API throttling, concurrency limits, a fixed model cap and an application circuit breaker. Hash visitor identifiers when needed for abuse control; do not add invasive tracking. A judge access code may provide a documented access path without billing, but it must not silently bypass the global spending cap.

When live capacity is exhausted, clearly offer an existing signed, sanitized recording and display its timestamp and build. The page must say `Recorded run`, not `Live`. Keep installable source/demo instructions available even if a cloud service is temporarily unavailable.

Execute generated fixture code only in dedicated AgentCore Code Interpreter sessions with verified sandbox network configuration and minimal execution-role access. Never import it into the supervisor's credentialed process. The worker's narrow tools mediate file/check operations; model calls remain outside the code session. Use a fresh session for final verification and stop sessions on completion. Sandbox mode permits some AWS connectivity, so verify permissions instead of claiming complete network isolation. [S19]

## 6. Website and intended domain

Deploy the website to a Vercel preview first. Check redirects, error pages, security headers, accessibility and signed-out navigation. Configure server-only cloud-control credentials in the hosting secret store, never in `NEXT_PUBLIC_*` variables.

Verify `dovet.site` through an actual registrar/account. If available, present the exact registration/renewal price and request purchase approval. If already owned, verify authority to edit it. If unavailable, record the blocker; do not automatically buy a premium domain or silently rename the brand. Keep the verified preview URL usable while a naming decision is pending.

Use the current Vercel CLI/domain workflow and inspect the exact DNS instructions for this project. `vercel domains inspect` and the dashboard determine the required records; do not hard-code a remembered IP or overwrite existing email records. Verify ownership, HTTPS issuance, canonical host and redirects. [S18]

Final domain checks: apex/`www` redirect behavior, TLS valid, no mixed content, sitemap canonical host, Open Graph images, robots rules and a working installation route. Document whether DNS propagation is pending instead of claiming the domain is live.

## 7. Public source and release

Create a repository only under an account/organization the owner authorizes. Add a real Apache-2.0 LICENSE from the official license text; review third-party licenses before release. Document where Codex/other AI tools assisted and what pre-existing components were used.

The README must include the user problem, short demo, architecture, prerequisites, exact setup, real credential requirements, safety limits, fixture reproduction, test commands, data flow, known integration limits and cleanup. Include a no-account replay/install path plus a genuine live path where available. Do not require judges to purchase a subscription to understand/test the core project.

Tag a stable version (for example `v0.1.0-hackathon`) only when checks pass. Package CLI/plugin assets with checksums. The website, video and submission reference this same commit. A public release is a publication event; run a secret/license scan before it and obtain approval for any private material.

## 8. Keep the judged build available

The published rules put the judging window through October 8, 2026 at 17:00 Pacific. Keep the tagged source, public video and reasonable no-cost judge access available at least through that window; recheck rules for amendments. Freeze the submitted version rather than silently replacing it with a materially different product during judging. [S02]

A spend cap should not remove the only functioning means of testing. Allocate owner-approved funds and a documented free judge access path for the judging window; keep ordinary public abuse controls separate from that access. An installable source release and accurately labelled replay are additional resources, not substitutes for promised working access. If funding/access cannot be maintained, resolve the submission-compliance gap before claiming readiness.

## 9. Owner-action boundaries

Codex can prepare commands, infrastructure, builds, recordings, metadata and forms. The owner may need to complete AWS model terms, cloud/account sign-in, OAuth consent, MFA/CAPTCHA, domain purchase, a code-signing identity, YouTube channel creation, eligibility attestations and final public submission.

When blocked, produce one exact action with the current URL/context and why it is required. Do not repeatedly retry credentials, scrape session cookies or claim to have pressed a submit button that was unavailable. Continue unrelated local work.

## 10. Release and rollback evidence

Maintain an actual `release-manifest.json`: build commit, SDK/CLI versions, schema version, installed plugin version, local test report, cloud invocation evidence, public website, source release, video URL, Devpost URL/receipt and unresolved limitations. Missing values remain null with a reason.

Rollback points: last verified website deployment, previous runtime version, previous packaged daemon and database backup before migration. Database changes must have an explicit recovery plan; do not assume destructive reverse migrations are safe. Test resource teardown separately from project-data deletion.
