"""Ledger durability (per-order cap + crash/conflict) and evaluation metrics tests."""

from __future__ import annotations

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash, committed_audit_count, get_refund, issue_refund
from lab8.metrics import summarize
from lab8.policy import order_refunded_vnd


def test_partial_refund_topup_crash_resume_preserves_order_cap(public_db):
    """Crash right after writing a top-up refund; resume must not double-pay or exceed the order cap."""
    conn = connect(public_db)
    try:
        with pytest.raises(InjectedCrash):
            issue_refund(conn, "C-014", 150000, crash_at="after_effect_before_checkpoint")

        resumed = issue_refund(conn, "C-014", 150000, crash_at=None)
        effect = get_refund(conn, "C-014")
        o515_total = order_refunded_vnd(conn, "O-515")
        audits = committed_audit_count(conn, "C-014")
    finally:
        conn.close()

    assert resumed["ok"] is True
    assert resumed["reason"] == "idempotent_replay"
    assert effect is not None
    assert int(effect["amount_vnd"]) == 120000
    assert o515_total == 150000
    assert audits == 1


def test_retry_conflict_after_partial_topup_keeps_original_amount(public_db):
    """Retrying a committed top-up claim with a smaller quote triggers amount_conflict and keeps old ledger."""
    conn = connect(public_db)
    try:
        first = issue_refund(conn, "C-014", 150000)
        second = issue_refund(conn, "C-014", 50000)
        effect = get_refund(conn, "C-014")
        o515_total = order_refunded_vnd(conn, "O-515")
        audits = committed_audit_count(conn, "C-014")
    finally:
        conn.close()

    assert first["ok"] is True
    assert second["ok"] is False
    assert second["conflict"] is True
    assert second["reason"] == "amount_conflict"
    assert effect is not None
    assert int(effect["amount_vnd"]) == 120000
    assert o515_total == 150000
    assert audits == 1


def test_summarize_zero_passes_and_p95_steps():
    """Zero passing trials yield None cost_per_success_vnd (no ZeroDivisionError) and valid p95_steps."""
    trials = []
    # 20 trials with steps 1..20 so ceil(0.95 * 20) - 1 = 18 -> sorted[18] == 19.0
    for idx in range(20):
        trials.append(
            {
                "shape": "single",
                "claim_id": f"C-{idx:03d}",
                "seed": 11 if idx < 10 else 22,
                "passed": False,
                "reason": "status denied != resolved",
                "cost_estimate": 15.0,
                "steps": idx + 1,
                "model_calls": 2,
                "tool_calls": 1,
            }
        )

    stats = summarize(trials)["single"]
    assert stats["trials"] == 20
    assert stats["graded_trials"] == 20
    assert stats["successes"] == 0
    assert stats["pass_rate"] == 0.0
    assert stats["pass_5"] == 0.0
    assert stats["seed_variance"] == 0.0
    assert stats["cost_per_success_vnd"] is None
    assert stats["total_simulated_cost_vnd"] == 300.0
    assert stats["p95_steps"] == 19.0
