---
id: S1-T05
title: "Sembrar BUG #1 — DivideByZero en CalculadoraConsumo"
sprint: S1
day: 1
status: done
priority: P1
type: implementation
tags: [demo-repo, dotnet, bug-seeded, day-1]
created: 2026-04-07T00:00:00
updated: 2026-04-07T01:15:00
estimated: 30m
actual: 15m
owner: claude
blocks: [S1-T08]
blocked_by: [S1-T04]
related_docs: [SPRINT-1, BACKLOG]
commits: [2c11e4b]
files_touched:
  - src/GMVM.EnergyTracker.Domain/Models/Medidor.cs
  - src/GMVM.EnergyTracker.Domain/Models/Lectura.cs
  - src/GMVM.EnergyTracker.Domain/Services/ICalculadoraConsumo.cs
  - src/GMVM.EnergyTracker.Domain/Services/CalculadoraConsumo.cs
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

**Decisión de arquitectura**: Modelos de entidad puestos en `Domain/Models/` (no en `Api/Models`) para Clean Architecture realista. Es lo que GlobalMVM va a esperar ver.

**Bug sembrado**: línea 17 de `CalculadoraConsumo.cs`:
```csharp
var diasTranscurridos = (actual.FechaLectura - previa.FechaLectura).Days;
```
Cuando dos lecturas son del mismo día (e.g., 14:00 y 16:00 del mismo día), `.Days = 0`, causa `DivideByZeroException` en la siguiente línea (`deltaKwh / diasTranscurridos`).

**Decisión deliberada de NO arreglar**: el bug es la pieza central del demo. El test del bug en [[S1-T08]] lo va a probar.

**Edge case manejado bien**: `previa is null` → primera lectura del medidor, retorna `actual.ValorKwh`. Esto NO es bug (es comportamiento correcto).

**Build**: 0 warnings, 0 errors.

## Outcome

4 archivos creados en `fixi-demo-dotnet/src/GMVM.EnergyTracker.Domain/`:
- `Models/Medidor.cs` (entidad)
- `Models/Lectura.cs` (entidad con `FechaLectura`, `ValorKwh`, `ConsumoCalculado`)
- `Services/ICalculadoraConsumo.cs` (interface)
- `Services/CalculadoraConsumo.cs` (impl con bug deliberado)

Branch: `feat/seed-intentional-bugs`
Commit: `2c11e4b`

Próxima: [[S1-T06]] (PERF #2 — N+1).

## History

- `2026-04-07 00:00` · created (status: pending)
- `2026-04-07 01:00` · started (status: in-progress)
- `2026-04-07 01:15` · completed (status: done) · actual: 15m
