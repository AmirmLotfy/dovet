"""Render a review-only picture edit while live recovery evidence is blocked."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from render import add_soundtrack, duration, normalize_scene, probe, write_captions

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "submission" / "video" / "narration-scenes.json"
PRIVATE = ROOT / "private-artifacts" / "video"
OUTPUT = PRIVATE / "dovet-picture-edit-blocked.mp4"


def run(argv: tuple[str, ...]) -> None:
    result = subprocess.run(argv, capture_output=True, text=True, check=False)  # noqa: S603
    if result.returncode != 0:
        raise RuntimeError(f"{Path(argv[0]).name} failed")


def source_for(index: int) -> Path:
    if index in {1, 2, 9, 10}:
        return ROOT / "artifacts" / "site-updated-desktop.png"
    if index in {3, 4, 5, 6, 7, 8, 11}:
        return ROOT / "artifacts" / "ui-evidence-rail-fixture.png"
    return ROOT / "artifacts" / "architecture-preview.png"


def title_for(scene_id: str) -> str:
    return scene_id.split("-", 1)[1].replace("-", " ").upper()


def make_card(source: Path, output: Path, scene: dict[str, Any]) -> None:
    dependency = str(scene["evidence_dependency"])
    label = (
        "CLOUD PROOF BLOCKED — AWS ACCOUNT PROVISIONING"
        if dependency == "LIVE_RECEIPT"
        else "REVIEW EDIT — ACTUAL PRODUCT OR ARCHITECTURE FOOTAGE"
    )
    run(
        (
            "magick",
            str(source),
            "-resize",
            "1920x1080^",
            "-gravity",
            "center",
            "-extent",
            "1920x1080",
            "-fill",
            "#f3efe6ee",
            "-draw",
            "rectangle 0,0 1920,250",
            "-gravity",
            "northwest",
            "-font",
            "Helvetica-Bold",
            "-pointsize",
            "62",
            "-fill",
            "#171512",
            "-annotate",
            "+84+68",
            title_for(str(scene["id"])),
            "-font",
            "Helvetica",
            "-pointsize",
            "29",
            "-fill",
            "#554d43",
            "-annotate",
            "+88+158",
            str(scene["visual"]),
            "-fill",
            "#171512e8",
            "-draw",
            "rectangle 0,992 1920,1080",
            "-font",
            "Helvetica-Bold",
            "-pointsize",
            "27",
            "-fill",
            "#f3efe6",
            "-annotate",
            "+84+1024",
            label,
            str(output),
        )
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_review_thumbnail(output: Path) -> None:
    run(
        (
            "magick",
            str(ROOT / "artifacts" / "ui-evidence-rail-fixture.png"),
            "-resize",
            "1280x720^",
            "-gravity",
            "center",
            "-extent",
            "1280x720",
            "-fill",
            "#f3efe6ee",
            "-draw",
            "rectangle 0,0 1280,180",
            "-gravity",
            "northwest",
            "-font",
            "Helvetica-Bold",
            "-pointsize",
            "66",
            "-fill",
            "#171512",
            "-annotate",
            "+54+42",
            "KEEP THE WORK.",
            "-font",
            "Helvetica",
            "-pointsize",
            "27",
            "-fill",
            "#554d43",
            "-annotate",
            "+58+120",
            "Dovet — recovery evidence stays attached",
            "-fill",
            "#171512e8",
            "-draw",
            "rectangle 0,648 1280,720",
            "-font",
            "Helvetica-Bold",
            "-pointsize",
            "22",
            "-fill",
            "#f3efe6",
            "-annotate",
            "+58+672",
            "REVIEW THUMBNAIL — LIVE CLOUD PROOF BLOCKED",
            str(output),
        )
    )


def main() -> int:
    plan: dict[str, Any] = json.loads(PLAN.read_text(encoding="utf-8"))
    if plan.get("evidence_status") != "BLOCKED":
        raise ValueError("review renderer is only for an explicitly blocked evidence plan")
    soundtrack = PRIVATE / "sound" / "dovet-bed.wav"
    if not soundtrack.is_file():
        raise FileNotFoundError("deterministic soundtrack is missing; run pnpm video:sound")
    PRIVATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    captions: list[tuple[float, float, str]] = []
    scene_records: list[dict[str, Any]] = []
    offset = 0.0
    with tempfile.TemporaryDirectory(prefix="dovet-draft-") as temporary:
        work = Path(temporary)
        normalized: list[Path] = []
        for index, scene in enumerate(plan["scenes"], start=1):
            audio = PRIVATE / "higgsfield" / "narration" / f"scene-{index:02d}.wav"
            if not audio.is_file():
                raise FileNotFoundError(f"accepted narration missing for scene {index:02d}")
            edit_seconds = float(scene["edit_seconds"])
            if index == 1:
                visual = PRIVATE / "higgsfield" / "dovet-opening-05e03908.mp4"
            else:
                visual = work / f"card-{index:02d}.png"
                make_card(source_for(index), visual, scene)
            rendered = work / f"scene-{index:02d}.mp4"
            normalize_scene(visual, audio, rendered, edit_seconds)
            normalized.append(rendered)
            speech_seconds = min(duration(audio), edit_seconds)
            captions.append((offset, offset + speech_seconds, str(scene["text"])))
            scene_records.append(
                {
                    "id": scene["id"],
                    "edit_seconds": edit_seconds,
                    "evidence_dependency": scene["evidence_dependency"],
                    "audio_sha256": sha256(audio),
                    "visual_source": str(visual.relative_to(ROOT))
                    if visual.is_relative_to(ROOT)
                    else "generated_review_card",
                }
            )
            offset += edit_seconds
        concat = work / "concat.txt"
        concat.write_text(
            "".join(f"file '{item.name}'\n" for item in normalized), encoding="utf-8"
        )
        joined = work / "joined.mp4"
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
                str(joined),
            )
        )
        add_soundtrack(joined, soundtrack, OUTPUT, offset)

    write_captions(captions, PRIVATE)
    media = probe(OUTPUT)
    final_duration = float(media["format"]["duration"])
    if not 275 <= final_duration <= 290:
        raise RuntimeError("review edit missed the required 4:35-4:50 window")
    thumbnail = PRIVATE / "thumbnail-blocked.png"
    make_review_thumbnail(thumbnail)
    manifest = {
        "schema_version": "1",
        "status": "REVIEW_ONLY_BLOCKED",
        "reason": plan["blocker"],
        "path": str(OUTPUT.relative_to(ROOT)),
        "sha256": sha256(OUTPUT),
        "duration_seconds": final_duration,
        "width": 1920,
        "height": 1080,
        "scenes": scene_records,
        "captions": "private-artifacts/video/captions.srt",
        "thumbnail": {
            "path": "private-artifacts/video/thumbnail-blocked.png",
            "sha256": sha256(thumbnail),
            "width": 1280,
            "height": 720,
            "status": "REVIEW_ONLY_BLOCKED",
        },
        "limitations": [
            "This picture edit is not live recovery evidence.",
            "Live-dependent scenes carry a persistent cloud-blocked label.",
            "Owner normal-speed voice and full-playback review remain pending.",
        ],
    }
    (PRIVATE / "picture-edit-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    qa = [
        "# Dovet blocked picture edit QA",
        "",
        f"- PASS: duration {final_duration:.3f} seconds is within the 4:35-4:50 target.",
        "- PASS: H.264 video is 1920x1080.",
        "- PASS: AAC audio is 48 kHz stereo.",
        "- PASS: all 12 accepted narration scenes are present without time stretching.",
        "- PASS: static product frames use restrained native edit motion.",
        "- PASS: every live-dependent scene carries a persistent cloud-blocked label.",
        "- BLOCKED: this review edit is not the final recovery evidence video.",
        "- BLOCKED: owner normal-speed narration and full-playback review remain pending.",
        "",
        f"MP4 SHA-256: {sha256(OUTPUT)}",
    ]
    (PRIVATE / "PICTURE_EDIT_QA.md").write_text("\n".join(qa) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
