import io
import json
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tollbooth.claude_hook import decide_hook, HOOK_SCHEMA_VERSION


def test_bulk_read_hook_advises_cheap():
    d = decide_hook({"tool": "Read", "params": {"file_size": 90000}})
    assert d["allow"] is True and d["tier"] == "bulk-read"
    assert d["model_hint"] == "cheap-bulk-model"
    assert d["hook_schema"] == HOOK_SCHEMA_VERSION


def test_small_read_stays_reasoning():
    d = decide_hook({"tool": "Read", "params": {"file_size": 400}})
    assert d["tier"] == "reason" and d["model_hint"] == "frontier-reasoning-model"


def test_destructive_command_flagged_exception():
    d = decide_hook({"tool": "Bash",
                     "params": {"command": "rm -rf /data/production exports"}})
    assert d["tier"] == "exception" and d["allow"] is True


def test_empty_event_never_crashes_or_blocks():
    d = decide_hook({})
    assert d["allow"] is True and d["tier"] in ("bulk-read", "reason", "exception")


def test_main_round_trips_stdin_stdout(monkeypatch, capsys):
    import tollbooth.claude_hook as hook
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"tool": "Glob"}'))
    hook.main()
    out = json.loads(capsys.readouterr().out)
    assert out["allow"] is True
