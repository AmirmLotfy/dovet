"""Verify and package the exact owner-upload set without publishing it."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
VIDEO = ROOT / "submission" / "video"
MANIFEST = VIDEO / "final-film-manifest.json"

DELIVERY_FILES = (
    "submission/video/dovet-submission-final-disclosed.mp4",
    "submission/video/thumbnail-youtube-4k.png",
    "submission/video/thumbnail-youtube-1280.png",
    "submission/gallery/dovet-devpost-cover-3x2.png",
    "submission/video/captions-final.srt",
    "submission/video/captions-final.vtt",
    "submission/video/final-film-manifest.json",
    "submission/video/DISCLOSED_QA_REPORT.md",
    "submission/YOUTUBE_METADATA.json",
    "submission/DEVPOST_FORM_COPY.md",
    "submission/DEVPOST.md",
    "submission/BUILDER_ARTICLE_FINAL.md",
    "submission/TESTING_INSTRUCTIONS.md",
    "submission/SUBMIT_NOW.md",
    "submission/OWNER_CONFIRMATIONS.md",
    "submission/BUILDER_STORIES.md",
    "submission/BUILD_DISCLOSURE.md",
    "submission/architecture.png",
    "submission/architecture.svg",
    "docs/architecture.svg",
    "docs/BUILD_STATE.md",
    "docs/BLOCKERS.md",
    "docs/CAPABILITIES.md",
    "README.md",
    "LICENSE",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path) -> dict[str, object]:
    result = subprocess.run(  # noqa: S603
        ("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("ffprobe failed for final submission cut")
    return cast(dict[str, object], json.loads(result.stdout))


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    video_path = ROOT / str(manifest["path"])
    if sha256(video_path) != manifest["sha256"]:
        raise RuntimeError("final film checksum does not match its manifest")
    media = probe(video_path)
    streams = media.get("streams")
    if not isinstance(streams, list):
        raise RuntimeError("ffprobe returned invalid streams")
    video = next(item for item in streams if item.get("codec_type") == "video")
    audio = next(item for item in streams if item.get("codec_type") == "audio")
    seconds = float(media["format"]["duration"])  # type: ignore[index]
    valid = (
        174 <= seconds < 180
        and video.get("codec_name") == "h264"
        and video.get("width") == 1920
        and video.get("height") == 1080
        and audio.get("codec_name") == "aac"
        and audio.get("sample_rate") == "48000"
        and audio.get("channels") == 2
    )
    if not valid:
        raise RuntimeError("final film failed the three-minute media contract")

    archives = sorted(
        ARTIFACTS.glob("dovet-source-*.tar.gz"), key=lambda item: item.stat().st_mtime
    )
    if not archives:
        raise RuntimeError("run pnpm release:package after tagging the committed tree")
    source = archives[-1]
    checksum = source.with_suffix(source.suffix + ".sha256")
    expected = checksum.read_text(encoding="utf-8").split()[0]
    if sha256(source) != expected:
        raise RuntimeError("source archive checksum is invalid")

    commit = subprocess.run(
        ("git", "rev-parse", "--short=12", "HEAD"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    bundle = ARTIFACTS / f"dovet-owner-upload-{commit}"
    if bundle.exists():
        raise RuntimeError(f"owner bundle already exists: {bundle.name}")
    bundle.mkdir(parents=True)
    for relative in DELIVERY_FILES:
        source_file = ROOT / relative
        if not source_file.is_file():
            raise FileNotFoundError(f"delivery file is missing: {relative}")
        target = bundle / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target)
    shutil.copy2(source, bundle / source.name)
    shutil.copy2(checksum, bundle / checksum.name)
    (bundle / "START-HERE.txt").write_text(
        "DOVET OWNER UPLOAD PACK\n\n"
        "1. Read submission/SUBMIT_NOW.md.\n"
        "2. Watch submission/video/dovet-submission-final-disclosed.mp4.\n"
        "3. Upload the video, thumbnail, and captions yourself.\n"
        "4. Publish the source and fill Devpost using the supplied copy.\n"
        "5. Preserve the AWS blocker disclosure.\n",
        encoding="utf-8",
    )
    archive_path = Path(shutil.make_archive(str(bundle), "zip", root_dir=bundle))
    digest = sha256(archive_path)
    archive_path.with_suffix(archive_path.suffix + ".sha256").write_text(
        f"{digest}  {archive_path.name}\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "bundle": str(archive_path.relative_to(ROOT)),
                "sha256": digest,
                "duration_seconds": seconds,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
