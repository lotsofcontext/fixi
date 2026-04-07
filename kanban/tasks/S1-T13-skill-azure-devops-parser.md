---
id: S1-T13
title: Agregar parser Azure DevOps Work Items al SKILL.md
sprint: S1
day: 3
status: in-progress
priority: P1
type: implementation
tags: [skill, azure-devops, parser, day-3]
created: 2026-04-07T00:00:00
updated: 2026-04-07T01:00:00
estimated: 45m
actual: ""
owner: agent-skill-ado
blocks: [S1-T15]
blocked_by: [S1-T12]
related_docs: [SPRINT-1, BACKLOG, SKILL, PLAN]
commits: []
files_touched: []
---

# S1-T13: Parser Azure DevOps Work Items en SKILL.md

> **Sprint**: [[SPRINT-1]] · **Día**: 3 · **Status**: pending
> **Owner**: claude · **Estimated**: 45m

## Contexto

[[SKILL]] actualmente maneja GitHub, Linear, Jira y texto libre, pero no Azure DevOps. GlobalMVM es 99% Azure → es THE diferenciador. Tarea PLAN 2.4.

## Acceptance Criteria

- [ ] Pattern regex para URLs ADO: `dev\.azure\.com/{org}/{project}/_workitems/edit/\d+`
- [ ] Sección en Paso 1 de SKILL.md con comando `az boards work-item show --id {n} --output json`
- [ ] Mapeo de campos ADO a estructura normalizada (System.Title → title, System.Description → body, System.Tags → labels, etc.)
- [ ] Fallback a WebFetch si `az` no auth
- [ ] Fallback a input manual si todo falla
- [ ] Pattern también soporta shorthand `ADO-{id}` o `WI-{id}`

## Plan

Edit `skill/SKILL.md` Paso 1, agregar nueva sección "### Azure DevOps Work Item" entre las existentes.

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 00:00` · created (status: pending)
