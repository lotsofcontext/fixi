---
id: S1-T06
title: "Sembrar PERF #2 — N+1 en MedidorService.ListarConResumen"
sprint: S1
day: 1
status: done
priority: P1
type: implementation
tags: [demo-repo, dotnet, perf-seeded, day-1]
created: 2026-04-07T00:00:00
updated: 2026-04-07T01:30:00
estimated: 45m
actual: 15m
owner: claude
blocks: [S1-T08]
blocked_by: [S1-T04, S1-T05]
related_docs: [SPRINT-1, BACKLOG]
commits: [89e7a58]
files_touched:
  - src/GMVM.EnergyTracker.Infrastructure/EnergyTrackerDbContext.cs
  - src/GMVM.EnergyTracker.Infrastructure/Seed/SeedData.cs
  - src/GMVM.EnergyTracker.Infrastructure/Services/MedidorService.cs
  - src/GMVM.EnergyTracker.Domain/Services/IMedidorService.cs
  - src/GMVM.EnergyTracker.Domain/Dtos/MedidorListItem.cs
---

# S1-T06: Sembrar PERF #2 — N+1 en MedidorService

> **Sprint**: [[SPRINT-1]] · **Día**: 1 · **Status**: pending
> **Owner**: claude · **Estimated**: 45m

## Contexto

Segundo bug intencional. Tipo: `performance`. Patrón clásico N+1 con EF Core: query para listar medidores + 1 query por cada medidor para obtener su última lectura. Con 50 medidores → 51 queries.

Realista: en producción con 4,000 medidores el endpoint hace timeout.

Repo target: [[fixi-demo-dotnet]]
Work item: WI-102

## Acceptance Criteria

- [ ] `src/GMVM.EnergyTracker.Infrastructure/EnergyTrackerDbContext.cs` creado
- [ ] `src/GMVM.EnergyTracker.Infrastructure/Seed/SeedData.cs` con 50 medidores + 5000 lecturas (deterministic)
- [ ] `src/GMVM.EnergyTracker.Domain/Services/IMedidorService.cs` creado
- [ ] `src/GMVM.EnergyTracker.Domain/Services/MedidorService.cs` con N+1 deliberado
- [ ] DTO `MedidorListItem` creado
- [ ] Compila sin errores

## Plan

1. DbContext con DbSets
2. Seed deterministic (fixed random seed) — 50 medidores, ~100 lecturas cada uno
3. Service interface
4. Implementación con `await _db.Medidores.ToListAsync()` + loop con `await _db.Lecturas.Where(...).FirstOrDefaultAsync()`
5. Verificar build
6. Medición de queries en [[S1-T08]]

## Notes & Attempts

**Decisión de DB**: SQLite — zero setup, file-based. EF Core abstrae todo igual.

**Seed deterministico**: `Random(20260407)` con semilla fija. 50 medidores × ~100 lecturas cada uno = ~5000 rows. Distribuidas a 5 clientes reales del sector energético colombiano (ISAGEN, EPM, XM, VEOLIA, CELSIA).

**Bug N+1 implementado en `MedidorService.ListarConResumenAsync()`**: 
1. `await _db.Medidores.ToListAsync()` → 1 query
2. `foreach (var medidor in medidores)` → 50 iteraciones
3. Cada iteración: `await _db.Lecturas.Where(...).FirstOrDefaultAsync()` → 1 query

Total: **51 queries** para 50 medidores. En producción con 4,000 medidores → 4,001 queries → timeout.

**Arquitectura considerada**: puse `MedidorService` en `Infrastructure/Services` (no en Domain) porque depende de EF Core. Domain solo tiene la interface. Esto es Clean Architecture canónico y Fixi lo va a navegar bien.

**Bug de typo encontrado**: usé `new Random(seed: 20260407)` (named arg) — falló porque `Random.ctor` no tiene parámetro nombrado `seed`, es positional. Cambiado a `new Random(20260407)`. Build OK.

## Outcome

5 archivos creados en `fixi-demo-dotnet/`:
- `Infrastructure/EnergyTrackerDbContext.cs` (EF Core + SQLite + indexes)
- `Infrastructure/Seed/SeedData.cs` (datos deterministicos)
- `Infrastructure/Services/MedidorService.cs` (con N+1)
- `Domain/Services/IMedidorService.cs` (interface)
- `Domain/Dtos/MedidorListItem.cs` (DTO)

Commit: `89e7a58`. Build: 0/0.

Próxima: [[S1-T07]] (SECURITY #3 — AdminController sin Authorize).

## History

- `2026-04-07 00:00` · created (status: pending)
- `2026-04-07 01:15` · started (status: in-progress)
- `2026-04-07 01:30` · completed (status: done) · actual: 15m
