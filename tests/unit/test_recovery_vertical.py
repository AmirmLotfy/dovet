from __future__ import annotations

import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType

import pytest


def load_runner() -> ModuleType:
    path = Path(__file__).resolve().parents[2] / "scripts" / "run_recovery_vertical.py"
    spec = importlib.util.spec_from_file_location("run_recovery_vertical", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_price_card_requires_fresh_aws_owned_source(tmp_path: Path) -> None:
    runner = load_runner()
    price_card = tmp_path / "price.json"
    price_card.write_text(
        json.dumps(
            {
                "model_id": "amazon.nova-micro-v1:0",
                "checked_at": datetime.now(UTC).isoformat(),
                "source_url": "https://example.com/untrusted-price",
                "input_usd_per_million_tokens": "0.035",
                "output_usd_per_million_tokens": "0.14",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid"):
        runner.read_price_card(price_card, model_id="amazon.nova-micro-v1:0")

    data = json.loads(price_card.read_text(encoding="utf-8"))
    data["source_url"] = "https://aws.amazon.com/bedrock/pricing/"
    price_card.write_text(json.dumps(data), encoding="utf-8")

    cap_microusd, loaded = runner.read_price_card(
        price_card,
        model_id="amazon.nova-micro-v1:0",
    )

    assert cap_microusd == 2_198
    assert loaded["source_url"] == "https://aws.amazon.com/bedrock/pricing/"
