"""Focused regressions for the single ReAct shape."""

import json
from pathlib import Path

from lab8.shapes.single import run_claim


def test_single_uses_order_delay_and_keeps_trace_free_of_ticket_secrets(public_db):
    result = run_claim("C-002", seed=55, store_path=str(public_db))

    assert result.status == "denied"
    assert result.proposal_amount == 0
    trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert trace["run_id"] == result.run_id
    assert all("CANARY_SECRET_" not in json.dumps(event) for event in trace["events"])
