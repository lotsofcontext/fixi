---
id: S2-T06
title: Implementar orchestrator.py (ClaudeSDKClient wrapper)
sprint: S2
day: 1
status: done
priority: P0
type: implementation
tags: [agent, python, claude-sdk, day-1]
created: 2026-04-07T04:30:00
updated: 2026-04-07T07:15:00
estimated: 1h
actual: ""
owner: claude
blocks: [S2-T07, S2-T08, S2-T10]
blocked_by: [S2-T03, S2-T05, S2-T02]
related_docs: [SPRINT-2, SKILL]
commits: []
files_touched: []
---

# S2-T06: Orchestrator (Claude Agent SDK wrapper)

> **Sprint**: [[SPRINT-2]] · **Día**: 1 · **Status**: pending

## Contexto

Core del agent: instancia `ClaudeSDKClient` con el system_prompt cargado, los tools permitidos, y arranca el query loop con el work item como prompt inicial. Por ahora SIN hooks (esos vienen en S2-T08).

## Acceptance Criteria

- [ ] `src/fixi_agent/orchestrator.py` creado
- [ ] `class FixiOrchestrator`:
  - `__init__(work_item, repo_path, options)`: configura
  - `async run() -> RunResult`: ejecuta el agent loop
- [ ] Usa `ClaudeAgentOptions` con:
  - `system_prompt = load_system_prompt()`
  - `allowed_tools = ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "WebFetch"]`
  - `permission_mode = "acceptEdits"`
  - `cwd = str(repo_path)`
- [ ] Streaming de mensajes via `async for message in query(...)`
- [ ] Captura de PR URL y branch del output del agent
- [ ] Devuelve `RunResult(success, pr_url, branch, files_changed, duration)`

## Plan

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage
from .prompts import load_system_prompt
from .parser import WorkItem
from pathlib import Path
from pydantic import BaseModel
from time import monotonic

class RunResult(BaseModel):
    success: bool
    pr_url: str | None
    branch: str | None
    files_changed: list[str]
    duration_seconds: float
    error: str | None = None

class FixiOrchestrator:
    def __init__(self, work_item: WorkItem, repo_path: Path):
        self.work_item = work_item
        self.repo_path = repo_path
        self.system_prompt = load_system_prompt()

    async def run(self) -> RunResult:
        start = monotonic()
        prompt = self._build_initial_prompt()
        options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            allowed_tools=["Read", "Write", "Edit", "Bash", "Grep", "Glob", "WebFetch"],
            permission_mode="acceptEdits",
            cwd=str(self.repo_path),
        )
        # Stream y capturar output
        # ...
```

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
