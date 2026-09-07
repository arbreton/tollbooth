import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from tollbooth.providers import (
    resolve, preset_preferences, price_usd, holders, key_configured)

ENV = {"OPENAI_API_KEY": "sk-test", "GOOGLE_API_KEY": "g-test"}


def test_price_math_known_models():
    # GPT-4o mini @ 3000 in / 175 out per min (LiveKit assumptions).
    assert price_usd("openai", "gpt-4o-mini", 3000, 175) == pytest.approx(0.000555, rel=1e-6)
    assert price_usd("google", "gemini-2.0-flash", 3000, 175) == pytest.approx(0.00037, rel=1e-6)


def test_unknown_model_fails_loud():
    with pytest.raises(ValueError):
        price_usd("openai", "gpt-99", 1, 1)


def test_resolve_first_configured():
    assert resolve("x", ["google", "openai"], "cheap", {}, ENV)[0] == "google"
    assert resolve("x", ["anthropic", "openai"], "cheap", {}, ENV) == (
        "openai", "gpt-4o-mini", "openai:env")


def test_resolve_wallet_beats_env_and_labels():
    out = resolve("x", ["openai"], "cheap", {"openai": "sk-w"}, ENV)
    assert out == ("openai", "gpt-4o-mini", "openai:wallet")


def test_resolve_skips_missing_capability():
    with pytest.raises(LookupError):
        resolve("x", ["local"], "nonsense-role", {}, ENV)


def test_resolve_raises_when_nothing_configured():
    with pytest.raises(LookupError):
        resolve("x", ["openai"], "cheap", {}, {})


def test_holders_and_key_configured():
    assert holders({"openai": "sk-w"}, {}) == {"openai"}
    assert key_configured("openai", {"openai": "sk-w"}, {}) is True
    assert key_configured("openai", {}, {}) is False
    assert key_configured("local", {}, {}) is False  # keyless != held


def test_presets_and_env_overlay():
    prefs = preset_preferences("balanced", {})
    assert prefs["bulk"][0] == "google" and prefs["reason"][0] == "anthropic"
    prefs = preset_preferences("balanced", {"BULK_PREFERENCE": "openai"})
    assert prefs["bulk"] == ["openai"]
    with pytest.raises(ValueError):
        preset_preferences("nope", {})
