---
id: S1-T08
title: Tests que fallan para los 3 bugs sembrados
sprint: S1
day: 1
status: pending
priority: P1
type: test
tags: [demo-repo, dotnet, xunit, regression, day-1]
created: 2026-04-07T00:00:00
updated: 2026-04-07T00:00:00
estimated: 1h30m
actual: ""
owner: claude
blocks: []
blocked_by: [S1-T05, S1-T06, S1-T07]
related_docs: [SPRINT-1, BACKLOG]
commits: []
files_touched: []
---

# S1-T08: Tests failing para los 3 bugs

> **Sprint**: [[SPRINT-1]] · **Día**: 1 · **Status**: pending
> **Owner**: claude · **Estimated**: 1h30m

## Contexto

Los tests son la **clave del demo**: sin tests failing no se puede demostrar que el fix de Fixi es *provably correct*. Cada bug debe tener al menos un test que **falle antes del fix y pase después**.

## Acceptance Criteria

- [ ] `Unit/CalculadoraConsumoTests.cs` con test que captura el `DivideByZeroException`
- [ ] `Integration/MedidoresEndpointTests.cs` con test que cuenta queries SQL via EF logging (assert ≤ 2)
- [ ] `Integration/AdminEndpointSecurityTests.cs` con 2 tests:
  - Anonymous request → debe ser 401 (actualmente 200)
  - User-role request → debe ser 403 (actualmente 200)
- [ ] `dotnet test` muestra **al menos 4 tests rojos** predecibles
- [ ] Tests son deterministicos (no flaky)

## Plan

1. **Test del bug**: arrange dos `Lectura` con misma `FechaLectura`, act `Calcular`, assert no exception + valor correcto
2. **Test de perf** (más complejo): hookear `DbCommandInterceptor` o `ILogger<DbContext>` para contar queries; correr endpoint; assert count
3. **Test de security**: usar `WebApplicationFactory` + JWT helper; correr request anon y request con user-role; assert status codes

**Riesgo conocido**: el test de query counting puede ser flaky. Fallback: medición de latencia con `Stopwatch` (assert < 500ms).

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar — incluir output de `dotnet test` mostrando los rojos]

## History

- `2026-04-07 00:00` · created (status: pending)
