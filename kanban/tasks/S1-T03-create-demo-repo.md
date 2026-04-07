---
id: S1-T03
title: Crear repo lotsofcontext/fixi-demo-dotnet en GitHub
sprint: S1
day: 1
status: done
priority: P1
type: implementation
tags: [github, demo-repo, infrastructure, day-1]
created: 2026-04-06T21:50:00
updated: 2026-04-06T22:30:00
estimated: 15m
actual: 40m
owner: claude
blocks: [S1-T04]
blocked_by: []
related_docs: [SPRINT-1, BACKLOG]
commits: []
files_touched: []
---

# S1-T03: Crear repo fixi-demo-dotnet en GitHub

> **Sprint**: [[SPRINT-1]] · **Día**: 1 · **Status**: done
> **Owner**: claude · **Estimated**: 15m · **Actual**: 40m

## Contexto

Necesitamos un repo separado (no subdirectorio de fixi) para que Fixi pueda operar contra él como cliente. Esto matchea el modelo mental: Fixi opera sobre repos de cliente, nunca sobre sí mismo.

## Acceptance Criteria

- [x] Repo `lotsofcontext/fixi-demo-dotnet` creado en GitHub
- [x] Público
- [x] Topics agregados
- [x] Clonado localmente en `Z:\fixi-demo-dotnet`
- [x] Default branch consistente con fixi (`master`, no `main`)

## Notes & Attempts

**Blocker inicial**: `gh` solo tenía login con `0xultravioleta`, sin admin a `lotsofcontext`. No se podía crear repo bajo otra cuenta de usuario (solo el dueño puede).

**Resolución**: usuario ejecutó `gh auth login` con cuenta `lotsofcontext`. Ahora hay dual login y `lotsofcontext` está activo.

**Creación**:
```
gh repo create lotsofcontext/fixi-demo-dotnet --public --description "..." --disable-wiki
```

**Topics**: fixi-demo, dotnet, aspnet-core, demo-repository, intentional-bugs, test-fixtures, energy-sector, sandbox

**Branch rename**: el repo se creó con `main` por default. Renombrado a `master` para consistencia con fixi:
```
git branch -m main master
git push -u origin master
gh repo edit lotsofcontext/fixi-demo-dotnet --default-branch master
```

## Outcome

Repo en https://github.com/lotsofcontext/fixi-demo-dotnet — público, con descripción y 8 topics, default branch `master`.

Clonado en `Z:\fixi-demo-dotnet\`. Listo para [[S1-T04]] (skeleton).

## History

- `2026-04-06 21:50` · created (status: pending)
- `2026-04-06 21:55` · blocked (gh auth missing for lotsofcontext)
- `2026-04-06 22:15` · unblocked (user ran gh auth login)
- `2026-04-06 22:20` · in-progress (creating repo)
- `2026-04-06 22:30` · completed (status: done) · actual: 40m
