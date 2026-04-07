#!/usr/bin/env python
"""Smoke test: run the Fixi agent against WI-101 in fixi-demo-dotnet.

This is NOT a pytest test — it's a standalone script meant to be run
interactively during development. It makes REAL API calls to Claude
and creates REAL branches/PRs in the demo repo.

Usage:
    cd agent
    venv/Scripts/python tests/integration/smoke_test.py

Prerequisites:
    - Claude Code CLI authenticated (claude --version works)
    - git configured with push access to lotsofcontext/fixi-demo-dotnet
    - fixi-demo-dotnet cloned at Z:/fixi-demo-dotnet (or adjust DEMO_REPO_PATH)
"""

from __future__ import annotations

import asyncio
import io
import os
import sys
from pathlib import Path

# Fix Windows cp1252 encoding for Unicode chars in Claude output (→, ✅, etc.)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# Ensure our package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fixi_agent.orchestrator import FixiOrchestrator


DEMO_REPO_URL = "https://github.com/lotsofcontext/fixi-demo-dotnet"
DEMO_REPO_LOCAL = Path("Z:/fixi-demo-dotnet")

# Use the local file work item (avoids network dependency for parsing)
WORK_ITEM_FILE = DEMO_REPO_LOCAL / "docs" / "issues" / "WI-101-bug-lectura-negativa.md"


async def main() -> int:
    print("=" * 60)
    print("FIXI AGENT SMOKE TEST")
    print("=" * 60)
    print()

    # Verify prerequisites
    if not WORK_ITEM_FILE.exists():
        print(f"ERROR: Work item file not found: {WORK_ITEM_FILE}")
        print("Make sure fixi-demo-dotnet is cloned at Z:/fixi-demo-dotnet")
        return 1

    print(f"Work item: {WORK_ITEM_FILE}")
    print(f"Repo: {DEMO_REPO_LOCAL} (local path, no clone needed)")
    print(f"Tracking mode: none (smoke test — no tracking writes)")
    print()
    print("Starting agent...")
    print("-" * 60)

    orchestrator = FixiOrchestrator(
        work_item_ref=str(WORK_ITEM_FILE),
        repo_path=DEMO_REPO_LOCAL,
        tracking_mode="none",
        skill_dir=Path("Z:/fixi/skill"),
    )

    result = await orchestrator.run()

    print("-" * 60)
    print()
    print("RESULT:")
    print(f"  Success:        {result.success}")
    print(f"  PR URL:         {result.pr_url or '(none)'}")
    print(f"  Branch:         {result.branch or '(none)'}")
    print(f"  Classification: {result.classification or '(none)'}")
    print(f"  Files changed:  {result.files_changed}")
    print(f"  Duration:       {result.duration_seconds}s")
    print(f"  Cost:           ${result.total_cost_usd or 0:.4f}")
    print(f"  Turns:          {result.num_turns}")
    if result.error:
        print(f"  Error:          {result.error}")
    print()

    if result.success:
        print("SMOKE TEST PASSED")
        return 0
    else:
        print("SMOKE TEST FAILED")
        if result.agent_output:
            print()
            print("Agent output (last 500 chars):")
            print(result.agent_output[-500:])
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
