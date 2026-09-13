"""Owned process-group lifecycle with birth-time verification."""

from __future__ import annotations

import os
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import psutil


@dataclass(frozen=True)
class OwnedProcess:
    pid: int
    create_time: float
    process_group: int

    @property
    def birth_id(self) -> str:
        return f"{self.pid}:{self.create_time:.6f}"


class WorkerStillActiveError(RuntimeError):
    pass


class ProcessManager:
    def start(
        self,
        argv: tuple[str, ...],
        *,
        cwd: Path,
        environment: dict[str, str],
    ) -> OwnedProcess:
        if not argv or any("\x00" in part for part in argv):
            raise ValueError("worker argv is invalid")
        process = subprocess.Popen(  # noqa: S603 - argv is a trusted template
            argv,
            cwd=cwd,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        observed = psutil.Process(process.pid)
        return OwnedProcess(process.pid, observed.create_time(), os.getpgid(process.pid))

    def is_same_process(self, owned: OwnedProcess) -> bool:
        try:
            process = psutil.Process(owned.pid)
            return abs(process.create_time() - owned.create_time) < 0.001 and process.is_running()
        except psutil.Error:
            return False

    def stop_confirmed(
        self,
        owned: OwnedProcess,
        *,
        graceful_seconds: float = 3,
        kill_seconds: float = 2,
    ) -> bool:
        if not self.is_same_process(owned):
            return True
        os.killpg(owned.process_group, signal.SIGTERM)
        if self._wait_group_exit(owned, graceful_seconds):
            return True
        if not self.is_same_process(owned):
            return True
        os.killpg(owned.process_group, signal.SIGKILL)
        if self._wait_group_exit(owned, kill_seconds):
            return True
        raise WorkerStillActiveError(f"owned process group {owned.process_group} did not stop")

    def _wait_group_exit(self, owned: OwnedProcess, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            members = []
            for process in psutil.process_iter(["pid"]):
                try:
                    if (
                        os.getpgid(process.pid) == owned.process_group
                        and process.status() != psutil.STATUS_ZOMBIE
                    ):
                        members.append(process.pid)
                except (OSError, psutil.Error):
                    continue
            if not members:
                return True
            time.sleep(0.02)
        return False
