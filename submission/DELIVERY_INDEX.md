# Dovet owner delivery index

Codex performs no upload, submission, public repository creation, DNS change, or legal acceptance.
This index separates the files available for review now from the final owner upload set.

## Available now

| Item | Path | Status |
|---|---|---|
| Marketing and docs source | `apps/site/` | PASS locally; owner deploys |
| Updated desktop capture | `artifacts/site-updated-desktop.png` | PASS |
| Updated mobile capture | `artifacts/site-updated-mobile.png` | PASS |
| Browser QA report | `artifacts/site-updated-verification.json` | PASS |
| Higgsfield production record | `submission/video/HIGGSFIELD_PRODUCTION.md` | TIMING PASS; owner listening pending |
| Higgsfield look test | `private-artifacts/video/dovet-style-preview.mp4` | PASS; not recovery evidence |
| Dylan voice audition | `private-artifacts/video/higgsfield/voice-01-d735e7fd.wav` | Timing PASS; owner listening review pending |
| Complete narration review | `private-artifacts/video/higgsfield/dovet-narration-review.wav` | 12 timing-gated scenes; owner listening review pending |
| Review-only 4:40 picture edit | `private-artifacts/video/dovet-picture-edit-blocked.mp4` | Clearly labelled BLOCKED; not recovery evidence |
| Devpost draft | `submission/DEVPOST.md` | PREPARED |
| Builder.aws drafts | `submission/BUILDER_STORIES.md` | PREPARED |
| YouTube metadata | `submission/YOUTUBE_METADATA.json` | PREPARED; final URLs/chapters pending |
| Owner action order | `submission/OWNER_ACTIONS.md` | PREPARED |

## Final owner upload set

These paths become release artifacts only after the live recovery receipt and protected tests pass:

| Item | Expected path |
|---|---|
| Public source archive | `artifacts/dovet-source-<commit>.tar.gz` |
| Source checksum | `artifacts/dovet-source-<commit>.tar.gz.sha256` |
| Final H.264/AAC film | `submission/video/dovet-demo.mp4` |
| YouTube thumbnail from app footage | `submission/video/thumbnail.png` |
| Captions | `submission/video/captions.srt` and `submission/video/captions.vtt` |
| Video QA | `submission/video/QA_REPORT.md` |
| Evidence-bound recording manifest | `submission/video/recording-manifest.json` |
| Release evidence | `artifacts/release-evidence.json` |

The remaining technical prerequisite is account authorization for Amazon Nova Micro in Bedrock
`us-east-1`. After the owner reviews and enables the model terms, rerun the bounded live vertical.
The render pipeline checks the receipt lineage and every media checksum before it can create the
final film.
