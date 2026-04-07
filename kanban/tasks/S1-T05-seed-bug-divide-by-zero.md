---
id: S1-T05
title: "Sembrar BUG #1 — DivideByZero en CalculadoraConsumo"
sprint: S1
day: 1
status: in-progress
priority: P1
type: implementation
tags: [demo-repo, dotnet, bug-seeded, day-1]
created: 2026-04-07T00:00:00
updated: 2026-04-07T01:00:00
estimated: 30m
actual: ""
owner: claude
blocks: [S1-T08]
blocked_by: [S1-T04]
related_docs: [SPRINT-1, BACKLOG]
commits: []
files_touched: []
---

# S1-T05: Sembrar BUG #1 — DivideByZero en CalculadoraConsumo

> **Sprint**: [[SPRINT-1]] · **Día**: 1 · **Status**: pending
> **Owner**: claude · **Estimated**: 30m

## Contexto

Primer bug intencional del demo. Tipo: `bug` (clasificación Fixi). Realista para sector energía: técnico en campo registra dos lecturas del mismo medidor en el mismo día (revisión post-tormenta), causa `DivideByZeroException` por usar `.Days` en vez de `.TotalDays`.

Repo target: [[fixi-demo-dotnet]]
Work item: WI-101

## Acceptance Criteria

- [ ] `src/GMVM.EnergyTracker.Domain/Services/ICalculadoraConsumo.cs` creado (interface)
- [ ] `src/GMVM.EnergyTracker.Domain/Services/CalculadoraConsumo.cs` creado con bug intencional
- [ ] El bug se reproduce con dos `Lectura` con misma `FechaLectura`
- [ ] Compila sin errores
- [ ] Modelos `Lectura` y `Medidor` creados (necesarios para la firma)

## Plan

1. Crear `Models/Medidor.cs` y `Models/Lectura.cs` en Domain
2. Crear interface `ICalculadoraConsumo`
3. Implementar `CalculadoraConsumo.Calcular(Lectura previa, Lectura actual)` con `.Days` (bug)
4. Verificar build limpio
5. Bug se materializa al ejecutar el test de [[S1-T08]]

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 00:00` · created (status: pending)
