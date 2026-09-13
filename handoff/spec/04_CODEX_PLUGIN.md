# 04 - Codex integration and plugin

## 1. Correction and capability boundary

OpenAI documents `account/rateLimits/read` and `account/rateLimits/updated` in the Codex app-server API. The earlier conversational claim that no supported local usage interface exists was too broad. Use the documented authenticated interface when the installed runtime exposes it; this is not a public endpoint for interrogating arbitrary accounts. [S04]

Codex also exposes managed thread/turn operations and SDKs. Dovet may control the app-server/runtime instances and threads it creates or is explicitly granted through supported mechanisms. It must not attach to undocumented Desktop sockets, modify private session databases, manipulate `auth.json`, or assume the Desktop app shares control endpoints with a new app-server process.

## 2. Initial supported adapter matrix

| Adapter | Capture | Stop | Resume/handoff | Quota |
|---|---|---|---|---|
| Managed Codex SDK/app-server | Structured events and explicit context | Owned thread/turn only | Same-runtime resume or portable checkpoint to another worker | Supported active-account limits when available |
| Bedrock Strands worker | Typed tool events | Owned process/task | New worker from Dovet checkpoint | Dovet cost ledger, not fictitious subscription percentage |
| Existing unowned Codex Desktop thread | Scoped files + explicit plugin summary | No automatic process control | Manual handoff proposal | No assumed desktop session introspection |
| Other hosts | Unsupported until conformance-tested | Unsupported | Checkpoint export only | Unknown |

Do not put Claude Code, Gemini CLI, Kiro or other logos in a supported-integrations strip unless the actual adapter passes conformance. A future MCP-capable host may consume Dovet tools, but that does not imply full run-control compatibility.

## 3. Version/capability probe

Capture `codex --version` and SDK version. Prefer the official Python SDK where its supported interface covers the needed operations. If a lower-level method is needed, generate and inspect the schema for the exact installed runtime:

```sh
codex app-server generate-json-schema --out artifacts/codex-schema
codex app-server generate-ts --out artifacts/codex-types
```

Use generated field shapes and method contracts, not examples copied across versions. Initialize the app-server connection according to its documented handshake; obtain capability information. Smoke-test read account state, create a harmless thread, start/interrupt a safe turn, persist its thread ID, resume it, and read usage if supported. Test error paths without leaking credentials. [S04, S05]

The adapter reports capabilities individually: `managed_start`, `structured_events`, `graceful_interrupt`, `same_provider_resume`, `rate_limits`, `safe_config_overrides`. Missing capability disables only the corresponding UI/action.

## 4. Usage normalization

Maintain one row per returned limit/window. Store `limitId`, `windowDurationMins`, `usedPercent`, `resetsAt` and observation time where returned. Calculate remaining as `max(0, 100-usedPercent)` only for a valid known sample. Do not hard-code primary = daily or secondary = weekly. Label actual durations, such as 5-hour or 7-day only when the returned minutes justify that label.

The threshold is `remaining <= 5` for any applicable known window selected by policy. Prefer pushed updates, refresh on startup/explicit request and conservatively while a managed run is active. Do not aggressively poll idle accounts. Display stale state after the configured freshness window, initially 120 seconds. No automatic quota-based switch on a stale or unknown reading.

At threshold, schedule a checkpoint at the next safe boundary, not an immediate kill mid-file. Recheck allowed fallback and budget. If no permitted fallback exists, preserve and pause. Codex allowance is not spendable money, and AWS credits are not a second Codex account.

## 5. Plugin form factor

The package supplies instructions and MCP tools; it is not a privileged Codex host extension. The independent service must already be installed and explicitly enabled. The bridge reconnects to that service and returns structured status/errors. It does not silently install a login service or begin background activity on first mention.

Current OpenAI documentation supports portable root `plugin.json` and `mcp.json` packages; the legacy `.codex-plugin/plugin.json` layout remains a compatibility option. Use the current `@plugin-creator` workflow if available in the target Codex environment, or follow the documented schemas. Do not publish using app-server plugin installation methods that the docs mark under development. [S06]

Target source layout:

```text
plugins/dovet/
  plugin.json
  mcp.json
  skills/dovet/SKILL.md
  assets/                 # original icons only
  README.md
```

Build the exact skill and manifest during implementation using the installed authoring tools and validated schema. The handoff is not itself an installable plugin. Prefer local/repository marketplace distribution for the hackathon. Public directory approval is a separate process and must not be promised by the deadline.

A compatibility manifest is allowed only when the target version requires it. Keep generated schemas and a packaging test in the repo. No invented `@Dovet` UI widget API: mentions invoke the plugin's actual skill/tool workflow.

## 6. Proposed MCP tools

All names here are our own interface contracts, not claims that Codex ships these tools.

| Tool | Purpose | Mutation policy |
|---|---|---|
| `dovet_status` | Current project/run, evidence freshness, known usage | Read-only |
| `dovet_list_projects` | Registered allowed projects | Read-only, no filesystem exploration |
| `dovet_get_run` | Run receipt/events with pagination | Read-only |
| `dovet_checkpoint` | Request safe snapshot for a registered owned run | Policy-gated; returns operation ID |
| `dovet_share_context` | Add concise user-visible objective/decisions | Explicit reported provenance |
| `dovet_start_managed_run` | Start a preapproved task using selected connection | Budget/scope confirmation |
| `dovet_request_recovery` | Evaluate recovery for an interrupted run | Cannot grant its own approval |
| `dovet_pause_run` | Pause only a Dovet-owned worker | Explicit operator action |
| `dovet_export_handoff` | Create redacted local export | Data-sharing/export confirmation |
| `dovet_open_console` | Return safe loopback navigation route | No auth secret in URL |

No `execute_shell`, `read_any_file`, `switch_account`, `get_cookies`, `approve_anything`, `dump_environment` or unrestricted cloud-download tool.

## 7. Skill behavior specification

When asked to protect work, the skill distinguishes existing observed work from a new managed task. It asks the daemon for project state before suggesting a path. It never says "protection enabled" until the daemon confirms policy approval and supported capabilities. It can summarize visible context, but must mark it reported rather than independently observed.

The skill must not collect passwords or ask users to paste tokens into chat. It directs connection setup to the OS/provider's authentication flow. The plugin cannot safely grant its own recovery approval; approval comes from the authenticated local console or explicit owner action with the exact bound proposal.

Uninstalling/disabling the plugin does not implicitly delete checkpoints or kill independent background work. Present that distinction and provide a deliberate daemon shutdown command.

## 8. Adapter conformance tests

Every supported adapter must pass: healthy start, event ordering, explicit cancellation, unexpected termination, recoverable failure, typed authentication failure, identifier persistence, source privacy, old-worker termination verification, budget denial, incomplete snapshot and repeated dispatch idempotency.

A conformance report includes runtime/SDK versions, platform, tested auth mode, date, limitations and observed request IDs. Its public version removes personal account identifiers.
