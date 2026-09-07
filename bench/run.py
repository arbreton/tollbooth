#!/usr/bin/env python3
"""Tollbooth bench (BENCH.md): frontier-baseline vs routed on 22 tasks.

Offline, deterministic, vendor-free. Each task is priced twice from its
scripted token profile: once pinned to claude-sonnet-5 (frontier baseline),
once through the balanced router (simulated keys, priced normally).
Writes results/<stamp>/summary.json + prints the savings table.

Usage: python bench/run.py [--out bench/results/<stamp>]
"""

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml  # noqa: E402

from tollbooth.router import classify, role_class  # noqa: E402
from tollbooth.providers import (  # noqa: E402
    PROVIDERS, preset_preferences, price_usd)
from tollbooth.ledger import Receipt, CallLedger  # noqa: E402

MODEL_ROLE = {"bulk": "cheap", "reason": "frontier"}
BASELINE = ("anthropic", "claude-sonnet-5")


def price_routed(task, prefs):
    tier = classify(task["text"], bytes_in=task.get("bytes_in", 0),
                    files=task.get("files", 0))
    role = role_class(tier)
    provider = prefs[role][0]
    model = PROVIDERS[provider][MODEL_ROLE[role]]
    cost = price_usd(provider, model, task["tokens_in"], task["tokens_out"])
    return tier, provider, model, round(cost, 6)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = (sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv
           else os.path.join(root, "bench", "results",
                             datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")))
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(root, "bench", "workload.yaml")) as f:
        tasks = yaml.safe_load(f)
    prefs = preset_preferences("balanced", {})
    ledger, base_total, misroutes, rows = CallLedger(), 0.0, [], []
    for t in tasks:
        provider, model = BASELINE
        base = price_usd(provider, model, t["tokens_in"], t["tokens_out"])
        base_total += base
        tier, rprov, rmodel, cost = price_routed(t, prefs)
        if tier != t["tier"]:
            misroutes.append({"id": t["id"], "expected": t["tier"], "got": tier})
        ledger.add(Receipt(t["id"], tier, rprov, rmodel, "balanced:simulated",
                           t["tokens_in"], t["tokens_out"], cost))
        rows.append({"id": t["id"], "tier": tier, "via": f"{rprov}/{rmodel}",
                     "baseline_usd": round(base, 6), "routed_usd": cost})
    routed_total = ledger.total_usd()
    summary = {
        "date": datetime.now(timezone.utc).isoformat(),
        "cost_model": "scripted token profiles (BENCH.md); frontier baseline = "
                      "claude-sonnet-5 for every task; routed = balanced preset, "
                      "simulated keys priced normally",
        "tasks": len(tasks),
        "baseline_total_usd": round(base_total, 6),
        "routed_total_usd": routed_total,
        "savings_ratio": round(routed_total / base_total, 4),
        "receipt_coverage": 1.0,
        "misroutes": misroutes,
        "misroute_rate": round(len(misroutes) / len(tasks), 4),
        "by_tier": ledger.total_by_tier(),
        "rows": rows,
    }
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(f"baseline ${summary['baseline_total_usd']:.4f}  "
          f"routed ${routed_total:.4f}  ratio {summary['savings_ratio']}  "
          f"misroutes {len(misroutes)}/{len(tasks)}")
    for m in misroutes:
        print("MISROUTE", m)
    print(f"-> {out}/summary.json")


if __name__ == "__main__":
    main()
