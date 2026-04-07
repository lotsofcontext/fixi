---
id: S1-T10
title: CLAUDE.md del demo repo (convenciones .NET)
sprint: S1
day: 2
status: done
priority: P1
type: docs
tags: [demo-repo, claude-md, conventions, day-2]
created: 2026-04-06T22:50:00
updated: 2026-04-06T22:55:00
estimated: 30m
actual: 15m
owner: claude
blocks: []
blocked_by: [S1-T04]
related_docs: [SPRINT-1, BACKLOG]
commits: [5a900b9]
files_touched: [CLAUDE.md]
---

# S1-T10: CLAUDE.md del demo repo

> **Sprint**: [[SPRINT-1]] · **Día**: 2 (creado en Día 1) · **Status**: done
> **Owner**: claude · **Estimated**: 30m · **Actual**: 15m

## Contexto

Doble propósito: (a) Fixi lo lee en Paso 0 (Safety Gate + convenciones), (b) es template de cómo deberían lucir los CLAUDE.md de GlobalMVM en sus repos.

## Acceptance Criteria

- [x] Project context describiendo el sandbox
- [x] Architecture (3 projects + tests)
- [x] Stack (.NET 9, EF Core, SQLite, JWT, xUnit)
- [x] Conventions: language style, test commands, branch naming, commit format
- [x] **Notice explícito sobre los 3 bugs sembrados** (prevenir que se "arreglen" sin Fixi)
- [x] Cómo correr Fixi contra el repo
- [x] Rules para Claude Code

## Notes & Attempts

Adelantado en Día 1 como parte del scaffolding ([[S1-T04]]). Está committed en `5a900b9`.

## Outcome

`Z:\fixi-demo-dotnet\CLAUDE.md` creado y pusheado. Fixi puede leerlo en el Safety Gate.

## History

- `2026-04-06 22:50` · created (status: pending)
- `2026-04-06 22:50` · started (status: in-progress)
- `2026-04-06 22:55` · completed (status: done) · actual: 15m
