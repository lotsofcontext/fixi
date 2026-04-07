---
id: S1-T12
title: Rehearsal Fixi contra WI-101 → run-01-github.md
sprint: S1
day: 2
status: done
priority: P1
type: research
tags: [rehearsal, demo, github, transcript, day-2]
created: 2026-04-07T00:00:00
updated: 2026-04-07T04:15:00
estimated: 1h30m
actual: 3m51s
owner: user+claude
blocks: [S1-T17]
blocked_by: [S1-T09, S1-T11]
related_docs: [SPRINT-1, BACKLOG, SKILL]
commits: [801d196, e083555, 63bf9ad]
files_touched:
  - fixi-demo-dotnet/src/GMVM.EnergyTracker.Domain/Services/CalculadoraConsumo.cs
  - fixi-demo-dotnet/docs/demos/run-01-github.md
---
pr_url: https://github.com/lotsofcontext/fixi-demo-dotnet/pull/1
pr_state: MERGED (then reverted on master for demo reproducibility)
fixi_runtime: 3m51s
---
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

**Ejecutado por el usuario en sesión separada de Claude Code**, con el skill `fix-issue` cargado e invocado contra `docs/issues/WI-101-bug-lectura-negativa.md`.

### Resultado de Fixi (reportado por el usuario)

Fixi ejecutó los 10 pasos end-to-end en **3m 51s**:

- **Safety Gate**: verificó contexto, working tree limpio
- **Parseo**: extrajo título, body, priority, tags del work item markdown
- **Clasificación**: `bug` con confianza ALTA (keywords: DivideByZero, exception, 500, stack trace)
- **Root Cause**: identificó `CalculadoraConsumo.Calcular` usando `TimeSpan.Days` que retorna 0 cuando ambas lecturas son del mismo día
- **Branch**: creó `fix/WI-101-divide-by-zero-mismo-dia` desde master
- **Fix**: +9 líneas, 1 archivo — guard clause `if (diasTranscurridos < 1) return deltaKwh;`
- **Tests**: `CalculadoraConsumoTests` pasó de 2 rojos a 4 verdes. Suite completa: 5/5 pass (excluyendo los 3 de WI-103 que son intencionales)
- **PR**: creó [PR #1](https://github.com/lotsofcontext/fixi-demo-dotnet/pull/1) con template completo (Issue / Clasificación / Causa Raíz / Cambios / Testing / Tracking)
- **Tracking**: reportó FIX COMPLETE

### Observaciones clave del comportamiento de Fixi

1. **Respetó "nunca inventar información"**: 2 de los acceptance criteria del work item referencian archivos que NO existen en el repo demo (`LecturasControllerTests.cs`, `CHANGELOG.md`). Fixi los marcó explícitamente como `[ ] N/A` en el PR body con justificación. NO inventó esos archivos para "cumplir" el AC.
2. **Cambio mínimo respetado**: solo +9 líneas, no tocó código adjacente, no refactorizó la función entera.
3. **Rama del promedio diario preservada**: el comportamiento para lecturas en días distintos es idéntico al original.
4. **El fix es idiomatic**: usa guard clause con comentario explicativo referenciando WI-101.

### Transcript documentado

Se creó [`fixi-demo-dotnet/docs/demos/run-01-github.md`](../../../fixi-demo-dotnet/docs/demos/run-01-github.md) con:
- Los 10 pasos detallados
- El diff exacto del fix
- Output de `dotnet test`
- Tabla de evidencia verificable (links a commits, PR, branches)
- Métricas del run
- 5 observaciones clave sobre comportamiento de Fixi

### ⚠️ Incident: fix accidentalmente mergeado a master

Al crear el branch para el transcript, el working directory estaba en la rama `fix/WI-101-divide-by-zero-mismo-dia` (Fixi la dejó checkeada después de crear el PR). No verifiqué con `git branch --show-current` antes de hacer `git checkout -b docs/run-01-transcript`.

**Resultado**: el branch del transcript se creó desde `801d196` (la cabeza del fix branch) en lugar de desde `f73d62b` (master). Cuando mergeé el branch a master, el fix se fue junto, contaminando el baseline del demo.

**Impacto**:
- Master dejó de tener 5 tests rojos y pasó a tener solo 3 (los de WI-103)
- El demo para GlobalMVM perdía parcialmente WI-101 como caso demostrable
- PR #1 mostraba como "merged" aunque técnicamente no se mergeó via UI

**Resolución**: el usuario eligió **Opción A (revert)**:
```
git revert 801d196 → commit 63bf9ad
git push origin master
```

El revert commit tiene un mensaje detallado explicando el contexto y que el fix sigue siendo correcto. Master vuelve a tener 5 tests rojos. PR #1 queda como evidencia histórica (GitHub lo muestra MERGED porque el commit está en el linaje de master).

**Lección para el futuro**: SIEMPRE verificar la branch activa con `git branch --show-current` antes de crear una rama nueva, especialmente cuando otro proceso (Fixi en este caso) puede haber dejado el repo en un estado diferente.

## Outcome

**Primer rehearsal end-to-end exitoso de Fixi contra un codebase .NET real**. 

Artefactos:
- [PR #1](https://github.com/lotsofcontext/fixi-demo-dotnet/pull/1) — la evidencia primaria (commit `801d196`, +9 líneas, tests verdes)
- [`fixi-demo-dotnet/docs/demos/run-01-github.md`](https://github.com/lotsofcontext/fixi-demo-dotnet/blob/master/docs/demos/run-01-github.md) — transcript completo
- Commit `63bf9ad` en master — revert para preservar baseline del demo

**Métricas validadas con dato real**:
- Tiempo total de Fixi: **3m 51s**
- Líneas modificadas: **+9**
- Archivos tocados: **1**
- Branches protegidos: master nunca fue tocado directamente por Fixi (el fix estaba en su propia branch aislada)
- Hallucinations: **0**

Sprint 1 ahora a **17/18 = 94%**. Solo queda T15 (rehearsal ADO).

## History

- `2026-04-07 00:00` · created (status: pending)
- `2026-04-07 03:50` · started (status: in-progress, user ejecutó Fixi en sesión separada)
- `2026-04-07 04:00` · Fixi terminó en 3m51s, PR #1 creado
- `2026-04-07 04:05` · transcript `run-01-github.md` documentado
- `2026-04-07 04:10` · incident: fix mergeado accidentalmente a master
- `2026-04-07 04:15` · completed (status: done) · revert commit `63bf9ad` restauró baseline
