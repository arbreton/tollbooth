#!/usr/bin/env python3
"""Tollbooth live demo: 8 representative tasks route + price in your terminal.

  python -m tollbooth.demo                  # simulated keys ($0, default)
  BYOK keys in env (.env) are honored automatically and labeled :env.

No vendor calls — token profiles are documented estimates (BENCH.md).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tollbooth.router import classify, role_class  # noqa: E402
from tollbooth.providers import (  # noqa: E402
    PROVIDERS, resolve, preset_preferences, price_usd, holders)
from tollbooth.ledger import Receipt, CallLedger, Budget  # noqa: E402

SHOWCASE = [
    ("Summarize auth.py + db.py + api.py for onboarding", 62000, 300),
    ("Scaffold a FastAPI CRUD resource from the user model", 4000, 1500),
    ("Generate pytest boilerplate for the billing module", 5000, 2000),
    ("Debug the race condition in the webhook worker", 9000, 1200),
    ("Read package.json to check the React version", 800, 100),
    ("DROP TABLE users on production", 200, 50),
    ("Write a Dockerfile for the Python service", 2500, 800),
    ("Design the checkout retry state machine", 6000, 1500),
]


MODEL_ROLE = {"bulk": "cheap", "reason": "frontier"}


def _resolve_demo(role, prefs, wallet):
    """Resolve with simulated fallback (labeled :simulated, priced normally)."""
    try:
        return resolve(role, prefs[role], MODEL_ROLE[role], wallet)
    except LookupError:
        provider = prefs[role][0]
        return provider, PROVIDERS[provider][MODEL_ROLE[role]], f"{provider}:simulated"


def run_demo(budget=None):
    prefs = preset_preferences(os.getenv("TOLLBOOTH_PRESET", "balanced"))
    wallet, ledger = {}, CallLedger()
    budget = budget or Budget()
    held = holders(wallet)
    print(f"preset=balanced  wallet={' / '.join(sorted(held)) or 'simulated'}")
    for i, (text, size, out) in enumerate(SHOWCASE):
        tier = classify(text, bytes_in=size)
        role = role_class(tier)
        provider, model, alias = _resolve_demo(role, prefs, wallet)
        tin = size // 4 or 500
        cost = price_usd(provider, model, tin, out)
        verdict = budget.check(cost, tier)
        degraded = verdict == "degrade"
        if degraded:
            # One step down, flagged on the receipt — never silent.
            cheap = preset_preferences("cheap")
            try:
                provider, model, alias = resolve(
                    role, cheap.get(role, cheap["bulk"]), MODEL_ROLE[role], wallet)
                cost = price_usd(provider, model, tin, out)
            except LookupError:
                pass  # no cheap route available: keep routing, still flagged
        ledger.add(Receipt(f"demo-{i}", tier, provider, model, alias,
                           tin, out, round(cost, 6), degraded))
        budget.spend(cost)
        print(f"[{tier:10s} · {provider}/{model} · ${cost:.4f}] {text[:58]}")
    print(f"total ${ledger.total_usd():.4f} across {len(ledger.receipts)} tasks "
          f"| by tier: {ledger.total_by_tier()}")


if __name__ == "__main__":
    run_demo()
