# Tollbooth — a model router for coding agents

> Most coding-agent tokens aren't reasoning. Tollbooth routes agent busywork to
> cheap models and keeps frontier models for the work that needs them — with
> receipts: every call routed, priced, capped, and bench-proven. Inspired by
> Spotify's published "Portal" routing idea.

Coding agents spend most tokens **not reasoning**: reading large files,
scaffolding predictable code, generating boilerplate tests. Tollbooth sits in
front of your agent loop and routes each unit of work to the cheapest model
that can do it — frontier models only where reasoning matters — while a
ledger prices every call and budgets enforce the ceiling.

## How it works (60 seconds)

```bash
git clone https://github.com/arbreton/tollbooth.git && cd tollbooth
pip install -e .  # stdlib only (+ pytest/pyyaml to run tests & bench)
cp .env.example .env   # BYOK: your keys, your bill (or run fully simulated)

python -m tollbooth.demo          # watch 8 tasks route + price live
python bench/run.py               # all-frontier vs routed: the savings table
python -m pytest tests -q         # green suite
```

A file read becomes `bulk-read → gemini-2.0-flash ($0.0004)` instead of
`frontier ($0.05)`. A debugging session stays on the frontier. The bench
proves the mix on a scripted 23-task workload; the ledger proves it per call.

## Docs

- `PRD.md` — users, jobs, tiers, guardrails, metrics
- `PLAN.md` — architecture, Claude-hooks wiring, phases, rejected alternatives
- `BENCH.md` — workload spec, metrics, how to run, anti-cherry-picking rules

Status: **P1 built — bench green offline.** Router + BYOK registry + ledger
with budget enforcement + Claude-hook reference + 23-task bench, zero vendor
calls: see `iterations/iter-01.md`. Savings figures (~90% on the bench) are
measured on the scripted workload with documented token profiles — they are
not production claims. This repo was extracted from a private monorepo, so
the public history starts at a single commit.
