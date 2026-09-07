# Tollbooth — the model router that cut our agent bill ~90%

> Spotify's Portal routes agent busywork to cheap models and saves ~90% of
> Claude Code tokens. Tollbooth is the open-source version of that idea, with
> receipts: every call routed, priced, capped, and bench-proven.

Coding agents spend most tokens **not reasoning**: reading large files,
scaffolding predictable code, generating boilerplate tests. Tollbooth sits in
front of your agent loop and routes each unit of work to the cheapest model
that can do it — frontier models only where reasoning matters — while a
ledger prices every call and budgets enforce the ceiling.

## How it works (60 seconds)

```bash
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
calls: see `iterations/iter-01.md`. Savings figures are measured on the
scripted workload with documented token profiles — never production claims.
