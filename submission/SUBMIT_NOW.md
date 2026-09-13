# Submit Dovet now

The deadline is September 15, 2026 at 03:00 Cairo. Run
`uv run python scripts/deadline_status.py` for the current clock.

## 1. Publish source

Create a public GitHub repository named `dovet` and publish the prepared local branch and tag. The
release must remain Apache-2.0 licensed. Add the generated source archive and `.sha256` checksum to
the GitHub release if convenient; the public Git tree and tag are the required source route.

Verify signed out:

- the repository opens without authentication;
- `README.md`, `LICENSE`, `docs/architecture.svg`, and setup commands are visible;
- tag `v0.1.0` points to the submitted source commit.

## 2. Upload the film

Upload `submission/video/dovet-submission-disclosed.mp4` in YouTube Studio. Use
`submission/video/thumbnail-disclosed.png`, add `submission/video/captions-disclosed.srt` as English
captions, and copy the title, description, and chapters from `submission/YOUTUBE_METADATA.json`.

Set visibility to **Public**. Open the final watch URL in a signed-out window and confirm the video,
thumbnail, captions, audio, and 4:40 duration. Do not use Unlisted for the final entry.

## 3. Complete Devpost

Use these exact high-level fields:

- Project: **Dovet**
- Tagline: **Keep the work. Change the agent.**
- Track: **Agents for Humans — Professional Agents**
- Website: **https://dovet.site**
- Source: the public GitHub repository URL
- Video: the public YouTube watch URL
- Description: `submission/DEVPOST.md`
- Testing instructions: `submission/TESTING_INSTRUCTIONS.md`
- Architecture: `submission/architecture.png` or `submission/architecture.svg`

Enter your AWS Builder ID. Personally review and accept only the eligibility, ownership,
contributor, third-party rights, and legal statements that are true for you. Save a screenshot or
PDF of the confirmation receipt and the final public entry URL.

## 4. Preserve the AWS disclosure

Use this sentence wherever the form has a limitations or testing field:

> AWS account provisioning blocked all Bedrock text-model invocations before submission. The
> Strands recovery integration is implemented, but this build records zero successful provider
> requests and does not claim a live Bedrock recovery or AgentCore deployment.

## 5. Optional bonus posts

Publish up to three Builder.aws drafts from `submission/BUILDER_STORIES.md` only after replacing
source placeholders and preserving each draft's evidence status. Add the resulting public URLs to
the Devpost entry if the form permits edits before the deadline.
