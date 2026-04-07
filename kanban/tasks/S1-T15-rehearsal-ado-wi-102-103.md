---
id: S1-T15
title: Rehearsal Fixi contra WI-102 y WI-103 (path Azure DevOps)
sprint: S1
day: 4
status: cancelled
priority: P1
type: research
tags: [rehearsal, demo, azure-devops, transcript, day-4, cancelled-pivot]
created: 2026-04-07T00:00:00
updated: 2026-04-07T04:30:00
estimated: 2h
actual: 0m
owner: claude
blocks: [S1-T17]
blocked_by: [S1-T13, S1-T14]
related_docs: [SPRINT-1, SPRINT-2, BACKLOG, SKILL]
commits: []
files_touched: []
cancelled_reason: "Pivot a Sprint 2: el rehearsal se hara contra el AGENT (Python Claude Agent SDK), no contra el SKILL. Validar el agent es estrategicamente mas valioso que validar el skill."
---

# S1-T15: Rehearsal Fixi contra WI-102 y WI-103 (Azure DevOps)

> **Sprint**: [[SPRINT-1]] · **Día**: 4 · **Status**: pending
> **Owner**: claude · **Estimated**: 2h

## Contexto

Segundo rehearsal real, esta vez por el path Azure DevOps. Cubre PERF (WI-102) y SECURITY (WI-103) — el security forzará GUIDED automático, demostrando los escaladores.

## Pre-requisitos (manuales)

- [ ] ADO sandbox creado (org throwaway)
- [ ] PAT configurado en `az`
- [ ] Mirror de `fixi-demo-dotnet` a Azure Repos del sandbox
- [ ] WI-102 y WI-103 creados como work items reales en ADO

## Acceptance Criteria

- [ ] Rehearsal WI-102 (perf): Fixi corrige N+1, 51 queries → ≤2, perf test pasa
- [ ] Rehearsal WI-103 (security): Fixi clasifica como security, **fuerza GUIDED**, agrega `[Authorize(Roles="Admin")]`, security tests pasan
- [ ] Ambos PRs creados en Azure Repos
- [ ] Transcript en `docs/demos/run-02-ado.md` con: setup ADO, dos runs documentados paso a paso, screenshots de los PRs, decisiones de Fixi

## Plan

Pre-setup (manual con usuario presente), después dos runs consecutivos en GUIDED, capturando todo en markdown.

## Notes & Attempts

**Decisión 2026-04-07**: tarea cancelada como parte del pivot a Sprint 2.

**Contexto del pivot**: el usuario observó (correctamente) que entregar "un skill de Claude Code" no cumple el requerimiento original de Jefferson Acevedo de GlobalMVM, que pidió textualmente un **"agente de automatización"**. Un skill requiere un humano dentro de una sesión de Claude Code para ejecutarse — no es deployable, no es triggerable desde CI/CD, no procesa tickets autonomamente.

**Decisión arquitectural**: construir un **agent real** sobre el Claude Agent SDK (Python oficial de Anthropic) que:
1. Reusa `SKILL.md` íntegro como `system_prompt`
2. Reusa `classification.md` y `guardrails.md` (estos últimos como `PreToolUse` hooks)
3. Se invoca via CLI (`fixi resolve --work-item <url>`) desde GitHub Actions o Azure DevOps Pipelines
4. Clona el target repo, lo analiza, lo corrige, abre PR
5. Es deployable como container (el Terraform de Sprint 1 ya cubre la infra)

**Por qué se cancela este rehearsal específicamente**: validar el skill por el path Azure DevOps tiene sentido limitado si la entrega final no es el skill sino el agent. Es mejor hacer **un solo rehearsal** del agent contra los work items que valida la entrega real (el agent), en vez de dos rehearsals (uno del skill, uno del agent).

**Reemplazada por**: [[S2-T17]] (rehearsal end-to-end del agent CLI contra fixi-demo-dotnet/WI-101) y [[S2-T18]] (rehearsal del agent contra WI-102 + WI-103 por path GitHub o Azure DevOps).

## Outcome

Cancelada. Trabajo migrado a Sprint 2. Ver [[SPRINT-2]] para el plan completo del agent.

## History

- `2026-04-07 00:00` · created (status: pending)
- `2026-04-07 04:30` · cancelled (pivot a Sprint 2 — agent reemplaza skill como entregable principal)
