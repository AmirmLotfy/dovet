# Dovet - actual demo film production and publication

## 1. Deliverable

Make a finished **4:35-4:50 English demo**, 1920x1080, H.264/AAC MP4, with readable subtitles and a public YouTube watch URL. Leave margin below the competition's five-minute maximum. Use real screen recordings, a simple architecture diagram and neutral synthetic narration. No AI-generated pretend product footage, talking avatar, dramatic trailer, stock office scenes or decorative music is needed.

The user does not need to appear on camera. The official rules accept screen recording and voiceover. [S02] This document is a production instruction; no finished film is claimed to exist yet.

## 2. Storyboard and edit budget

| Segment | Approximate edit time | Show | Required proof |
|---|---:|---|---|
| Problem and promise | 0:00-0:22 | Actual managed task, brief brand title | Real task title, not a fabricated "live" dashboard |
| Intent and boundaries | 0:22-0:50 | Task brief, approved paths, acceptance contract | The scope really constrains the worker |
| Real interruption | 0:50-1:12 | Working Codex session, operator interruption | Owned process/turn ID; labelled demonstration fault |
| Preserve what matters | 1:12-1:43 | Snapshot, changed files, failing checks, evidence rail | Immutable manifest/source hashes |
| Strands decision | 1:43-2:12 | Evidence tools and concise decision explanation | Actual tool trace and target worker |
| Replacement work | 2:12-2:46 | Bedrock worker reads checkpoint, resumes task | New attempt ID and actual source changes |
| Independent verification | 2:46-3:16 | Actual protected test result tied to snapshot | Report and suite digest; no model-issued green badge |
| Human boundary | 3:16-3:43 | A real blocked permission/budget request | Pending approval, no mutation before approval |
| Product and architecture | 3:43-4:20 | Plugin entry, local service, AgentCore, hosted demo | Real integration status and accurate adapter labels |
| Close | 4:20-4:40 | Final verified run and source/install links | Same release tag, no invented impact metric |

Timings are an edit plan, not a requirement to make live agent work finish in those seconds. Show a clear time-compression label for shortened waiting, preserve original event times, and retain raw footage. Do not splice separate runs into one claimed uninterrupted recovery.

## 3. Recording harness

Implement `pnpm demo:record` as an orchestrated fixture runner and browser recorder. It creates a fresh fixture/worktree, starts a real managed run, subscribes to real events and opens the actual local console. Use stable `data-testid` hooks for navigation, not brittle text coordinates.

Set both the Playwright viewport and video size explicitly to 1920x1080; default recording dimensions can be smaller. Close the browser context so the video is finalized before rendering. [S15]

Wait on backend states and event IDs, not fixed sleeps pretending to represent completion. The fault trigger targets only the owned demonstration worker. Before rendering, reconcile the captured run ID, checkpoint digest, replacement attempt and final test report against the recording manifest.

Capture the genuine Codex -> Bedrock local path. A hosted fixture may use Bedrock -> Bedrock for no-account judge testing; label that accurately. Do not display Codex's logo over a different runtime. Do not show full personal desktop screens, account menus, local home paths containing private identifiers, AWS secrets or internal company code.

Use browser capture for the console. For terminal details, render real sanitized event output in the console's evidence drawer or use a terminal recorder tied to the same run. Do not reconstruct a fictitious transcript as a real recording.

## 4. Narration pipeline

Generate the narration from `NARRATION.md` after the actual build and recording pass. Edit unsupported feature sentences out. Insert measured counts only by reading the verified manifest. The script remains understandable without performance numbers.

Use Amazon Polly with an actually supported English voice/engine discovered by `DescribeVoices`, subject to the owner's usage approval. A neutral voice at a natural pace is sufficient. Do not imitate a real named person's voice. Generate speech marks for sentence/word timing where supported, then align subtitles to the edited scene schedule. [S16]

Cache audio by script/voice/engine hash to avoid paying again for unchanged scenes. Each scene has its own WAV/MP3 and metadata. If credentials are unavailable, produce a clean record-yourself script and list the precise blocked step; do not pretend text is a completed audio asset.

