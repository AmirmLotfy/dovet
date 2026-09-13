"""Assemble evidence-linked footage, narration, captions, music, and QA evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, cast

from dovet.evidence import RunEvidenceStore

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission" / "video"
PRIVATE = ROOT / "private-artifacts" / "video"
DATA_ROOT = Path.home() / "Library" / "Application Support" / "Dovet"


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
    return cast(dict[str, Any], json.loads(result.stdout))


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


def scene_marks(scene: dict[str, Any], audio_duration: float) -> list[tuple[float, str]]:
    timing_value = scene.get("timing")
    if timing_value:
        timing = ROOT / str(timing_value)
        if not timing.is_file():
            raise FileNotFoundError(f"scene {scene.get('id', 'unknown')} timing is missing")
        return sentence_marks(timing)
    caption = str(scene.get("caption", "")).strip()
    if not caption:
        raise ValueError(f"scene {scene.get('id', 'unknown')} has no timing or caption")
    if audio_duration <= 0:
        raise ValueError("narration audio duration must be positive")
    return [(0.0, caption)]


def write_captions(items: list[tuple[float, float, str]], output_root: Path) -> None:
    srt: list[str] = []
    vtt = ["WEBVTT", ""]
    for index, (start, end, text) in enumerate(items, start=1):
        srt.extend([str(index), f"{clock(start)} --> {clock(end)}", text, ""])
        vtt.extend([f"{clock(start, vtt=True)} --> {clock(end, vtt=True)}", text, ""])
    (output_root / "captions.srt").write_text("\n".join(srt), encoding="utf-8")
    (output_root / "captions.vtt").write_text("\n".join(vtt), encoding="utf-8")


def scene_duration(scene: dict[str, Any], audio_duration: float) -> float:
    requested = float(scene.get("edit_seconds", audio_duration))
    if requested < audio_duration:
        raise ValueError(
            f"scene {scene.get('id', 'unknown')} edit window is shorter than its narration"
        )
    if requested <= 0 or requested > 90:
        raise ValueError(f"scene {scene.get('id', 'unknown')} edit window is invalid")
    return requested


def normalize_scene(clip: Path, audio: Path, output: Path, target_seconds: float) -> None:
    video_filter = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#171512,"
        "setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=300"
    )
    image_input = clip.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    clip_args = ("-loop", "1", "-i", str(clip)) if image_input else (
        "-stream_loop",
        "-1",
        "-i",
        str(clip),
    )
    run(
        (
            "ffmpeg",
            "-y",
            *clip_args,
            "-i",
            str(audio),
            "-filter_complex",
            (
                f"[0:v]{video_filter},trim=duration={target_seconds:.3f},setpts=PTS-STARTPTS[v];"
                f"[1:a]apad=pad_dur={target_seconds:.3f},"
                f"atrim=duration={target_seconds:.3f},asetpts=PTS-STARTPTS[a]"
            ),
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-t",
            f"{target_seconds:.3f}",
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


def add_soundtrack(video: Path, soundtrack: Path, output: Path, total: float) -> None:
    fade_start = max(0.0, total - 3)
    run(
        (
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-stream_loop",
            "-1",
            "-i",
            str(soundtrack),
            "-filter_complex",
            (
                "[0:a]loudnorm=I=-16:TP=-1.5:LRA=7,"
                "aformat=channel_layouts=stereo[voice];"
                f"[1:a]atrim=duration={total:.3f},volume=0.12,"
                f"afade=t=out:st={fade_start:.3f}:d=3[bed];"
                "[voice][bed]amix=inputs=2:duration=first:dropout_transition=2[a]"
            ),
            "-map",
            "0:v:0",
            "-map",
            "[a]",
            "-c:v",
            "copy",
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


def make_thumbnail(video: Path, output: Path, at_seconds: float) -> None:
    with tempfile.TemporaryDirectory(prefix="dovet-thumbnail-") as temporary:
        frame = Path(temporary) / "frame.png"
        run(
            (
                "ffmpeg",
                "-y",
                "-ss",
                f"{at_seconds:.3f}",
                "-i",
                str(video),
                "-frames:v",
                "1",
                "-vf",
                "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720",
                str(frame),
            )
        )
        run(
            (
                "magick",
                str(frame),
                "-fill",
                "#f3efe6ee",
                "-draw",
                "rectangle 0,0 1280,190",
                "-font",
                "Helvetica",
                "-fill",
                "#171512",
                "-pointsize",
                "70",
                "-gravity",
                "northwest",
                "-annotate",
                "+56+48",
                "KEEP THE WORK.",
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
        default=PRIVATE / "recording-manifest.json",
    )
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    manifest: dict[str, Any] = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("capture_status") != "RECORDED":
        raise ValueError("recording manifest is not a completed capture")
    if manifest.get("capture_mode") != "evidence_replay_of_live_run":
        raise ValueError("recording manifest is not a live evidence replay")
    run_id = str(manifest.get("run_id", ""))
    evidence = RunEvidenceStore(DATA_ROOT / "receipts").read(run_id)
    lineage = {
        "release_commit": evidence.release_commit,
        "run_id": evidence.run_id,
        "checkpoint_sha256": evidence.final_snapshot_sha256,
        "codex_thread_id": evidence.codex_thread_id,
        "codex_turn_id": evidence.codex_turn_id,
        "model_id": evidence.model_id,
    }
    if any(manifest.get(key) != value for key, value in lineage.items()):
        raise ValueError("recording manifest does not match the validated live receipt")
    scenes = manifest.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("recording manifest has no scenes")
    output_root = args.output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    caption_items: list[tuple[float, float, str]] = []
    offset = 0.0
    with tempfile.TemporaryDirectory(prefix="dovet-render-") as temporary:
        temporary_root = Path(temporary)
        intermediates: list[Path] = []
        for index, scene in enumerate(scenes):
            clip = ROOT / str(scene["clip"])
            audio = ROOT / str(scene["audio"])
            if not clip.is_file() or not audio.is_file():
                raise FileNotFoundError(f"scene {scene.get('id', index)} input is missing")
            if sha256(clip) != scene.get("clip_sha256"):
                raise ValueError(f"scene {scene.get('id', index)} clip checksum changed")
            if sha256(audio) != scene.get("audio_sha256"):
                raise ValueError(f"scene {scene.get('id', index)} audio checksum changed")
            audio_duration = duration(audio)
            edit_duration = scene_duration(scene, audio_duration)
            marks = scene_marks(scene, audio_duration)
            for mark_index, (start, text) in enumerate(marks):
                end = (
                    marks[mark_index + 1][0] - 0.05
                    if mark_index + 1 < len(marks)
                    else audio_duration
                )
                caption_items.append((offset + start, offset + max(start + 0.2, end), text))
            normalized = temporary_root / f"scene-{index:02d}.mp4"
            normalize_scene(clip, audio, normalized, edit_duration)
            intermediates.append(normalized)
            offset += edit_duration
        concat = temporary_root / "concat.txt"
        concat.write_text(
            "".join(f"file '{path.name}'\n" for path in intermediates),
            encoding="utf-8",
        )
        joined = temporary_root / "joined.mp4"
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
                str(joined),
            )
        )
        final = output_root / "dovet-demo.mp4"
        soundtrack_value = manifest.get("soundtrack")
        if soundtrack_value:
            soundtrack = ROOT / str(soundtrack_value)
            if not soundtrack.is_file():
                raise FileNotFoundError("soundtrack input is missing")
            add_soundtrack(joined, soundtrack, final, duration(joined))
        else:
            final.write_bytes(joined.read_bytes())
    write_captions(caption_items, output_root)
    media = probe(final)
    final_duration = float(media["format"]["duration"])
    video_streams = [item for item in media["streams"] if item.get("codec_type") == "video"]
    audio_streams = [item for item in media["streams"] if item.get("codec_type") == "audio"]
    if (
        not video_streams
        or not audio_streams
        or video_streams[0].get("width") != 1920
        or video_streams[0].get("height") != 1080
        or not 275 <= final_duration <= 290
    ):
        raise RuntimeError("final media failed 4:35-4:50 duration, dimension, or audio checks")
    thumbnail_time = float(manifest.get("thumbnail_time_seconds", 8.0))
    if manifest.get("thumbnail_source") != "application_footage":
        raise ValueError("thumbnail_source must identify application footage")
    if not 0 <= thumbnail_time < final_duration:
        raise ValueError("thumbnail time is outside the finished video")
    make_thumbnail(final, output_root / "thumbnail.png", thumbnail_time)
    qa = [
        "# Dovet video QA",
        "",
        f"- PASS: duration {final_duration:.3f} seconds is within the 4:35-4:50 target.",
        "- PASS: video is 1920x1080.",
        "- PASS: audio stream is present.",
        "- PASS: captions were derived from narration scene timing and approved script text.",
        "- PASS: the thumbnail frame is declared as actual application footage.",
        "- BLOCKED: owner playback review and signed-out verification after manual upload.",
        "",
        f"MP4 SHA-256: {sha256(final)}",
    ]
    (output_root / "QA_REPORT.md").write_text("\n".join(qa) + "\n", encoding="utf-8")
    reviewed = dict(manifest)
    reviewed["final_video"] = {
        "path": "submission/video/dovet-demo.mp4",
        "sha256": sha256(final),
        "duration_seconds": final_duration,
        "width": 1920,
        "height": 1080,
        "audio_present": True,
    }
    (output_root / "recording-manifest.json").write_text(
        json.dumps(reviewed, indent=2) + "\n", encoding="utf-8"
    )
    print(final.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
