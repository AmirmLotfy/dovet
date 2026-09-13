# Dovet owner delivery index

Codex performs no upload, submission, public repository creation, DNS change, or legal acceptance.

| Owner task | File | Status |
|---|---|---|
| Watch and upload the film | `submission/video/dovet-submission-disclosed.mp4` | READY WITH AWS DISCLOSURE |
| Upload thumbnail | `submission/video/thumbnail-disclosed.png` | READY |
| Upload English captions | `submission/video/captions-disclosed.srt` | READY |
| Copy YouTube title, description, chapters | `submission/YOUTUBE_METADATA.json` | READY; replace URL placeholders |
| Copy Devpost narrative | `submission/DEVPOST.md` | READY |
| Follow exact order | `submission/SUBMIT_NOW.md` | READY |
| Publish source archive | `artifacts/dovet-source-<commit>.tar.gz` | GENERATED AFTER LOCAL TAG |
| Verify source checksum | matching `.sha256` file | GENERATED AFTER LOCAL TAG |
| Supply judge setup | `submission/TESTING_INSTRUCTIONS.md` | READY |
| Review architecture | `docs/architecture.svg` | READY |
| Publish optional build posts | `submission/BUILDER_STORIES.md` | READY WITH DISCLOSURES |
| Complete legal fields | `submission/OWNER_CONFIRMATIONS.md` | OWNER ONLY |

The upload video intentionally remains named `dovet-submission-disclosed.mp4`. The absent
`dovet-demo.mp4` remains the evidence-gated live-recovery output, preventing the AWS block from being
mistaken for a passed provider integration.
