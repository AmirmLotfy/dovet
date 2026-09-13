"""Single-writer leases that require confirmed old-worker termination."""

from __future__ import annotations

from dataclasses import dataclass

from .database import Ledger


class LeaseError(RuntimeError):
    """A workspace writer lease transition was rejected."""


@dataclass(frozen=True)
class Lease:
    workspace_key: str
    run_id: str
    generation: int
    owner_instance_id: str


class LeaseStore:
    def __init__(self, ledger: Ledger) -> None:
        self.ledger = ledger

    def acquire(
        self,
        *,
        workspace_key: str,
        run_id: str,
        owner_instance_id: str,
        process_birth_id: str,
        acquired_at: str,
        expires_at: str,
        expected_generation: int | None = None,
    ) -> Lease:
        with self.ledger.transaction() as connection:
            current = connection.execute(
                "SELECT * FROM workspace_leases WHERE workspace_key=?", (workspace_key,)
            ).fetchone()
            if current is None:
                generation = 1
                connection.execute(
                    """INSERT INTO workspace_leases VALUES(?,?,?,?,?,?,?,?,NULL)""",
                    (
                        workspace_key,
                        run_id,
                        generation,
                        owner_instance_id,
                        process_birth_id,
                        acquired_at,
                        acquired_at,
                        expires_at,
                    ),
                )
            else:
                if (
                    current["run_id"] == run_id
                    and current["owner_instance_id"] == owner_instance_id
                ):
                    return Lease(workspace_key, run_id, current["generation"], owner_instance_id)
                if current["prior_writer_stopped_at"] is None:
                    raise LeaseError("prior writer termination is unconfirmed")
                if expected_generation != current["generation"]:
                    raise LeaseError("lease generation changed")
                generation = current["generation"] + 1
                updated = connection.execute(
                    """UPDATE workspace_leases SET
                       run_id=?,generation=?,owner_instance_id=?,process_birth_id=?,
                       acquired_at=?,heartbeat_at=?,expires_at=?,prior_writer_stopped_at=NULL
                       WHERE workspace_key=? AND generation=?
                       AND prior_writer_stopped_at IS NOT NULL""",
                    (
                        run_id,
                        generation,
                        owner_instance_id,
                        process_birth_id,
                        acquired_at,
                        acquired_at,
                        expires_at,
                        workspace_key,
                        expected_generation,
                    ),
                )
                if updated.rowcount != 1:
                    raise LeaseError("competing writer won the lease")
            self.ledger.append_event_in_transaction(
                connection,
                event_id=f"ev-lease-{workspace_key}-{generation}",
                run_id=run_id,
                event_type="lease.acquired",
                source_kind="system",
                knowledge_kind="observed",
                source_event_id=f"lease:{workspace_key}:{generation}",
                payload={"workspace_key": workspace_key, "generation": generation},
                observed_at=acquired_at,
            )
            return Lease(workspace_key, run_id, generation, owner_instance_id)

    def confirm_stopped(
        self,
        *,
        workspace_key: str,
        run_id: str,
        generation: int,
        stopped_at: str,
    ) -> None:
        with self.ledger.transaction() as connection:
            updated = connection.execute(
                """UPDATE workspace_leases SET prior_writer_stopped_at=?,heartbeat_at=?
                   WHERE workspace_key=? AND run_id=? AND generation=?
                   AND prior_writer_stopped_at IS NULL""",
                (stopped_at, stopped_at, workspace_key, run_id, generation),
            )
            if updated.rowcount != 1:
                raise LeaseError("lease stop confirmation is stale")
            self.ledger.append_event_in_transaction(
                connection,
                event_id=f"ev-lease-{workspace_key}-{generation}-stopped",
                run_id=run_id,
                event_type="lease.writer_stopped",
                source_kind="system",
                knowledge_kind="verified",
                source_event_id=f"lease:{workspace_key}:{generation}:stopped",
                payload={"workspace_key": workspace_key, "generation": generation},
                observed_at=stopped_at,
            )
