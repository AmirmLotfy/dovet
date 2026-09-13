"""Finish the local evidence package immediately after Bedrock authorization appears."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import boto3
from dovet.evidence import InvalidRunEvidence, RunEvidenceStore

ROOT = Path(__file__).resolve().parents[1]
RELEASE_REPORT = ROOT / "artifacts" / "release-evidence.json"
DATA_ROOT = Path.home() / "Library" / "Application Support" / "Dovet"


def run(argv: tuple[str, ...], *, environment: dict[str, str] | None = None) -> None:
    result = subprocess.run(  # noqa: S603
        argv,
        cwd=ROOT,
        env=environment,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{Path(argv[0]).name} failed with exit {result.returncode}")


def current_commit() -> str:
    result = subprocess.run(  # noqa: S603
        ("git", "rev-parse", "HEAD"), cwd=ROOT, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", default="amazon.nova-micro-v1:0")
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--price-card", type=Path, required=True)
    parser.add_argument("--budget-microusd", type=int, required=True)
    args = parser.parse_args()
    if args.budget_microusd <= 0:
        raise ValueError("budget must be a positive explicit bound")
    environment = os.environ.copy()
    try:
        existing = RunEvidenceStore(DATA_ROOT / "receipts").read("vertical_run")
    except (FileNotFoundError, InvalidRunEvidence):
        existing = None
    if existing is None or existing.release_commit != current_commit():
        if os.environ.get("DOVET_LIVE_BEDROCK") != "approved":
            raise RuntimeError("set DOVET_LIVE_BEDROCK=approved for the bounded paid run")
        bedrock = boto3.client("bedrock", region_name=args.region)
        availability = bedrock.get_foundation_model_availability(modelId=args.model_id)
        if availability.get("authorizationStatus") != "AUTHORIZED":
            print(
                json.dumps(
                    {
                        "status": "BLOCKED",
                        "reason": "Bedrock model remains unauthorized",
                        "authorization": availability.get("authorizationStatus", "UNKNOWN"),
                    }
                )
            )
            return 2
        run(
            (
                sys.executable,
                "scripts/run_recovery_vertical.py",
                "--model-id",
                args.model_id,
                "--region",
                args.region,
                "--price-card",
                str(args.price_card.resolve()),
                "--budget-microusd",
                str(args.budget_microusd),
            ),
            environment=environment,
        )
    run(("pnpm", "video:sound"))
    run(("pnpm", "demo:record"))
    run(("pnpm", "video:render"))
    run(
        (
            "uv",
            "run",
            "pytest",
            "-q",
            "tests/unit",
            "tests/integration",
            "-m",
            "not live",
            "--junitxml=artifacts/test-report-core.xml",
        )
    )
    run(("pnpm", "check"))
    run(("pnpm", "--filter", "@dovet/console", "test"))
    run(("pnpm", "build"))
    run(("pnpm", "test:e2e"))

    release = subprocess.run(  # noqa: S603
        ("pnpm", "release:check"), cwd=ROOT, check=False
    )
    report = json.loads(RELEASE_REPORT.read_text(encoding="utf-8"))
    unresolved = set(report.get("unresolved_items", []))
    owner_only = {"public_source", "devpost_submission"}
    status = "READY_FOR_OWNER_PUBLICATION" if unresolved <= owner_only else "BLOCKED"
    print(
        json.dumps(
            {
                "status": status,
                "release_check_exit": release.returncode,
                "unresolved_items": sorted(unresolved),
                "final_video": "submission/video/dovet-demo.mp4",
            }
        )
    )
    return 0 if status == "READY_FOR_OWNER_PUBLICATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
