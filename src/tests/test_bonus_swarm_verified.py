"""Unit tests for Topic B3 — Swarm with Code Verifier (swarm_verified).

Verifies:
1. Swarm's known weakness on seed 55 (C-002) is successfully intercepted and fixed by the verifier.
2. The trace records 'verifier_override' event.
3. All 8 adversarial claims in bonus/cases.jsonl pass under swarm_verified.
4. Trace contract v1 and crash safety are preserved.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from bonus.swarm_verified import run_claim as run_swarm_verified
from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.durability import InjectedCrash
from lab8.metrics import check_trace, trial_pass
from lab8.shapes.swarm_reference import run_claim as run_swarm
from tests.conftest import BY_ID, CLAIMS, WORLD

BONUS_DIR = Path(__file__).resolve().parents[1] / "bonus"
ADV_WORLD = load_json(BONUS_DIR / "world.json")
ADV_CLAIMS = load_jsonl(BONUS_DIR / "cases.jsonl")
ADV_BY_ID = {c["claim_id"]: c for c in ADV_CLAIMS}


def _store(tmp_path, name: str, world=WORLD, claims=CLAIMS) -> Path:
    path = tmp_path / name
    init_store(path, world, claims).close()
    return path


def test_swarm_verified_fixes_seed_55_miss(tmp_path):
    """Seed 55 on C-002 makes swarm believe customer ticket delay (5 days) over DB (2 days).

    Swarm pays 20,000 VND (fails because expected is denied, 0 VND).
    Swarm_verified detects the mismatch, overrides back to DB, and returns denied (passes).
    """
    store_swarm = _store(tmp_path, "swarm-c002-s55.sqlite")
    swarm_res = run_swarm("C-002", seed=55, store_path=str(store_swarm))
    assert swarm_res.status == "resolved"
    assert swarm_res.proposal_amount == 20000

    # Under verified swarm:
    store_ver = _store(tmp_path, "swarm-ver-c002-s55.sqlite")
    started = time.time()
    ver_res = run_swarm_verified("C-002", seed=55, store_path=str(store_ver))
    conn = connect(store_ver)
    try:
        passed, reason = trial_pass(ver_res.as_dict(), BY_ID["C-002"]["expected"], conn, started_at=started)
    finally:
        conn.close()

    assert ver_res.status == "denied"
    assert ver_res.proposal_amount == 0
    assert passed, reason

    # Verify trace has verifier_override
    trace_body = json.loads(Path(ver_res.trace_path).read_text(encoding="utf-8"))
    override_events = [ev for ev in trace_body["events"] if ev.get("kind") == "verifier_override"]
    assert len(override_events) == 1
    assert override_events[0]["payload"]["original_proposal"] == 20000
    assert override_events[0]["payload"]["corrected_proposal"] == 0


@pytest.mark.parametrize("claim_id", [f"ADV-{i:03d}" for i in range(1, 9)])
@pytest.mark.parametrize("seed", [11, 55])
def test_swarm_verified_adversarial_cases(tmp_path, claim_id, seed):
    """All 8 adversarial cases must pass with swarm_verified."""
    store = _store(tmp_path, f"adv-{claim_id}-s{seed}.sqlite", world=ADV_WORLD, claims=ADV_CLAIMS)
    started = time.time()
    res = run_swarm_verified(claim_id, seed=seed, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(res.as_dict(), ADV_BY_ID[claim_id]["expected"], conn, started_at=started)
    finally:
        conn.close()
    assert passed, f"{claim_id} seed {seed} failed: {reason}"


def test_swarm_verified_crash_safety(tmp_path):
    store = _store(tmp_path, "crash-test.sqlite")
    with pytest.raises(InjectedCrash):
        run_swarm_verified(
            "C-012",
            seed=11,
            store_path=str(store),
            crash_at="after_effect_before_checkpoint",
        )
    # Resume after crash
    res = run_swarm_verified("C-012", seed=11, store_path=str(store))
    assert res.status == "resolved"
