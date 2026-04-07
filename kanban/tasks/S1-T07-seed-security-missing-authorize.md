---
id: S1-T07
title: "Sembrar SECURITY #3 — AdminController sin [Authorize]"
sprint: S1
day: 1
status: pending
priority: P1
type: implementation
tags: [demo-repo, dotnet, security-seeded, owasp, day-1]
created: 2026-04-07T00:00:00
updated: 2026-04-07T00:00:00
estimated: 20m
actual: ""
owner: claude
blocks: [S1-T08]
blocked_by: [S1-T06]
related_docs: [SPRINT-1, BACKLOG]
commits: []
files_touched: []
---

# S1-T07: Sembrar SECURITY #3 — AdminController sin [Authorize]

> **Sprint**: [[SPRINT-1]] · **Día**: 1 · **Status**: pending
> **Owner**: claude · **Estimated**: 20m

## Contexto

Tercer bug intencional. Tipo: `security`. **OWASP A01:2021 Broken Access Control** — el más alto del OWASP Top 10. `AdminController` no tiene `[Authorize(Roles="Admin")]` mientras `UsuariosController` sí. Endpoints destructivos (resetear lecturas, eliminar usuarios) accesibles sin auth.

Bug realista: el #1 error real en .NET, por omisión.

Cuando Fixi clasifique este issue, debe **forzar GUIDED automático** por ser security.

Repo target: [[fixi-demo-dotnet]]
Work item: WI-103

## Acceptance Criteria

- [ ] `src/GMVM.EnergyTracker.Api/Controllers/UsuariosController.cs` creado **CON** `[Authorize]` (baseline limpio)
- [ ] `src/GMVM.EnergyTracker.Api/Controllers/AdminController.cs` creado **SIN** `[Authorize]` (bug)
- [ ] `src/GMVM.EnergyTracker.Api/Program.cs` configura JWT auth
- [ ] El contraste entre los dos controllers es obvio (mismo patrón, omisión deliberada)
- [ ] Compila sin errores

## Plan

1. Models/Usuario.cs con role
2. Program.cs: JWT Bearer config, DI, EF, Swagger, controllers
3. UsuariosController.cs con `[Authorize]` — el patrón correcto
4. AdminController.cs **sin** atributo — el bug
5. appsettings.json con JWT config (no secrets reales)
6. Verificar build

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 00:00` · created (status: pending)
