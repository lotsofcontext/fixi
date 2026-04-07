---
id: S1-T09
title: Pre-crear 3 work items markdown en docs/issues/
sprint: S1
day: 2
status: in-progress
priority: P1
type: docs
tags: [demo-repo, work-items, day-2]
created: 2026-04-07T00:00:00
updated: 2026-04-07T01:00:00
estimated: 1h
actual: ""
owner: agent-work-items
blocks: [S1-T12]
blocked_by: [S1-T08]
related_docs: [SPRINT-1, BACKLOG]
commits: []
files_touched: []
---

# S1-T09: Pre-crear 3 work items markdown

> **Sprint**: [[SPRINT-1]] · **Día**: 2 · **Status**: pending
> **Owner**: claude · **Estimated**: 1h

## Contexto

Fixi necesita issues parseables para ejecutarse contra el demo. Creamos los 3 work items en formato Azure DevOps export markdown, bilingüe español/inglés (matchea estilo GlobalMVM).

## Acceptance Criteria

- [ ] `docs/issues/WI-101-bug-lectura-negativa.md` — formato ADO export, español
- [ ] `docs/issues/WI-102-perf-listado-medidores.md` — formato ADO export, español
- [ ] `docs/issues/WI-103-security-endpoint-admin.md` — formato ADO export, español
- [ ] Cada uno con: descripción, evidencia (stack trace o curl), pasos para reproducir, acceptance criteria, tags
- [ ] Reportadores realistas (Camilo Restrepo, Joaris Angulo, Jefferson Acevedo)

## Plan

Usar los textos detallados del agente demo-repo-designer como base. Cada WI debe ser parseable por Fixi en Paso 1.

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 00:00` · created (status: pending)
