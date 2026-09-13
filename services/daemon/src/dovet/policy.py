"""Deterministic authorization for advisory recovery decisions."""

from __future__ import annotations

from dataclasses import dataclass

from .models import RecoveryAction, RecoveryDecision


@dataclass(frozen=True)
class GuardContext:
    incident_id: str
    run_id: str
    policy_sha256: str
    snapshot_sha256: str
    checkpoint_id: str
    eligible_provider_ids: frozenset[str]
    writer_stopped: bool
    snapshot_valid: bool
    scope_permitted: bool
    provider_ready: bool
    budget_reserved: bool
    approval_consumable: bool
    verification_profile_trusted: bool
    evidence_ids: frozenset[str]


@dataclass(frozen=True)
class GuardResult:
    allowed: bool
    code: str
    explanation: str


def evaluate(decision: RecoveryDecision, context: GuardContext) -> GuardResult:
    checks = [
        (decision.incident_id == context.incident_id, "STALE_INCIDENT"),
        (decision.run_id == context.run_id, "WRONG_RUN"),
        (decision.expected_policy_sha256 == context.policy_sha256, "POLICY_CHANGED"),
        (set(decision.evidence_ids) <= context.evidence_ids, "UNKNOWN_EVIDENCE"),
    ]
    for passed, code in checks:
        if not passed:
            return GuardResult(False, code, "The proposal no longer matches authoritative state.")

    mutating = decision.action in {
        RecoveryAction.RESUME,
        RecoveryAction.RESTART,
        RecoveryAction.HANDOFF,
    }
    if not mutating:
        if decision.action is RecoveryAction.VERIFY and not context.verification_profile_trusted:
            return GuardResult(
                False, "UNTRUSTED_VERIFICATION", "Verification profile is not approved."
            )
        return GuardResult(True, "AUTHORIZED", "Read-only or pause action is permitted.")

    required = [
        (context.writer_stopped, "WORKER_STILL_ACTIVE"),
        (context.snapshot_valid, "SNAPSHOT_INCOMPLETE"),
        (context.scope_permitted, "POLICY_DENIED"),
        (context.provider_ready, "PROVIDER_UNAVAILABLE"),
        (context.budget_reserved, "BUDGET_UNKNOWN"),
        (context.approval_consumable, "APPROVAL_REQUIRED"),
        (decision.checkpoint_id == context.checkpoint_id, "CHECKPOINT_CHANGED"),
        (decision.expected_snapshot_sha256 == context.snapshot_sha256, "HASH_MISMATCH"),
        (
            decision.target_provider_profile_id in context.eligible_provider_ids,
            "UNAUTHORIZED_PROVIDER",
        ),
    ]
    for passed, code in required:
        if not passed:
            return GuardResult(False, code, "Deterministic recovery precondition failed.")
    return GuardResult(True, "AUTHORIZED", "All deterministic recovery preconditions passed.")
