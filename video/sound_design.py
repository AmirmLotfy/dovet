"""Generate Dovet's deterministic, original low-volume music bed."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "private-artifacts" / "video" / "sound" / "dovet-bed.wav"


def run(argv: tuple[str, ...]) -> None:
    result = subprocess.run(argv, capture_output=True, text=True, check=False)  # noqa: S603
    if result.returncode != 0:
        raise RuntimeError(f"{Path(argv[0]).name} failed while generating the music bed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=float, default=295.0)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if not 10 <= args.duration < 300:
        raise ValueError("duration must be at least 10 seconds and below five minutes")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    # A quiet D minor/add-nine mineral pad. Every oscillator and envelope is fixed, making the
    # result reproducible and original; there are no downloaded samples or model-generated stems.
    expression = (
        "0.024*(sin(2*PI*73.416*t)+0.58*sin(2*PI*110*t)+"
        "0.42*sin(2*PI*146.832*t)+0.28*sin(2*PI*164.814*t))*"
        "(0.82+0.18*sin(2*PI*0.03125*t))"
    )
    audio_filter = (
        f"aevalsrc=exprs='{expression}|{expression}':s=48000:d={args.duration:.3f},"
        "highpass=f=45,lowpass=f=1500,"
        "afade=t=in:st=0:d=2,"
        f"afade=t=out:st={max(0.0, args.duration - 3):.3f}:d=3"
    )
    run(
        (
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            audio_filter,
            "-c:a",
            "pcm_s24le",
            str(output),
        )
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "path": str(output.relative_to(ROOT)),
                "duration_seconds": args.duration,
                "sample_rate_hz": 48000,
                "provenance": "deterministic_original_synthesis",
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
