---
id: S1-T04
title: Skeleton GMVM.EnergyTracker (4 projects + config)
sprint: S1
day: 1
status: done
priority: P1
type: implementation
tags: [dotnet, scaffolding, demo-repo, day-1]
created: 2026-04-06T22:30:00
updated: 2026-04-06T22:55:00
estimated: 45m
actual: 25m
owner: claude
blocks: [S1-T05, S1-T06, S1-T07, S1-T08, S1-T09, S1-T10, S1-T11]
blocked_by: [S1-T03]
related_docs: [SPRINT-1, BACKLOG]
commits: [5a900b9]
files_touched:
  - GMVM.EnergyTracker.sln
  - global.json
  - .gitignore
  - .editorconfig
  - CLAUDE.md
  - src/GMVM.EnergyTracker.Api/
  - src/GMVM.EnergyTracker.Domain/
  - src/GMVM.EnergyTracker.Infrastructure/
  - tests/GMVM.EnergyTracker.Tests/
---

# S1-T04: Skeleton GMVM.EnergyTracker

> **Sprint**: [[SPRINT-1]] · **Día**: 1 · **Status**: done
> **Owner**: claude · **Estimated**: 45m · **Actual**: 25m

## Contexto

Solution layout multi-project realista (no toy) para demostrar que Fixi puede navegar codebases reales: Api + Domain + Infrastructure + Tests.

## Acceptance Criteria

- [x] Solution `GMVM.EnergyTracker.sln` creado
- [x] 3 projects en `src/`: Api (webapi), Domain (classlib), Infrastructure (classlib)
- [x] 1 project en `tests/`: Tests (xunit)
- [x] Project references configuradas correctamente
- [x] NuGet packages agregados: EF Core 9, SQLite, JWT, Swagger, Mvc.Testing
- [x] `dotnet build` limpio (0 warnings, 0 errors)
- [x] Files de config: global.json, .gitignore, .editorconfig
- [x] CLAUDE.md con convenciones del demo
- [x] Templates removidos (WeatherForecast, Class1, UnitTest1)

## Notes & Attempts

**Decisión de framework**: solo .NET 9 SDK instalado, no .NET 8 LTS. Se usa .NET 9 para no perder tiempo. Reversible si GlobalMVM lo prefiere.

**Comandos clave**:
```
dotnet new sln --name GMVM.EnergyTracker
dotnet new webapi --name GMVM.EnergyTracker.Api --framework net9.0 --use-controllers
dotnet new classlib --name GMVM.EnergyTracker.Domain --framework net9.0
dotnet new classlib --name GMVM.EnergyTracker.Infrastructure --framework net9.0
dotnet new xunit --name GMVM.EnergyTracker.Tests --framework net9.0
dotnet sln add (todos)
dotnet add reference (cross-project)
dotnet add package (EF Core, SQLite, JWT, Swagger, Mvc.Testing, InMemory)
```

**Cleanup de templates**: removidos `WeatherForecastController.cs`, `WeatherForecast.cs`, `Class1.cs` (×2), `UnitTest1.cs` antes del primer commit.

**Build verificado**: `dotnet build` → 0 warnings, 0 errors, 4 dlls.

## Outcome

Solution compilando limpio con la estructura completa para sembrar los 3 bugs. Pushed a `lotsofcontext/fixi-demo-dotnet` master.

Commit: `5a900b9` — "chore: scaffold GMVM.EnergyTracker solution"

Próxima tarea: [[S1-T05]] (sembrar BUG #1).

## History

- `2026-04-06 22:30` · created (status: pending)
- `2026-04-06 22:30` · started (status: in-progress)
- `2026-04-06 22:55` · completed (status: done) · actual: 25m
