"""Record a validated local recovery receipt at an explicit 1920x1080."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx
from dovet.evidence import InvalidRunEvidence, RunEvidenceStore

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path.home() / "Library" / "Application Support" / "Dovet"
PRIVATE_VIDEO = ROOT / "private-artifacts" / "video"
PREFLIGHT = ROOT / "artifacts" / "recording-preflight.json"
NARRATION_PLAN = ROOT / "submission" / "video" / "narration-scenes.json"


def run(argv: tuple[str, ...], *, environment: dict[str, str] | None = None) -> None:
    completed = subprocess.run(  # noqa: S603
        argv,
        cwd=ROOT,
        env=environment,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"{Path(argv[0]).name} failed with exit {completed.returncode}")


def write_preflight(status: str, detail: str, *, run_id: str) -> None:
    PREFLIGHT.parent.mkdir(exist_ok=True)
    PREFLIGHT.write_text(
        json.dumps(
            {
                "status": status,
                "run_id": run_id,
                "checked_at": datetime.now(UTC).isoformat(),
                "detail": detail,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def pair_url() -> str:
    bridge_path = DATA_ROOT / "bridge-token"
    token = bridge_path.read_text(encoding="utf-8").strip()
    if len(token) < 32:
        raise RuntimeError("local bridge credential is invalid")
    deadline = time.monotonic() + 15
    while True:
        try:
            response = httpx.post(
                "http://127.0.0.1:4317/api/v1/session/issue",
                headers={"X-Dovet-Bridge": token},
                timeout=2,
            )
            response.raise_for_status()
            value = response.json().get("url")
            if isinstance(value, str) and value.startswith("http://127.0.0.1:4317/#pair="):
                return value
            raise RuntimeError("local service returned an invalid pairing response")
        except httpx.HTTPError:
            if time.monotonic() >= deadline:
                raise RuntimeError("local service did not become ready") from None
            time.sleep(0.2)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="vertical_run")
    args = parser.parse_args()
    try:
        evidence = RunEvidenceStore(DATA_ROOT / "receipts").read(args.run_id)
    except FileNotFoundError:
        write_preflight(
            "BLOCKED",
            "A validated PASS receipt from the live recovery has not been persisted.",
            run_id=args.run_id,
        )
        print(json.dumps({"status": "BLOCKED", "reason": "verified live receipt unavailable"}))
        return 2
    except InvalidRunEvidence as error:
        write_preflight("BLOCKED", str(error), run_id=args.run_id)
        print(json.dumps({"status": "BLOCKED", "reason": "verified live receipt unavailable"}))
        return 2

    run(("pnpm", "--filter", "@dovet/console", "build"))
    subprocess.run(  # noqa: S603
        ("uv", "run", "dovet", "service", "stop"),
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    run(("uv", "run", "dovet", "service", "install"))
    run(("uv", "run", "dovet", "service", "start"))
    pairing = pair_url()
    raw_root = PRIVATE_VIDEO / "raw"
    raw_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    environment = os.environ.copy()
    environment.update(
        {
            "DOVET_RECORD_RUN_ID": args.run_id,
            "DOVET_PAIR_URL": pairing,
            "DOVET_RECORD_BASE_URL": "http://127.0.0.1:4317",
            "DOVET_RECORD_OUTPUT_DIR": str(raw_root),
        }
    )
    run(
        (
            "pnpm",
            "--filter",
            "@dovet/console",
            "exec",
            "playwright",
            "test",
            "tests/record-demo.spec.ts",
            "--project=record",
        ),
        environment=environment,
    )
    videos = sorted(raw_root.rglob("*.webm"), key=lambda path: path.stat().st_mtime)
    if not videos:
        raise RuntimeError("Playwright did not finalize a recording")
    clip = videos[-1]
    narration = json.loads(NARRATION_PLAN.read_text(encoding="utf-8"))
    scenes = []
    for index, scene in enumerate(narration["scenes"], start=1):
        audio = PRIVATE_VIDEO / "higgsfield" / "narration" / f"scene-{scene['id'][:2]}.wav"
        if not audio.is_file():
            raise RuntimeError(f"accepted narration is missing for scene {scene['id']}")
        if index == 1:
            visual = PRIVATE_VIDEO / "higgsfield" / "dovet-opening-05e03908.mp4"
        elif index in {2, 3, 10}:
            visual = ROOT / "artifacts" / "site-updated-desktop.png"
        elif index == 11:
            visual = ROOT / "artifacts" / "architecture-preview.png"
        else:
            visual = clip
        if not visual.is_file():
            raise RuntimeError(f"visual source is missing for scene {scene['id']}")
        scenes.append(
            {
                "id": scene["id"],
                "clip": str(visual.relative_to(ROOT)),
                "clip_sha256": sha256(visual),
                "audio": str(audio.relative_to(ROOT)),
                "audio_sha256": sha256(audio),
                "caption": scene["text"],
                "edit_seconds": scene["edit_seconds"],
                "evidence_dependency": scene["evidence_dependency"],
            }
        )
    manifest = {
        "schema_version": "1",
        "capture_status": "RECORDED",
        "capture_mode": "evidence_replay_of_live_run",
        "recorded_at": datetime.now(UTC).isoformat(),
        "release_commit": evidence.release_commit,
        "run_id": evidence.run_id,
        "checkpoint_sha256": evidence.final_snapshot_sha256,
        "model_id": evidence.model_id,
        "codex_thread_id": evidence.codex_thread_id,
        "codex_turn_id": evidence.codex_turn_id,
        "clip": str(clip.relative_to(ROOT)),
        "clip_sha256": sha256(clip),
        "scenes": scenes,
        "soundtrack": "private-artifacts/video/sound/dovet-bed.wav",
        "thumbnail_source": "application_footage",
        "thumbnail_time_seconds": 55,
        "viewport": {"width": 1920, "height": 1080},
        "accelerated_portions": [],
        "limitations": [
            "This clip replays the validated evidence receipt after the live recovery completed."
        ],
    }
    output = PRIVATE_VIDEO / "recording-manifest.json"
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_preflight("PASS", "validated receipt recorded", run_id=args.run_id)
    print(json.dumps({"status": "RECORDED", "manifest": str(output.relative_to(ROOT))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
