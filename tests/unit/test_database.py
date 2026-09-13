from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from dovet.database import Ledger


def seed_run(connection: sqlite3.Connection) -> None:
    connection.execute(
        "INSERT INTO projects VALUES(?,?,?,?,?,?,?,?,?)",
        ("p1", "Fixture", "/fixture", "fingerprint", "approved", "managed", "t", "t", None),
    )
    connection.execute(
        "INSERT INTO project_policies VALUES(?,?,?,?,?,?,?,?)",
        ("pol1", "p1", 1, "{}", "a" * 64, "t", "owner", "t"),
    )
    connection.execute(
        "INSERT INTO provider_profiles VALUES(?,?,?,?,?,?,?,?,?,?)",
        ("provider1", "Codex", "codex", 1, "{}", None, "{}", None, "t", "t"),
    )
    connection.execute(
        "INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        ("task1", "p1", "pol1", "Task", "Objective", 1, "[]", "[]", "ready", "t", "t"),
    )
    connection.execute(
        "INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "run1",
            "task1",
            "provider1",
            None,
            1,
            "managed",
            "running",
            "b" * 40,
            "/work",
            None,
            None,
            None,
            None,
            1,
            None,
            None,
            None,
            "t",
        ),
    )


def test_migration_and_event_deduplication(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "state.sqlite3")
    ledger.migrate()
    ledger.migrate()
    with ledger.transaction() as connection:
        seed_run(connection)
    first = ledger.append_event(
        event_id="event1",
        run_id="run1",
        event_type="worker.started",
        source_kind="adapter",
        knowledge_kind="observed",
        source_event_id="provider-event-1",
        payload={"pid": 1},
        observed_at="t",
    )
    replay = ledger.append_event(
        event_id="event2",
        run_id="run1",
        event_type="worker.started",
        source_kind="adapter",
        knowledge_kind="observed",
        source_event_id="provider-event-1",
        payload={"pid": 2},
        observed_at="t",
    )
    assert first["id"] == replay["id"] == "event1"
    assert first["seq"] == 1


def test_transaction_rolls_back(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "state.sqlite3")
    ledger.migrate()
    with pytest.raises(RuntimeError):
        with ledger.transaction() as connection:
            connection.execute(
                "INSERT INTO projects VALUES(?,?,?,?,?,?,?,?,?)",
                ("p1", "Fixture", "/fixture", "fingerprint", "approved", "managed", "t", "t", None),
            )
            raise RuntimeError("abort")
    with ledger.connect() as connection:
        assert connection.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0


def test_foreign_key_rejects_bad_lineage(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "state.sqlite3")
    ledger.migrate()
    with pytest.raises(sqlite3.IntegrityError):
        with ledger.transaction() as connection:
            connection.execute(
                "INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                ("t", "missing", "missing", "x", "x", 1, "[]", "[]", "ready", "t", "t"),
            )
