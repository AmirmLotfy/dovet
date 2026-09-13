"""SQLite operational ledger and transactional invariants."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any


class Ledger:
    def __init__(self, path: Path, *, schema_path: Path | None = None) -> None:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = path
        self.schema_path = schema_path or self._find_schema()

    @staticmethod
    def _find_schema() -> Path:
        packaged = Path(__file__).with_name("schema.sql")
        if packaged.exists():
            return packaged
        checkout = Path(__file__).resolve().parents[4] / "handoff" / "contracts" / "schema.sql"
        if not checkout.exists():
            raise FileNotFoundError("Dovet schema.sql was not packaged")
        return checkout

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, isolation_level=None, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    def migrate(self) -> None:
        sql = self.schema_path.read_text(encoding="utf-8")
        checksum = hashlib.sha256(sql.encode()).hexdigest()
        with self.connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
            ).fetchone()
            if exists:
                row = connection.execute(
                    "SELECT checksum FROM schema_migrations WHERE version=1"
                ).fetchone()
                if row and row[0] != checksum:
                    raise RuntimeError("migration 1 checksum mismatch")
                return
            connection.executescript(sql)
            connection.execute(
                "INSERT INTO schema_migrations(version, applied_at, checksum) VALUES(1, ?, ?)",
                ("2026-09-13T00:00:00Z", checksum),
            )

    @contextmanager
    def transaction(self, *, immediate: bool = True) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
            yield connection
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()

    def append_event(
        self,
        *,
        event_id: str,
        run_id: str,
        event_type: str,
        source_kind: str,
        knowledge_kind: str,
        source_event_id: str,
        payload: dict[str, Any],
        observed_at: str,
    ) -> sqlite3.Row:
        with self.transaction() as connection:
            return self.append_event_in_transaction(
                connection,
                event_id=event_id,
                run_id=run_id,
                event_type=event_type,
                source_kind=source_kind,
                knowledge_kind=knowledge_kind,
                source_event_id=source_event_id,
                payload=payload,
                observed_at=observed_at,
            )

    def append_event_in_transaction(
        self,
        connection: sqlite3.Connection,
        *,
        event_id: str,
        run_id: str,
        event_type: str,
        source_kind: str,
        knowledge_kind: str,
        source_event_id: str,
        payload: dict[str, Any],
        observed_at: str,
    ) -> sqlite3.Row:
        """Append an idempotent event inside an existing mutation transaction."""
        existing = connection.execute(
            "SELECT * FROM run_events WHERE run_id=? AND source_kind=? AND source_event_id=?",
            (run_id, source_kind, source_event_id),
        ).fetchone()
        if existing:
            assert isinstance(existing, sqlite3.Row)
            return existing
        sequence = connection.execute(
            "SELECT COALESCE(MAX(seq), 0) + 1 FROM run_events WHERE run_id=?", (run_id,)
        ).fetchone()[0]
        connection.execute(
            """INSERT INTO run_events(
                id,run_id,seq,event_type,source_kind,knowledge_kind,source_event_id,
                payload_json,observed_at
            ) VALUES(?,?,?,?,?,?,?,?,?)""",
            (
                event_id,
                run_id,
                sequence,
                event_type,
                source_kind,
                knowledge_kind,
                source_event_id,
                json.dumps(payload, separators=(",", ":"), sort_keys=True),
                observed_at,
            ),
        )
        inserted = connection.execute("SELECT * FROM run_events WHERE id=?", (event_id,)).fetchone()
        assert isinstance(inserted, sqlite3.Row)
        return inserted
