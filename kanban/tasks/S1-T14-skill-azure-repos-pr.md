---
id: S1-T14
title: Agregar Azure Repos PR creation al SKILL.md
sprint: S1
day: 3
status: done
priority: P1
type: implementation
tags: [skill, azure-devops, azure-repos, day-3]
created: 2026-04-07T00:00:00
updated: 2026-04-07T02:30:00
estimated: 45m
actual: 25m
owner: agent-skill-ado
blocks: [S1-T15]
blocked_by: [S1-T13]
related_docs: [SPRINT-1, BACKLOG, SKILL, PLAN]
commits: [fae1f18]
files_touched:
  - skill/SKILL.md
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

**Bundled con [[S1-T13]]** y delegado al mismo agente (`agent-skill-ado`) porque editan el mismo archivo (`skill/SKILL.md`). El commit `fae1f18` cubre ambos.

**Output del agente — sección Paso 8 ADO** (líneas 338-513):
- Auto-detección de remote: `git remote get-url origin` matcheado contra `dev\.azure\.com|visualstudio\.com`
- Branch GitHub se mantiene como default (`gh pr create`)
- Branch ADO nuevo: `az repos pr create --source-branch ... --target-branch ... --title ... --description "@/tmp/pr-body.md"`
- Extracción de `webUrl` y `pullRequestId` del JSON de respuesta usando `jq`
- Linkeo PR ↔ Work Item con `az repos pr work-item add` SOLO cuando `source_type == azure-devops`
- También actualizó la sección de normalización en Paso 1 y el campo "Fuente" del PR template para incluir `azure-devops`

**Decisiones de diseño flagged por el agente**:
1. **Body template duplicado** — aparece 3 veces (template ref + GitHub heredoc + ADO heredoc). El agente lo dejó así por fidelidad al estilo existente (heredocs bash con `'EOF'` quoting). Refactor disponible si lo queremos.
2. **`/tmp/pr-body.md`** — usó path POSIX. En Windows git-bash funciona, en pure PowerShell habría que usar `$TEMP`. Aceptable para el demo.
3. **System.Description HTML** — flagged como "strip o avisar" (no prescribió tool específica).
4. **No tocó Paso 9 (tracking)** — `azure-devops` fluye via `source_type` template variable, no hay enum hardcoded que actualizar.

## Outcome

Mismo commit que [[S1-T13]]: `fae1f18`. SKILL.md de 518 → 656 líneas (+144).

Próxima tarea desbloqueada: [[S1-T15]] (rehearsal ADO con WI-102 y WI-103).

## History

- `2026-04-07 00:00` · created (status: pending)
- `2026-04-07 01:00` · started (in-progress, bundled with T13 in agent-skill-ado)
- `2026-04-07 02:30` · completed (status: done) · actual: 25m
