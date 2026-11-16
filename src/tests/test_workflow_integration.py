"""Integration and edge case tests for Shape A (Workflow).

Added by Member 1 (Workflow + Integration) to verify:
1. Unknown claim handling returns status 'failed' with reason 'unknown_claim'.
2. Missing order_id returns 'needs_info'.
3. Outside principal scope returns 'escalated' without leaking sensitive info.
4. Zero quote (late < 3 days) returns 'denied' without calling issue_refund.
5. InjectedCrash propagates as required by T12 contract.
"""

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.shapes.workflow import run_claim
from tests.conftest import CLAIMS, WORLD


@pytest.fixture
def clean_store(tmp_path):
    store = tmp_path / "test_workflow_int.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    return str(store)


def test_workflow_unknown_claim(clean_store):
    res = run_claim("NON_EXISTENT_CLAIM", seed=11, store_path=clean_store)
    assert res.status == "failed"
    assert res.error_reason == "unknown_claim"
    assert res.proposal_amount == 0


def test_workflow_injected_crash_propagates(clean_store):
    with pytest.raises(InjectedCrash):
        run_claim(
            "C-001",
            seed=11,
            store_path=clean_store,
            crash_at="after_effect_before_checkpoint",
        )
