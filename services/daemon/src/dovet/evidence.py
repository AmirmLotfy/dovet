"""Read validated, sanitized recovery receipts for the local evidence UI."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .models import KnowledgeKind, RunEvidenceEventView, RunEvidenceView, RunVerificationView

RUN_ID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
COMMIT = re.compile(r"^[a-f0-9]{40}$")
MAX_RECEIPT_BYTES = 1_000_000


class InvalidRunEvidence(ValueError):
    """Raised when a receipt cannot support a verified UI claim."""


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InvalidRunEvidence(f"{name} is missing")
    return value


def _text(value: object, name: str, *, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value:
        raise InvalidRunEvidence(f"{name} is invalid")
    if pattern is not None and pattern.fullmatch(value) is None:
        raise InvalidRunEvidence(f"{name} is invalid")
    return value


def _integer(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise InvalidRunEvidence(f"{name} is invalid")
    return value


def _timestamp(value: object, name: str) -> datetime:
    text = _text(value, name)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise InvalidRunEvidence(f"{name} is invalid") from error
    if parsed.tzinfo is None:
        raise InvalidRunEvidence(f"{name} must include a timezone")
    return parsed


class RunEvidenceStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def read(self, run_id: str) -> RunEvidenceView:
        if RUN_ID.fullmatch(run_id) is None:
            raise InvalidRunEvidence("run id is invalid")
        path = self.root / f"{run_id}.json"
        if path.is_symlink() or not path.is_file():
            raise FileNotFoundError(run_id)
        if path.stat().st_size > MAX_RECEIPT_BYTES:
            raise InvalidRunEvidence("receipt exceeds size limit")
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise InvalidRunEvidence("receipt is not valid JSON") from error
        data = _mapping(raw, "receipt")
        if (
            data.get("status") != "PASS"
            or data.get("hidden_chain_of_thought_recorded") is not False
        ):
            raise InvalidRunEvidence("receipt is not eligible for verified display")
        receipt_run_id = _text(data.get("run_id"), "run_id", pattern=RUN_ID)
        if receipt_run_id != run_id:
            raise InvalidRunEvidence("receipt run id does not match")
        policy = _mapping(data.get("policy_result"), "policy_result")
        verification = _mapping(data.get("verification"), "verification")
        decision = _mapping(data.get("recovery_decision"), "recovery_decision")
        candidate = _mapping(data.get("candidate_report"), "candidate_report")
        interruption = _mapping(data.get("managed_codex"), "managed_codex")
        if policy.get("allowed") is not True or decision.get("action") != "handoff":
            raise InvalidRunEvidence("receipt lacks an authorized handoff")
        if verification.get("status") != "passed":
            raise InvalidRunEvidence("independent verification did not pass")
        changed_paths = candidate.get("changed_paths")
        tool_calls = data.get("supervisor_tool_calls")
        if not isinstance(changed_paths, list) or not all(
            isinstance(path_value, str) for path_value in changed_paths
        ):
            raise InvalidRunEvidence("candidate paths are invalid")
        if not isinstance(tool_calls, list) or not all(
            isinstance(call, str) for call in tool_calls
        ):
            raise InvalidRunEvidence("supervisor tool evidence is invalid")

        initial_snapshot = _text(
            data.get("initial_snapshot_sha256"), "initial_snapshot_sha256", pattern=SHA256
        )
        final_snapshot = _text(
            data.get("final_snapshot_sha256"), "final_snapshot_sha256", pattern=SHA256
        )
        target = _text(
            decision.get("targetProviderProfileId"), "targetProviderProfileId"
        )
        suite_digest = _text(
            verification.get("suite_digest"), "suite_digest", pattern=SHA256
        )
        events = [
            RunEvidenceEventView(
                id="ev_interrupted",
                seq=1,
                title="Managed Codex worker interrupted",
                detail=(
                    f"Owned turn {_text(interruption.get('turn_id'), 'turn_id')} stopped during "
                    "an intentional demonstration fault."
                ),
                knowledge_kind=KnowledgeKind.OBSERVED,
            ),
            RunEvidenceEventView(
                id="ev_checkpoint",
                seq=2,
                title="Checkpoint sealed",
                detail=(
                    f"Immutable source manifest {initial_snapshot[:12]} captured before recovery."
                ),
                knowledge_kind=KnowledgeKind.VERIFIED,
            ),
            RunEvidenceEventView(
                id="ev_recommended",
                seq=3,
                title="Strands recommended a handoff",
                detail=(
                    f"The supervisor consulted {len(tool_calls)} evidence tools and selected "
                    f"{target}."
                ),
                knowledge_kind=KnowledgeKind.REPORTED,
            ),
            RunEvidenceEventView(
                id="ev_authorized",
                seq=4,
                title="Deterministic policy authorized recovery",
                detail=(
                    f"Policy result {_text(policy.get('code'), 'policy code')}: "
                    f"{_text(policy.get('explanation'), 'policy explanation')}"
                ),
                knowledge_kind=KnowledgeKind.VERIFIED,
            ),
            RunEvidenceEventView(
                id="ev_candidate",
                seq=5,
                title="Replacement worker produced a candidate",
                detail=(
                    f"Restricted Bedrock worker changed {len(changed_paths)} authorized path"
                    f"{'s' if len(changed_paths) != 1 else ''}."
                ),
                knowledge_kind=KnowledgeKind.REPORTED,
            ),
            RunEvidenceEventView(
                id="ev_verified",
                seq=6,
                title="Independent protected checks passed",
                detail=(
                    f"Suite {suite_digest[:12]} passed on snapshot {final_snapshot[:12]}."
                ),
                knowledge_kind=KnowledgeKind.VERIFIED,
            ),
        ]
        try:
            return RunEvidenceView(
                run_id=receipt_run_id,
                title="Recover CSV importer",
                project="Importer fixture",
                status="verified",
                source="live_receipt",
                recorded_at=_timestamp(data.get("recorded_at"), "recorded_at"),
                release_commit=_text(data.get("release_commit"), "release_commit", pattern=COMMIT),
                model_id=_text(data.get("model_id"), "model_id"),
                codex_thread_id=_text(interruption.get("thread_id"), "thread_id", pattern=RUN_ID),
                codex_turn_id=_text(interruption.get("turn_id"), "turn_id", pattern=RUN_ID),
                initial_snapshot_sha256=initial_snapshot,
                final_snapshot_sha256=final_snapshot,
                changed_paths=changed_paths,
                verification=RunVerificationView(
                    status="passed",
                    snapshot_sha256=_text(
                        verification.get("snapshot_sha256"),
                        "verification snapshot",
                        pattern=SHA256,
                    ),
                    suite_digest=suite_digest,
                    output_sha256=_text(
                        verification.get("output_sha256"), "output_sha256", pattern=SHA256
                    ),
                    duration_ms=_integer(verification.get("duration_ms"), "duration_ms"),
                ),
                events=events,
            )
        except ValidationError as error:
            raise InvalidRunEvidence("receipt fields failed validation") from error
