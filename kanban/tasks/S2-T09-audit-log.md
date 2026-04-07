---
id: S2-T09
title: Implementar audit log (PostToolUse hook → JSONL)
sprint: S2
day: 2
status: pending
priority: P1
type: implementation
tags: [agent, python, observability, day-2]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 30m
actual: ""
owner: claude
blocks: []
blocked_by: [S2-T08]
related_docs: [SPRINT-2]
commits: []
files_touched: []
---

# S2-T09: Audit log via PostToolUse hook

> **Sprint**: [[SPRINT-2]] · **Día**: 2 · **Status**: pending

## Contexto

Cada tool_use del agent se logea a un archivo JSONL para auditoría posterior. GlobalMVM puede revisar exactamente qué hizo el agent.

## Acceptance Criteria

- [ ] PostToolUse hook que escribe entry JSONL por cada tool call
- [ ] Path configurable via `--audit-log <path>` o env `FIXI_AUDIT_LOG`
- [ ] Cada entry: `{run_id, timestamp, tool_name, tool_input, tool_output_summary}`
- [ ] Default path: `./fixi-audit-{run_id}.jsonl`
- [ ] El archivo se incluye en el RunResult devuelto por el orchestrator

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
