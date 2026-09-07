# iter-01 — P1 bench green (offline)

**Date:** 2026-09-06 · **Scope:** router + registry + ledger + hooks + demo +
23-task bench. No vendor calls; scripted token profiles.

## Results (`bench/results/iter-01/summary.json`)

- Baseline (sonnet-5 everything): **$0.6819** · Routed (balanced): **$0.1050**
- **Savings ratio 0.154** — beats the < 0.20 target (≈85% saved).
- Receipt coverage 1.0 · Misroutes **1/23 (4.3%)**, under the 10% target.
- Unit tests green (see verify).

## Published miss (per BENCH anti-cherry-picking rules)

- `scaffold-ci` ("Generate a GitHub Actions workflow for pytest") → classified
  `test-gen`. Defensible either way (CI workflow *is* test scaffolding);
  kept as a miss, not relabeled. If misses cluster here, split a `ci-gen`
  tier or weight `pytest` toward scaffold context.

## What broke (fixed)

1. Role/class key collision (`bulk` vs `cheap`) crashed the demo — provider
   roles now documented as cheap|frontier, tier families as bulk|reason.
2. `\btest\b` missed `pytest` — pattern now matches both.
3. Workload count drifted to 23 tasks — docs updated to match the file.

## Next (iter-02)

Live smoke: one real metered day on free tiers (replace profiles with
measured tokens), then Claude-hook dogfood on a real repo.
