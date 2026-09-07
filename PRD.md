# PRD — Tollbooth model router + cost governor

**Version:** 0.1 (plan+P1) · **Date:** 2026-09-06 · **Owner:** ariane
**One-liner:** Route each unit of agent work to the cheapest capable model,
receipt every call, enforce spend ceilings — and prove the savings on a bench.

## 1. Problem

AI coding-agent bills scale with usage, not value. Most tokens go to
I/O-heavy, predictable work (bulk file reads, scaffolding, boilerplate
tests) that runs fine on $0.10–0.60/MTok models — yet defaults send
everything to $2–30/MTok frontier models. Teams discover this in the invoice,
with no per-call attribution and no lever except "use the agent less."

## 2. Users

1. **Eng lead / indie hacker** running agents daily: wants the same output
   for ~10% of the spend, with a receipt per call.
2. **Platform/ops owner** (the Emvo COO archetype): wants spend ceilings
   that *enforce* (degrade gracefully, never silently), plus audit trails.
3. **Agent-framework builders**: want routing as a library + Claude-hook
   reference, not a platform lock-in.

## 3. Jobs to be done

- "When my agent reads 5 large files, don't bill me frontier prices for it."
- "When spend hits the daily cap, degrade to cheap models — don't stop work."
- "When finance asks where $X went, show the per-call ledger."
- "When I add a new model, re-route without rewriting the agent."

## 4. Non-goals (v1)

- Rewriting agents (advisory layer: classify → price → allow/redirect).
- Training routers (heuristic + explicit override; model-based later).
- Multi-tenant SaaS billing (single-operator BYOK; wallet = their keys).

## 5. Functional requirements

**Routing (the Portal bet):**
- F1. Classify each work unit: `bulk-read | scaffold | test-gen | reason |
  exception`. Heuristic reference implementation + `force_tier` override.
- F2. Tier → ordered provider preference from env (`*_PREFERENCE`), resolved
  against held keys (wallet/env), first reachable wins.
- F3. Claude Code hook reference: PreToolUse-style hook reads tool params
  (e.g. file size on Read) and returns allow/redirect + tier + reason.

**Ledger + governor (the Emvo bet):**
- F4. Every routed call appends a receipt: tier, provider, model, key alias,
  tokens, USD. Never the key itself.
- F5. Budgets: per-task and per-day caps enforced in the governor, not
  prompts. Cap hit → degrade tier (frontier→cheap) + flag, never silent
  downgrade of *correctness-critical* (`exception`) work without logging.
- F6. Unknown (provider, model) fails loud — a $0 entry for a paid model
  corrupts every metric downstream.

**BYOK:**
- F7. No keys in repo; wallet (RAM) → env → simulated fallback (demo mode).
  Presets: `cheap`, `balanced` (route), `frontier` (baseline), `free` (local).

## 6. Guardrails

- G1. `exception` tier (prod incidents, destructive ops, prompt-injection
  signals) never auto-degrades below frontier without an explicit flag.
- G2. Key hygiene: env-first, RAM wallet, masked status, rotation without
  code changes.
- G3. Bench honesty: scripted token profiles published in-repo; savings =
  measured on the scripted mix, labeled with commit + date; 3-seed avg where
  randomness exists (v1 is deterministic).

## 7. Metrics (targets — published only from BENCH runs)

- Routed-vs-frontier cost ratio **< 0.20** on the 23-task bench (>80% saved).
- 100% of calls receipted; 100% cap breaches degrade-with-flag, zero silent.
- Misroute rate on labeled set < 10% (heuristic), < 5% with model router (later).
- Bench runtime < 5s offline (no vendor calls in the loop).

## 8. Milestones

- M0 docs (this folder) → M1 router/ledger/bench offline (built) →
  M2 live smoke on free tiers (measure one real day) → M3 Claude-hook dogfood
  on a real repo → M4 upload + LinkedIn post with the savings table.
