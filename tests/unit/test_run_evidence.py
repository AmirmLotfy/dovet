from __future__ import annotations

import json
from pathlib import Path

import pytest
from dovet.evidence import InvalidRunEvidence, RunEvidenceStore


def receipt() -> dict[str, object]:
    digest = "a" * 64
    return {
        "status": "PASS",
        "run_id": "vertical_run",
        "recorded_at": "2026-09-13T02:00:00Z",
        "release_commit": "b" * 40,
        "model_id": "amazon.nova-micro-v1:0",
        "hidden_chain_of_thought_recorded": False,
        "managed_codex": {"thread_id": "thread_1", "turn_id": "turn_1"},
        "initial_snapshot_sha256": digest,
        "final_snapshot_sha256": digest,
        "supervisor_tool_calls": [
            "get_incident",
            "get_checkpoint",
            "get_policy",
            "list_eligible_workers",
        ],
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


def write_receipt(root: Path, value: dict[str, object]) -> None:
    root.mkdir(exist_ok=True)
    (root / "vertical_run.json").write_text(json.dumps(value), encoding="utf-8")


def test_projects_verified_receipt_into_evidence_rail(tmp_path: Path) -> None:
    write_receipt(tmp_path, receipt())

    evidence = RunEvidenceStore(tmp_path).read("vertical_run")

    assert evidence.status == "verified"
    assert [event.knowledge_kind.value for event in evidence.events] == [
        "observed",
        "verified",
        "reported",
        "verified",
        "reported",
        "verified",
    ]
    assert evidence.changed_paths == ["src/parcel_import/importer.py"]


@pytest.mark.parametrize("mutation", ["failed", "chain_of_thought", "wrong_run"])
def test_rejects_receipt_that_cannot_support_verified_claim(
    tmp_path: Path, mutation: str
) -> None:
    value = receipt()
    if mutation == "failed":
        value["status"] = "FAIL"
    elif mutation == "chain_of_thought":
        value["hidden_chain_of_thought_recorded"] = True
    else:
        value["run_id"] = "other_run"
    write_receipt(tmp_path, value)

    with pytest.raises(InvalidRunEvidence):
        RunEvidenceStore(tmp_path).read("vertical_run")
