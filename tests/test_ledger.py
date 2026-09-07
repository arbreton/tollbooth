import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from tollbooth.ledger import Receipt, CallLedger, Budget, price_call


def _receipt(tier="bulk-read", cost=0.01):
    return Receipt("t1", tier, "openai", "gpt-4o-mini", "openai:env",
                   1000, 100, cost)


def test_ledger_totals_and_tiers():
    ledger = CallLedger()
    ledger.add(_receipt("bulk-read", 0.01))
    ledger.add(_receipt("reason", 0.05))
    assert ledger.total_usd() == pytest.approx(0.06)
    assert ledger.total_by_tier() == {"bulk-read": 0.01, "reason": 0.05}
    assert ledger.degraded_count() == 0


def test_budget_allows_and_tracks():
    budget = Budget(max_per_task_usd=2.0, max_per_day_usd=50.0)
    assert budget.check(0.5, "bulk-read") == "allow"
    budget.spend(0.5)
    assert budget.spent_today_usd == pytest.approx(0.5)


def test_budget_degrades_over_cap():
    budget = Budget(max_per_day_usd=1.0)
    budget.spend(0.99)
    assert budget.check(0.5, "bulk-read") == "degrade"


def test_exception_tier_degradation_proof_by_default():
    budget = Budget(max_per_day_usd=0.0)
    assert budget.check(99.0, "exception") == "allow"
    strict = Budget(max_per_day_usd=0.0, degrade_exception_tier=True)
    assert strict.check(99.0, "exception") == "degrade"


def test_price_call_rounds():
    assert price_call("openai", "gpt-4o-mini", 3000, 175) == pytest.approx(0.000555, rel=1e-6)
