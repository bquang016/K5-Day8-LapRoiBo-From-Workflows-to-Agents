"""Shape B: bounded single-agent read loop; all money and writes stay in code."""

from __future__ import annotations

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, make_run_id
from lab8.shapes.common import finish
from lab8.tools import tool_cost
from lab8.trace import Trace


def run_claim(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None):
    conn = connect(store_path)
    try:
        budget = Budget()
        trace = Trace(make_run_id("single", claim_id, seed))
        observation = {"claim_id": claim_id}

        def decide(seen):
            # MockLLM contributes measured model cost; deterministic policy code chooses tools.
            complete(budget, seed=seed, purpose="react", prompt=str(seen))
            name, result = seen.get("last_tool"), seen.get("last_result")
            if name == "get_claim_view":
                trace.add("tool", {"tool": name, "found": bool(result.get("found")), "order_id": result.get("order_id")})
            elif name == "lookup_order":
                trace.add("tool", {"tool": name, "visible": bool(result.get("visible")), "reason": result.get("reason"), "order": result.get("order")})
            elif name == "compute_compensation":
                trace.add("tool", {"tool": name, "result": result})
            if name is None:
                return {"tool": "get_claim_view", "args": {"claim_id": claim_id}}
            if name == "get_claim_view":
                if not result.get("found"):
                    return {"final": {"status": "failed", "error_reason": "unknown_claim"}}
                if not result.get("order_id"):
                    return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}
                return {"tool": "lookup_order", "args": {"order_id": result["order_id"], "principal_id": result["principal_id"]}}
            if name == "lookup_order":
                if not result.get("visible"):
                    return {"final": {"status": "escalated", "error_reason": result.get("reason")}}
                return {"tool": "compute_compensation", "args": {"order": result["order"]}}
            if name == "compute_compensation":
                return {"final": {"status": "denied" if int(result.get("amount_vnd", 0)) <= 0 else "ready", "quote": result}}
            return {"final": {"status": "failed", "error_reason": "unexpected_tool"}}

        loop = run_react(conn, budget, observation=observation, decide=decide, max_steps=8)
        final = loop["final"]
        if final["status"] in {"failed", "needs_info", "escalated"}:
            trace.add("decision", {"status": final["status"]})
            return finish(conn, shape="single", claim_id=claim_id, seed=seed, status=final["status"], proposal_amount=0, budget=budget, trace=trace, error_reason=final.get("error_reason"))
        quote = final.get("quote") or {}
        amount = int(quote.get("amount_vnd", 0))
        trace.add("quote", quote)
        if amount <= 0:
            return finish(conn, shape="single", claim_id=claim_id, seed=seed, status="denied", proposal_amount=0, budget=budget, trace=trace, error_reason=quote.get("reason"))
        try:
            outcome = issue_refund(conn, claim_id, amount, crash_at=crash_at)
        except InjectedCrash:
            trace.add("crash", {"at": crash_at})
            trace.write()
            raise
        if not outcome["ok"]:
            status = "failed" if outcome["conflict"] else "denied"
            return finish(conn, shape="single", claim_id=claim_id, seed=seed, status=status, proposal_amount=amount, budget=budget, trace=trace, error_reason=outcome["reason"])
        return finish(conn, shape="single", claim_id=claim_id, seed=seed, status="resolved", proposal_amount=amount, budget=budget, trace=trace)
    finally:
        conn.close()
