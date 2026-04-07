---
id: S1-T13
title: Agregar parser Azure DevOps Work Items al SKILL.md
sprint: S1
day: 3
status: done
priority: P1
type: implementation
tags: [skill, azure-devops, parser, day-3]
created: 2026-04-07T00:00:00
updated: 2026-04-07T02:30:00
estimated: 45m
actual: 25m
owner: agent-skill-ado
blocks: [S1-T15]
blocked_by: [S1-T12]
related_docs: [SPRINT-1, BACKLOG, SKILL, PLAN]
commits: [fae1f18]
files_touched:
  - skill/SKILL.md
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

**Delegado a `agent-skill-ado`** (subagent paralelo). El mismo agente hace [[S1-T13]] y [[S1-T14]] en un solo commit porque editan el mismo archivo.

**Output del agente — sección Paso 1 ADO** (líneas 72-88):
- Pattern: `dev\.azure\.com/[^/]+/[^/]+/_workitems/edit/\d+` + shorthand `ADO-N`, `WI-N`, `AB#N`
- Comando primario: `az boards work-item show --id {id} --output json --organization https://dev.azure.com/{org}`
- Field mapping completo (System.Title, System.Description (HTML, hay que strip), System.Tags (semicolon split), Microsoft.VSTS.Common.Priority, System.WorkItemType para hint de clasificación)
- Fallback 1: WebFetch
- Fallback 2: input manual
- `source_type` = "azure-devops"

**Decisión de diseño flag**: el agente notó que `System.Description` viene como HTML. Documentado como "strip tags o avisar al usuario" sin prescribir una herramienta específica (consistente con cómo se trata el HTML en WebFetch del resto del skill).

## Outcome

`skill/SKILL.md` modificado. Sección ADO insertada entre Linear y Jira como pedido. Tareas T13 y T14 completadas en el mismo commit `fae1f18`.

## History

- `2026-04-07 00:00` · created (status: pending)
- `2026-04-07 01:00` · started (in-progress, delegated to agent-skill-ado)
- `2026-04-07 02:30` · completed (status: done) · actual: 25m
