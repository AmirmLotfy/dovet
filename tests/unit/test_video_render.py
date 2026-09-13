from __future__ import annotations

import json
from pathlib import Path

import pytest

from video.render import clock, scene_duration, sentence_marks


def test_caption_clock_formats_srt_and_vtt() -> None:
    assert clock(62.345) == "00:01:02,345"
    assert clock(62.345, vtt=True) == "00:01:02.345"


def test_sentence_marks_come_from_polly_timing(tmp_path: Path) -> None:
    timing = tmp_path / "scene.jsonl"
    timing.write_text(
        "\n".join(
            [
                json.dumps({"time": 0, "type": "sentence", "value": "Keep the work."}),
                json.dumps({"time": 820, "type": "sentence", "value": "Change the agent."}),
            ]
        )
    )
    assert sentence_marks(timing) == [(0.0, "Keep the work."), (0.82, "Change the agent.")]


def test_scene_duration_accepts_silent_edit_tail() -> None:
    assert scene_duration({"id": "checkpoint", "edit_seconds": 22}, 14.2) == 22


def test_scene_duration_rejects_truncated_narration() -> None:
    with pytest.raises(ValueError, match="shorter than its narration"):
        scene_duration({"id": "checkpoint", "edit_seconds": 12}, 14.2)


def test_submission_scene_plan_hits_required_edit_window() -> None:
    root = Path(__file__).resolve().parents[2]
    plan = json.loads(
        (root / "submission" / "video" / "narration-scenes.json").read_text(
            encoding="utf-8"
        )
    )
    assert plan["evidence_status"] == "BLOCKED"
    assert sum(scene["edit_seconds"] for scene in plan["scenes"]) == 280
    assert {scene["evidence_dependency"] for scene in plan["scenes"]} == {
        "LOCKED",
        "LIVE_RECEIPT",
    }
