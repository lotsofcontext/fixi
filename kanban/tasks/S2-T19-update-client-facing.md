---
id: S2-T19
title: Update CLIENT-FACING.md — narrativa skill → agent
sprint: S2
day: 4
status: pending
priority: P0
type: docs
tags: [docs, client-facing, day-4]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 1h
actual: ""
owner: claude
blocks: [S2-T20]
blocked_by: [S2-T18]
related_docs: [SPRINT-2, CLIENT-FACING]
commits: []
files_touched: []
---

# S2-T19: Update CLIENT-FACING con narrativa de agent

> **Sprint**: [[SPRINT-2]] · **Día**: 4 · **Status**: pending

## Contexto

Actualizar el doc para reflejar que el entregable es un **agent CLI**, no un skill de Claude Code. Mantener el skill posicionado como "la lógica que el agent ejecuta" (capas).

## Acceptance Criteria

- [ ] Sección "Cómo lo pueden probar hoy" actualizada con `pip install` y `fixi resolve`
- [ ] Nueva sección "Integración con CI/CD": ejemplos de GH Actions y ADO Pipelines
- [ ] Sección de arquitectura actualizada: trigger → CLI → orchestrator → agent SDK → tools
- [ ] Diagramas actualizados (referenciar `diagrams.md`)
- [ ] Posicionamiento "como capas": skill = brain humano-readable, agent = body deployable
- [ ] Métricas actualizadas con dato real de los runs del agent (S2-T18)
- [ ] Versión bump a 3.0

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
