# Judge testing instructions

Dovet runs locally on macOS. The public site and recorded replay cannot control the judge's machine.

## Prerequisites

- Python 3.12
- uv
- Node.js 24
- pnpm 11
- Git
- FFmpeg

An authenticated Codex installation is needed only for the managed Codex probe and live usage read.
AWS credentials are not required for the local test suite.

## Install and test

```sh
git clone https://github.com/AmirmLotfy/dovet.git
cd dovet
pnpm setup
pnpm doctor
pnpm check
pnpm test
pnpm build
pnpm test:e2e
```

Expected submitted-build evidence:

- 54 Python unit, integration, and tooling tests pass.
- TypeScript package tests and builds pass.
- Six normal desktop/mobile browser checks pass. Four separate 1920x1080 story-recording checks capture the actual local console and website. The evidence-gated live-recovery recorder remains skipped without a validated receipt.
- A fresh Python 3.12 install imports the packaged Strands supervisor and restricted worker and runs
  the packaged database migration.
- `pnpm release:check` returns **BLOCKED**, by design, because the submitted build has zero successful
  Bedrock requests, no evidence-gated `dovet-demo.mp4`, no public-source receipt inside the local
  checkout, and no Devpost receipt.

## Inspect the working local features

```sh
uv run dovet doctor
uv run dovet usage --json
uv run dovet bundle verify /path/to/checkpoint.dovet
uv run dovet bundle restore /path/to/checkpoint.dovet --to /new/empty/directory
```

The local daemon binds to loopback and stores its append-only ledger and immutable artifacts in the
owner's application-data directory. `dovet service install` is opt-in and is not required for tests.

## Current cloud limitation

AWS account provisioning blocked all Bedrock text-model invocations before submission. Agreement,
entitlement, region, and model discovery passed, while authorization stayed `NOT_AUTHORIZED`; direct
and Strands requests returned `ValidationException: Operation not allowed`. The submitted evidence
records zero successful provider requests. AgentCore was not deployed. Do not expect the live marked
test to pass without an independently authorized and budget-approved AWS account.
