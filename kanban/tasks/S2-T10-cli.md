---
id: S2-T10
title: Implementar cli.py (click) — fixi resolve
sprint: S2
day: 2
status: done
priority: P0
type: implementation
tags: [agent, python, cli, day-2]
created: 2026-04-07T04:30:00
updated: 2026-04-07T08:00:00
estimated: 45m
actual: ""
owner: claude
blocks: [S2-T11, S2-T12]
blocked_by: [S2-T06]
related_docs: [SPRINT-2]
commits: []
files_touched: []
---

# S2-T10: CLI entry point

> **Sprint**: [[SPRINT-2]] · **Día**: 2 · **Status**: pending

## Contexto

CLI con `click` que es el entry point principal del package. Diseñado para invocación desde CI/CD.

## Acceptance Criteria

- [ ] `src/fixi_agent/cli.py` creado
- [ ] Comando principal: `fixi resolve --work-item <url> [--repo <url>] [--branch <name>] [--output json|human] [--audit-log <path>]`
- [ ] Sub-comando: `fixi version`
- [ ] Sub-comando: `fixi check` (verifica deps: Claude Code CLI, ANTHROPIC_API_KEY, git)
- [ ] Help en español
- [ ] Exit codes: 0 = success, 1 = parse error, 2 = clone error, 3 = agent error, 4 = guardrail violation, 5 = unknown
- [ ] Entry point registrado en pyproject.toml

## Plan

```python
import click, asyncio, sys
from .parser import parse_work_item
from .cloner import clone_repo
from .orchestrator import FixiOrchestrator
from .output import format_result

@click.group()
@click.version_option()
def main():
    """Fixi — Autonomous issue resolution agent."""
    pass

@main.command()
@click.option("--work-item", required=True, help="URL or reference of work item")
@click.option("--repo", help="Target repo URL (auto-detected if omitted)")
@click.option("--branch", help="Branch to clone (default: repo default)")
@click.option("--output", type=click.Choice(["json", "human"]), default="human")
@click.option("--audit-log", type=click.Path(), help="Path for audit JSONL")
def resolve(work_item, repo, branch, output, audit_log):
    """Resolve a work item end-to-end: clone, analyze, fix, PR."""
    asyncio.run(_resolve_async(work_item, repo, branch, output, audit_log))

# ...
```

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
