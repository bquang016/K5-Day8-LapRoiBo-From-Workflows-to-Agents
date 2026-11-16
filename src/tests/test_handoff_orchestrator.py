from __future__ import annotations

import json

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.handoff import READONLY_TOOLS, WRITE_TOOLS
from lab8.shapes.orchestrator import run_claim


def _trace(result):
    with open(result.trace_path, encoding="utf-8") as handle:
        return json.load(handle)


def test_orchestrator_traces_only_a_sanitized_readonly_handoff(public_db):
    result = run_claim("C-010", seed=11, store_path=str(public_db))

    assert result.status == "resolved"
    body = _trace(result)
    assert body["run_id"] == result.run_id
    assert isinstance(body["events"], list)

    handoff = next(event["payload"] for event in body["events"] if event["kind"] == "handoff")
    assert set(handoff) == {
        "contract_version",
        "request_id",
        "claim_id",
        "principal_scope",
        "task",
        "facts",
        "allowed_tools",
        "max_output_tokens",
    }
    assert set(handoff["allowed_tools"]) <= READONLY_TOOLS
    assert not (set(handoff["allowed_tools"]) & WRITE_TOOLS)

    artifact = json.dumps(body, ensure_ascii=False)
    for forbidden in (
        "CANARY_SECRET_",
        "parent_secret",
        "raw_headers",
        "0901000107",
        "12 Le Loi Q1",
        "CANARY_INTERNAL_O107",
    ):
        assert forbidden not in artifact


def test_orchestrator_uses_host_for_approval_denial(public_db):
    result = run_claim("C-007", seed=11, store_path=str(public_db))
    conn = connect(public_db)
    try:
        denied = conn.execute(
            "SELECT COUNT(*) AS n FROM audit_events "
            "WHERE claim_id = 'C-007' AND event_type = 'policy_denied'"
        ).fetchone()["n"]
        refund = conn.execute(
            "SELECT 1 FROM refund_ledger WHERE claim_id = 'C-007'"
        ).fetchone()
    finally:
        conn.close()

    assert result.status == "denied"
    assert result.proposal_amount == 35_000
    assert denied == 1
    assert refund is None


def test_orchestrator_passes_full_quote_for_order_cap(public_db):
    result = run_claim("C-014", seed=11, store_path=str(public_db))

    assert result.status == "resolved"
    assert result.proposal_amount == 150_000
    assert result.refund_effects[0]["amount_vnd"] == 120_000


def test_orchestrator_propagates_crash_and_resume_is_idempotent(public_db):
    with pytest.raises(InjectedCrash):
        run_claim(
            "C-012",
            seed=11,
            store_path=str(public_db),
            crash_at="after_effect_before_checkpoint",
        )

    result = run_claim("C-012", seed=11, store_path=str(public_db))
    conn = connect(public_db)
    try:
        refund_count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'"
        ).fetchone()["n"]
        audit_count = conn.execute(
            "SELECT COUNT(*) AS n FROM audit_events "
            "WHERE claim_id = 'C-012' AND event_type = 'refund_committed'"
        ).fetchone()["n"]
    finally:
        conn.close()

    assert result.status == "resolved"
    assert refund_count == 1
    assert audit_count == 1
