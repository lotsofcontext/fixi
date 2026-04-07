# Sprint 2 — Fixi Agent (Python + Claude Agent SDK)

> **Pivot estratégico**: el deliverable final NO es un skill de Claude Code, es un **agent real** built on Claude Agent SDK (Python oficial), invocable desde CI/CD pipelines.
>
> **Objetivo**: CLI Python `fixi` instalable que toma un work item URL, clona el target repo, analiza, fixea, abre PR — todo autónomo y disparable desde GitHub Actions o Azure DevOps Pipelines.
>
> Ver también: [[SPRINT-1]] (cerrado al 94%, T15 cancelado), [[PLAN]], [[SKILL]] (ahora es system_prompt del agent), [[BACKLOG]]

---

## Definition of Done

El sprint está completo cuando:

1. `pip install fixi-agent` instala la CLI desde el repo local
2. `fixi resolve --work-item <url> --repo <url>` ejecuta el flujo end-to-end:
   - Clona el target repo en tmpdir
   - Parse el work item (GH Issue, ADO Work Item, Linear, Jira, free text)
   - Levanta `ClaudeSDKClient` con `SKILL.md` como system_prompt
   - Aplica los 13 guardrails como `PreToolUse` hooks
   - Resuelve el issue (branch + fix + tests + commit + push + PR)
   - Reporta resultado en JSON o human-readable
   - Limpia el tmpdir
3. **Workflow ejemplo de GitHub Actions** corre la CLI exitosamente contra `fixi-demo-dotnet/WI-101` y abre un PR real
4. **Workflow ejemplo de Azure Pipelines** documentado (no necesariamente ejecutable sin sandbox)
5. **Dockerfile** que empaca Python + Node + Claude Code CLI + fixi-agent en una imagen
6. **Tests unitarios** del parser de work items, hooks de guardrails, y orchestrator
7. **Test de integración** que ejecuta el agent contra `fixi-demo-dotnet` en CI
8. `docs/demos/run-03-agent-cli.md` con transcript del rehearsal real
9. **CLIENT-FACING.md actualizado** con la narrativa "agent" en lugar de "skill"
10. **PLAN.md actualizado** con el agent como pieza central de Phase 6

---

## Arquitectura del agent

```
┌──────────────────────────────────────────────────────────┐
│  Trigger:                                                 │
│   - GitHub Actions step                                   │
│   - Azure DevOps Pipeline step                            │
│   - Manual CLI invocation                                 │
│   - Cron job                                              │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  fixi resolve --work-item <url> [--repo <url>]            │
│  (Python CLI, click-based)                                │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  1. Parse work item URL → detect source                   │
│  2. Fetch content (gh / az / WebFetch / file)             │
│  3. Detect target repo (from work item or --repo)         │
│  4. Clone to /tmp/fixi-{run_id} (auth via env vars)       │
│  5. Initialize ClaudeSDKClient with:                      │
│     - system_prompt = SKILL.md content                    │
│     - allowed_tools = [Read, Write, Edit, Bash, Grep,     │
│                        Glob, WebFetch]                    │
│     - permission_mode = acceptEdits                       │
│     - hooks = 13 guardrails as PreToolUse                 │
│  6. await query() with work item as initial prompt        │
│  7. Stream messages to stdout (or capture to JSON)        │
│  8. Capture PR URL, branch, commits from agent output     │
│  9. Cleanup tmpdir                                        │
│  10. Exit code: 0 = success, non-zero = failure           │
└──────────────────────────────────────────────────────────┘
```

### Layout del proyecto

```
fixi/
└── agent/
    ├── README.md                ← cómo instalar y usar
    ├── pyproject.toml           ← package config + dependencies
    ├── Dockerfile               ← multi-stage: node + claude code + python + fixi
    ├── docker-compose.yml       ← dev local
    ├── .github/
    │   └── workflows/
    │       └── example-fixi-resolve.yml  ← workflow GH Actions de ejemplo
    ├── azure-pipelines/
    │   └── example-fixi-resolve.yml      ← pipeline ADO de ejemplo
    ├── src/
    │   └── fixi_agent/
    │       ├── __init__.py
    │       ├── cli.py           ← entry point (click)
    │       ├── parser.py        ← work item URL parser
    │       ├── cloner.py        ← git clone con auth
    │       ├── orchestrator.py  ← ClaudeSDKClient wrapper
    │       ├── hooks.py         ← 13 guardrails como PreToolUse hooks
    │       ├── prompts.py       ← system_prompt loader (SKILL.md)
    │       └── output.py        ← JSON / human formatters
    └── tests/
        ├── unit/
        │   ├── test_parser.py
        │   ├── test_hooks.py
        │   └── test_prompts.py
        └── integration/
            └── test_agent_e2e.py  ← contra fixi-demo-dotnet
```

