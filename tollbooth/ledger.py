"""Cost ledger + budget governor: receipt everything, enforce ceilings.

Receipts carry model + key_alias, never key material. Budgets degrade one
tier step on breach and flag it — except `exception` work, which is
degradation-proof by default (PRD G1).
"""

from dataclasses import dataclass, field

from .providers import price_usd


@dataclass
class Receipt:
    task_id: str
    tier: str
    provider: str
    model: str
    key_alias: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    degraded: bool = False


@dataclass
class Budget:
    max_per_task_usd: float = 2.00
    max_per_day_usd: float = 50.00
    spent_today_usd: float = 0.0
    degrade_exception_tier: bool = False

    def check(self, projected_usd: float, tier: str) -> str:
        """'allow' | 'degrade' | 'deny'. Exception tier never degrades
        unless explicitly opted in."""
        if tier == "exception" and not self.degrade_exception_tier:
            return "allow"
        if self.spent_today_usd + projected_usd > self.max_per_day_usd:
            return "degrade"
        return "allow"

    def spend(self, amount_usd: float) -> None:
        self.spent_today_usd = round(self.spent_today_usd + amount_usd, 6)


@dataclass
class CallLedger:
    receipts: list = field(default_factory=list)

    def add(self, receipt: Receipt) -> None:
        self.receipts.append(receipt)

    def total_usd(self) -> float:
        return round(sum(r.cost_usd for r in self.receipts), 6)

    def total_by_tier(self) -> dict:
        out = {}
        for r in self.receipts:
            out[r.tier] = round(out.get(r.tier, 0.0) + r.cost_usd, 6)
        return out

    def degraded_count(self) -> int:
        return sum(1 for r in self.receipts if r.degraded)


def price_call(provider: str, model: str, tokens_in: int, tokens_out: int) -> float:
    return round(price_usd(provider, model, tokens_in, tokens_out), 6)
