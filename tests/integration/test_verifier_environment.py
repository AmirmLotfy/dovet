from __future__ import annotations

import sys
from pathlib import Path

from dovet.verifier import VerificationCommand, Verifier, digest_tree


def test_verifier_binds_candidate_root_without_inheriting_user_home(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    suite = tmp_path / "protected"
    candidate.mkdir()
    suite.mkdir()
    (suite / "contract.txt").write_text("trusted suite\n", encoding="utf-8")
    command = VerificationCommand(
        id="environment",
        argv=(
            sys.executable,
            "-c",
            (
                "import os, pathlib; "
                "root = pathlib.Path(os.environ['DOVET_CANDIDATE_ROOT']); "
                "home = pathlib.Path(os.environ['HOME']); "
                "assert root == pathlib.Path.cwd(); "
                "assert home == root / '.verifier-home'"
            ),
        ),
        timeout_seconds=5,
    )
    verifier = Verifier({command.id: command})

    result = verifier.run(
        command.id,
        candidate_root=candidate,
        protected_suite=suite,
        expected_suite_digest=digest_tree(suite),
        expected_snapshot_sha256="a" * 64,
        current_snapshot_sha256="a" * 64,
    )

    assert result.status == "passed"
