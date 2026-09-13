from __future__ import annotations

from datetime import UTC, datetime, timedelta

from dovet.usage import (
    CodexUsageReader,
    PreservationLevel,
    UsageState,
    parse_rate_limits,
    preservation_advice,
)


def observed() -> datetime:
    return datetime(2026, 9, 13, tzinfo=UTC)


def test_usage_parser_prefers_multi_bucket_and_never_invents_missing_values() -> None:
    snapshot = parse_rate_limits(
        {
            "accountId": "must-not-be-retained",
            "rateLimitsByLimitId": {
                "codex": {
                    "primary": {
                        "usedPercent": 76,
                        "windowDurationMins": 300,
                        "resetsAt": 1_800_000_000,
                    },
                    "secondary": {"usedPercent": 20},
                }
            },
        },
        observed_at=observed(),
    )
    assert snapshot.state == UsageState.KNOWN
    assert [window.remaining_percent for window in snapshot.windows] == [24, 80]
    assert "account" not in str(snapshot.public_dict()).casefold()
    assert preservation_advice(snapshot).level == PreservationLevel.PREPARE

    missing = parse_rate_limits({"rateLimits": None}, observed_at=observed())
    assert missing.state == UsageState.UNKNOWN
    assert missing.windows == ()
    assert preservation_advice(missing).level == PreservationLevel.UNKNOWN


def test_stale_usage_becomes_unknown_for_automatic_action() -> None:
    snapshot = parse_rate_limits(
        {"rateLimits": {"primary": {"usedPercent": 90}}}, observed_at=observed()
    )
    stale = snapshot.with_freshness(
        now=observed() + timedelta(seconds=61), maximum_age_seconds=60
    )
    assert stale.state == UsageState.STALE
    advice = preservation_advice(stale)
    assert advice.level == PreservationLevel.UNKNOWN
    assert advice.pause_managed_run_requested is False


def test_pause_advice_is_explicitly_scoped_to_managed_runs() -> None:
    snapshot = parse_rate_limits(
        {"rateLimits": {"primary": {"usedPercent": 90}}}, observed_at=observed()
    )
    advice = preservation_advice(snapshot)
    assert advice.level == PreservationLevel.PAUSE
    assert advice.checkpoint_requested is True
    assert advice.pause_managed_run_requested is True
    assert "only a Dovet-managed run" in advice.reason


def test_reader_uses_service_pinned_codex_path(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("DOVET_CODEX_BIN", "/approved/codex")
    assert CodexUsageReader().codex_bin == "/approved/codex"
