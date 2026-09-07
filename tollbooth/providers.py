"""BYOK provider registry for text LLMs (prices verified 2026-09-06).

Same shape as OBRA's registry: presets, env overlays, shared-credential
aliases, RAM-only wallet. Unknown (provider, model) fails loud — never $0.
"""

import os

# provider -> role -> default model + env var holding the key.
PROVIDERS = {
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "cheap": "gpt-4o-mini",
        "frontier": "gpt-5.4",
    },
    "google": {
        "env_key": "GOOGLE_API_KEY",
        "cheap": "gemini-2.0-flash",
        "frontier": "gemini-2.5-pro",
    },
    "anthropic": {
        "env_key": "ANTHROPIC_API_KEY",
        "cheap": "claude-haiku-4-5",
        "frontier": "claude-sonnet-5",
    },
    "local": {
        "env_key": None,
        "cheap": "ollama/qwen3",
        "frontier": None,
    },
}

# Presets: ordered provider preference per tier-class.
PRESETS = {
    "cheap": {"bulk": ["openai"], "reason": ["openai"]},
    "balanced": {"bulk": ["google", "openai"], "reason": ["anthropic", "openai"]},
    "frontier": {"bulk": ["anthropic"], "reason": ["anthropic"]},
    "free": {"bulk": ["local"], "reason": ["local"]},
}

KEY_ALIASES = {}

# (provider, model) -> price per 1M tokens. Verified 2026-09-06; re-check monthly.
PRICES = {
    ("openai", "gpt-4o-mini"): {"in_per_1m": 0.15, "out_per_1m": 0.60},
    ("openai", "gpt-5.4"): {"in_per_1m": 2.50, "out_per_1m": 15.00},
    ("google", "gemini-2.0-flash"): {"in_per_1m": 0.10, "out_per_1m": 0.40},
    ("google", "gemini-2.5-pro"): {"in_per_1m": 1.25, "out_per_1m": 10.00},
    ("anthropic", "claude-haiku-4-5"): {"in_per_1m": 1.00, "out_per_1m": 5.00},
    ("anthropic", "claude-sonnet-5"): {"in_per_1m": 2.00, "out_per_1m": 10.00},
    ("local", "ollama/qwen3"): {"in_per_1m": 0.0, "out_per_1m": 0.0},
}


def holders(wallet: dict, env: dict = None) -> set:
    env = os.environ if env is None else env
    held = set()
    for name, spec in PROVIDERS.items():
        var = spec.get("env_key")
        if var is None:
            continue
        if (wallet.get(name) or "").strip():
            held.add(name)
            continue
        target = KEY_ALIASES.get(name)
        if target and (wallet.get(target) or "").strip():
            held.add(name)
            continue
        if var and (env.get(var) or "").strip():
            held.add(name)
    return held


def key_configured(provider: str, wallet: dict, env: dict = None) -> bool:
    return provider in holders(wallet, env)


def resolve(role_class: str, preference: list, role: str,
            wallet: dict, env: dict = None):
    """First provider in preference with a usable key for `role`.

    `role_class` is "bulk"|"reason" (tier family, used in errors);
    `role` is "cheap"|"frontier" (model key). Returns (provider, model,
    alias). Raises LookupError — never silent.
    """
    for provider in preference:
        spec = PROVIDERS.get(provider)
        if not spec or not spec.get(role):
            continue
        if provider in holders(wallet, env):
            alias = "wallet" if (wallet.get(provider) or "").strip() or \
                (wallet.get(KEY_ALIASES.get(provider, "")) or "").strip() else "env"
            return provider, spec[role], f"{provider}:{alias}"
    raise LookupError(f"no configured provider for {role} in {preference}")


def preset_preferences(preset: str, env: dict = None) -> dict:
    try:
        prefs = {k: list(v) for k, v in PRESETS[preset].items()}
    except KeyError:
        raise ValueError(f"unknown preset {preset!r}; choose from {sorted(PRESETS)}")
    env = os.environ if env is None else env
    for cls, var in (("bulk", "BULK_PREFERENCE"), ("reason", "REASON_PREFERENCE")):
        raw = (env.get(var) or "").strip()
        if raw:
            prefs[cls] = [p.strip() for p in raw.split(",") if p.strip()]
    return prefs


def price_usd(provider: str, model: str, tokens_in: int, tokens_out: int) -> float:
    try:
        p = PRICES[(provider, model)]
    except KeyError:
        raise ValueError(f"no price for {(provider, model)} — add to PRICES, never assume $0")
    return tokens_in / 1_000_000 * p["in_per_1m"] + tokens_out / 1_000_000 * p["out_per_1m"]
