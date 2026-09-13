"""Conservative Codex usage observation and managed-run preservation policy."""

from __future__ import annotations

import json
import os
import selectors
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class UsageState(StrEnum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    STALE = "stale"
    UNAVAILABLE = "unavailable"


class PreservationLevel(StrEnum):
    NORMAL = "normal"
    PREPARE = "prepare"
    PAUSE = "pause"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class UsageWindow:
    limit_id: str
    window: str
    used_percent: float
    remaining_percent: float
    window_minutes: int | None
    resets_at: int | None


@dataclass(frozen=True)
class UsageSnapshot:
    observed_at: datetime
    state: UsageState
    windows: tuple[UsageWindow, ...]
    source: str = "codex-app-server"
    error: str | None = None

    def public_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["observed_at"] = self.observed_at.isoformat()
        value["state"] = self.state.value
        return value

    def with_freshness(self, *, now: datetime, maximum_age_seconds: int) -> UsageSnapshot:
        age = (now - self.observed_at).total_seconds()
        if self.state == UsageState.KNOWN and (age < 0 or age > maximum_age_seconds):
            return UsageSnapshot(
                observed_at=self.observed_at,
                state=UsageState.STALE,
                windows=self.windows,
                source=self.source,
                error="usage observation is stale",
            )
        return self


@dataclass(frozen=True)
class PreservationAdvice:
    level: PreservationLevel
    checkpoint_requested: bool
    pause_managed_run_requested: bool
    reason: str


def preservation_advice(snapshot: UsageSnapshot) -> PreservationAdvice:
    """Advise preservation; execution still requires Dovet managed-run policy."""
    if snapshot.state != UsageState.KNOWN or not snapshot.windows:
        return PreservationAdvice(
            PreservationLevel.UNKNOWN,
            checkpoint_requested=False,
            pause_managed_run_requested=False,
            reason="Codex usage is unknown; no automatic interruption is authorized.",
        )
    remaining = min(window.remaining_percent for window in snapshot.windows)
    if remaining <= 5:
        level = PreservationLevel.CRITICAL
    elif remaining <= 15:
        level = PreservationLevel.PAUSE
    elif remaining <= 25:
        level = PreservationLevel.PREPARE
    else:
        level = PreservationLevel.NORMAL
    return PreservationAdvice(
        level,
        checkpoint_requested=level != PreservationLevel.NORMAL,
        pause_managed_run_requested=level in {PreservationLevel.PAUSE, PreservationLevel.CRITICAL},
        reason=(
            f"Lowest observed Codex window has {remaining:g}% remaining; "
            "only a Dovet-managed run may be paused."
        ),
    )


def parse_rate_limits(result: object, *, observed_at: datetime | None = None) -> UsageSnapshot:
    now = observed_at or datetime.now(UTC)
    if not isinstance(result, dict):
        return UsageSnapshot(now, UsageState.UNKNOWN, (), error="usage response is missing")
    raw_buckets = result.get("rateLimitsByLimitId")
    if not isinstance(raw_buckets, dict) or not raw_buckets:
        legacy = result.get("rateLimits")
        if isinstance(legacy, dict):
            limit_id = legacy.get("limitId")
            raw_buckets = {str(limit_id or "codex"): legacy}
        else:
            return UsageSnapshot(now, UsageState.UNKNOWN, (), error="usage windows are missing")
    windows: list[UsageWindow] = []
    for limit_id, bucket in sorted(raw_buckets.items()):
        if not isinstance(bucket, dict):
            continue
        for name in ("primary", "secondary"):
            raw = bucket.get(name)
            if not isinstance(raw, dict):
                continue
            used = raw.get("usedPercent")
            if isinstance(used, bool) or not isinstance(used, (int, float)):
                continue
            used_float = float(used)
            if not 0 <= used_float <= 100:
                continue
            duration = raw.get("windowDurationMins")
            resets_at = raw.get("resetsAt")
            windows.append(
                UsageWindow(
                    limit_id=str(limit_id),
                    window=name,
                    used_percent=used_float,
                    remaining_percent=100 - used_float,
                    window_minutes=duration if isinstance(duration, int) else None,
                    resets_at=resets_at if isinstance(resets_at, int) else None,
                )
            )
    if not windows:
        return UsageSnapshot(now, UsageState.UNKNOWN, (), error="usage values are missing")
    return UsageSnapshot(now, UsageState.KNOWN, tuple(windows))


class CodexUsageReader:
    """Read the installed Codex app-server protocol without accessing auth files."""

    def __init__(self, codex_bin: str | None = None, *, timeout_seconds: float = 8) -> None:
        self.codex_bin = (
            codex_bin or os.environ.get("DOVET_CODEX_BIN") or shutil.which("codex") or "codex"
        )
        self.timeout_seconds = timeout_seconds

    def _response(self, process: subprocess.Popen[str], request_id: int) -> dict[str, Any]:
        assert process.stdout is not None
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        deadline = time.monotonic() + self.timeout_seconds
        try:
            while time.monotonic() < deadline:
                ready = selector.select(max(0, deadline - time.monotonic()))
                if not ready:
                    break
                line = process.stdout.readline()
                if not line:
                    break
                message = json.loads(line)
                if isinstance(message, dict) and message.get("id") == request_id:
                    return message
        finally:
            selector.close()
        raise TimeoutError("Codex app-server response timed out")

    @staticmethod
    def _send(process: subprocess.Popen[str], message: dict[str, object]) -> None:
        assert process.stdin is not None
        process.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
        process.stdin.flush()

    def read(self) -> UsageSnapshot:
        process: subprocess.Popen[str] | None = None
        try:
            process = subprocess.Popen(  # noqa: S603
                (self.codex_bin, "app-server", "--stdio"),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )
            self._send(
                process,
                {
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "clientInfo": {
                            "name": "dovet",
                            "title": "Dovet usage observer",
                            "version": "0.1.0",
                        },
                        "capabilities": {"experimentalApi": True},
                    },
                },
            )
            initialized = self._response(process, 1)
            if "error" in initialized:
                raise RuntimeError("Codex app-server initialization failed")
            self._send(process, {"method": "initialized", "params": {}})
            self._send(
                process,
                {
                    "id": 2,
                    "method": "account/rateLimits/read",
                    "params": {"excludeResetCreditDetails": True},
                },
            )
            response = self._response(process, 2)
            if "error" in response:
                raise RuntimeError("Codex usage read failed")
            return parse_rate_limits(response.get("result"))
        except (OSError, RuntimeError, TimeoutError, json.JSONDecodeError):
            return UsageSnapshot(
                datetime.now(UTC),
                UsageState.UNAVAILABLE,
                (),
                error="Codex usage is unavailable",
            )
        finally:
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=2)
