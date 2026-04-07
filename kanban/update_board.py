#!/usr/bin/env python3
"""
Fixi Kanban Board Updater

Reads kanban/tasks/*.md, parses YAML frontmatter, generates BOARD.md,
and appends history entries for any status changes since last run.

Usage:
    python kanban/update_board.py

State is cached in kanban/.state.json (committed to track snapshots).
History is appended to kanban/history/YYYY-MM-DD.md.

No external dependencies — Python stdlib only.
"""

from __future__ import annotations

import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Force UTF-8 stdout on Windows so arrows and box-drawing chars work
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

KANBAN_DIR = Path(__file__).parent
TASKS_DIR = KANBAN_DIR / "tasks"
HISTORY_DIR = KANBAN_DIR / "history"
BOARD_FILE = KANBAN_DIR / "BOARD.md"
STATE_FILE = KANBAN_DIR / ".state.json"

STATUS_ORDER = ["in-progress", "blocked", "pending", "done", "cancelled"]
STATUS_ICONS = {
    "in-progress": "🔄",
    "blocked": "⛔",
    "pending": "📋",
    "done": "✅",
    "cancelled": "🚫",
}
STATUS_LABELS = {
    "in-progress": "In Progress",
    "blocked": "Blocked",
    "pending": "Pending",
    "done": "Done",
    "cancelled": "Cancelled",
}


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str] | None:
    """Parse minimal YAML frontmatter. Returns (frontmatter_dict, body) or None."""
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end == -1:
        return None
    fm_text = content[3:end].strip()
    body = content[end + 4:].lstrip()

    fm: dict[str, Any] = {}
    current_list_key: str | None = None

    for raw_line in fm_text.split("\n"):
        line = raw_line.rstrip()
        if not line.strip():
            current_list_key = None
            continue

        # Continuation list item: "  - value"
        if line.startswith("  - ") or line.startswith("- "):
            value = line.strip()[2:].strip().strip('"').strip("'")
            if current_list_key and isinstance(fm.get(current_list_key), list):
                fm[current_list_key].append(value)
            continue

        # key: value
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()

        if val == "":
            # Likely a list follows
            fm[key] = []
            current_list_key = key
            continue

        current_list_key = None

        # Inline list [a, b, c]
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            if not inner:
                fm[key] = []
            else:
                items = [i.strip().strip('"').strip("'") for i in inner.split(",")]
                fm[key] = [i for i in items if i]
            continue

        # Quoted string
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            fm[key] = val[1:-1]
            continue

        fm[key] = val

    return fm, body


def load_tasks() -> dict[str, dict[str, Any]]:
    tasks: dict[str, dict[str, Any]] = {}
    if not TASKS_DIR.exists():
        return tasks
    for task_file in sorted(TASKS_DIR.glob("*.md")):
        content = task_file.read_text(encoding="utf-8")
        result = parse_frontmatter(content)
        if not result:
            print(f"WARN: {task_file.name} has no valid frontmatter, skipping")
            continue
        fm, body = result
        if "id" not in fm:
            print(f"WARN: {task_file.name} has no 'id' field, skipping")
            continue
        tasks[fm["id"]] = {"frontmatter": fm, "body": body, "path": task_file}
    return tasks


