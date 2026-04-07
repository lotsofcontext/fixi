---
id: S1-T09
title: Pre-crear 3 work items markdown en docs/issues/
sprint: S1
day: 2
status: done
priority: P1
type: docs
tags: [demo-repo, work-items, day-2]
created: 2026-04-07T00:00:00
updated: 2026-04-07T02:30:00
estimated: 1h
actual: 25m
owner: agent-work-items
blocks: [S1-T12]
blocked_by: [S1-T08]
related_docs: [SPRINT-1, BACKLOG]
commits: [af200ac]
files_touched:
  - docs/issues/WI-101-bug-lectura-negativa.md
  - docs/issues/WI-102-perf-listado-medidores.md
  - docs/issues/WI-103-security-endpoint-admin.md
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

**Delegado a `agent-work-items`** (subagent paralelo, isolation: worktree).

Output del agente:
- 3 archivos creados (85, 93, 95 líneas respectivamente, 273 total)
- Formato: ADO work item export-style con tabla de header (Work Item ID, Type, State, Priority, Severity, Area Path, Iteration Path, Reported by, etc.)
- Bilingüe: español prosa + inglés términos técnicos
- Contexto colombiano realista (ISAGEN, XM, EPM como clientes)
- Reporters: Camilo Restrepo, Joaris Angulo, Jefferson Acevedo (matchea personas reales mencionadas en el handoff)
- Cero secrets hardcoded (placeholder `<JWT_SECRET>` donde aplica)
- Cada uno con acceptance criteria específico que Fixi puede usar como definition of done

**Verificación manual**:
- WI-101 abre con stack trace de `DivideByZeroException` en `CalculadoraConsumo.Calcular`
- WI-102 incluye métricas QA (queries por request) y target específico (≤2 queries)
- WI-103 menciona explícitamente OWASP A01:2021 + CVSS 9.1 + curl evidence

## Outcome

3 archivos en `docs/issues/`. Commit: `af200ac`.

Próximas tareas que se desbloquean: [[S1-T11]] (README demo puede referenciarlos), [[S1-T12]] (rehearsal contra WI-101).

## History

- `2026-04-07 00:00` · created (status: pending)
- `2026-04-07 01:00` · started (in-progress, delegated to agent-work-items)
- `2026-04-07 02:30` · completed (status: done) · actual: 25m
