from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from dovet.approvals import ApprovalError, ApprovalStore
from dovet.budget import BudgetError, BudgetStore
from dovet.database import Ledger
from dovet.leases import LeaseError, LeaseStore


def seed_control_state(connection: sqlite3.Connection) -> None:
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
    connection.execute(
        """INSERT INTO actions(
            id,run_id,checkpoint_id,policy_id,kind,request_json,explanation,
            evidence_ids_json,digest,idempotency_key,status,lease_generation,
            created_at,updated_at,dispatched_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            "action1",
            "run1",
            None,
            "pol1",
            "handoff",
            '{"command":"recover"}',
            "Observed interruption requires recovery.",
            "[]",
            "d" * 64,
            "idem-action1",
            "proposed",
            None,
            "t",
            "t",
            None,
        ),
    )
    connection.execute(
        """INSERT INTO budget_accounts(
            id,project_id,period_start,period_end,currency,ceiling_microusd,
            unknown_cost_action,approved_at,created_at
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        ("budget1", "p1", "t0", "t1", "USD", 1000, "pause", "t", "t"),
    )


@pytest.fixture
def control_ledger(tmp_path: Path) -> Ledger:
    ledger = Ledger(tmp_path / "state.sqlite3")
    ledger.migrate()
    with ledger.transaction() as connection:
        seed_control_state(connection)
    return ledger


def test_approval_is_hash_bound_single_use_and_rejects_replay(control_ledger: Ledger) -> None:
    approvals = ApprovalStore(control_ledger)
    with pytest.raises(ApprovalError, match="stale"):
        approvals.issue(
            approval_id="approval-bad",
            action_id="action1",
            action_digest="e" * 64,
            snapshot_sha256="s" * 64,
            nonce="bad-nonce",
            expires_at="2026-09-13T01:00:00Z",
            created_at="2026-09-13T00:00:00Z",
        )
    receipt = approvals.issue(
        approval_id="approval1",
        action_id="action1",
        action_digest="d" * 64,
        snapshot_sha256="s" * 64,
        nonce="secret-nonce",
        expires_at="2026-09-13T01:00:00Z",
        created_at="2026-09-13T00:00:00Z",
    )
    assert receipt.status == "pending"
    assert approvals.decide(
        nonce="secret-nonce",
        actor_id="owner",
        approve=True,
        decided_at="2026-09-13T00:10:00Z",
    ).status == "approved"
    with pytest.raises(ApprovalError, match="stale"):
        approvals.consume(
            approval_id="approval1",
            action_digest="d" * 64,
            snapshot_sha256="changed",
            consumed_at="2026-09-13T00:20:00Z",
        )
    assert approvals.consume(
        approval_id="approval1",
        action_digest="d" * 64,
        snapshot_sha256="s" * 64,
        consumed_at="2026-09-13T00:20:00Z",
    ).status == "consumed"
    with pytest.raises(ApprovalError, match="not consumable"):
        approvals.consume(
            approval_id="approval1",
            action_digest="d" * 64,
            snapshot_sha256="s" * 64,
            consumed_at="2026-09-13T00:21:00Z",
        )


def test_expired_approval_remains_expired_after_rejection(control_ledger: Ledger) -> None:
    approvals = ApprovalStore(control_ledger)
    approvals.issue(
        approval_id="approval-expired",
        action_id="action1",
        action_digest="d" * 64,
        snapshot_sha256="s" * 64,
        nonce="expired-nonce",
        expires_at="2026-09-13T01:00:00Z",
        created_at="2026-09-13T00:00:00Z",
    )
    with pytest.raises(ApprovalError, match="expired"):
        approvals.decide(
            nonce="expired-nonce",
            actor_id="owner",
            approve=True,
            decided_at="2026-09-13T01:00:00Z",
        )
    with control_ledger.connect() as connection:
        row = connection.execute(
            "SELECT status FROM approvals WHERE id='approval-expired'"
        ).fetchone()
        assert row is not None and row["status"] == "expired"


def test_lease_expiry_does_not_authorize_a_competing_writer(control_ledger: Ledger) -> None:
    leases = LeaseStore(control_ledger)
    first = leases.acquire(
        workspace_key="workspace1",
        run_id="run1",
        owner_instance_id="daemon-a",
        process_birth_id="birth-a",
        acquired_at="2026-09-13T00:00:00Z",
        expires_at="2026-09-13T00:01:00Z",
    )
    with pytest.raises(LeaseError, match="unconfirmed"):
        leases.acquire(
            workspace_key="workspace1",
            run_id="run1",
            owner_instance_id="daemon-b",
            process_birth_id="birth-b",
            acquired_at="2026-09-13T02:00:00Z",
            expires_at="2026-09-13T02:01:00Z",
            expected_generation=first.generation,
        )
    leases.confirm_stopped(
        workspace_key="workspace1",
        run_id="run1",
        generation=first.generation,
        stopped_at="2026-09-13T02:00:00Z",
    )
    second = leases.acquire(
        workspace_key="workspace1",
        run_id="run1",
        owner_instance_id="daemon-b",
        process_birth_id="birth-b",
        acquired_at="2026-09-13T02:00:01Z",
        expires_at="2026-09-13T02:01:01Z",
        expected_generation=first.generation,
    )
    assert second.generation == 2


def test_budget_rejects_unknown_over_cap_and_changed_replay(control_ledger: Ledger) -> None:
    budgets = BudgetStore(control_ledger)
    with pytest.raises(BudgetError, match="unknown"):
        budgets.reserve(
            reservation_id="reservation-unknown",
            budget_account_id="budget1",
            action_id="action1",
            amount_microusd=None,
            created_at="t",
        )
    with pytest.raises(BudgetError, match="ceiling"):
        budgets.reserve(
            reservation_id="reservation-over",
            budget_account_id="budget1",
            action_id="action1",
            amount_microusd=1001,
            created_at="t",
        )
    held = budgets.reserve(
        reservation_id="reservation1",
        budget_account_id="budget1",
        action_id="action1",
        amount_microusd=900,
        created_at="t",
    )
    replay = budgets.reserve(
        reservation_id="reservation-replay-id",
        budget_account_id="budget1",
        action_id="action1",
        amount_microusd=900,
        created_at="later",
    )
    assert held == replay
    with pytest.raises(BudgetError, match="amount changed"):
        budgets.reserve(
            reservation_id="reservation-change",
            budget_account_id="budget1",
            action_id="action1",
            amount_microusd=800,
            created_at="later",
        )
