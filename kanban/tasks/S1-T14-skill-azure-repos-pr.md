---
id: S1-T14
title: Agregar Azure Repos PR creation al SKILL.md
sprint: S1
day: 3
status: pending
priority: P1
type: implementation
tags: [skill, azure-devops, azure-repos, day-3]
created: 2026-04-07T00:00:00
updated: 2026-04-07T00:00:00
estimated: 45m
actual: ""
owner: claude
blocks: [S1-T15]
blocked_by: [S1-T13]
related_docs: [SPRINT-1, BACKLOG, SKILL, PLAN]
commits: []
files_touched: []
---

# S1-T14: Azure Repos PR creation en SKILL.md

> **Sprint**: [[SPRINT-1]] · **Día**: 3 · **Status**: pending
> **Owner**: claude · **Estimated**: 45m

## Contexto

Complemento de [[S1-T13]]. Después de parsear un work item ADO, Fixi necesita crear el PR en Azure Repos (no GitHub). Tarea PLAN 6.1.

## Acceptance Criteria

- [ ] Auto-detección del remote: si `git remote get-url origin` matchea `dev.azure.com` → usar `az repos pr create`
- [ ] Sección en Paso 8 de SKILL.md con comando `az repos pr create`
- [ ] Sintaxis: `az repos pr create --source-branch {branch} --target-branch {default} --title "..." --description "..."`
- [ ] PR template idéntico al de GitHub (issue link, classification, root cause, changes, testing checklist)
- [ ] Fallback a `gh pr create` si no es ADO

## Plan

Edit `skill/SKILL.md` Paso 8 (Crear PR), agregar lógica de detección y comando alternativo.

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 00:00` · created (status: pending)
