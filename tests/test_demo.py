import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tollbooth.demo import run_demo, SHOWCASE
from tollbooth.ledger import Budget


def test_showcase_shape():
    assert len(SHOWCASE) == 8
    for text, size, out in SHOWCASE:
        assert isinstance(text, str) and size >= 0 and out >= 0


def test_demo_prints_totals_table(capsys):
    run_demo()
    out = capsys.readouterr().out
    assert "total $" in out and "by tier:" in out
    assert "preset=balanced" in out


def test_budget_degrade_and_exception_proof():
    tiny = Budget(max_per_day_usd=0.000001)
    assert tiny.check(0.5, "bulk-read") == "degrade"
    assert tiny.check(99.0, "exception") == "allow"  # G1 holds even here
