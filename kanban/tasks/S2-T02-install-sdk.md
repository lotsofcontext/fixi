---
id: S2-T02
title: Instalar claude-agent-sdk + verificar import
sprint: S2
day: 1
status: pending
priority: P0
type: implementation
tags: [agent, python, dependencies, day-1]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 15m
actual: ""
owner: claude
blocks: [S2-T03, S2-T06]
blocked_by: [S2-T01]
related_docs: [SPRINT-2]
commits: []
files_touched: []
---

# S2-T02: Instalar claude-agent-sdk

> **Sprint**: [[SPRINT-2]] · **Día**: 1 · **Status**: pending

## Contexto

Instalar el SDK oficial Python de Claude Agent y verificar que se puede importar y que la CLI de Claude Code está disponible (el SDK la wrappea).

## Acceptance Criteria

- [ ] `claude-agent-sdk` agregado a `pyproject.toml` dependencies
- [ ] `python -c "from claude_agent_sdk import query, ClaudeAgentOptions; print('OK')"` funciona
- [ ] `claude --version` devuelve versión válida (Claude Code CLI 2.0.0+)
- [ ] Si Claude Code CLI no está instalado, documentar el comando para instalar (`npm install -g @anthropic-ai/claude-code`)
- [ ] Otras deps: `click` (CLI), `httpx` (web), `pydantic` (parsing), `structlog` (logging)

## Plan

1. Editar pyproject.toml dependencies
2. Crear venv local: `python -m venv venv`
3. `pip install -e .[dev]`
4. Smoke test imports
5. Verificar `claude --version`

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
