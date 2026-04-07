---
id: S1-T12
title: Rehearsal Fixi contra WI-101 → run-01-github.md
sprint: S1
day: 2
status: pending
priority: P1
type: research
tags: [rehearsal, demo, github, transcript, day-2]
created: 2026-04-07T00:00:00
updated: 2026-04-07T00:00:00
estimated: 1h30m
actual: ""
owner: claude
blocks: [S1-T17]
blocked_by: [S1-T09, S1-T11]
related_docs: [SPRINT-1, BACKLOG, SKILL]
commits: []
files_touched: []
---

# S1-T12: Rehearsal Fixi contra WI-101 (path GitHub)

> **Sprint**: [[SPRINT-1]] · **Día**: 2 · **Status**: pending
> **Owner**: claude · **Estimated**: 1h30m

## Contexto

Primer rehearsal end-to-end real: ejecutar Fixi contra el bug `WI-101` usando el path GitHub (work item parseado de markdown, PR creado en GitHub). Capturar transcript completo en `docs/demos/run-01-github.md` para que Joaris pueda diffearlo.

## Acceptance Criteria

- [ ] `/fix-issue` invocado contra WI-101 desde la sesión Claude Code en `Z:\fixi-demo-dotnet`
- [ ] Safety Gate ejecutado y reportado
- [ ] Clasificación correcta: `bug`
- [ ] Root cause encontrado en `CalculadoraConsumo.cs`
- [ ] Branch `fix/WI-101-...` creado
- [ ] Fix mínimo aplicado (`.Days` → `.TotalDays` o guard clause)
- [ ] `dotnet test` muestra el test del bug pasando (3 rojos restantes)
- [ ] PR creado en `lotsofcontext/fixi-demo-dotnet`
- [ ] Transcript en `docs/demos/run-01-github.md` con: input, cada paso de Fixi, output, screenshot del PR

## Plan

Es Sprint dentro de un sprint. Nivel GUIDED para poder pausar y documentar cada paso.

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 00:00` · created (status: pending)
