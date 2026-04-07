---
id: S1-T11
title: README bilingüe del demo repo
sprint: S1
day: 2
status: done
priority: P1
type: docs
tags: [demo-repo, readme, bilingual, day-2]
created: 2026-04-07T00:00:00
updated: 2026-04-07T03:00:00
estimated: 45m
actual: 20m
owner: claude
blocks: [S1-T12]
blocked_by: [S1-T08, S1-T09]
related_docs: [SPRINT-1, BACKLOG]
commits: [f73d62b]
files_touched:
  - README.md
  - README.es.md
  - docs/issues/WI-101-bug-lectura-negativa.md
  - docs/issues/WI-102-perf-listado-medidores.md
  - docs/issues/WI-103-security-endpoint-admin.md
---

# S1-T11: README bilingüe del demo repo

> **Sprint**: [[SPRINT-1]] · **Día**: 2 · **Status**: pending
> **Owner**: claude · **Estimated**: 45m

## Contexto

`README.md` (inglés) + `README.es.md` (español) con walkthrough completo: cómo clonar, cómo correr tests (rojos), cómo invocar Fixi contra cada work item, criterios de éxito por issue.

Es lo primero que ve Joaris cuando hace clone.

## Acceptance Criteria

- [ ] `README.md` (en) describiendo el sandbox
- [ ] `README.es.md` (es) sincronizado
- [ ] Pasos: clone → restore → build → test (4+ rojos esperados) → invocar Fixi
- [ ] Tabla de los 3 work items con links a `docs/issues/`
- [ ] Sección de "expected output" por issue
- [ ] Disclaimer: "los bugs son intencionales, no los arregles a mano"

## Plan

Estructura similar al README de fixi (concisa, navegable). Los wiki links no aplican aquí (es un repo cliente, no Obsidian Vault).

## Notes & Attempts

**Corrección de ubicación detectada**: el agente `agent-work-items` (S1-T09) puso los work items en `Z:\fixi\docs\issues\` (este repo) cuando deberían estar en `fixi-demo-dotnet/docs/issues/` (el demo repo, donde el usuario los va a clonar y usar). Se movieron los 3 archivos a su ubicación correcta como parte de esta tarea.

**README.md (English) y README.es.md (Spanish) creados en sync**:
- Disclaimer prominent al inicio: "este repo incluye código roto a propósito, no lo arregles a mano"
- Tabla con los 3 work items, archivo donde vive cada bug, y test de aceptación
- Prerequisites: .NET 9 SDK, Claude Code con skill fix-issue
- Quick start: 4 comandos (clone, restore, build, test)
- Output esperado del baseline: `Failed: 5, Passed: 3, Total: 8`
- Cómo invocar Fixi contra cada work item con los 9 pasos del workflow
- Nota de que WI-103 (security) fuerza GUIDED automático
- Estructura del proyecto completa
- Verificación post-Fixi (3 PRs, 8 tests verdes, master limpio)

**Decisión de no usar wiki links**: el demo repo NO es Obsidian Vault — usa links markdown estándar relativos para que rendericen en GitHub.

## Outcome

3 archivos nuevos en `fixi-demo-dotnet/`:
- `README.md` (176 líneas, en)
- `README.es.md` (176 líneas, es)
- `docs/issues/` (3 work items movidos desde fixi)

Commit: `f73d62b`. Pushed a `lotsofcontext/fixi-demo-dotnet master`.

**Sprint 1 Día 2 — completo desde Stream A**.

Próxima desbloqueada: [[S1-T12]] (rehearsal real de Fixi vs WI-101).

## History

- `2026-04-07 00:00` · created (status: pending)
- `2026-04-07 02:45` · started (status: in-progress)
- `2026-04-07 03:00` · completed (status: done) · actual: 20m