---

## Tareas (S2-T01..S2-T20)

### Día 1 — Bootstrap y core (S2-T01..S2-T07)

| # | Tarea | Estimado | Bloqueado por |
|---|-------|----------|---------------|
| S2-T01 | Crear `fixi/agent/` skeleton (pyproject.toml, src/, tests/, README) | 30m | — |
| S2-T02 | Instalar `claude-agent-sdk` + deps, verificar import | 15m | S2-T01 |
| S2-T03 | Implementar `prompts.py` (loader de SKILL.md como system_prompt) | 30m | S2-T01 |
| S2-T04 | Implementar `parser.py` (work item URL → estructura normalizada) | 1h | S2-T01 |
| S2-T05 | Implementar `cloner.py` (git clone a tmpdir con auth) | 45m | S2-T01 |
| S2-T06 | Implementar `orchestrator.py` (ClaudeSDKClient básico, sin hooks aún) | 1h | S2-T03, S2-T05 |
| S2-T07 | Smoke test: orchestrator resuelve WI-101 contra demo repo (sin hooks) | 30m | S2-T06 |

**Punto de control Día 1**: el agent (sin hooks) puede resolver WI-101 end-to-end al menos una vez.

### Día 2 — Guardrails y CLI (S2-T08..S2-T13)

| # | Tarea | Estimado | Bloqueado por |
|---|-------|----------|---------------|
| S2-T08 | Implementar `hooks.py` con los 13 guardrails como PreToolUse hooks | 2h | S2-T06 |
| S2-T09 | Implementar audit log (PostToolUse hook → JSONL file) | 30m | S2-T08 |
| S2-T10 | Implementar `cli.py` (click) — `fixi resolve --work-item ...` | 45m | S2-T06 |
| S2-T11 | Implementar `output.py` (JSON + human formatters) | 30m | S2-T10 |
| S2-T12 | Wire CLI → orchestrator → output, end-to-end | 30m | S2-T08, S2-T11 |
| S2-T13 | Tests unitarios: parser, hooks, prompts | 1h30m | S2-T08 |

**Punto de control Día 2**: `fixi resolve --work-item <url>` desde la CLI funciona, con guardrails activos.

### Día 3 — Containerización y CI/CD examples (S2-T14..S2-T17)

| # | Tarea | Estimado | Bloqueado por |
|---|-------|----------|---------------|
| S2-T14 | Dockerfile multi-stage (node + Claude Code CLI + python + fixi-agent) | 1h30m | S2-T12 |
| S2-T15 | docker-compose.yml para dev local + ejemplo de invocación | 30m | S2-T14 |
| S2-T16 | GitHub Actions workflow de ejemplo (`example-fixi-resolve.yml`) | 45m | S2-T14 |
| S2-T17 | Azure Pipelines workflow de ejemplo (`example-fixi-resolve.yml`) | 45m | S2-T14 |

**Punto de control Día 3**: la CLI corre dentro de Docker. El workflow de GH Actions está listo para ejecutar.

### Día 4 — Rehearsal real y documentación (S2-T18..S2-T20)

| # | Tarea | Estimado | Bloqueado por |
|---|-------|----------|---------------|
| S2-T18 | **Rehearsal end-to-end**: ejecutar el agent CLI contra WI-101 + WI-102 + WI-103 en `fixi-demo-dotnet`, capturar transcripts en `docs/demos/run-03-agent-cli.md` | 2h | S2-T16 |
| S2-T19 | Update CLIENT-FACING.md: skill → agent narrativa, links a transcripts del agent | 1h | S2-T18 |
| S2-T20 | Update PLAN.md: el agent es el deliverable principal de Phase 6, no MCP/A2A | 30m | S2-T19 |

