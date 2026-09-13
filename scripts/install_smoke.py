"""Install the built wheel in isolation and record sanitized release evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "install-smoke.json"


def run(argv: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(  # noqa: S603
        argv,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"{Path(argv[0]).name} failed during isolated install smoke test")
    return completed


def main() -> int:
    run(("uv", "build"))
    wheels = sorted((ROOT / "dist").glob("dovet-*.whl"))
    if len(wheels) != 1:
        raise RuntimeError("expected exactly one Dovet wheel")
    wheel = wheels[0]
    with tempfile.TemporaryDirectory(prefix="dovet-install-smoke-") as temporary:
        environment = Path(temporary) / "venv"
        run(("uv", "venv", "--python", "3.12", str(environment)))
        python = environment / "bin" / "python"
        cli = environment / "bin" / "dovet"
        run(("uv", "pip", "install", "--python", str(python), str(wheel)))
        version = run((str(cli), "--version")).stdout.strip()
        run(
            (
                str(python),
                "-c",
                (
                    "from pathlib import Path; from dovet.bundles import inspect_bundle; "
                    "from dovet.database import Ledger; "
                    "from dovet_supervisor.agent import EvidenceEnvelope; "
                    "from dovet_worker.tools import WorkerScope; "
                    "Ledger(Path('smoke-state.sqlite3')).migrate(); "
                    "assert callable(inspect_bundle); "
                    "assert EvidenceEnvelope({}).records == {}; "
                    "assert WorkerScope('x', Path('.'), frozenset(), 1).lease_generation == 1"
                ),
            )
        )
    OUTPUT.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "checked_at": datetime.now(UTC).isoformat(),
                "status": "PASS",
                "wheel": wheel.name,
                "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
                "cli_version": version,
                "packaged_schema_migration": "PASS",
                "supervisor_import": "PASS",
                "worker_import": "PASS",
                "checkpoint_bundle_import": "PASS",
                "temporary_environment_retained": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "artifact": str(OUTPUT.relative_to(ROOT))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
