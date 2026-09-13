from __future__ import annotations

import json
from pathlib import Path

from dovet.api import SessionState, create_app
from dovet.evidence import RunEvidenceStore
from fastapi.testclient import TestClient


def write_receipt(root: Path) -> None:
    digest = "a" * 64
    root.mkdir(exist_ok=True)
    value = {
        "status": "PASS",
        "run_id": "vertical_run",
        "recorded_at": "2026-09-13T02:00:00Z",
        "release_commit": "b" * 40,
        "model_id": "amazon.nova-micro-v1:0",
        "hidden_chain_of_thought_recorded": False,
        "managed_codex": {"thread_id": "thread_1", "turn_id": "turn_1"},
        "initial_snapshot_sha256": digest,
        "final_snapshot_sha256": digest,
        "supervisor_tool_calls": ["get_incident", "get_checkpoint"],
        "recovery_decision": {
            "action": "handoff",
            "targetProviderProfileId": "bedrock_nova",
        },
        "policy_result": {
            "allowed": True,
            "code": "AUTHORIZED",
            "explanation": "All deterministic preconditions passed.",
        },
        "candidate_report": {"changed_paths": ["src/parcel_import/importer.py"]},
        "verification": {
            "status": "passed",
            "snapshot_sha256": digest,
            "suite_digest": digest,
            "output_sha256": digest,
            "duration_ms": 42,
        },
    }
    (root / "vertical_run.json").write_text(json.dumps(value), encoding="utf-8")


def test_authenticated_console_can_read_verified_run_receipt(tmp_path: Path) -> None:
    write_receipt(tmp_path)
    sessions = SessionState()
    nonce = sessions.issue_pairing_nonce()
    client = TestClient(
        create_app(state=sessions, evidence_store=RunEvidenceStore(tmp_path)),
        base_url="http://127.0.0.1:4317",
    )
    paired = client.post("/api/v1/session/pair", json={"nonce": nonce})
    assert paired.status_code == 200

    response = client.get("/api/v1/runs/vertical_run")

    assert response.status_code == 200
    assert response.json()["source"] == "live_receipt"
    assert response.json()["verification"]["status"] == "passed"


def test_built_console_serves_run_route_for_browser_navigation(tmp_path: Path) -> None:
    console = tmp_path / "console"
    console.mkdir()
    (console / "index.html").write_text("<title>Dovet console</title>", encoding="utf-8")
    client = TestClient(
        create_app(console_dir=console),
        base_url="http://127.0.0.1:4317",
    )

    response = client.get("/runs/vertical_run")

    assert response.status_code == 200
    assert "Dovet console" in response.text
