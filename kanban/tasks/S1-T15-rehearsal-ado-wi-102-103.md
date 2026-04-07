---
id: S1-T15
title: Rehearsal Fixi contra WI-102 y WI-103 (path Azure DevOps)
sprint: S1
day: 4
status: pending
priority: P1
type: research
tags: [rehearsal, demo, azure-devops, transcript, day-4]
created: 2026-04-07T00:00:00
updated: 2026-04-07T00:00:00
estimated: 2h
actual: ""
owner: claude
blocks: [S1-T17]
blocked_by: [S1-T13, S1-T14]
related_docs: [SPRINT-1, BACKLOG, SKILL]
commits: []
files_touched: []
---

# S1-T15: Rehearsal Fixi contra WI-102 y WI-103 (Azure DevOps)

> **Sprint**: [[SPRINT-1]] · **Día**: 4 · **Status**: pending
> **Owner**: claude · **Estimated**: 2h

## Contexto

Segundo rehearsal real, esta vez por el path Azure DevOps. Cubre PERF (WI-102) y SECURITY (WI-103) — el security forzará GUIDED automático, demostrando los escaladores.

## Pre-requisitos (manuales)

- [ ] ADO sandbox creado (org throwaway)
- [ ] PAT configurado en `az`
- [ ] Mirror de `fixi-demo-dotnet` a Azure Repos del sandbox
- [ ] WI-102 y WI-103 creados como work items reales en ADO

## Acceptance Criteria

- [ ] Rehearsal WI-102 (perf): Fixi corrige N+1, 51 queries → ≤2, perf test pasa
- [ ] Rehearsal WI-103 (security): Fixi clasifica como security, **fuerza GUIDED**, agrega `[Authorize(Roles="Admin")]`, security tests pasan
- [ ] Ambos PRs creados en Azure Repos
- [ ] Transcript en `docs/demos/run-02-ado.md` con: setup ADO, dos runs documentados paso a paso, screenshots de los PRs, decisiones de Fixi

## Plan

Pre-setup (manual con usuario presente), después dos runs consecutivos en GUIDED, capturando todo en markdown.

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 00:00` · created (status: pending)
