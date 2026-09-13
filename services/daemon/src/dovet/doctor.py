"""Read-only capability inspection without credential disclosure."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    status: str
    detail: str


def _version(name: str, argv: tuple[str, ...]) -> DoctorCheck:
    path = shutil.which(argv[0])
    if path is None:
        return DoctorCheck(name, "blocked", "executable not found")
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=10, check=False)  # noqa: S603
    detail = (completed.stdout or completed.stderr).strip().splitlines()[0]
    return DoctorCheck(name, "ready" if completed.returncode == 0 else "blocked", detail)


def run_doctor() -> list[DoctorCheck]:
    checks = [
        _version("codex", ("codex", "--version")),
        _version("python", ("python3", "--version")),
        _version("node", ("node", "--version")),
        _version("uv", ("uv", "--version")),
        _version("git", ("git", "--version")),
        _version("aws", ("aws", "--version")),
        _version("ffmpeg", ("ffmpeg", "-version")),
        _version("vercel", ("vercel", "--version")),
    ]
    aws = subprocess.run(
        ("aws", "sts", "get-caller-identity", "--output", "json", "--no-cli-pager"),
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    checks.append(
        DoctorCheck(
            "aws_credentials",
            "ready" if aws.returncode == 0 else "blocked",
            "authenticated identity available"
            if aws.returncode == 0
            else "credentials unavailable or expired",
        )
    )
    return checks


def doctor_json() -> str:
    return json.dumps([asdict(check) for check in run_doctor()], indent=2)
