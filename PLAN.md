# PLAN — Tollbooth build plan

## 1. Architecture

```
Agent loop (Claude Code, Codex, custom…)
  │  work unit: {kind, bytes, files, prompt_len}
  ▼
┌─────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────────┐
│ Router  │─▶│ BYOK registry│─▶│ Governor   │─▶│ Vendor call  │
│ tier +  │  │ prefs + keys │  │ caps check │  │ (yours)      │
│ model   │  │ first wins   │  │ degrade?   │  │              │
└─────────┘  └──────────────┘  └────────────┘  └──────────────┘
      │              │               │
      └──────▶ LEDGER (tier, provider, model, key_alias, tokens, USD)
```

- **Router:** heuristic reference (`router.py`): byte thresholds, file-count,
  verb lists, injection signals + `force_tier` override. Interface frozen so
  a small-model classifier drops in later.
- **Registry:** providers × {cheap, frontier} models × prices (`providers.py`),
  presets (`cheap|balanced|frontier|free`), `{STAGE}_PREFERENCE` env overlays,
  shared-credential aliases. Same BYOK shape as OBRA (wallet → env → simulated).
- **Governor:** per-task/per-day caps (`ledger.py:Budget`). Breach → tier
  degrades one step + `degraded: true` on the receipt. `exception` tier is
  degradation-proof by default.
- **Hooks:** `hooks/claude_hook.py` — pure `decide_hook(event) -> decision`
  plus a `settings.json` wiring example. The agent keeps calling vendors;
  Tollbooth advises which model and records what it cost.

## 2. Repo layout (built)

```
tollbooth/
├── README.md · PRD.md · PLAN.md · BENCH.md
├── tollbooth/{__init__,router,providers,ledger,hooks,claude_hook,demo}.py
├── hooks/settings.example.json
├── bench/{workload.yaml,run.py,results/}
├── tests/test_{router,providers,ledger,hooks,demo}.py
├── iterations/iter-01.md
├── .env.example · .gitignore
```

## 3. Phases

- **P0 docs** (done) → **P1 offline core** (done: router/ledger/bench all
  green, no vendor calls) → **P2 live smoke** (one real day on free tiers,
  measure true mix) → **P3 dogfood** (hook on a real repo for a week,
  publish diary) → **P4 public release**.

## 4. Task breakdown (P1, built)

Router tiers + heuristics + override · provider registry + 4 presets + env
overlays + aliases · price table (verified 2026-09-06) · ledger + budgets +
degrade logic · Claude-hook decision fn + settings example · 23-task workload
+ runner + savings table · demo REPL · iter-01 log.

## 5. Risks

- Heuristic misroutes (tracked: labeled-set misroute metric, model router later).
- Price drift (pins dated; ledger recomputes from table; re-verify monthly).
- Hook API drift (Claude/Codex hook schemas change — reference is versioned).
- Savings don't transfer (workload mix differs per team — bench is a template,
  fork it with your traces).

## 6. Rejected alternatives (and why)

- **Managed platform (Vapi-style fee):** contradicts the thesis — the product
  *is* escaping per-minute taxes, not adding one.
- **Training a router model first:** heuristics + override ship today and are
  auditable; learned routing needs labeled traces we don't have yet.
- **Rewriting the agent loop:** adoption dies. Advisory layer (classify →
  price → allow/redirect) integrates in an afternoon.
- **Yet another dashboard SaaS:** the ledger is a JSONL file + 40-line
  summary. Boring infra wins.
