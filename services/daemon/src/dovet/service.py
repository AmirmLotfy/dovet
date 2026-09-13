"""Opt-in launchd lifecycle for the independent Dovet daemon."""

from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

LABEL = "site.dovet.supervisor"


def _plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def _data_root() -> Path:
    return Path.home() / "Library" / "Application Support" / "Dovet"


def _write_plist() -> Path:
    executable = shutil.which("dovet") or sys.argv[0]
    root = _data_root()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    logs = root / "logs"
    logs.mkdir(mode=0o700, exist_ok=True)
    target = _plist_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    body = {
        "Label": LABEL,
        "ProgramArguments": [
            executable,
            "serve",
        ],
        "RunAtLoad": True,
        "KeepAlive": False,
        "WorkingDirectory": str(root),
        "StandardOutPath": str(logs / "daemon.stdout.log"),
        "StandardErrorPath": str(logs / "daemon.stderr.log"),
        "ProcessType": "Background",
        "Umask": 0o077,
    }
    codex = shutil.which("codex")
    if codex is not None:
        body["EnvironmentVariables"] = {"DOVET_CODEX_BIN": codex}
    temporary = target.with_suffix(".plist.tmp")
    temporary.write_bytes(plistlib.dumps(body, sort_keys=True))
    os.chmod(temporary, 0o600)
    os.replace(temporary, target)
    return target


def service_command(action: str) -> int:
    target = _plist_path()
    domain = f"gui/{os.getuid()}"
    if action == "install":
        _write_plist()
        print(f"Installed {LABEL}. Start it explicitly with: dovet service start")
        return 0
    if action == "start":
        if not target.exists():
            print("Service is not installed", file=sys.stderr)
            return 1
        enabled = subprocess.run(
            ("launchctl", "enable", f"{domain}/{LABEL}"), check=False
        ).returncode  # noqa: S603
        if enabled != 0:
            return enabled
        return subprocess.run(
            ("launchctl", "bootstrap", domain, str(target)), check=False
        ).returncode  # noqa: S603
    if action == "stop":
        return subprocess.run(("launchctl", "bootout", f"{domain}/{LABEL}"), check=False).returncode  # noqa: S603
    if action == "status":
        result = subprocess.run(
            ("launchctl", "print", f"{domain}/{LABEL}"), capture_output=True, check=False
        )  # noqa: S603
        print("running" if result.returncode == 0 else "stopped")
        return 0
    if action == "uninstall":
        subprocess.run(
            ("launchctl", "bootout", f"{domain}/{LABEL}"), capture_output=True, check=False
        )  # noqa: S603
        target.unlink(missing_ok=True)
        print("Service removed. Checkpoints and repositories were preserved.")
        return 0
    return 2
