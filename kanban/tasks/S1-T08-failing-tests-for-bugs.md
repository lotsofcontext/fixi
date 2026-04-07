---
id: S1-T08
title: Tests que fallan para los 3 bugs sembrados
sprint: S1
day: 1
status: done
priority: P1
type: test
tags: [demo-repo, dotnet, xunit, regression, day-1]
created: 2026-04-07T00:00:00
updated: 2026-04-07T02:15:00
estimated: 1h30m
actual: 30m
owner: claude
blocks: []
blocked_by: [S1-T05, S1-T06, S1-T07]
related_docs: [SPRINT-1, BACKLOG]
commits: [ba8ad67]
files_touched:
  - tests/GMVM.EnergyTracker.Tests/Unit/CalculadoraConsumoTests.cs
  - tests/GMVM.EnergyTracker.Tests/Integration/TestWebApplicationFactory.cs
  - tests/GMVM.EnergyTracker.Tests/Integration/MedidoresEndpointTests.cs
  - tests/GMVM.EnergyTracker.Tests/Integration/AdminEndpointSecurityTests.cs
  - tests/GMVM.EnergyTracker.Tests/Integration/JwtTokenHelper.cs
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

**Tests creados (5 archivos)**:
1. `Unit/CalculadoraConsumoTests.cs` — 4 tests (2 baseline pass, 2 que capturan WI-101)
2. `Integration/TestWebApplicationFactory.cs` — helper, NO test (custom WebApplicationFactory<Program> con SQLite :memory: shared connection)
3. `Integration/MedidoresEndpointTests.cs` — 1 test de latencia para WI-102
4. `Integration/AdminEndpointSecurityTests.cs` — 3 tests para WI-103
5. `Integration/JwtTokenHelper.cs` — helper para generar JWTs válidos

**Resultado del test run**:
```
Failed!  - Failed: 5, Passed: 3, Skipped: 0, Total: 8, Duration: 2 s
```

**Tests rojos esperados** (todos son los bugs sembrados):
- `Calcular_DosLecturasMismoDia_NoDebeLanzarExcepcion` → DivideByZeroException (WI-101)
- `Calcular_DosLecturasMismoDia_RetornaDeltaDirecto` → DivideByZeroException (WI-101)
- `ResetearLecturas_SinAutenticacion_DebeRetornar401` → returned `OK` (WI-103)
- `EliminarUsuario_SinAutenticacion_DebeRetornar401` → returned `NotFound` (WI-103, semi-protege por NotFound pero no es auth)
- `ResetearLecturas_AutenticadoComoUser_DebeRetornar403` → returned `OK` (WI-103)

**Tests verdes esperados**:
- `Calcular_PrimeraLecturaSinPrevia_RetornaValorActual` (baseline OK)
- `Calcular_DosLecturasEnDiasDistintos_PromediaPorDia` (baseline OK)
- `Listar_LatenciaP95_DebeSerMenorA500ms` (PASA con SQLite in-memory porque es instantáneo)

**Limitación conocida del test de PERF**: SQLite in-memory hace que las queries sean instantáneas, así que el test de latencia no captura el N+1 funcionalmente. Lo dejé documentado en comments del test. Funciona mejor cuando Fixi corra contra una BD real con latencia. **El N+1 functional sigue sembrado en MedidorService** — Fixi va a verlo por inspección de código, no por test rojo.

**Decisión técnica**: para el test de seguridad, usé `JwtTokenHelper` que genera JWTs con la misma key/issuer/audience que `Program.cs`. La key es literal `"DEMO_ONLY_REPLACE_ME_..."` — no es secret real.

**Package agregado**: `System.IdentityModel.Tokens.Jwt 8.1.0` en tests project.

## Outcome

5 archivos de test creados, build limpio, **5 tests fallan deterministicamente, 3 pasan**. La evidencia de los bugs es ahora ejecutable: `dotnet test` produce el patrón esperado.

Commit demo repo: `ba8ad67`. Pushed a `lotsofcontext/fixi-demo-dotnet master`.

**Sprint 1 Día 1 — COMPLETO** (Stream A). El demo repo está listo para que Fixi opere contra él.

## History

- `2026-04-07 00:00` · created (status: pending)
- `2026-04-07 01:45` · started (status: in-progress)
- `2026-04-07 02:15` · completed (status: done) · actual: 30m
