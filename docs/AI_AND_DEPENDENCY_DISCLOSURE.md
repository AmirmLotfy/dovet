# AI and dependency disclosure

OpenAI Codex assisted with implementation, research, testing, documentation, and preparation of
submission materials. No hidden chain-of-thought is stored in Dovet checkpoints or evidence.

The product uses the open-source packages pinned in `uv.lock`, `pnpm-lock.yaml`, and
`apps/site/package-lock.json`. Runtime components include the Strands Agents SDK, AWS SDK for
Python, Amazon Bedrock AgentCore SDK, FastAPI, Pydantic, SQLite, React, Vite, and Next.js. Test and
production tooling includes pytest, Playwright, axe, FFmpeg, Ruff, mypy, and TypeScript.

Emergit was reviewed as a separate pre-existing local recovery project. Dovet independently
implements compatible safety ideas: credential and build-output omission, preservation of the last
verified checkpoint after a failed capture, conservative Codex usage states, and portable recovery
into a separate directory. Dovet's archive format and validator were independently implemented. No
Emergit source code or product assets were copied into Dovet. Dovet does not adopt Emergit account
association, cooldown hooks, or arbitrary-session behavior.

The owner must confirm project authorship, eligibility dates, contributor identities, and final
third-party disclosures before public submission. This file does not make those legal attestations.
