"""Run the authorized Codex interruption to Strands recovery vertical slice."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import boto3
from dovet.artifacts import ArtifactStore
from dovet.bundles import export_bundle, inspect_bundle
from dovet.canonical import digest_json
from dovet.checkpoints import CheckpointEngine
from dovet.policy import GuardContext, evaluate
from dovet.verifier import VerificationCommand, Verifier, digest_tree
from dovet_supervisor.agent import EvidenceEnvelope, build_agent, recommend
from dovet_worker.agent import build_worker, recover
from dovet_worker.tools import RestrictedTools, WorkerScope

ROOT = Path(__file__).resolve().parents[1]
PROTECTED = ROOT / "tests" / "acceptance-protected"
FIXTURE = ROOT / "examples" / "importer"
PRIVATE = ROOT / "artifacts" / "private"
DEFAULT_RECEIPTS = Path.home() / "Library" / "Application Support" / "Dovet" / "receipts"


def read_price_card(path: Path, *, model_id: str) -> tuple[int, dict[str, Any]]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if data.get("model_id") != model_id:
        raise ValueError("price card model does not match the requested model")
    checked_at = datetime.fromisoformat(str(data["checked_at"]).replace("Z", "+00:00"))
    if datetime.now(UTC) - checked_at > timedelta(days=7):
        raise ValueError("price card is stale")
    input_rate = Decimal(str(data["input_usd_per_million_tokens"]))
    output_rate = Decimal(str(data["output_usd_per_million_tokens"]))
    source_url = str(data.get("source_url", ""))
    source = urlparse(source_url)
    if (
        input_rate < 0
        or output_rate < 0
        or source.scheme != "https"
        or source.hostname not in {"aws.amazon.com", "docs.aws.amazon.com"}
    ):
        raise ValueError("price card is invalid")
    maximum_input_tokens = 42_000
    maximum_output_tokens = 5_200
    cap_microusd = math.ceil(
        float(input_rate * maximum_input_tokens + output_rate * maximum_output_tokens)
    )
    return cap_microusd, data


def verify(
    candidate: Path,
    *,
    snapshot_sha256: str,
    suite_digest: str,
) -> dict[str, object]:
    command = VerificationCommand(
        id="protected-importer",
        argv=(sys.executable, "-m", "pytest", "-q", str(PROTECTED)),
        timeout_seconds=90,
    )
    result = Verifier({command.id: command}).run(
        command.id,
        candidate_root=candidate,
        protected_suite=PROTECTED,
        expected_suite_digest=suite_digest,
        expected_snapshot_sha256=snapshot_sha256,
        current_snapshot_sha256=snapshot_sha256,
    )
    return {
        "status": result.status,
        "exit_code": result.exit_code,
        "duration_ms": result.duration_ms,
        "output_sha256": result.output_sha256,
        "suite_digest": result.suite_digest,
        "snapshot_sha256": result.snapshot_sha256,
    }


def release_commit() -> str:
    completed = subprocess.run(  # noqa: S603
        ("git", "rev-parse", "HEAD"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    commit = completed.stdout.strip()
    if len(commit) != 40 or any(character not in "0123456789abcdef" for character in commit):
        raise RuntimeError("release commit is invalid")
    return commit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--price-card", type=Path, required=True)
    parser.add_argument("--budget-microusd", type=int, required=True)
    parser.add_argument("--receipt-dir", type=Path, default=DEFAULT_RECEIPTS)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts" / "recovery-vertical-live.json",
    )
    args = parser.parse_args()
    if os.environ.get("DOVET_LIVE_BEDROCK") != "approved":
        raise RuntimeError("set DOVET_LIVE_BEDROCK=approved for this bounded paid run")
    availability = boto3.client(
        "bedrock", region_name=args.region
    ).get_foundation_model_availability(modelId=args.model_id)
    if availability.get("authorizationStatus") != "AUTHORIZED":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "model_id": args.model_id,
                    "authorization_status": availability.get("authorizationStatus", "UNKNOWN"),
                    "successful_provider_requests": 0,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return 2
    cap_microusd, price_card = read_price_card(args.price_card, model_id=args.model_id)
    if cap_microusd > args.budget_microusd:
        raise RuntimeError("verified worst-case model cap exceeds the approved run budget")

    PRIVATE.mkdir(parents=True, exist_ok=True)
    interruption = ROOT / "artifacts" / "managed-codex-interruption-live.json"
    subprocess.run(  # noqa: S603
        (
            sys.executable,
            str(ROOT / "scripts" / "probe_managed_codex.py"),
            "--output",
            str(interruption),
        ),
        cwd=ROOT,
        check=True,
    )
    interruption_data: dict[str, Any] = json.loads(interruption.read_text(encoding="utf-8"))
    if interruption_data.get("status") != "PASS":
        raise RuntimeError("managed Codex interruption did not pass")

    work_root = Path(tempfile.mkdtemp(prefix="vertical-", dir=PRIVATE))
    candidate = work_root / "candidate"
    shutil.copytree(FIXTURE, candidate)
    store = ArtifactStore(work_root / "artifacts")
    engine = CheckpointEngine(store)
    paths = [
        "README.md",
        "pyproject.toml",
        "src/parcel_import/__init__.py",
        "src/parcel_import/importer.py",
        "tests/test_public.py",
    ]
    initial = engine.capture(
        root=candidate,
        paths=paths,
        run_id="vertical_run",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="0" * 40,
    )
    suite_digest = digest_tree(PROTECTED)
    baseline = verify(candidate, snapshot_sha256=initial.snapshot_sha256, suite_digest=suite_digest)
    if baseline["status"] == "passed":
        raise RuntimeError("fixture unexpectedly passed before recovery")

    tool_calls: list[str] = []
    evidence_ids = frozenset({"incident_1", "checkpoint_1", "policy_1", "workers_1"})
    records = {
        "incident:incident_1": {
            "run_id": "vertical_run",
            "kind": "demonstration_fault",
            "owned_worker_stopped": True,
            "interruption_receipt_sha256": digest_json(interruption_data),
        },
        "checkpoint:checkpoint_1": {
            "id": "checkpoint_1",
            "snapshot_sha256": initial.snapshot_sha256,
            "complete": True,
            "verification": baseline,
        },
        "policy:task_1": {
            "policy_sha256": "a" * 64,
            "allowed_provider_profiles": ["bedrock_nova"],
            "budget_reserved_microusd": cap_microusd,
            "protected_tests": True,
        },
        "workers:task_1": {
            "profiles": [{"id": "bedrock_nova", "model_id": args.model_id, "ready": True}]
        },
    }
    supervisor = build_agent(
        model_id=args.model_id,
        region=args.region,
        evidence=EvidenceEnvelope(records),
        record_tool_call=tool_calls.append,
    )
    prompt = (
        "Recover incident_1 for run vertical_run and task_1. Inspect all four evidence records. "
        "The protected checks fail on a complete checkpoint and bedrock_nova is the only eligible "
        "replacement. Recommend the smallest safe next action."
    )
    decision = asyncio.run(recommend(supervisor, prompt))
    guard = evaluate(
        decision,
        GuardContext(
            incident_id="incident_1",
            run_id="vertical_run",
            policy_sha256="a" * 64,
            snapshot_sha256=initial.snapshot_sha256,
            checkpoint_id="checkpoint_1",
            eligible_provider_ids=frozenset({"bedrock_nova"}),
            writer_stopped=True,
            snapshot_valid=True,
            scope_permitted=True,
            provider_ready=True,
            budget_reserved=True,
            approval_consumable=True,
            verification_profile_trusted=True,
            evidence_ids=evidence_ids,
        ),
    )
    if not guard.allowed or decision.action.value != "handoff":
        raise RuntimeError(f"recovery proposal was not authorized: {guard.code}")

    worker_events: list[dict[str, object]] = []
    token = secrets.token_urlsafe(32)
    importer = candidate / "src" / "parcel_import" / "importer.py"
    restricted = RestrictedTools(
        WorkerScope(
            token=token,
            root=candidate,
            allowed_paths=frozenset({"src/parcel_import/importer.py"}),
            lease_generation=2,
            approved_commands=(
                (
                    "public-importer",
                    (sys.executable, "-m", "pytest", "-q", "tests/test_public.py"),
                ),
            ),
        ),
        current_lease_generation=lambda: 2,
        record=lambda kind, payload: worker_events.append({"kind": kind, "payload": payload}),
    )
    worker = build_worker(model_id=args.model_id, region=args.region, restricted=restricted)
    task = (
        "Implement the README contract in src/parcel_import/importer.py. "
        "The registered tools already enforce the authorized scope. The current source SHA-256 is "
        f"{hashlib.sha256(importer.read_bytes()).hexdigest()}. "
        "Use the file tools, then run only public-importer. Do not access protected tests."
    )
    candidate_report = asyncio.run(recover(worker, task))
    final_checkpoint = engine.capture(
        root=candidate,
        paths=paths,
        run_id="vertical_run",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="0" * 40,
    )
    final = verify(
        candidate,
        snapshot_sha256=final_checkpoint.snapshot_sha256,
        suite_digest=suite_digest,
    )
    bundle_evidence: dict[str, object] | None = None
    if final["status"] == "passed":
        bundle_directory = PRIVATE / "checkpoint-bundles"
        bundle_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        bundle_path = bundle_directory / (
            f"vertical_run-{final_checkpoint.snapshot_sha256[:12]}.dovet"
        )
        inspection = (
            inspect_bundle(bundle_path)
            if bundle_path.exists()
            else export_bundle(final_checkpoint, store, bundle_path)
        )
        if inspection.checkpoint.snapshot_sha256 != final_checkpoint.snapshot_sha256:
            raise RuntimeError("existing checkpoint bundle belongs to a different snapshot")
        bundle_evidence = {
            "bundle_sha256": inspection.bundle_sha256,
            "checkpoint_id": inspection.checkpoint.id,
            "object_count": inspection.object_count,
            "total_object_bytes": inspection.total_object_bytes,
        }
    receipt = {
        "status": "PASS" if final["status"] == "passed" else "FAIL",
        "run_id": "vertical_run",
        "recorded_at": datetime.now(UTC).isoformat(),
        "release_commit": release_commit(),
        "model_id": args.model_id,
        "region": args.region,
        "demonstration_fault": True,
        "interruption_receipt_sha256": digest_json(interruption_data),
        "managed_codex": {
            "thread_id": interruption_data["thread_id"],
            "turn_id": interruption_data["turn_id"],
        },
        "initial_snapshot_sha256": initial.snapshot_sha256,
        "supervisor_tool_calls": tool_calls,
        "recovery_decision": decision.model_dump(by_alias=True, mode="json"),
        "policy_result": {
            "allowed": guard.allowed,
            "code": guard.code,
            "explanation": guard.explanation,
        },
        "candidate_report": candidate_report.model_dump(mode="json"),
        "worker_events": worker_events,
        "final_snapshot_sha256": final_checkpoint.snapshot_sha256,
        "verification": final,
        "checkpoint_bundle": bundle_evidence,
        "budget": {
            "reserved_cap_microusd": cap_microusd,
            "approved_cap_microusd": args.budget_microusd,
            "price_card_source": price_card["source_url"],
            "price_card_checked_at": price_card["checked_at"],
            "actual_cost_basis": "unknown_until_provider_usage_is_reconciled",
        },
        "hidden_chain_of_thought_recorded": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if receipt["status"] == "PASS":
        args.receipt_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        receipt_path = args.receipt_dir / f"{receipt['run_id']}.json"
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        receipt_path.chmod(0o600)
    print(json.dumps({"status": receipt["status"], "output": str(args.output)}))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
