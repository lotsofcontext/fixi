---
id: S2-T07
title: Smoke test — orchestrator resuelve WI-101 sin hooks
sprint: S2
day: 1
status: pending
priority: P0
type: test
tags: [agent, python, smoke-test, day-1]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 30m
actual: ""
owner: claude
blocks: [S2-T08]
blocked_by: [S2-T06]
related_docs: [SPRINT-2]
commits: []
files_touched: []
---

# S2-T07: Smoke test del orchestrator

> **Sprint**: [[SPRINT-2]] · **Día**: 1 · **Status**: pending

## Contexto

Antes de implementar hooks, validar que el orchestrator (sin hooks aún) puede resolver WI-101 contra el demo repo end-to-end. Si esto funciona, el camino está despejado para los siguientes 12 días de Sprint 2.

## Acceptance Criteria

- [ ] Script standalone `tests/integration/smoke_test.py` que:
  - Clona `fixi-demo-dotnet` en tmpdir
  - Lee `docs/issues/WI-101-bug-lectura-negativa.md` como work item
  - Instancia `FixiOrchestrator`
  - Ejecuta `await orchestrator.run()`
  - Verifica que el resultado tiene `success=True` y `pr_url` no-vacío
- [ ] El smoke test corre exitosamente al menos una vez
- [ ] Tiempo total < 5 minutos
- [ ] No contamina el master del demo repo (el branch del fix queda en su rama)

## Plan

1. Setup ANTHROPIC_API_KEY en env
2. Correr `python tests/integration/smoke_test.py`
3. Verificar PR creado en GitHub
4. Si falla: debug, iterar
5. Si pasa: commit y avanzar

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar — incluir métricas: duración real, tokens consumidos, costo aproximado]

## History

- `2026-04-07 04:30` · created (status: pending)
