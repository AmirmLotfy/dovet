"""Narrow file and verification tools for the fallback worker."""

from __future__ import annotations

import os
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from dovet.canonical import sha256_bytes
from dovet.paths import resolve_beneath


@dataclass(frozen=True)
class WorkerScope:
    token: str
    root: Path
    allowed_paths: frozenset[str]
    lease_generation: int
    approved_commands: tuple[tuple[str, tuple[str, ...]], ...] = ()


@dataclass(frozen=True)
class CheckResult:
    command_id: str
    exit_code: int
    duration_ms: int
    output: str


class RestrictedTools:
    def __init__(
        self,
        scope: WorkerScope,
        *,
        current_lease_generation: Callable[[], int] | None = None,
        record: Callable[[str, dict[str, object]], None] | None = None,
    ) -> None:
        self.scope = scope
        self.current_lease_generation = current_lease_generation or (
            lambda: scope.lease_generation
        )
        self.record = record

    def _authorize(self, token: str) -> None:
        if token != self.scope.token:
            raise PermissionError("worker scope denied")
        if self.current_lease_generation() != self.scope.lease_generation:
            raise PermissionError("workspace lease changed")

    def _event(self, kind: str, payload: dict[str, object]) -> None:
        if self.record is not None:
            self.record(kind, payload)

    def _path(self, token: str, relative: str, *, allow_missing: bool = False) -> Path:
        self._authorize(token)
        if relative not in self.scope.allowed_paths:
            raise PermissionError("worker scope denied")
        return resolve_beneath(self.scope.root, relative, allow_missing=allow_missing)

    def list_files(self, token: str) -> list[str]:
        self._authorize(token)
        return sorted(self.scope.allowed_paths)

    def read_file(self, token: str, relative: str, expected_sha256: str | None = None) -> str:
        data = self._path(token, relative).read_bytes()
        if expected_sha256 is not None and sha256_bytes(data) != expected_sha256:
            raise RuntimeError("source hash changed")
        return data.decode("utf-8")

    def create_file(self, token: str, relative: str, content: str) -> str:
        path = self._path(token, relative, allow_missing=True)
        if path.exists():
            raise FileExistsError(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        digest = sha256_bytes(content.encode())
        self._event("file.created", {"path": relative, "sha256": digest})
        return digest

    def apply_patch(
        self, token: str, relative: str, base_sha256: str, unified_patch: str
    ) -> str:
        """Apply a bounded unified diff to one authorized UTF-8 file."""
        path = self._path(token, relative)
        data = path.read_bytes()
        if len(data) > 512_000 or len(unified_patch.encode()) > 512_000:
            raise ValueError("worker patch exceeds size limit")
        if sha256_bytes(data) != base_sha256:
            raise RuntimeError("source hash changed")
        source = data.decode("utf-8").splitlines(keepends=True)
        encoded = "".join(_apply_unified_hunks(source, unified_patch)).encode("utf-8")
        path.write_bytes(encoded)
        digest = sha256_bytes(encoded)
        self._event("file.patched", {"path": relative, "sha256": digest})
        return digest

    def run_check(self, token: str, command_id: str) -> CheckResult:
        self._authorize(token)
        argv = dict(self.scope.approved_commands).get(command_id)
        if argv is None:
            raise PermissionError("command is not approved")
        started = time.monotonic()
        completed = subprocess.run(
            argv,
            cwd=self.scope.root,
            env={
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "HOME": str(self.scope.root / ".worker-home"),
                "LANG": "C.UTF-8",
                "PYTHONDONTWRITEBYTECODE": "1",
            },
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        output = (completed.stdout + completed.stderr)[-16_000:]
        result = CheckResult(
            command_id=command_id,
            exit_code=completed.returncode,
            duration_ms=round((time.monotonic() - started) * 1000),
            output=output,
        )
        self._event("check.finished", {"command_id": command_id, "exit_code": completed.returncode})
        return result

    def report_milestone(self, token: str, summary: str, evidence_ids: list[str]) -> None:
        self._authorize(token)
        self._event("worker.milestone", {"summary": summary, "evidence_ids": evidence_ids})


def _apply_unified_hunks(source: list[str], patch: str) -> list[str]:
    lines = patch.splitlines(keepends=True)
    result: list[str] = []
    source_index = 0
    index = 0
    while index < len(lines) and not lines[index].startswith("@@ "):
        index += 1
    if index == len(lines):
        raise ValueError("patch has no unified hunks")
    while index < len(lines):
        header = lines[index].strip()
        if not header.startswith("@@ "):
            raise ValueError("unexpected patch content")
        old_range = header.split(" ")[1]
        target_index = max(int(old_range.split(",")[0][1:]) - 1, 0)
        if target_index < source_index:
            raise ValueError("overlapping patch hunks")
        result.extend(source[source_index:target_index])
        source_index = target_index
        index += 1
        while index < len(lines) and not lines[index].startswith("@@ "):
            line = lines[index]
            if line.startswith(" "):
                expected = line[1:]
                if source_index >= len(source) or source[source_index] != expected:
                    raise ValueError("patch context does not match")
                result.append(source[source_index])
                source_index += 1
            elif line.startswith("-"):
                expected = line[1:]
                if source_index >= len(source) or source[source_index] != expected:
                    raise ValueError("patch deletion does not match")
                source_index += 1
            elif line.startswith("+"):
                result.append(line[1:])
            elif line.startswith("\\ No newline"):
                pass
            else:
                raise ValueError("unsupported patch line")
            index += 1
    result.extend(source[source_index:])
    return result
