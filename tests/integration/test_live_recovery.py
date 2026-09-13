from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.live
def test_authorized_codex_to_bedrock_recovery() -> None:
    if os.environ.get("DOVET_LIVE_BEDROCK") != "approved":
        pytest.skip("set DOVET_LIVE_BEDROCK=approved for the bounded paid integration")
    root = Path(__file__).resolve().parents[2]
    price_card = Path(
        os.environ.get(
            "DOVET_PRICE_CARD",
            str(root / "artifacts" / "private" / "nova-micro-price-card.json"),
        )
    )
    completed = subprocess.run(  # noqa: S603
        (
            sys.executable,
            str(root / "scripts" / "run_recovery_vertical.py"),
            "--model-id",
            "amazon.nova-micro-v1:0",
            "--region",
            "us-east-1",
            "--price-card",
            str(price_card),
            "--budget-microusd",
            "50000",
        ),
        cwd=root,
        check=False,
    )
    assert completed.returncode == 0
