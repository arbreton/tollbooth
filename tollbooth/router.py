"""Tier router for agent work units.

Tiers: bulk-read | scaffold | test-gen → cheap class; reason | exception →
frontier class. Heuristic reference implementation with explicit
`force_tier` override (bench determinism); a learned classifier drops behind
`classify()` later without changing callers.
"""

import re

TIERS = ("bulk-read", "scaffold", "test-gen", "reason", "exception")
CHEAP_TIERS = ("bulk-read", "scaffold", "test-gen")

BULK_BYTES = 20_000  # reads above this are bulk, not skims

INJECTION_PATTERNS = [
    r"\b(ignore|forget|disregard|override|bypass).{0,30}(rules?|instructions?|polic(y|ies)|prompts?|guidelines?)\b",
]
DESTRUCTIVE_PATTERNS = [
    r"\b(drop|delete|truncate|rm -rf|format|wipe).{0,30}(database|table|production|disk|bucket)\b",
    r"\b(prod|production).{0,20}(deploy|release|migrate|incident|outage|p0|sev-?1)\b",
]

READ_VERBS = re.compile(r"\b(read|summariz|explain|survey|audit|review)\b", re.IGNORECASE)
WRITE_VERBS = re.compile(r"\b(scaffold|generate|create|write|boilerplate|stub)\b", re.IGNORECASE)
TEST_VERBS = re.compile(r"\b(pytest|test)\b", re.IGNORECASE)
REASON_VERBS = re.compile(
    r"\b(debug|architect|design|decide|refactor|migrate|optimiz|trade-?off|why|root.?cause)\b",
    re.IGNORECASE)


def _any(patterns, text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def classify(text: str, bytes_in: int = 0, files: int = 0,
             force_tier: str = None) -> str:
    """Classify one unit of agent work. Size signals dominate verbs."""
    if force_tier is not None:
        if force_tier not in TIERS:
            raise ValueError(f"bad tier {force_tier!r}")
        return force_tier
    if _any(INJECTION_PATTERNS, text) or _any(DESTRUCTIVE_PATTERNS, text):
        return "exception"
    if bytes_in >= BULK_BYTES or files >= 3:
        return "bulk-read"
    if TEST_VERBS.search(text) and WRITE_VERBS.search(text):
        return "test-gen"
    if REASON_VERBS.search(text):
        return "reason"
    if WRITE_VERBS.search(text):
        return "scaffold"
    if READ_VERBS.search(text):
        return "bulk-read" if bytes_in >= 2000 else "reason"
    return "reason"  # default: when in doubt, spend on understanding


def role_class(tier: str) -> str:
    """Tier -> provider role class (cheap vs frontier)."""
    return "bulk" if tier in CHEAP_TIERS else "reason"
