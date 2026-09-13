"""Write an auditable hackathon deadline clock without external dependencies."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "deadline-status.json"
PACIFIC = ZoneInfo("America/Los_Angeles")
CAIRO = ZoneInfo("Africa/Cairo")
DEADLINE = datetime(2026, 9, 14, 17, 0, tzinfo=PACIFIC)
MEDIA_RESERVE = timedelta(hours=8)


def main() -> int:
    checked_at = datetime.now(tz=CAIRO)
    remaining = DEADLINE.astimezone(CAIRO) - checked_at
    remaining_seconds = max(0, int(remaining.total_seconds()))
    reserve_at = DEADLINE - MEDIA_RESERVE
    status = "CLOSED" if remaining_seconds == 0 else (
        "MEDIA_RESERVE" if checked_at >= reserve_at.astimezone(CAIRO) else "BUILD_WINDOW"
    )
    payload = {
        "status": status,
        "checked_at": checked_at.isoformat(),
        "deadline_pacific": DEADLINE.isoformat(),
        "deadline_cairo": DEADLINE.astimezone(CAIRO).isoformat(),
        "media_reserve_starts_cairo": reserve_at.astimezone(CAIRO).isoformat(),
        "remaining_seconds": remaining_seconds,
        "remaining_hours": round(remaining_seconds / 3600, 2),
        "source": "handoff/hackathon/REQUIREMENTS.md",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
