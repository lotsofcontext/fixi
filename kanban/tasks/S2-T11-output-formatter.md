---
id: S2-T11
title: Implementar output.py (JSON + human formatters)
sprint: S2
day: 2
status: pending
priority: P1
type: implementation
tags: [agent, python, output, day-2]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 30m
actual: ""
owner: claude
blocks: [S2-T12]
blocked_by: [S2-T10]
related_docs: [SPRINT-2]
commits: []
files_touched: []
---

# S2-T11: Output formatters

> **Sprint**: [[SPRINT-2]] · **Día**: 2 · **Status**: pending

## Contexto

Formatear el `RunResult` para CI/CD (JSON parseable) o terminal humano (rich tables).

## Acceptance Criteria

- [ ] `src/fixi_agent/output.py` creado
- [ ] `format_result(result, fmt) -> str` con dos modos: json, human
- [ ] JSON output: dump completo del RunResult + audit_log_path
- [ ] Human output: tabla con resumen, status, PR URL, branch, files, duration
- [ ] Streaming durante ejecución también respeta el formato (mensajes de progreso a stderr en json mode)

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
