---
id: S1-T02
title: Audit wiki links — formato dual para client-facing vs internos
sprint: S1
day: 1
status: done
priority: P0
type: docs
tags: [docs, obsidian, wiki-links, day-1]
created: 2026-04-06T21:35:00
updated: 2026-04-06T21:50:00
estimated: 30m
actual: 25m
owner: claude
blocks: []
blocked_by: [S1-T01]
related_docs: [SPRINT-1, BACKLOG]
commits: [be4638f]
files_touched: [docs/diagrams.md]
---

# S1-T02: Audit wiki links — formato dual

> **Sprint**: [[SPRINT-1]] · **Día**: 1 · **Status**: done
> **Owner**: claude · **Estimated**: 30m · **Actual**: 25m

## Contexto

El agente backlog-prioritizer detectó que los `[[wiki links]]` de Obsidian no renderizan en GitHub. Necesitamos formato dual:

- **Docs internos** (PLAN, SPEC, BACKLOG, SPRINT-1, kanban) → mantener `[[wiki]]` para Obsidian Vault
- **Docs client-facing** (README, README.es, CLIENT-FACING, diagrams) → links estándar `[texto](ruta.md)` para GitHub

## Acceptance Criteria

- [x] Identificar todos los archivos con `[[wiki]]`
- [x] Convertir wiki links en client-facing docs
- [x] Mantener wiki links en docs internos
- [x] Verificar que no quedan wikis en client-facing

## Notes & Attempts

`grep` identificó 5 archivos con wikis:
- `docs/PLAN.md` — interno, mantener
- `docs/SPEC.md` — interno, mantener
- `docs/planning/BACKLOG.md` — interno, mantener
- `docs/planning/SPRINT-1.md` — interno, mantener
- `docs/diagrams.md` — **client-facing, convertir**

`CLIENT-FACING.md` ya estaba limpio (sin wikis).

Conversión en `diagrams.md`: 6 wiki links convertidos a links relativos:
- `[[SKILL]]` → `[skill/SKILL.md](../skill/SKILL.md)`
- `[[classification|...]]` → `[...](../skill/references/classification.md)`
- etc.

Verificación final con `grep "\[\["` en `docs/diagrams.md` → 0 matches.

## Outcome

`docs/diagrams.md` ahora renderiza correctamente en GitHub mientras los docs internos siguen siendo navegables en Obsidian.

Commit: `be4638f` — "docs: convert wiki links to markdown in diagrams.md"

## History

- `2026-04-06 21:35` · created (status: pending)
- `2026-04-06 21:36` · started (status: in-progress)
- `2026-04-06 21:50` · completed (status: done) · actual: 25m
