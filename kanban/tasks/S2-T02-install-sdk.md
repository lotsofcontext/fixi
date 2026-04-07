---
id: S2-T02
title: Instalar claude-agent-sdk + verificar import
sprint: S2
day: 1
status: done
priority: P0
type: implementation
tags: [agent, python, dependencies, day-1]
created: 2026-04-07T04:30:00
updated: 2026-04-07T05:50:00
estimated: 15m
actual: 20m
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

**Pre-checks**: Python 3.11.4 ✅, Claude Code CLI 2.1.91 ✅. Ambos cumplen los requisitos del SDK.

**Setup del venv**:
```bash
cd Z:/fixi/agent
python -m venv venv
venv/Scripts/python.exe -m pip install --upgrade pip  # 23.1.2 → 26.0.1
venv/Scripts/pip.exe install -e ".[dev]"
```

**Versiones instaladas**:
- `claude-agent-sdk` **0.1.56** (la versión más reciente al 2026-04-07)
- `mcp` 1.27.0 (transitiva del SDK)
- `click` 8.3.2, `pydantic` 2.12.5, `httpx` 0.28.1, `structlog` 25.5.0
- `pytest` 9.0.2, `pytest-asyncio` 1.3.0, `pytest-cov` 7.1.0, `pytest-mock` 3.15.1
- `ruff` 0.15.9, `mypy` 1.20.0
- `fixi-agent` 0.1.0 (editable install desde local)

Total: ~50 paquetes (incluyendo dependencias transitivas).

**Smoke tests ejecutados**:
1. `from claude_agent_sdk import query, ClaudeAgentOptions, ClaudeSDKClient, HookMatcher` → OK
2. `import fixi_agent; print(fixi_agent.__version__)` → `0.1.0` OK

**Inspección de la API surface del SDK** (relevante para los siguientes tasks):

`ClaudeAgentOptions` tiene exactamente los campos que necesitamos según el plan:
- `system_prompt`: str | preset | file → carga de SKILL.md (S2-T03)
- `allowed_tools`: list[str] → tools permitidos
- `permission_mode`: `default` | `acceptEdits` | `plan` | `bypassPermissions` | `dontAsk`
- `cwd`: str | Path → working directory del agent
- `hooks`: dict de eventos (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`, `Notification`, etc.) → para los 13 guardrails (S2-T08)
- `can_use_tool`: callback alternativo a hooks (más granular)
- `max_turns`, `max_budget_usd` → límites
- `agents`: dict de subagents (futuro Sprint 3)
- `mcp_servers`: para custom MCP tools

Funciones top-level del SDK exportadas: `query`, `ClaudeSDKClient`, `HookMatcher`, `HookContext`, `AgentDefinition`, `AssistantMessage`, `Message`, `ContentBlock`, `PermissionMode`, etc. — todo lo que necesitamos.

**Decisión**: para Fixi vamos a usar `ClaudeSDKClient` (bidireccional) en vez de `query()` (one-shot) porque queremos poder hacer preguntas de clarificación al usuario en GUIDED mode. Para FULL_AUTO podemos usar `query()`.

**No problemas encontrados**: el install fue limpio, no hubo conflictos de versiones, todas las deps optional `[dev]` se instalaron sin errores.

## Outcome

`fixi-agent` instalado en venv local con todas las deps. SDK importable. Listo para empezar a implementar componentes core (S2-T03..S2-T06).

Notar: `agent/venv/` está en `.gitignore` así que NO se commitea — los siguientes desarrolladores deben correr `python -m venv venv && venv/Scripts/pip install -e ".[dev]"` para reproducir.

## History

- `2026-04-07 04:30` · created (status: pending)
- `2026-04-07 05:30` · started (status: in-progress)
- `2026-04-07 05:50` · completed (status: done) · actual: 20m
