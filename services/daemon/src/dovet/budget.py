"""Transactional micro-USD budget reservations."""

from __future__ import annotations

from dataclasses import dataclass

from .database import Ledger


class BudgetError(RuntimeError):
    """A provider-cost reservation could not be made safely."""


@dataclass(frozen=True)
class Reservation:
    id: str
    action_id: str
    amount_microusd: int
    status: str


class BudgetStore:
    def __init__(self, ledger: Ledger) -> None:
        self.ledger = ledger

    def reserve(
        self,
        *,
        reservation_id: str,
        budget_account_id: str,
        action_id: str,
        amount_microusd: int | None,
        created_at: str,
    ) -> Reservation:
        if amount_microusd is None:
            raise BudgetError("provider cost is unknown")
        if amount_microusd < 0:
            raise BudgetError("provider cost cannot be negative")
        with self.ledger.transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM budget_reservations WHERE action_id=?", (action_id,)
            ).fetchone()
            if existing is not None:
                if existing["amount_microusd"] != amount_microusd:
                    raise BudgetError("idempotent reservation amount changed")
                return Reservation(
                    existing["id"], action_id, existing["amount_microusd"], existing["status"]
                )
            account = connection.execute(
                "SELECT ceiling_microusd FROM budget_accounts WHERE id=?", (budget_account_id,)
            ).fetchone()
            action = connection.execute(
                "SELECT run_id FROM actions WHERE id=?", (action_id,)
            ).fetchone()
            if account is None or action is None:
                raise BudgetError("budget account or action does not exist")
            committed = connection.execute(
                """SELECT COALESCE(SUM(amount_microusd),0) FROM budget_reservations
                   WHERE budget_account_id=? AND status IN ('held','settled','uncertain')""",
                (budget_account_id,),
            ).fetchone()[0]
            if committed + amount_microusd > account["ceiling_microusd"]:
                raise BudgetError("budget ceiling exceeded")
            connection.execute(
                "INSERT INTO budget_reservations VALUES(?,?,?,?,'held',?,NULL)",
                (reservation_id, budget_account_id, action_id, amount_microusd, created_at),
            )
            self.ledger.append_event_in_transaction(
                connection,
                event_id=f"ev-{reservation_id}-held",
                run_id=action["run_id"],
                event_type="budget.reserved",
                source_kind="policy",
                knowledge_kind="observed",
                source_event_id=f"budget:{reservation_id}:held",
                payload={"reservation_id": reservation_id, "amount_microusd": amount_microusd},
                observed_at=created_at,
            )
            return Reservation(reservation_id, action_id, amount_microusd, "held")
