"""Claude Code hook reference: route expensive tool uses before they run.

Wiring (`.claude/settings.json`, see `hooks/settings.example.json`):
hook fires on PreToolUse -> this script reads the event JSON on stdin ->
prints a JSON decision to stdout. Pure `decide_hook(event)` is unit-tested;
`main()` is the thin stdio wrapper. Hook schema versions drift — pin the
version this file targets (see HOOK_SCHEMA_VERSION).
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tollbooth.router import classify  # noqa: E402

HOOK_SCHEMA_VERSION = "claude-code-hooks-2026-06"


def decide_hook(event: dict) -> dict:
    """Return {"allow": bool, "tier": str, "model_hint": str, "reason": str}.

    Never blocks — worst case it advises the cheap tier and the agent may
    still escalate. Blocking hooks belong to policy engines, not routers.
    """
    tool = (event.get("tool") or event.get("tool_name") or "").lower()
    params = event.get("params", {}) or {}
    text = f"{tool} {json.dumps(params, default=str)}"

    size_bytes = 0
    for key in ("file_size", "bytes", "content_length"):
        try:
            size_bytes = max(size_bytes, int(params.get(key, 0) or 0))
        except (ValueError, TypeError):
            pass
    files = params.get("files", [])
    file_count = len(files) if isinstance(files, list) else 0
    if not size_bytes and isinstance(params.get("file_path"), str):
        try:
            size_bytes = os.path.getsize(params["file_path"])
        except OSError:
            pass

    tier = classify(text, bytes_in=size_bytes, files=file_count)
    cheap = tier in ("bulk-read", "scaffold", "test-gen")
    return {
        "allow": True,
        "tier": tier,
        "model_hint": "cheap-bulk-model" if cheap else "frontier-reasoning-model",
        "reason": (f"{tool or 'unknown tool'} looks like {tier} work "
                   f"({size_bytes} bytes, {file_count} files)"),
        "hook_schema": HOOK_SCHEMA_VERSION,
    }


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        event = {}
    print(json.dumps(decide_hook(event if isinstance(event, dict) else {})))


if __name__ == "__main__":
    main()
