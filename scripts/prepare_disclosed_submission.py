"""Prepare an upload-ready hackathon cut with the AWS blocker disclosed.

This command never converts the review edit into live recovery evidence. It copies
only a checksum-verified, visibly blocked edit to a distinct submission filename.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "private-artifacts" / "video"
SUBMISSION = ROOT / "submission" / "video"
SOURCE_MANIFEST = PRIVATE / "picture-edit-manifest.json"
OUTPUT = SUBMISSION / "dovet-submission-disclosed.mp4"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe(path: Path) -> dict[str, object]:
    result = subprocess.run(  # noqa: S603
        (
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("ffprobe failed for disclosed submission cut")
    return json.loads(result.stdout)


def main() -> int:
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    if source.get("status") != "REVIEW_ONLY_BLOCKED":
        raise RuntimeError("source edit must remain REVIEW_ONLY_BLOCKED")
    limitations = source.get("limitations")
    if not isinstance(limitations, list) or not any(
        "not live recovery evidence" in str(item) for item in limitations
    ):
        raise RuntimeError("source manifest is missing its evidence limitation")

    source_video = ROOT / str(source["path"])
    expected_digest = str(source["sha256"])
    if sha256(source_video) != expected_digest:
        raise RuntimeError("source picture-edit checksum does not match its manifest")

    SUBMISSION.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_video, OUTPUT)
    shutil.copyfile(PRIVATE / "captions.srt", SUBMISSION / "captions-disclosed.srt")
    shutil.copyfile(PRIVATE / "captions.vtt", SUBMISSION / "captions-disclosed.vtt")
    shutil.copyfile(PRIVATE / "thumbnail-blocked.png", SUBMISSION / "thumbnail-disclosed.png")

    media = probe(OUTPUT)
    streams = media.get("streams", [])
    if not isinstance(streams, list):
        raise RuntimeError("ffprobe returned an invalid stream list")
    video = next(item for item in streams if item.get("codec_type") == "video")
    audio = next(item for item in streams if item.get("codec_type") == "audio")
    duration = float(media["format"]["duration"])  # type: ignore[index]
    valid = (
        duration < 300
        and video.get("codec_name") == "h264"
        and video.get("width") == 1920
        and video.get("height") == 1080
        and audio.get("codec_name") == "aac"
        and audio.get("sample_rate") == "48000"
        and audio.get("channels") == 2
    )
    if not valid:
        raise RuntimeError("disclosed submission cut failed media requirements")

    manifest = {
        "schema_version": "1",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "READY_WITH_DISCLOSED_AWS_BLOCKER",
        "evidence_status": "BLOCKED",
        "path": str(OUTPUT.relative_to(ROOT)),
        "sha256": sha256(OUTPUT),
        "duration_seconds": duration,
        "video": {"codec": "h264", "width": 1920, "height": 1080},
        "audio": {"codec": "aac", "sample_rate": 48000, "channels": 2},
        "captions": [
            "submission/video/captions-disclosed.srt",
            "submission/video/captions-disclosed.vtt",
        ],
        "thumbnail": "submission/video/thumbnail-disclosed.png",
        "claims": {
            "managed_codex_interruption": "PASS",
            "immutable_checkpoint_and_restore": "PASS",
            "deterministic_policy_and_local_engine": "PASS",
            "strands_bedrock_invocation": "BLOCKED_ZERO_SUCCESSFUL_REQUESTS",
            "agentcore_deployment": "NOT_DEPLOYED_OPTIONAL_REQUIREMENT",
        },
        "limitations": [
            (
                "The film is suitable for an honest deadline submission, not proof of a live "
                "Bedrock recovery."
            ),
            "Cloud-dependent scenes carry a persistent AWS account-provisioning blocker label.",
            (
                "The deterministic UI fixture is a contract demonstration and recorded replay, "
                "not a live cloud run."
            ),
            (
                "The owner must listen through once and perform all public uploads and legal "
                "attestations."
            ),
        ],
    }
    manifest_path = SUBMISSION / "submission-cut-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
