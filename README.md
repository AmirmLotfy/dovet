# Dovet

**Keep the work. Change the agent.**

Dovet is a local-first supervisor for recovering interrupted, explicitly managed coding-agent work. It preserves selected working state, asks a Strands agent for a bounded recovery recommendation, enforces permissions and budget in deterministic code, starts an authorized replacement worker, and independently verifies the result.

Dovet does not rotate ChatGPT accounts, recover private model reasoning, capture unsaved editor bytes, control arbitrary Codex Desktop sessions, or promise execution while a local machine sleeps.

The implementation is being built against the immutable specification in `handoff/`. Current evidence and blockers live in `docs/BUILD_STATE.md`, `docs/CAPABILITIES.md`, and `docs/BLOCKERS.md`.

## Development

Prerequisites: Python 3.12, uv, Node 24, pnpm 11, Git, and FFmpeg.

```sh
pnpm setup
pnpm doctor
pnpm test
pnpm build
```

Live-provider tests are opt-in and require an approved Dovet policy and funded budget:

```sh
pnpm test:integration
```

The local daemon binds to loopback, stores operational truth in SQLite, and uses a separate app-data directory for immutable artifacts and managed worktrees. The Codex plugin is a short-lived MCP bridge; it is not the durability layer.

## License

Apache-2.0. See `LICENSE` and `NOTICE`.

