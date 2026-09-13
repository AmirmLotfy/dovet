from __future__ import annotations

from dataclasses import replace

from dovet.models import RecoveryDecision
from dovet.policy import GuardContext, evaluate


def decision() -> RecoveryDecision:
    return RecoveryDecision.model_validate(
        {
            "version": "DovetRecovery/1",
            "incidentId": "incident_1",
            "runId": "run_1",
            "action": "handoff",
            "checkpointId": "checkpoint_1",
            "targetProviderProfileId": "bedrock_1",
            "expectedSnapshotSha256": "a" * 64,
            "expectedPolicySha256": "b" * 64,
            "evidenceIds": ["evidence_1"],
            "explanation": "Owned worker stopped and the checkpoint is valid.",
            "uncertainties": [],
            "preconditions": ["writer_stopped", "snapshot_valid", "budget_reserved"],
        }
    )


def context() -> GuardContext:
    return GuardContext(
        incident_id="incident_1",
        run_id="run_1",
        policy_sha256="b" * 64,
        snapshot_sha256="a" * 64,
        checkpoint_id="checkpoint_1",
        eligible_provider_ids=frozenset({"bedrock_1"}),
        writer_stopped=True,
        snapshot_valid=True,
        scope_permitted=True,
        provider_ready=True,
        budget_reserved=True,
        approval_consumable=True,
        verification_profile_trusted=True,
        evidence_ids=frozenset({"evidence_1"}),
    )


def test_authorized_recovery() -> None:
    assert evaluate(decision(), context()).allowed


def test_old_writer_blocks_recovery() -> None:
    result = evaluate(decision(), replace(context(), writer_stopped=False))
    assert not result.allowed
    assert result.code == "WORKER_STILL_ACTIVE"


def test_stale_or_replayed_state_is_rejected() -> None:
    assert (
        evaluate(decision(), replace(context(), snapshot_sha256="c" * 64)).code == "HASH_MISMATCH"
    )
    assert (
        evaluate(decision(), replace(context(), approval_consumable=False)).code
        == "APPROVAL_REQUIRED"
    )
