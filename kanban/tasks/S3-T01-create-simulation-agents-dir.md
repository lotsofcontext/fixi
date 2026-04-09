---
id: S3-T01
title: Crear .claude/agents/ dir para agentes de simulacion GlobalMVM
sprint: S3
day: 1
status: done
priority: P0
type: scaffolding
tags: [sprint-3, agents, simulation, globalmvm, day-1]
created: 2026-04-08T00:00:00
updated: 2026-04-08T00:00:00
estimated: 5m
actual: 2m
owner: claude
blocks: [S3-T02, S3-T03, S3-T04, S3-T05, S3-T06, S3-T07, S3-T08, S3-T09]
blocked_by: []
related_docs: [HANDOFF-FIXI-SPRINT3-SIMULATION-AGENTS]
commits: []
files_touched:
  - .claude/agents/
---

# S3-T01: Crear .claude/agents/ dir para agentes de simulacion

> **Sprint**: S3 · **Dia**: 1 · **Status**: done

## Contexto

Sprint 3 introduce un equipo de 8 agentes subagent de Claude Code que simulan al equipo tecnico de GlobalMVM (reunion 2026-04-06). Se usan como pre-pitch dry-runs, validacion de deliverables, generacion de FAQ defensivo, y roleplay de objeciones. Requieren `.claude/agents/` como home estandar de subagents de Claude Code.

## Acceptance Criteria

- [x] `Z:\fixi\.claude\agents\` creado (el harness resolvera los agentes desde ahi)
- [x] Unblocks S3-T02..S3-T09 (cada uno escribe un agente)

## Outcome

Directorio creado por efecto de Write tool al escribir el primer agente. Los 8 task files que siguen llenan el contenido.

## History

- `2026-04-08 00:00` · created + done (scaffolding triv)
