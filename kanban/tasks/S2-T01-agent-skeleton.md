---
id: S2-T01
title: Crear fixi/agent/ skeleton (pyproject.toml, src, tests, README)
sprint: S2
day: 1
status: done
priority: P0
type: implementation
tags: [agent, python, scaffolding, day-1]
created: 2026-04-07T04:30:00
updated: 2026-04-07T05:15:00
estimated: 30m
actual: 15m
owner: claude
blocks: [S2-T02, S2-T03, S2-T04, S2-T05, S2-T06]
blocked_by: []
related_docs: [SPRINT-2, SKILL]
commits: []
files_touched:
  - agent/pyproject.toml
  - agent/README.md
  - agent/.gitignore
  - agent/src/fixi_agent/__init__.py
  - agent/src/fixi_agent/py.typed
  - agent/tests/__init__.py
  - agent/tests/unit/__init__.py
  - agent/tests/integration/__init__.py
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

**Layout escogido**: src layout (`src/fixi_agent/`) — moderno, evita ambigüedades de imports en tests, recomendado por PyPA.

**`pyproject.toml`** con secciones:
- `[build-system]`: setuptools
- `[project]`: metadata + dependencies (claude-agent-sdk, click, pydantic, httpx, structlog)
- `[project.optional-dependencies]` dev: pytest, pytest-asyncio, ruff, mypy
- `[project.scripts]`: `fixi = "fixi_agent.cli:main"` (entry point CLI registrado)
- `[tool.pytest.ini_options]`: asyncio_mode = "auto", strict markers
- `[tool.ruff]`: line-length 100, target py311, select E/W/F/I/B/UP/N
- `[tool.mypy]`: strict mode

**`__init__.py`** con docstring y `__version__ = "0.1.0"`.

**`py.typed`** marker para que mypy/IDE detecten que el package tiene type hints.

**`.gitignore`** con todo lo standard de Python + artifacts específicos de Fixi (`fixi-audit-*.jsonl`, `.fixi-runs/`).

**`README.md`** placeholder con: use case, status (Sprint 2 in progress), local dev quickstart, link a SPRINT-2.md.

**Decisión sobre Python version**: requires-python = ">=3.11" para tener match-statements y mejor type system. La SDK seguramente requiere similar.

## Outcome

8 archivos creados en `Z:/fixi/agent/`. Estructura lista para que las siguientes tareas (S2-T02..S2-T06) implementen los componentes core.

Verificación pendiente del install: necesita venv + `pip install -e .[dev]` que se hace en [[S2-T02]].

## History

- `2026-04-07 04:30` · created (status: pending)
- `2026-04-07 05:00` · started (status: in-progress)
- `2026-04-07 05:15` · completed (status: done) · actual: 15m
