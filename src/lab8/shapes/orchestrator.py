"""Shape C — orchestrator plus read-only investigators.

The parent reads only the safe claim view, delegates structured lookups through
``handoff.v1``, and remains the sole caller of the host refund boundary. Raw
claim rows, parent secrets, headers, and ticket text are never put in a handoff
or trace.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.handoff import make_handoff
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace


INVESTIGATOR_TOOLS = [
    "lookup_order",
    "lookup_policy",
    "lookup_refund_history",
    "compute_compensation",
]


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    """Run one claim while keeping delegation read-only and sanitized."""
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(
    conn: sqlite3.Connection,
    claim_id: str,
    *,
    seed: int,
    crash_at: str | None,
) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id("orchestrator", claim_id, seed))

    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    trace.add(
        "claim_lookup",
        {
            "found": bool(claim.get("found")),
            "claim_id": claim_id,
            "has_order_id": bool(claim.get("order_id")),
        },
    )

    if not claim.get("found"):
        trace.add("decision", {"status": "failed", "reason": "unknown_claim"})
        return finish(
            conn,
            shape="orchestrator",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )

    if not claim.get("order_id"):
        trace.add("decision", {"status": "needs_info", "reason": "missing_order_id"})
        return finish(
            conn,
            shape="orchestrator",
            claim_id=claim_id,
            seed=seed,
            status="needs_info",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="missing_order_id",
        )

    # Facts stay empty: structured, scoped read tools provide all evidence.
    # Ticket text and parent context therefore never cross this boundary.
    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="verify_order_and_compute_entitlement",
        facts={},
        allowed_tools=INVESTIGATOR_TOOLS,
    )
    trace.add("handoff", safe_dump(handoff))

    investigated = run_readonly_investigators(
        conn,
        budget,
        handoff,
        principal_id=str(claim["principal_id"]),
    )
    tools = investigated["tools"]
    order_view = tools.get("lookup_order") or {}
    trace.add(
        "investigation",
        {
            "order_visible": bool(order_view.get("visible")),
            "order_reason": order_view.get("reason"),
            "policy_count": len((tools.get("lookup_policy") or {}).get("policies") or []),
            "refund_history_visible": bool(
                (tools.get("lookup_refund_history") or {}).get("visible")
            ),
        },
    )

    if not order_view.get("visible"):
        reason = str(order_view.get("reason") or "order_not_visible")
        trace.add("decision", {"status": "escalated", "reason": reason})
        return finish(
            conn,
            shape="orchestrator",
            claim_id=claim_id,
            seed=seed,
            status="escalated",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    quote = tools.get("compute_compensation") or {
        "amount_vnd": 0,
        "reason": "quote_unavailable",
        "clause_ids": [],
        "parts": {},
    }
    proposal = int(quote.get("amount_vnd") or 0)
    trace.add(
        "quote",
        {
            "amount_vnd": proposal,
            "reason": quote.get("reason"),
            "clause_ids": list(quote.get("clause_ids") or []),
            "parts": dict(quote.get("parts") or {}),
        },
    )

    if proposal <= 0:
        reason = str(quote.get("reason") or "no_entitlement")
        trace.add("decision", {"status": "denied", "reason": reason})
        return finish(
            conn,
            shape="orchestrator",
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    # The host binds approval to this claim and applies the per-order cap.
    outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    trace.add(
        "host_outcome",
        {
            "ok": bool(outcome.get("ok")),
            "reason": outcome.get("reason"),
            "conflict": bool(outcome.get("conflict")),
        },
    )

    if not outcome["ok"]:
        status = "failed" if outcome.get("conflict") else "denied"
        trace.add("decision", {"status": status, "reason": outcome.get("reason")})
        return finish(
            conn,
            shape="orchestrator",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=str(outcome.get("reason") or "refund_rejected"),
        )

    trace.add("decision", {"status": "resolved", "reason": outcome.get("reason")})
    return finish(
        conn,
        shape="orchestrator",
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )
