"""CLI entry point for Fixi Agent.

Invocable from CI/CD pipelines (GitHub Actions, Azure Pipelines)
or manually from a terminal.

Usage:
    fixi resolve --work-item <url> --repo <url>
    fixi resolve --work-item docs/issues/WI-101.md --repo-path ./my-repo
    fixi version
    fixi check
"""

from __future__ import annotations

import asyncio
import io
import json
import os
import sys
from pathlib import Path

import click
import structlog

from . import __version__
from .orchestrator import FixiOrchestrator, RunResult

# Fix Windows cp1252 encoding for Unicode chars in Claude output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True
    )


# Exit codes
EXIT_OK = 0
EXIT_PARSE_ERROR = 1
EXIT_CLONE_ERROR = 2
EXIT_AGENT_ERROR = 3
EXIT_GUARDRAIL_VIOLATION = 4
EXIT_UNKNOWN = 5


def _configure_logging(verbose: bool) -> None:
    """Configure structlog for CLI output."""
    import logging

    log_level = logging.DEBUG if verbose else logging.INFO
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
    )


@click.group()
@click.version_option(version=__version__, prog_name="fixi")
def main() -> None:
    """Fixi — Autonomous issue resolution agent.

    Resolves tickets end-to-end from CI/CD pipelines: clones the
    target repo, parses the work item, runs the agent loop with
    SKILL.md as system prompt, and opens a PR.
    """


@main.command()
@click.option(
    "--work-item", "-w",
    required=True,
    help="URL, shorthand, or file path of the work item to resolve.",
)
@click.option(
    "--repo", "-r",
    default=None,
    help="HTTPS URL of the target repo to clone. If omitted, uses --repo-path or cwd.",
)
@click.option(
    "--repo-path",
    default=None,
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help="Local path to the target repo (skip cloning).",
)
@click.option(
    "--branch", "-b",
    default=None,
    help="Branch to clone/checkout (default: repo's default branch).",
)
@click.option(
    "--tracking-mode", "-t",
    type=click.Choice(["hq", "client", "none"]),
    default="none",
    help="Tracking mode: hq (triple-write), client (ACTIVO.md only), none (skip).",
)
@click.option(
    "--skill-dir",
    default=None,
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help="Path to skill/ directory. Auto-detected if omitted.",
)
@click.option(
    "--output", "-o",
    type=click.Choice(["json", "human"]),
    default="human",
    help="Output format: json (for CI/CD parsing) or human (for terminal).",
)
@click.option(
    "--max-turns",
    default=None,
    type=int,
    help="Maximum agent turns (default: SDK default).",
)
@click.option(
    "--max-budget",
    default=None,
    type=float,
    help="Maximum cost in USD (default: SDK default).",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Enable debug logging.",
)
def resolve(
    work_item: str,
    repo: str | None,
    repo_path: str | None,
    branch: str | None,
    tracking_mode: str,
    skill_dir: str | None,
    output: str,
    max_turns: int | None,
    max_budget: float | None,
    verbose: bool,
) -> None:
    """Resolve a work item end-to-end: clone, analyze, fix, PR."""
    _configure_logging(verbose)

    orchestrator = FixiOrchestrator(
        work_item_ref=work_item,
        repo_url=repo,
        repo_path=Path(repo_path) if repo_path else None,
        branch=branch,
        tracking_mode=tracking_mode,
        skill_dir=Path(skill_dir) if skill_dir else None,
        max_turns=max_turns,
        max_budget_usd=max_budget,
    )

    result = asyncio.run(orchestrator.run())
    _print_result(result, output)
    sys.exit(_exit_code(result))


@main.command()
def check() -> None:
    """Verify prerequisites: Claude Code CLI, git, auth tokens."""
    import shutil
    import subprocess

    all_ok = True

    # Claude Code CLI
    claude_path = shutil.which("claude") or shutil.which("claude.CMD")
    if claude_path:
        try:
            v = subprocess.run(
                [claude_path, "--version"], capture_output=True, text=True, timeout=10
            )
            click.echo(f"  [OK] Claude Code CLI: {v.stdout.strip()} at {claude_path}")
        except Exception as e:
            click.echo(f"  [FAIL] Claude Code CLI found but errored: {e}")
            all_ok = False
    else:
        click.echo("  [FAIL] Claude Code CLI not found. Install: npm i -g @anthropic-ai/claude-code")
        all_ok = False

    # git
    git_path = shutil.which("git")
    if git_path:
        v = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
        click.echo(f"  [OK] git: {v.stdout.strip()}")
    else:
        click.echo("  [FAIL] git not found")
        all_ok = False

    # GH_TOKEN
    if os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"):
        click.echo("  [OK] GitHub token: set")
    else:
        click.echo("  [WARN] GH_TOKEN / GITHUB_TOKEN not set (needed for GitHub repos)")

    # AZURE_DEVOPS_PAT
    if os.environ.get("AZURE_DEVOPS_PAT"):
        click.echo("  [OK] Azure DevOps PAT: set")
    else:
        click.echo("  [WARN] AZURE_DEVOPS_PAT not set (needed for ADO repos)")

    # skill/ directory
    try:
        from .prompts import _find_skill_dir
        sd = _find_skill_dir()
        click.echo(f"  [OK] skill/ directory: {sd}")
    except FileNotFoundError:
        click.echo("  [WARN] skill/ directory not auto-detected. Pass --skill-dir to resolve.")

    click.echo()
    if all_ok:
        click.echo("All prerequisites OK. Ready to run: fixi resolve --work-item <url>")
    else:
        click.echo("Some prerequisites missing. Fix the FAIL items above.")
        sys.exit(1)


def _print_result(result: RunResult, fmt: str) -> None:
    """Print the run result in the requested format."""
    if fmt == "json":
        data = result.model_dump(exclude={"agent_output"})
        if result.work_item:
            data["work_item"] = result.work_item.model_dump()
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        click.echo()
        click.echo("=" * 60)
        if result.success:
            click.echo("FIX COMPLETE")
        else:
            click.echo("FIX FAILED")
        click.echo("=" * 60)
        click.echo()
        if result.work_item:
            click.echo(f"  Issue:          {result.work_item.title}")
            click.echo(f"  External ID:    {result.work_item.external_id}")
            click.echo(f"  Source:         {result.work_item.source_type.value}")
        if result.classification:
            click.echo(f"  Classification: {result.classification}")
        click.echo(f"  Branch:         {result.branch or '(none)'}")
        click.echo(f"  PR:             {result.pr_url or '(none)'}")
        click.echo(f"  Files changed:  {len(result.files_changed)}")
        click.echo(f"  Duration:       {result.duration_seconds:.1f}s")
        if result.total_cost_usd is not None:
            click.echo(f"  Cost:           ${result.total_cost_usd:.4f}")
        click.echo(f"  Turns:          {result.num_turns}")
        if result.error:
            click.echo(f"  Error:          {result.error}")
        click.echo()


def _exit_code(result: RunResult) -> int:
    """Map RunResult to an exit code."""
    if result.success:
        return EXIT_OK
    if result.error and "parse" in result.error.lower():
        return EXIT_PARSE_ERROR
    if result.error and "clone" in result.error.lower():
        return EXIT_CLONE_ERROR
    if result.error and "guardrail" in result.error.lower():
        return EXIT_GUARDRAIL_VIOLATION
    if result.error and "agent" in result.error.lower():
        return EXIT_AGENT_ERROR
    return EXIT_UNKNOWN
