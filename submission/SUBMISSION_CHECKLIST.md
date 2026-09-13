# Submission completion checklist

Checked at 2026-09-14 01:27 Cairo: **25.55 hours remained** before the September 15
03:00 Cairo deadline. Re-run `uv run python scripts/deadline_status.py` before upload.

## Working product

- PASS — local checkpoint, policy, approval, budget, lease, verifier, daemon, MCP bridge, and Codex usage code
- PASS — real managed Codex interruption and byte-identical checkpoint restore
- PASS — 54 local unit, integration, and tooling tests plus six desktop/mobile browser checks
- PASS — portable checkpoint validation and separate-directory restore
- PASS — authenticated recovery-receipt API and evidence-rail UI
- PASS — isolated wheel install, packaged migration, supervisor, and worker imports
- FAIL baseline — 13 protected importer checks before the blocked cloud recovery
- BLOCKED — successful Strands/Bedrock request; current successful provider requests: zero
- NOT DEPLOYED — AgentCore Runtime and Code Interpreter; optional for the hackathon

## Upload assets

- READY WITH DISCLOSURE — `submission/video/dovet-submission-disclosed.mp4`, 4:40, H.264/AAC, 1920x1080
- READY — `submission/video/thumbnail-disclosed.png`, 1280x720
- READY — `submission/video/captions-disclosed.srt` and `.vtt`
- READY — `submission/YOUTUBE_METADATA.json`
- READY — `submission/DEVPOST.md`
- READY — public-site source and https://dovet.site
- READY — README, Apache-2.0 license, architecture diagram, security policy, and AI/dependency disclosure
- READY AFTER LOCAL TAG — source archive and SHA-256 checksum
- READY — three Builder.aws drafts; optional bonus posts

## Owner-only completion

- Publish the source repository and `v0.1.0` tag.
- Upload the disclosed film to YouTube, set it to **Public**, add the thumbnail and English captions,
  and verify playback signed out.
- Replace the source and Devpost URL placeholders in the YouTube description.
- Confirm eligibility, authorship, contributor, third-party rights, AWS Builder ID, and legal fields.
- Submit Devpost and save the confirmation receipt.
- Optionally publish up to three Builder.aws stories after inserting the public source URL.

## Submission risk

The rules require Strands Agents for real work. The repository contains a real Strands recovery
implementation and tested deterministic boundaries, but AWS account authorization blocked every
model invocation. Submit with that limitation exactly as written. This is weaker evidence than the
intended live vertical slice, but it is an honest working-project submission and better than missing
the deadline.
