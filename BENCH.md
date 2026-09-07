# BENCH — Tollbooth benchmark spec

Prove savings or they don't exist. Offline, deterministic, vendor-free:
scripted token profiles stand in for measured usage until M2 live smoke.

## 1. Workload (`bench/workload.yaml`, 23 tasks)

Mix modeled on a real agent day: 12× `bulk-read` (large-file summarization,
40–80k input tokens), 5× `scaffold` (predictable code from refs), 3×
`test-gen` (boilerplate tests), 2× `reason` (debugging/architecture).
Each task: `{id, tier (expected), tokens_in, tokens_out, bytes}`.

## 2. Method (`bench/run.py`)

For each task, price twice from the same profile: once with the `frontier`
preset pinned to a single frontier model, once with the `balanced` preset
(routed). Output `results/<stamp>/summary.json` + console table:
per-tier totals, ratio, absolute savings, receipts count.

## 3. Metrics

- **Savings ratio** = routed_total / frontier_total → target **< 0.20**.
- **Receipt coverage** = receipted calls / all calls → must be 1.0.
- **Misroute rate** on the labeled set (expected vs classified tier).
- **Budget behavior**: scripted over-cap run must degrade-with-flag, never
  silent, never touch `exception` tier.

## 4. Anti-cherry-picking rules

- Workload file is versioned; numbers always cite commit + date.
- Token profiles are documented estimates (COSTS-style table in-method),
  not measurements — M2 replaces profiles with one real metered day.
- No seed tuning: v1 deterministic, zero randomness.
- Publish misses too: any task where routing costs MORE gets its own row.
