"""Assemble evidence-linked screen recordings, Polly audio, captions, and QA evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission" / "video"


def run(argv: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(argv, capture_output=True, text=True, check=False)  # noqa: S603
    if result.returncode != 0:
        raise RuntimeError(f"{Path(argv[0]).name} failed")
    return result


def probe(path: Path) -> dict[str, Any]:
    result = run(
        (
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        )
    )
    return json.loads(result.stdout)


def duration(path: Path) -> float:
    data = probe(path)
    return float(data["format"]["duration"])


def clock(seconds: float, *, vtt: bool = False) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1_000)
    separator = "." if vtt else ","
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{milliseconds:03d}"


def sentence_marks(path: Path) -> list[tuple[float, str]]:
    marks: list[tuple[float, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = json.loads(line)
        if value.get("type") == "sentence":
            marks.append((float(value["time"]) / 1000, str(value["value"]).strip()))
    if not marks:
        raise ValueError(f"no sentence speech marks in {path.name}")
    return marks


def write_captions(items: list[tuple[float, float, str]]) -> None:
    srt: list[str] = []
    vtt = ["WEBVTT", ""]
    for index, (start, end, text) in enumerate(items, start=1):
        srt.extend([str(index), f"{clock(start)} --> {clock(end)}", text, ""])
        vtt.extend([f"{clock(start, vtt=True)} --> {clock(end, vtt=True)}", text, ""])
    (OUTPUT / "captions.srt").write_text("\n".join(srt), encoding="utf-8")
    (OUTPUT / "captions.vtt").write_text("\n".join(vtt), encoding="utf-8")


def normalize_scene(clip: Path, audio: Path, output: Path) -> None:
    video_filter = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#171512,"
        "setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=300"
    )
    run(
        (
            "ffmpeg",
            "-y",
            "-i",
            str(clip),
            "-i",
            str(audio),
            "-filter_complex",
            f"[0:v]{video_filter}[v]",
            "-map",
            "[v]",
            "-map",
            "1:a:0",
            "-shortest",
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
            "160k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            str(output),
        )
    )


def make_thumbnail(video: Path, output: Path) -> None:
    font = Path("/System/Library/Fonts/Helvetica.ttc")
    if not font.exists():
        raise RuntimeError("thumbnail font is unavailable")
    filter_value = (
        "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
        "drawbox=x=0:y=0:w=1280:h=190:color=#f3efe6@0.94:t=fill,"
        f"drawtext=fontfile={font}:text='KEEP THE WORK.':"
        "fontcolor=#171512:fontsize=70:x=56:y=48"
    )
    run(
        (
            "ffmpeg",
            "-y",
            "-ss",
            "2",
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-vf",
            filter_value,
            str(output),
        )
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=OUTPUT / "recording-manifest.json",
    )
    args = parser.parse_args()
    manifest: dict[str, Any] = json.loads(args.manifest.read_text(encoding="utf-8"))
    if not manifest.get("release_commit"):
        raise ValueError("recording manifest is not bound to a release commit")
    if not manifest.get("run_id") or not manifest.get("checkpoint_sha256"):
        raise ValueError("recording manifest lacks recovery lineage")
    scenes = manifest.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("recording manifest has no scenes")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    caption_items: list[tuple[float, float, str]] = []
    offset = 0.0
    with tempfile.TemporaryDirectory(prefix="dovet-render-") as temporary:
        temporary_root = Path(temporary)
        intermediates: list[Path] = []
        for index, scene in enumerate(scenes):
            clip = ROOT / str(scene["clip"])
            audio = ROOT / str(scene["audio"])
            timing = ROOT / str(scene["timing"])
            if not clip.is_file() or not audio.is_file() or not timing.is_file():
                raise FileNotFoundError(f"scene {scene.get('id', index)} input is missing")
            audio_duration = duration(audio)
            marks = sentence_marks(timing)
            for mark_index, (start, text) in enumerate(marks):
                end = (
                    marks[mark_index + 1][0] - 0.05
                    if mark_index + 1 < len(marks)
                    else audio_duration
                )
                caption_items.append((offset + start, offset + max(start + 0.2, end), text))
            normalized = temporary_root / f"scene-{index:02d}.mp4"
            normalize_scene(clip, audio, normalized)
            intermediates.append(normalized)
            offset += duration(normalized)
        concat = temporary_root / "concat.txt"
        concat.write_text(
            "".join(f"file '{path.name}'\n" for path in intermediates),
            encoding="utf-8",
        )
        final = OUTPUT / "dovet-demo.mp4"
        run(
            (
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "1",
                "-i",
                str(concat),
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                str(final),
            )
        )
    write_captions(caption_items)
    media = probe(final)
    final_duration = float(media["format"]["duration"])
    video_streams = [item for item in media["streams"] if item.get("codec_type") == "video"]
    audio_streams = [item for item in media["streams"] if item.get("codec_type") == "audio"]
    if (
        not video_streams
        or not audio_streams
        or video_streams[0].get("width") != 1920
        or video_streams[0].get("height") != 1080
        or final_duration >= 300
    ):
        raise RuntimeError("final media failed duration, dimension, or audio checks")
    make_thumbnail(final, OUTPUT / "thumbnail.png")
    qa = [
        "# Dovet video QA",
        "",
        f"- PASS: duration {final_duration:.3f} seconds is below five minutes.",
        "- PASS: video is 1920x1080.",
        "- PASS: audio stream is present.",
        "- PASS: captions were derived from Polly sentence timing.",
        "- BLOCKED: owner playback review and public signed-out upload verification.",
        "",
        f"MP4 SHA-256: {sha256(final)}",
    ]
    (OUTPUT / "QA_REPORT.md").write_text("\n".join(qa) + "\n", encoding="utf-8")
    reviewed = dict(manifest)
    reviewed["final_video"] = {
        "path": "submission/video/dovet-demo.mp4",
        "sha256": sha256(final),
        "duration_seconds": final_duration,
        "width": 1920,
        "height": 1080,
        "audio_present": True,
    }
    args.manifest.write_text(json.dumps(reviewed, indent=2) + "\n", encoding="utf-8")
    print(final.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
