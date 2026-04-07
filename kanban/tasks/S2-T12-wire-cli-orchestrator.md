---
id: S2-T12
title: Wire CLI → orchestrator → output end-to-end
sprint: S2
day: 2
status: done
priority: P0
type: implementation
tags: [agent, python, integration, day-2]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 30m
actual: ""
owner: claude
blocks: [S2-T14]
blocked_by: [S2-T08, S2-T11]
related_docs: [SPRINT-2]
commits: []
files_touched: []
---

# S2-T12: Wire all components together

> **Sprint**: [[SPRINT-2]] · **Día**: 2 · **Status**: pending

## Contexto

Conectar todas las piezas en `cli.py`:
1. parse work item → 2. clone repo → 3. orchestrator (con hooks) → 4. format result → 5. exit

## Acceptance Criteria

- [ ] `fixi resolve` flujo completo funciona end-to-end
- [ ] Manejo de errores en cada paso (con exit codes correctos)
- [ ] Smoke test E2E: `fixi resolve --work-item docs/issues/WI-101.md --repo Z:/fixi-demo-dotnet` produce PR
- [ ] Cleanup del tmpdir incluso si hay error
- [ ] Logging consistente

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
