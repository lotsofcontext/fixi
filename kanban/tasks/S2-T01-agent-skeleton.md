---
id: S2-T01
title: Crear fixi/agent/ skeleton (pyproject.toml, src, tests, README)
sprint: S2
day: 1
status: pending
priority: P0
type: implementation
tags: [agent, python, scaffolding, day-1]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 30m
actual: ""
owner: claude
blocks: [S2-T02, S2-T03, S2-T04, S2-T05, S2-T06]
blocked_by: []
related_docs: [SPRINT-2, SKILL]
commits: []
files_touched: []
---

# S2-T01: Skeleton del agent project

> **Sprint**: [[SPRINT-2]] · **Día**: 1 · **Status**: pending

## Contexto

Bootstrap del proyecto Python que va a hostear el agent. Estructura siguiendo convenciones modernas de packaging Python (pyproject.toml + src layout).

## Acceptance Criteria

- [ ] `fixi/agent/` directory creado
- [ ] `pyproject.toml` con metadata, dependencies, build-system, entry point CLI
- [ ] `src/fixi_agent/__init__.py` con `__version__`
- [ ] `tests/__init__.py` (para que pytest los descubra)
- [ ] `README.md` placeholder con cómo va a funcionar
- [ ] `.python-version` o `python_requires=">=3.11"` en pyproject
- [ ] `.gitignore` para Python (venvs, __pycache__, .pytest_cache, etc.)

## Plan

1. `mkdir Z:/fixi/agent/{src/fixi_agent,tests/{unit,integration}}`
2. Crear pyproject.toml con `[project]`, `[project.scripts] fixi = "fixi_agent.cli:main"`, `[tool.pytest.ini_options]`
3. Crear `__init__.py` files
4. README placeholder

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
