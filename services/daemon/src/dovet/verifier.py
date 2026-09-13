"""Independent verification using immutable trusted command templates."""

from __future__ import annotations

import hashlib
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .canonical import digest_json


@dataclass(frozen=True)
class VerificationCommand:
    id: str
    argv: tuple[str, ...]
    timeout_seconds: int


@dataclass(frozen=True)
class VerificationResult:
    command_id: str
    exit_code: int | None
    duration_ms: int
    output: bytes
    output_sha256: str
    status: str
    suite_digest: str
    snapshot_sha256: str


def digest_tree(root: Path) -> str:
    entries: list[dict[str, object]] = []
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        entries.append(
            {
                "path": relative,
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return digest_json(entries)


class Verifier:
    def __init__(self, commands: dict[str, VerificationCommand]) -> None:
        self.commands = commands

    def run(
        self,
        command_id: str,
        *,
        candidate_root: Path,
        protected_suite: Path,
        expected_suite_digest: str,
        expected_snapshot_sha256: str,
        current_snapshot_sha256: str,
    ) -> VerificationResult:
        command = self.commands[command_id]
        suite_before = digest_tree(protected_suite)
        if suite_before != expected_suite_digest:
            return self._blocked(command_id, "tampered", suite_before, current_snapshot_sha256)
        if current_snapshot_sha256 != expected_snapshot_sha256:
            return self._blocked(
                command_id, "stale_snapshot", suite_before, current_snapshot_sha256
            )
        environment = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONDONTWRITEBYTECODE": "1",
            "DOVET_PROTECTED_SUITE": str(protected_suite),
        }
        started = time.monotonic()
        try:
            completed = subprocess.run(  # noqa: S603 - approved immutable argv only
                command.argv,
                cwd=candidate_root,
                env=environment,
                capture_output=True,
                timeout=command.timeout_seconds,
                check=False,
            )
            output = (completed.stdout + completed.stderr)[:1_000_000]
            exit_code = completed.returncode
            status = "passed" if exit_code == 0 else "failed"
        except subprocess.TimeoutExpired as error:
            output = ((error.stdout or b"") + (error.stderr or b""))[:1_000_000]
            exit_code = None
            status = "timeout"
        duration = int((time.monotonic() - started) * 1000)
        suite_after = digest_tree(protected_suite)
        if suite_after != expected_suite_digest:
            status = "tampered"
        return VerificationResult(
            command_id,
            exit_code,
            duration,
            output,
            hashlib.sha256(output).hexdigest(),
            status,
            suite_after,
            current_snapshot_sha256,
        )

    @staticmethod
    def _blocked(command_id: str, status: str, suite: str, snapshot: str) -> VerificationResult:
        output = status.encode()
        return VerificationResult(
            command_id,
            None,
            0,
            output,
            hashlib.sha256(output).hexdigest(),
            status,
            suite,
            snapshot,
        )
