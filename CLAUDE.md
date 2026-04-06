# Fixi — Autonomous Issue Resolution Agent

## Project Context
Fixi is a Claude Code skill that automates the full lifecycle of issue resolution: intake → classification → analysis → fix → PR → tracking.

## Architecture
- `skill/SKILL.md` — Core 10-step workflow
- `skill/references/classification.md` — 7-type taxonomy with keywords and decision tree
- `skill/references/guardrails.md` — 13 safety rules

## Development
- `docs/PLAN.md` — 5-phase roadmap (36 tasks)
- `docs/SPEC.md` — Full technical specification

## Rules
- NEVER invent information. If data is missing, halt and ask.
- NEVER modify code outside the scope of the ticket.
- ALWAYS create a branch. NEVER commit to main.
- ALWAYS run tests before creating PR.
- Conventional commits: fix:, feat:, refactor:, etc.
