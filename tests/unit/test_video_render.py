from __future__ import annotations

import json
from pathlib import Path

from video.render import clock, sentence_marks


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