def load_state() -> dict[str, Any]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict[str, Any]) -> None:
    STATE_FILE.write_text(
        json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def detect_changes(
    tasks: dict[str, dict[str, Any]], prev_state: dict[str, Any]
) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    for tid, task in tasks.items():
        new_status = task["frontmatter"].get("status", "pending")
        prev = prev_state.get(tid, {})
        old_status = prev.get("status")
        if old_status != new_status:
            changes.append(
                {
                    "id": tid,
                    "title": task["frontmatter"].get("title", ""),
                    "old": old_status or "",
                    "new": new_status,
                }
            )
    # Also detect newly removed tasks (cancelled by deletion)
    for tid in prev_state:
        if tid not in tasks:
            changes.append(
                {
                    "id": tid,
                    "title": prev_state[tid].get("title", ""),
                    "old": prev_state[tid].get("status", ""),
                    "new": "removed",
                }
            )
    return changes


def append_history(changes: list[dict[str, str]]) -> Path | None:
    if not changes:
        return None
    HISTORY_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    history_file = HISTORY_DIR / f"{today}.md"

    if not history_file.exists():
        header = (
            f"# Kanban History — {today}\n\n"
            f"> Auto-generado por `update_board.py`. Append-only.\n"
            f"> Ver: [[BOARD]] · [[README]]\n\n"
            f"## Eventos\n\n"
        )
        history_file.write_text(header, encoding="utf-8")

    timestamp = datetime.now().strftime("%H:%M:%S")
    with history_file.open("a", encoding="utf-8") as f:
        for c in changes:
            old = c["old"] or "new"
            f.write(
                f"- `{timestamp}` · [[{c['id']}]] · **{old} → {c['new']}** · {c['title']}\n"
            )

    return history_file


def render_board(tasks: dict[str, dict[str, Any]]) -> str:
    columns: dict[str, list[dict[str, Any]]] = {s: [] for s in STATUS_ORDER}
    for task in tasks.values():
        status = task["frontmatter"].get("status", "pending")
        columns.setdefault(status, []).append(task)

    for col in columns.values():
        col.sort(key=lambda t: t["frontmatter"].get("id", ""))

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = sum(len(c) for c in columns.values())
    counts = {s: len(columns[s]) for s in STATUS_ORDER}
    # Cancelled tasks are excluded from the progress denominator — they
    # represent decided-not-to-do work, not remaining work.
    active = total - counts["cancelled"]
    progress = round(counts["done"] / active * 100) if active > 0 else 0

    lines: list[str] = []
    lines.append("# Fixi Kanban Board")
    lines.append("")
    lines.append(f"> **Última actualización**: {timestamp}")
    lines.append(f"> **Auto-generado** por `update_board.py` — NO editar a mano.")
    lines.append(
        "> Ver: [[README|Cómo usar el kanban]] · [[SPRINT-1|Sprint actual]] · "
        "[[SPRINT-2|Sprint siguiente]] · [[BACKLOG|Backlog]] · [[PLAN|Roadmap]]"
    )
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append("| Total | 🔄 In Progress | ⛔ Blocked | 📋 Pending | ✅ Done | 🚫 Cancelled | Progress |")
    lines.append("|-------|----------------|------------|-------------|---------|---------------|----------|")
    lines.append(
        f"| **{total}** | {counts['in-progress']} | {counts['blocked']} | "
        f"{counts['pending']} | {counts['done']} | {counts['cancelled']} | **{progress}%** |"
    )
    lines.append("")
    lines.append(f"_Progress = done / (total − cancelled) = {counts['done']}/{active}_")
    lines.append("")

    # Progress bar
    bar_width = 30
    filled = int(progress / 100 * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    lines.append(f"```")
    lines.append(f"{bar} {progress}%")
    lines.append(f"```")
    lines.append("")

    # Sprint breakdown
    sprints: dict[str, dict[str, int]] = {}
    for task in tasks.values():
        sprint = task["frontmatter"].get("sprint", "?")
        status = task["frontmatter"].get("status", "pending")
        sprints.setdefault(sprint, {s: 0 for s in STATUS_ORDER})
        sprints[sprint][status] = sprints[sprint].get(status, 0) + 1

    if sprints:
        lines.append("## Por Sprint")
        lines.append("")
        lines.append("| Sprint | Total | Done | In Progress | Pending | Blocked | Cancelled | Progress |")
        lines.append("|--------|-------|------|-------------|---------|---------|-----------|----------|")
        for sprint in sorted(sprints.keys()):
            counts_s = sprints[sprint]
            total_s = sum(counts_s.values())
            active_s = total_s - counts_s.get("cancelled", 0)
            progress_s = round(counts_s.get("done", 0) / active_s * 100) if active_s > 0 else 0
            lines.append(
                f"| **{sprint}** | {total_s} | {counts_s.get('done', 0)} | "
                f"{counts_s.get('in-progress', 0)} | {counts_s.get('pending', 0)} | "
                f"{counts_s.get('blocked', 0)} | {counts_s.get('cancelled', 0)} | "
                f"**{progress_s}%** |"
            )
        lines.append("")

    # Render columns in priority order
    for status in STATUS_ORDER:
        col = columns[status]
        if not col:
            continue
        icon = STATUS_ICONS[status]
        label = STATUS_LABELS[status]
        lines.append(f"## {icon} {label} ({len(col)})")
        lines.append("")

        if status == "in-progress":
            lines.append("| ID | Task | Sprint | Day | Owner | Updated |")
            lines.append("|----|------|--------|-----|-------|---------|")
            for t in col:
                fm = t["frontmatter"]
                day = fm.get("day", "")
                day_str = f"D{day}" if day else "—"
                lines.append(
                    f"| [[{fm['id']}]] | {fm.get('title', '')} | "
                    f"{fm.get('sprint', '')} | {day_str} | "
                    f"{fm.get('owner', '')} | {fm.get('updated', '')} |"
                )
        elif status == "blocked":
            lines.append("| ID | Task | Sprint | Reason | Blocked Since |")
            lines.append("|----|------|--------|--------|---------------|")
            for t in col:
                fm = t["frontmatter"]
                lines.append(
                    f"| [[{fm['id']}]] | {fm.get('title', '')} | "
                    f"{fm.get('sprint', '')} | {fm.get('blocked_reason', '')} | "
                    f"{fm.get('updated', '')} |"
                )
        elif status == "pending":
            lines.append("| ID | Task | Sprint | Day | Priority | Estimated |")
            lines.append("|----|------|--------|-----|----------|-----------|")
            for t in col:
                fm = t["frontmatter"]
                day = fm.get("day", "")
                day_str = f"D{day}" if day else "—"
                lines.append(
                    f"| [[{fm['id']}]] | {fm.get('title', '')} | "
                    f"{fm.get('sprint', '')} | {day_str} | "
                    f"{fm.get('priority', '')} | {fm.get('estimated', '')} |"
                )
        elif status == "done":
            lines.append("| ID | Task | Sprint | Estimated | Actual | Completed |")
            lines.append("|----|------|--------|-----------|--------|-----------|")
            for t in col:
                fm = t["frontmatter"]
                lines.append(
                    f"| [[{fm['id']}]] | {fm.get('title', '')} | "
                    f"{fm.get('sprint', '')} | {fm.get('estimated', '')} | "
                    f"{fm.get('actual', '')} | {fm.get('updated', '')} |"
                )
        elif status == "cancelled":
            lines.append("| ID | Task | Sprint | Reason |")
            lines.append("|----|------|--------|--------|")
            for t in col:
                fm = t["frontmatter"]
                lines.append(
                    f"| [[{fm['id']}]] | {fm.get('title', '')} | "
                    f"{fm.get('sprint', '')} | {fm.get('cancelled_reason', '')} |"
                )

        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    if not TASKS_DIR.exists():
        TASKS_DIR.mkdir(parents=True)
        print(f"Created {TASKS_DIR}")

    tasks = load_tasks()
    print(f"Loaded {len(tasks)} task(s)")

    prev_state = load_state()
    changes = detect_changes(tasks, prev_state)

    # IMPORTANT: save state BEFORE writing history.
    # If we crash after history but before state, the next run would
    # re-detect the same changes and append duplicate history entries.
    new_state = {
        tid: {
            "status": t["frontmatter"].get("status", "pending"),
            "title": t["frontmatter"].get("title", ""),
            "sprint": t["frontmatter"].get("sprint", ""),
            "updated": t["frontmatter"].get("updated", ""),
        }
        for tid, t in tasks.items()
    }
    save_state(new_state)

    if changes:
        history_file = append_history(changes)
        print(f"Detected {len(changes)} status change(s):")
        for c in changes:
            old = c["old"] or "new"
            print(f"  {c['id']}: {old} → {c['new']}")
        if history_file:
            print(f"History appended to {history_file.relative_to(KANBAN_DIR.parent)}")
    else:
        print("No status changes since last run")

    board_content = render_board(tasks)
    BOARD_FILE.write_text(board_content, encoding="utf-8")
    print(f"BOARD.md updated ({len(tasks)} tasks)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
