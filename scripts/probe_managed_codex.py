"""Run the explicit managed-Codex interruption and checkpoint probe."""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path

from dovet.artifacts import ArtifactStore
from dovet.canonical import digest_json
from dovet.checkpoints import CheckpointEngine
from dovet.codex_adapter import ManagedCodexAdapter


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=45.0)
    args = parser.parse_args()

    private_root = args.output.parent / "private"
    private_root.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="managed-codex-", dir=private_root))
    (workspace / "README.md").write_text(
        "Synthetic Dovet interruption probe. No user repository content.\n", encoding="utf-8"
    )
    prompt = (
        "This is an authorized synthetic interruption test. First create progress.txt with "
        "exactly `checkpoint-ready\\n`. Then create notes.md and slowly write a detailed list "
        "of recovery invariants. Do not touch files outside this directory."
    )
    started = time.monotonic()
    with ManagedCodexAdapter() as adapter:
        managed = adapter.start_turn(cwd=workspace, prompt=prompt)
        progress = workspace / "progress.txt"
        deadline = time.monotonic() + args.timeout
        while not progress.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        if not progress.exists():
            adapter.interrupt(managed.thread_id)
            adapter.finish(managed)
            raise TimeoutError("managed Codex worker did not create the checkpoint boundary")
        adapter.interrupt(managed.thread_id)
        result = adapter.finish(managed)

    engine = CheckpointEngine(ArtifactStore(private_root / "artifact-store"))
    captured = engine.capture(
        root=workspace,
        paths=["README.md", "progress.txt"],
        run_id="managed_codex_probe",
        task_version=1,
        policy_sha256="a" * 64,
        base_commit="0" * 40,
    )
    recovered = workspace.parent / f"{workspace.name}-recovered"
    engine.restore(captured, recovered)
    passed = (recovered / "progress.txt").read_text(encoding="utf-8") == "checkpoint-ready\n"
    receipt = {
        "status": "PASS" if passed else "FAIL",
        "probe": "managed Codex interruption to immutable checkpoint",
        "thread_id": managed.thread_id,
        "turn_id": managed.turn_id,
        "interruption_observed": True,
        "snapshot_sha256": captured.snapshot_sha256,
        "checkpoint_sha256": digest_json(captured.model_dump(mode="json")),
        "captured_paths": [entry.path for entry in captured.manifest.files],
        "recovered_bytes_verified": passed,
        "elapsed_ms": round((time.monotonic() - started) * 1000),
        "worker_final_response_present": bool(result.final_response),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