Do not overlap narration with spoken audio from the coding host. Keep incidental system sounds muted. Target comfortable consistent speech loudness and listen to the result; normalization alone does not catch awkward pronunciation, clipped syllables or a missing sentence.

## 5. Editing/rendering pipeline

Implement `pnpm video:render` using FFmpeg or an equivalent local reproducible render script. Inputs are genuine captured clips, actual architecture artwork, narration, subtitles and a scene manifest. No external paid video generator is necessary.

Crop/reframe only to improve legibility, never to hide an error while claiming success. Keep actions large enough to read at 1080p. Use restrained cuts and short fades; no constant camera zoom, glitch transitions or excessive callouts.

Output:

```text
submission/video/
  dovet-demo.mp4
  captions.srt
  captions.vtt
  thumbnail.png
  youtube-metadata.json
  recording-manifest.json
  QA_REPORT.md
private-artifacts/video/
  raw/*.webm
  audio/*
  timing/*.json
  event-trace.jsonl
```

The manifest records release commit, fixture hash, actual run IDs, scene source ranges, accelerated portions, tool versions, media checksums and narration hash. Keep raw potentially private captures out of the public repository; publish only reviewed synthetic evidence.

The thumbnail is a real console screenshot with **KEEP THE WORK.** as the primary line and a small Dovet wordmark. Use the oxide/paper palette, no robotic face, lightning bolt, fake award or "#1" claim. Produce a 1280x720 image as a broadly compatible target and verify the platform's current upload limits before publishing.

## 6. Automated and human media checks

Use `ffprobe` to reject missing video/audio, wrong dimensions and duration at or above 300 seconds. Confirm subtitles do not exceed video duration, the first/last frames are not accidentally blank, and timestamps are monotonic. Check rendered scene lengths against the planned voiceover.

Run OCR only as a last resort; prefer DOM/source log secret scanning and manual viewing of the final frames. Watch the final movie at normal speed. Check public readability at ordinary player size, pronunciation of Dovet/Strands/Codex, audio continuity, truthful cut labels and absence of secrets. Owner approval follows this QA, not merely a successful render exit code.

## 7. YouTube title and metadata

**Title:** Dovet - Keep the work. Change the agent. | Agents for Humans

**Description template, completed from the release manifest:**

```text
Dovet helps developers recover interrupted managed coding-agent work.
This demo shows a real interrupted run, preserved working state,
Strands-supervised recovery and independent verification.

Project: {verified_public_site}
Source and setup: {verified_public_release}
Hackathon submission: {verified_devpost_url_when_available}

Built for Agents for Humans, Professional Agents.

This demonstration uses synthetic code and an intentionally triggered
interruption. Hosted and local adapter differences are labelled in the video.
Narration is generated with an authorized synthetic voice.

Chapters:
{derive_chapters_from_final_edit}
```

Do not publish unresolved braces, fake links, unsupported results or chapters from an obsolete edit. Audience/age-related platform settings require the owner's truthful determination. No children appear or are targeted by this developer-tool video, but Codex should not make legal declarations without owner review.

## 8. Upload/publication workflow

A valid automated upload uses the owner's authorized YouTube OAuth credentials and appropriate upload scope. Create the upload draft, attach metadata/subtitles/thumbnail and request final publication approval. Never ask the user to paste a Google account password into a script.

**Important:** Google restricts uploads from certain unaudited API projects to private visibility. Therefore a new YouTube API project is not a guaranteed route to the required public video. Verify the actual channel/project state. When restricted, use the ordinary authorized YouTube Studio flow in a supported browser, or have the owner upload the finished MP4 and supplied metadata. Do not attempt to bypass the audit restriction. [S17]

The final video must be **Public**, not merely Unlisted. Verify playback signed out, HD processing, caption availability and the actual watch URL. Save the verification timestamp in `links.json`. An uploaded private draft is not submission-ready.

Domain purchase, CAPTCHA/MFA, OAuth consent, final legal attestations and public publication can require the owner. Codex should pause only for the exact blocked action and continue local media preparation where possible.

## 9. Completion condition

Video work is complete only when the rendered film passes QA, the owner approves it, the actual public URL plays signed out and that URL is attached to the verified Devpost submission. Otherwise report the precise remaining stage: recorded, rendered, approved, uploaded-private, processing, public or submitted.
