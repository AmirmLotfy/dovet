"""Durable, hash-bound, one-use approval records."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .database import Ledger


class ApprovalError(RuntimeError):
    """Approval cannot be issued, decided, or consumed safely."""


@dataclass(frozen=True)
class ApprovalReceipt:
    id: str
    status: str
    action_id: str


class ApprovalStore:
    def __init__(self, ledger: Ledger) -> None:
        self.ledger = ledger

    @staticmethod
    def _nonce_hash(nonce: str) -> str:
        return hashlib.sha256(nonce.encode()).hexdigest()

    def issue(
        self,
        *,
        approval_id: str,
        action_id: str,
        action_digest: str,
        snapshot_sha256: str,
        nonce: str,
        expires_at: str,
        created_at: str,
    ) -> ApprovalReceipt:
        with self.ledger.transaction() as connection:
            action = connection.execute(
                "SELECT run_id,digest FROM actions WHERE id=?", (action_id,)
            ).fetchone()
            if action is None or action["digest"] != action_digest:
                raise ApprovalError("action digest is stale")
            existing = connection.execute(
                "SELECT * FROM approvals WHERE action_id=?", (action_id,)
            ).fetchone()
            if existing is not None:
                if (
                    existing["action_digest"] != action_digest
                    or existing["snapshot_sha256"] != snapshot_sha256
                ):
                    raise ApprovalError("existing approval is bound to different state")
                return ApprovalReceipt(existing["id"], existing["status"], action_id)
            connection.execute(
                """INSERT INTO approvals(
                    id,action_id,action_digest,snapshot_sha256,nonce_hash,status,
                    actor_id,expires_at,decided_at,consumed_at,created_at
                ) VALUES(?,?,?,?,?,'pending',NULL,?,NULL,NULL,?)""",
                (
                    approval_id,
                    action_id,
                    action_digest,
                    snapshot_sha256,
                    self._nonce_hash(nonce),
                    expires_at,
                    created_at,
                ),
            )
            self.ledger.append_event_in_transaction(
                connection,
                event_id=f"ev-{approval_id}-issued",
                run_id=action["run_id"],
                event_type="approval.issued",
                source_kind="system",
                knowledge_kind="observed",
                source_event_id=f"approval:{approval_id}:issued",
                payload={"approval_id": approval_id, "action_id": action_id},
                observed_at=created_at,
            )
            return ApprovalReceipt(approval_id, "pending", action_id)

    def decide(
        self, *, nonce: str, actor_id: str, approve: bool, decided_at: str
    ) -> ApprovalReceipt:
        expired = False
        receipt: ApprovalReceipt
        with self.ledger.transaction() as connection:
            row = connection.execute(
                """SELECT approvals.*,actions.run_id FROM approvals
                   JOIN actions ON actions.id=approvals.action_id WHERE nonce_hash=?""",
                (self._nonce_hash(nonce),),
            ).fetchone()
            if row is None:
                raise ApprovalError("approval nonce is invalid")
            if row["status"] != "pending":
                raise ApprovalError("approval was already decided")
            if decided_at >= row["expires_at"]:
                connection.execute(
                    "UPDATE approvals SET status='expired',decided_at=? WHERE id=?",
                    (decided_at, row["id"]),
                )
                self.ledger.append_event_in_transaction(
                    connection,
                    event_id=f"ev-{row['id']}-expired",
                    run_id=row["run_id"],
                    event_type="approval.expired",
                    source_kind="system",
                    knowledge_kind="observed",
                    source_event_id=f"approval:{row['id']}:expired",
                    payload={"approval_id": row["id"]},
                    observed_at=decided_at,
                )
                expired = True
                receipt = ApprovalReceipt(row["id"], "expired", row["action_id"])
            else:
                decision = "approved" if approve else "denied"
                connection.execute(
                    "UPDATE approvals SET status=?,actor_id=?,decided_at=? WHERE id=?",
                    (decision, actor_id, decided_at, row["id"]),
                )
                self.ledger.append_event_in_transaction(
                    connection,
                    event_id=f"ev-{row['id']}-{decision}",
                    run_id=row["run_id"],
                    event_type=f"approval.{decision}",
                    source_kind="human",
                    knowledge_kind="observed",
                    source_event_id=f"approval:{row['id']}:{decision}",
                    payload={"approval_id": row["id"], "actor_id": actor_id},
                    observed_at=decided_at,
                )
                receipt = ApprovalReceipt(row["id"], decision, row["action_id"])
        if expired:
            raise ApprovalError("approval expired")
        return receipt

    def consume(
        self,
        *,
        approval_id: str,
        action_digest: str,
        snapshot_sha256: str,
        consumed_at: str,
    ) -> ApprovalReceipt:
        with self.ledger.transaction() as connection:
            row = connection.execute(
                """SELECT approvals.*,actions.run_id FROM approvals
                   JOIN actions ON actions.id=approvals.action_id WHERE approvals.id=?""",
                (approval_id,),
            ).fetchone()
            if row is None:
                raise ApprovalError("approval does not exist")
            if row["status"] != "approved":
                raise ApprovalError("approval is not consumable")
            if consumed_at >= row["expires_at"]:
                raise ApprovalError("approval expired")
            if row["action_digest"] != action_digest or row["snapshot_sha256"] != snapshot_sha256:
                raise ApprovalError("approval is bound to stale state")
            updated = connection.execute(
                """UPDATE approvals SET status='consumed',consumed_at=?
                   WHERE id=? AND status='approved'""",
                (consumed_at, approval_id),
            )
            if updated.rowcount != 1:
                raise ApprovalError("approval replay detected")
            self.ledger.append_event_in_transaction(
                connection,
                event_id=f"ev-{approval_id}-consumed",
                run_id=row["run_id"],
                event_type="approval.consumed",
                source_kind="system",
                knowledge_kind="observed",
                source_event_id=f"approval:{approval_id}:consumed",
                payload={"approval_id": approval_id, "action_id": row["action_id"]},
                observed_at=consumed_at,
            )
            return ApprovalReceipt(approval_id, "consumed", row["action_id"])
