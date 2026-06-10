#!/usr/bin/env python3
"""Persist and restore Quantum Queen analysis context across Devin compaction.

This hook is intentionally non-blocking. It snapshots the project's planning
files on lifecycle events and emits a compact restoration hint after compaction.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(os.environ.get("DEVIN_PROJECT_DIR", os.getcwd())).resolve()
CONTEXT_DIR = PROJECT / ".planning" / "context"
SNAPSHOT_DIR = CONTEXT_DIR / "snapshots"
LATEST = CONTEXT_DIR / "latest_context.md"
RESTORE = CONTEXT_DIR / "restore_after_compaction.md"
COMPACTION_LOG = CONTEXT_DIR / "compaction_events.jsonl"
EVENT_LOG = CONTEXT_DIR / "hook_events.jsonl"
PLANNING_FILES = ["task_plan.md", "findings.md", "progress.md"]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_stdin_json() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception as exc:  # keep hook non-blocking
        return {"_stdin_error": f"{type(exc).__name__}: {exc}"}


def run(cmd: list[str], timeout: int = 5) -> str:
    try:
        return subprocess.check_output(cmd, cwd=PROJECT, text=True, stderr=subprocess.STDOUT, timeout=timeout).strip()
    except Exception as exc:
        return f"unavailable ({type(exc).__name__}: {exc})"


def read_file(name: str, max_chars: int = 30000) -> str:
    path = PROJECT / name
    if not path.exists():
        return f"[missing: {name}]"
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) > max_chars:
        return text[:max_chars] + f"\n\n[truncated: {len(text) - max_chars} chars omitted]"
    return text


def build_context(event_name: str, event: dict) -> str:
    timestamp = utc_now()
    git_status = run(["git", "status", "--short"])
    hook_source = event.get("hook_event_name") or event_name or "unknown"

    sections = [
        "# Quantum Queen Analysis Context Snapshot",
        "",
        f"- Snapshot time: `{timestamp}`",
        f"- Hook event: `{hook_source}`",
        f"- Project: `{PROJECT}`",
        "",
        "## Restore Instructions",
        "",
        "After context compaction or session restart, re-read these files before making analysis decisions:",
        "",
        "1. `task_plan.md` — approved A+B analysis plan and phase status.",
        "2. `findings.md` — durable findings from MQL5/product/data exploration.",
        "3. `progress.md` — latest completed work, errors, and next steps.",
        "4. `.planning/context/restore_after_compaction.md` — most recent compaction summary and recovery prompt.",
        "",
        "## Current Git Status",
        "",
        "```text",
        git_status or "clean or unavailable",
        "```",
    ]

    prompt = event.get("prompt")
    if prompt:
        sections.extend([
            "",
            "## Latest User Prompt Captured by Hook",
            "",
            str(prompt),
        ])

    for name in PLANNING_FILES:
        sections.extend([
            "",
            f"---\n\n## `{name}`",
            "",
            read_file(name),
        ])

    return "\n".join(sections).rstrip() + "\n"


def persist_snapshot(event_name: str, event: dict) -> str:
    CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    context = build_context(event_name, event)
    LATEST.write_text(context, encoding="utf-8")
    stamp = utc_now().replace(":", "").replace("-", "")
    snapshot_path = SNAPSHOT_DIR / f"{stamp}-{event_name or 'event'}.md"
    snapshot_path.write_text(context, encoding="utf-8")

    with EVENT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "time": utc_now(),
            "event": event_name,
            "hook_event_name": event.get("hook_event_name"),
            "snapshot": str(snapshot_path.relative_to(PROJECT)),
        }, ensure_ascii=False) + "\n")

    # Keep a simple latest copy with a predictable name. Do not delete old snapshots.
    return str(snapshot_path.relative_to(PROJECT))


def handle_post_compaction(event: dict) -> None:
    snapshot_rel = persist_snapshot("PostCompaction", event)
    summary = event.get("summary")

    COMPACTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with COMPACTION_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "time": utc_now(),
            "summary": summary,
            "snapshot": snapshot_rel,
        }, ensure_ascii=False) + "\n")

    restore_text = "\n".join([
        "# Restore After Devin Context Compaction",
        "",
        f"- Compaction time: `{utc_now()}`",
        f"- Latest snapshot: `{snapshot_rel}`",
        "",
        "## Required Recovery Steps",
        "",
        "Before continuing Quantum Queen analysis, read:",
        "",
        "- `task_plan.md`",
        "- `findings.md`",
        "- `progress.md`",
        "- `.planning/context/latest_context.md`",
        "",
        "Then continue from the latest incomplete phase in `task_plan.md`.",
        "",
        "## Compactor Summary",
        "",
        summary or "[No compactor summary was provided by Devin.]",
        "",
    ])
    RESTORE.write_text(restore_text, encoding="utf-8")

    add_context = (
        "Context compaction completed. Quantum Queen analysis state was persisted. "
        "Before making analysis decisions, read task_plan.md, findings.md, progress.md, "
        "and .planning/context/latest_context.md. Continue from the latest incomplete phase."
    )
    print(json.dumps({"decision": "approve", "reason": add_context, "add_context": add_context}, ensure_ascii=False))


def main() -> int:
    event = read_stdin_json()
    event_name = event.get("hook_event_name") or os.environ.get("HOOK_EVENT_NAME") or "unknown"
    try:
        if event_name == "PostCompaction":
            handle_post_compaction(event)
        else:
            snapshot_rel = persist_snapshot(event_name, event)
            if event_name == "SessionStart":
                hint = (
                    "Quantum Queen analysis has persistent planning context. "
                    "Read task_plan.md, findings.md, progress.md, and .planning/context/latest_context.md before continuing."
                )
                print(json.dumps({"decision": "approve", "reason": hint, "add_context": hint}, ensure_ascii=False))
            else:
                print(json.dumps({"decision": "approve", "reason": f"Context snapshot saved: {snapshot_rel}"}, ensure_ascii=False))
        return 0
    except Exception as exc:
        # Never block the agent due to persistence failures.
        print(json.dumps({"decision": "approve", "reason": f"Context hook error ignored: {type(exc).__name__}: {exc}"}, ensure_ascii=False))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
