# Fixi — Autonomous Issue Resolution Agent

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

## Rules
- NEVER invent information. If data is missing, halt and ask.
- NEVER modify code outside the scope of the ticket.
- ALWAYS create a branch. NEVER commit to main.
- ALWAYS run tests before creating PR.
- Conventional commits: fix:, feat:, refactor:, etc.
- ALWAYS commit granularly: un commit por cada unidad lógica completada (un diagrama, un doc, una sección). No acumular cambios grandes.
