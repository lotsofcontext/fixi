---
id: S2-T13
title: Tests unitarios — parser, hooks, prompts
sprint: S2
day: 2
status: done
priority: P1
type: test
tags: [agent, python, tests, day-2]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 1h30m
actual: ""
owner: claude
blocks: []
blocked_by: [S2-T08]
related_docs: [SPRINT-2]
commits: []
files_touched: []
---

# S2-T13: Tests unitarios

> **Sprint**: [[SPRINT-2]] · **Día**: 2 · **Status**: pending

## Contexto

Tests pytest para los componentes core: parser, hooks, prompts.

## Acceptance Criteria

- [ ] `tests/unit/test_parser.py` con tests para cada source type
- [ ] `tests/unit/test_hooks.py` con tests para cada uno de los 13 guardrails
- [ ] `tests/unit/test_prompts.py` para verificar load_system_prompt
- [ ] `pytest tests/unit/` corre verde
- [ ] Coverage > 70% en los archivos cubiertos

## Plan

Mocks de subprocess para los parsers de gh/az. Mocks de filesystem para hooks.

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
