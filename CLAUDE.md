# Fixi — Autonomous Issue Resolution Agent

## North Star Prompt (Jefferson Acevedo, GlobalMVM — reunión 2026-04-06)

Este es el prompt literal que dio el ingeniero cliente. **Todo lo que construimos en Fixi debe poder cumplir esta descripción.** Si una decisión de diseño no puede trazarse de vuelta a este prompt, sobra. Si una capability que el prompt exige no está cubierta, es un gap que hay que cerrar.

> Actúa como un agente de automatización de desarrollo de software encargado de gestionar tickets y requerimientos. Debes conectarte a fuentes de conocimiento disponibles como repositorios de código, sistemas de tickets y documentación técnica para analizar cada solicitud. Clasifica y prioriza el ticket según su tipo (bug, mejora, nueva funcionalidad), valida el código fuente existente relacionado, propone y aplica ajustes siguiendo buenas prácticas de desarrollo y estándares definidos, crea automáticamente una nueva rama con una nomenclatura adecuada, realiza los cambios necesarios en el código, ejecuta validaciones básicas, genera el commit con un mensaje claro y estructurado, y deja creado el Pull Request listo para aprobación incluyendo descripción técnica, cambios realizados y posibles impactos. No debes inventar información, si faltan datos debes indicarlo claramente y detener el flujo.

**Capabilities no-negociables que el prompt exige:**
1. Conectarse a **fuentes de conocimiento**: repos de código, sistemas de tickets, documentación técnica
2. **Clasificar y priorizar** por tipo (bug / mejora / nueva funcionalidad)
3. **Validar código fuente existente** relacionado al ticket antes de tocarlo
4. **Proponer y aplicar** ajustes siguiendo buenas prácticas y estándares definidos
5. **Crear rama** con nomenclatura adecuada (nunca tocar main)
6. **Ejecutar validaciones básicas** (tests, lint, build)
7. **Commit** con mensaje claro y estructurado (conventional commits)
8. **Pull Request listo para aprobación** con descripción técnica, cambios realizados, posibles impactos
9. **Halt-and-ask** cuando falten datos — jamás inventar información

## Project Context
Fixi is a Claude Code skill that automates the full lifecycle of issue resolution: intake → classification → analysis → fix → PR → tracking.

## Architecture
- `skill/SKILL.md` — Core 10-step workflow
- `skill/references/classification.md` — 7-type taxonomy with keywords and decision tree
- `skill/references/guardrails.md` — 13 safety rules

## Development
- `docs/PLAN.md` — 6-phase roadmap (46 tasks, includes Azure/MCP/A2A/demo)
- `docs/SPEC.md` — Full technical specification
- `docs/diagrams.md` — 5 Mermaid diagrams (flow, classification, autonomy, tracking, architecture)
- `docs/CLIENT-FACING.md` — Business-language doc for GlobalMVM
- `docs/planning/BACKLOG.md` — Prioritized backlog items
- `docs/planning/SPRINT-1.md` — Day-by-day Sprint 1 execution plan
- `kanban/` — Self-updating Kanban board for task tracking
  - `kanban/BOARD.md` — Auto-generated board (NEVER edit manually)
  - `kanban/tasks/` — Individual task files (frontmatter = source of truth)
  - `kanban/history/` — Append-only daily transition logs
  - `kanban/update_board.py` — Run after editing any task file

## Kanban workflow (MANDATORY)
- Antes de empezar trabajo en Sprint 1: editar el task file relevante en `kanban/tasks/`
- Cambiar `status:` a `in-progress`, actualizar `updated:`, agregar nota en `## Notes & Attempts`
- Correr `python kanban/update_board.py` (regenera BOARD, guarda history)
- Al completar: cambiar a `done`, llenar `actual:`, `commits:`, `files_touched:`, sección `## Outcome`
- Re-correr el script. Commit todo junto: task file + BOARD + .state.json + history

## Rules
- NEVER invent information. If data is missing, halt and ask.
- NEVER modify code outside the scope of the ticket.
- ALWAYS create a branch. NEVER commit to main.
- ALWAYS run tests before creating PR.
- Conventional commits: fix:, feat:, refactor:, etc.
- ALWAYS commit granularly: un commit por cada unidad lógica completada (un diagrama, un doc, una sección). No acumular cambios grandes.