**Punto de control Día 4 (SHIP)**: el agent está validado end-to-end, documentado, y listo para que GlobalMVM lo clone, instale, y ejecute en sus pipelines.

---

## Decisiones técnicas

| Decisión | Valor | Razón |
|----------|-------|-------|
| Lenguaje | **Python** | SDK oficial Anthropic, mayor madurez (1220 snippets), matchea convenciones consultoria-x |
| Paquete | `fixi-agent` (PyPI-style) | Distribuible via `pip install` cuando se publique |
| CLI command | `fixi` | Corto, memorable |
| CLI framework | `click` | Standard, robust, buenos defaults para CI/CD |
| Async runtime | `asyncio` | El SDK es async-first |
| Logging | `structlog` o stdlib `logging` con JSON formatter | Parseable por CI/CD systems |
| Testing | `pytest` + `pytest-asyncio` | Standard Python |
| Container base | `python:3.12-slim-bookworm` + Node 22 + Claude Code CLI | Multi-stage para minimizar tamaño |
| Auth git | env vars `GH_TOKEN` (GitHub) y `AZURE_DEVOPS_PAT` (ADO) | Standard para CI/CD |
| Auth Anthropic | `ANTHROPIC_API_KEY` env var | Standard SDK pattern |
| Output format | `--output json` o `--output human` (default human) | JSON para CI/CD, human para terminal |
| Permission mode | `acceptEdits` autonomo, `default` cuando un guardrail dispara | Balanceo seguridad/autonomía |

---

## Lo que se preserva del Sprint 1 (sin cambios)

- `skill/SKILL.md` — se vuelve el `system_prompt` del agent (cargado en runtime)
- `skill/references/classification.md` — referenciado por el system prompt
- `skill/references/guardrails.md` — los 13 se traducen a hooks Python en `agent/src/fixi_agent/hooks.py`
- `terraform/` — sin cambios, sigue siendo el target de deployment del agent containerizado
- `fixi-demo-dotnet/` — sin cambios, sigue siendo el sandbox de validación
- `docs/diagrams.md` — actualizar solo el flujo principal para reemplazar "humano invoca skill" con "trigger invoca agent CLI"
- `docs/PLAN.md` — actualizar Phase 6 para reflejar el agent como entregable central
- `docs/CLIENT-FACING.md` — actualizar narrativa de skill a agent en Sprint 2 día 4
- Kanban completo y `update_board.py` — sin cambios

---

## Riesgos del Sprint

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| Claude Agent SDK requiere Claude Code CLI instalado en el container | Confirmado | Multi-stage Dockerfile que instale Node + Claude Code CLI primero |
| Auth de Anthropic API key vs OAuth de Claude Code | Media | Documentar ambas opciones, usar API key como default para CI/CD |
| Hooks no disparan correctamente para nuestros casos edge | Alta | Tests unitarios exhaustivos de hooks antes de wire a orchestrator |
| El agent falla en repos grandes por context window | Media | Implementar pre-filter del codebase (grep heurístico) antes de pasar a Claude |
| GH Actions sin acceso al ANTHROPIC_API_KEY rompe el demo | Baja | Documentar setup de secrets en el workflow ejemplo |
| Latencia del agent end-to-end > 5min en repos reales | Media | Medir y documentar; si excede, usar `--max-turns` para acotar |
| Conflicto entre `acceptEdits` permission mode y guardrails | Media | Hooks denegan operaciones específicas, dejan que el resto fluya |

---

## Post-sprint (Sprint 3 candidates)

Items potenciales para después del agent core:

- HTTP server (FastAPI) wrapping del CLI — `POST /resolve` con webhook callbacks
- Webhook receivers para ADO y GitHub (auto-trigger en work item creation)
- MCP server exposing Fixi como tool a otros agentes
- Self-dogfooding: cron job que corre `fixi resolve` contra issues del propio repo de Fixi
- Multi-agent orchestration: spawn de subagents especializados (reviewer, tester, fixer)
- Triple-write tracking integration (Mission Control)
- Public `/status` y `/verify/:fix_id` endpoints
- Helm chart para deployment en Kubernetes (alternativa a ACI)
