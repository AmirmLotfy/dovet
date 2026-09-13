# Implementation decisions

## D-001 — Compatible MCP line

Pin MCP 2.1.1. Strands 1.55.1 requires MCP below 2.2; MCP 2.x exposes `MCPServer` instead of `FastMCP`.

## D-002 — Local Python package

Use one distributable Python package containing daemon, supervisor and restricted-worker modules. This keeps one lockfile while retaining process and trust boundaries.

## D-003 — AgentCore protocol

Use authenticated HTTP on port 8080 for the typed recovery-decision runtime. It fits the request/response supervisor and supports `/ping` plus `/invocations` without exposing its evidence tools as a public MCP surface.

## D-004 — Budget

The owner approved a $50 aggregate planning ceiling through the judging period. Every paid invocation must reserve from the local micro-USD ledger. Infrastructure deployment still requires review of the concrete resource plan.
# Dovet implementation decisions

## TypeScript compiler compatibility

The initial dependency audit found TypeScript 7.0.2, but the pinned OpenAPI generator
`openapi-typescript==7.13.0` fails during module initialization against that compiler API.
Dovet therefore pins TypeScript 5.9.3 across the workspace. This keeps generated API
contracts reproducible and avoids hand-maintained duplicate request and response types.

## D-006 — AWS login credential provider

AWS CLI 2.36.29 authenticated with `aws login`, but botocore 1.43.93 rejected that
credential provider until its CRT extra was installed. Dovet pins
`botocore[crt]==1.43.93` beside boto3 so the Python SDK can use the same short-lived login
session without copying CLI cache data or introducing long-lived access keys.

## D-007 — Emergit safety ideas adapted to Dovet

The separate pre-existing Emergit project was reviewed for recovery failure modes. Dovet
independently implements three compatible behaviors: explicit credential/build/VCS omissions,
retention and validation of the prior ready checkpoint when a newer capture fails, and conservative
Codex usage states with preservation thresholds. These do not introduce account rotation, auth-file
access, arbitrary-session interruption, or Emergit's plugin-lifetime architecture. No Emergit source
or assets were copied.

## D-008 — Codex path in the durable LaunchAgent

Interactive usage reads passed while the launchd service initially returned unavailable because its
default PATH could not find Codex. Service installation now resolves Codex through the authenticated
interactive environment and stores that non-secret executable path as DOVET_CODEX_BIN in the
LaunchAgent. The restarted daemon returned a known usage window through its authenticated loopback
API.
