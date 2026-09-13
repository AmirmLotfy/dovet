"""Generate scene narration and sentence timing through an authorized Polly call."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import boto3

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "private-artifacts" / "video"


def key(text: str, voice: str, engine: str) -> str:
    return hashlib.sha256(f"{voice}\0{engine}\0{text}".encode()).hexdigest()[:16]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--script",
        type=Path,
        default=ROOT / "submission" / "video" / "narration-scenes.json",
    )
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    plan: dict[str, Any] = json.loads(args.script.read_text(encoding="utf-8"))
    evidence_status = str(plan.get("evidence_status", "BLOCKED"))
    voice = str(plan["voice_id"])
    engine = str(plan["engine"])
    region = str(plan["region"])
    scenes = plan["scenes"]
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("narration plan has no scenes")
    if not args.apply:
        print(
            json.dumps(
                {
                    "status": "PREVIEW",
                    "region": region,
                    "voice_id": voice,
                    "engine": engine,
                    "scene_count": len(scenes),
                    "evidence_status": evidence_status,
                    "message": (
                        "No Polly request was sent. Apply requires reconciled PASS evidence."
                    ),
                },
                indent=2,
            )
        )
        return 0
    if os.environ.get("DOVET_POLLY_APPLY") != "approved":
        raise RuntimeError("set DOVET_POLLY_APPLY=approved for the authorized narration run")
    if evidence_status != "PASS":
        raise RuntimeError("narration evidence is not reconciled; Polly synthesis is blocked")
    client = boto3.client("polly", region_name=region)
    voices = client.describe_voices(Engine=engine, LanguageCode="en-US").get("Voices", [])
    if not any(item.get("Id") == voice for item in voices):
        raise RuntimeError("selected voice and engine were not returned by DescribeVoices")
    audio_dir = PRIVATE / "audio"
    timing_dir = PRIVATE / "timing"
    audio_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    timing_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    manifest: list[dict[str, str]] = []
    for scene in scenes:
        scene_id = str(scene["id"])
        text = str(scene["text"]).strip()
        digest = key(text, voice, engine)
        audio = audio_dir / f"{scene_id}-{digest}.mp3"
        timing = timing_dir / f"{scene_id}-{digest}.jsonl"
        if not audio.exists():
            response = client.synthesize_speech(
                Engine=engine,
                OutputFormat="mp3",
                Text=text,
                TextType="text",
                VoiceId=voice,
            )
            audio.write_bytes(response["AudioStream"].read())
            os.chmod(audio, 0o600)
        if not timing.exists():
            response = client.synthesize_speech(
                Engine=engine,
                OutputFormat="json",
                SpeechMarkTypes=["sentence"],
                Text=text,
                TextType="text",
                VoiceId=voice,
            )
            timing.write_bytes(response["AudioStream"].read())
            os.chmod(timing, 0o600)
        manifest.append(
            {
                "id": scene_id,
                "audio": str(audio.relative_to(ROOT)),
                "timing": str(timing.relative_to(ROOT)),
            }
        )
    output = PRIVATE / "narration-manifest.json"
    output.write_text(json.dumps({"scenes": manifest}, indent=2) + "\n", encoding="utf-8")
    print(output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
