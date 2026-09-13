"""Render a short, explicitly non-evidentiary preview of the Dovet film direction."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "private-artifacts" / "video"
EVIDENCE = ROOT / "artifacts" / "higgsfield-media-evidence.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(argv: tuple[str, ...]) -> None:
    result = subprocess.run(argv, capture_output=True, text=True, check=False)  # noqa: S603
    if result.returncode != 0:
        lines = result.stderr.strip().splitlines()
        detail = lines[-1] if lines else "unknown error"
        raise RuntimeError(
            f"{Path(argv[0]).name} failed while rendering the style preview: {detail}"
        )


def main() -> int:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    opener = PRIVATE / "higgsfield" / "dovet-opening-05e03908.mp4"
    voice = PRIVATE / "higgsfield" / "voice-01-d735e7fd.wav"
    screenshot = ROOT / "artifacts" / "site-updated-desktop.png"
    bed = PRIVATE / "sound" / "dovet-bed.wav"
    for path in (opener, voice, screenshot, bed):
        if not path.is_file():
            raise FileNotFoundError(path)
    if sha256(opener) != evidence["opening"]["sha256"]:
        raise ValueError("Higgsfield opener checksum changed")
    if sha256(voice) != evidence["narration_audition"]["sha256"]:
        raise ValueError("Higgsfield voice checksum changed")

    output = PRIVATE / "dovet-style-preview.mp4"
    video_filter = (
        "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
        "setsar=1,fps=30[v0];"
        "[1:v]scale=1920:-2,crop=1920:1080:0:0,"
        "zoompan=z='min(zoom+0.00035,1.025)':d=90:s=1920x1080:fps=30,"
        "setsar=1[v1];"
        "[v0][v1]xfade=transition=fade:duration=0.8:offset=5.2[base];"
        "[4:v]format=rgba[label];[base][label]overlay=0:996[v]"
    )
    audio_filter = (
        "[2:a]adelay=250|250,loudnorm=I=-16:TP=-1.5:LRA=7,"
        "aformat=channel_layouts=stereo[voice];"
        "[3:a]atrim=duration=8.6,volume=0.12,afade=t=out:st=7.6:d=1[bed];"
        "[voice][bed]amix=inputs=2:duration=longest:dropout_transition=1[a]"
    )
    with tempfile.TemporaryDirectory(prefix="dovet-style-preview-") as temporary:
        label = Path(temporary) / "label.png"
        run(
            (
                "magick",
                "-size",
                "1920x84",
                "xc:#171512",
                "-font",
                "Helvetica",
                "-fill",
                "#f3efe6",
                "-pointsize",
                "26",
                "-gravity",
                "west",
                "-annotate",
                "+52+0",
                "PRODUCTION LOOK TEST  •  NOT RECOVERY EVIDENCE",
                str(label),
            )
        )
        run(
            (
            "ffmpeg",
            "-y",
            "-i",
            str(opener),
            "-loop",
            "1",
            "-t",
            "3.4",
            "-i",
            str(screenshot),
            "-i",
            str(voice),
            "-i",
            str(bed),
            "-loop",
            "1",
            "-i",
            str(label),
            "-filter_complex",
            f"{video_filter};{audio_filter}",
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-t",
            "8.6",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            str(output),
            )
        )
    report = {
        "schema_version": "1",
        "status": "PASS",
        "kind": "production_look_test_not_recovery_evidence",
        "path": str(output.relative_to(ROOT)),
        "sha256": sha256(output),
        "duration_seconds": 8.6,
        "width": 1920,
        "height": 1080,
        "publication": "OWNER_ACTION",
    }
    (ROOT / "artifacts" / "video-style-preview.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
