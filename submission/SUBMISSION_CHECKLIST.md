# Dovet submission checklist

Status: **OWNER READY WITH DISCLOSED AWS BLOCKER**

## Verified build

- PASS — 54 Python unit, integration, and tooling tests.
- PASS — TypeScript checks, package tests, and production builds.
- PASS — six normal desktop/mobile browser checks plus four 1920x1080 real-footage recording checks.
- PASS — real Dovet-managed Codex interruption and byte-identical checkpoint restore.
- PASS — immutable portable bundle, single-writer policy, durable daemon, and independent verification controls.
- BLOCKED — zero successful Bedrock requests; no live Strands recovery claim.
- NOT DEPLOYED — AgentCore runtime; no hosted recovery claim.

## Owner upload set

- READY — `submission/video/dovet-submission-final-disclosed.mp4`, 2:57.255, H.264/AAC, 1920x1080.
- READY — `submission/video/thumbnail-final.png`, 1280x720.
- READY — `submission/video/captions-final.srt` and `.vtt`.
- READY — `submission/YOUTUBE_METADATA.json`.
- READY — `submission/DEVPOST.md` and `submission/TESTING_INSTRUCTIONS.md`.
- READY — architecture diagram, Apache-2.0 license, AI/dependency disclosure, and three Builder.aws drafts.
- READY AFTER TAG — source archive, checksum, and owner upload ZIP.

## Owner-only completion

- Publish the source repository and immutable `v0.1.1` tag.
- Upload the video, thumbnail, and captions to YouTube; set visibility to **Public** and verify signed out.
- Replace the public source and Devpost URL placeholders.
- Complete eligibility, authorship, contributor, rights, AWS Builder ID, and legal fields personally.
- Submit Devpost and save the confirmation receipt and public URL.

## Required limitation

> AWS account provisioning blocked all Bedrock text-model invocations before submission. The Strands recovery integration is implemented, but this build records zero successful provider requests and does not claim a live Bedrock recovery or AgentCore deployment.
