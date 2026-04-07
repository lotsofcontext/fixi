---
id: S2-T18
title: Rehearsal end-to-end del agent CLI vs WI-101/102/103
sprint: S2
day: 4
status: pending
priority: P0
type: research
tags: [agent, rehearsal, demo, day-4]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 2h
actual: ""
owner: claude
blocks: [S2-T19]
blocked_by: [S2-T16]
related_docs: [SPRINT-2]
commits: []
files_touched: []
---

# S2-T18: Rehearsal end-to-end del agent

> **Sprint**: [[SPRINT-2]] · **Día**: 4 · **Status**: pending

## Contexto

**El rehearsal real** del entregable final. Reemplaza los rehearsals del skill ([[S1-T12]] y [[S1-T15]]). Ejecutar `fixi resolve` contra los 3 work items del demo repo y capturar transcripts.

## Acceptance Criteria

- [ ] `fixi resolve --work-item .../WI-101.md --repo lotsofcontext/fixi-demo-dotnet` ejecutado, produce PR
- [ ] `fixi resolve --work-item .../WI-102.md --repo lotsofcontext/fixi-demo-dotnet` ejecutado, produce PR
- [ ] `fixi resolve --work-item .../WI-103.md --repo lotsofcontext/fixi-demo-dotnet` ejecutado, produce PR (con escalación a default mode por security)
- [ ] `docs/demos/run-03-agent-cli.md` con transcripts de los 3 runs
- [ ] Métricas medidas: duración por run, líneas modificadas, costo token aproximado
- [ ] Verificación: `dotnet test` antes y después debe mostrar la transición correcta de fails
- [ ] Optionally: corre el GitHub Actions workflow de ejemplo contra WI-101 y captura el run ID

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
