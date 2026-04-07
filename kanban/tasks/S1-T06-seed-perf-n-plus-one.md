---
id: S1-T06
title: "Sembrar PERF #2 — N+1 en MedidorService.ListarConResumen"
sprint: S1
day: 1
status: pending
priority: P1
type: implementation
tags: [demo-repo, dotnet, perf-seeded, day-1]
created: 2026-04-07T00:00:00
updated: 2026-04-07T00:00:00
estimated: 45m
actual: ""
owner: claude
blocks: [S1-T08]
blocked_by: [S1-T04, S1-T05]
related_docs: [SPRINT-1, BACKLOG]
commits: []
files_touched: []
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

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 00:00` · created (status: pending)
