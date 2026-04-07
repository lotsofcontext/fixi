---
id: S1-T07
title: "Sembrar SECURITY #3 — AdminController sin [Authorize]"
sprint: S1
day: 1
status: done
priority: P1
type: implementation
tags: [demo-repo, dotnet, security-seeded, owasp, day-1]
created: 2026-04-07T00:00:00
updated: 2026-04-07T01:45:00
estimated: 20m
actual: 15m
owner: claude
blocks: [S1-T08]
blocked_by: [S1-T06]
related_docs: [SPRINT-1, BACKLOG]
commits: [0516e9f]
files_touched:
  - src/GMVM.EnergyTracker.Domain/Models/Usuario.cs
  - src/GMVM.EnergyTracker.Infrastructure/EnergyTrackerDbContext.cs
  - src/GMVM.EnergyTracker.Api/Program.cs
  - src/GMVM.EnergyTracker.Api/Controllers/MedidoresController.cs
  - src/GMVM.EnergyTracker.Api/Controllers/UsuariosController.cs
  - src/GMVM.EnergyTracker.Api/Controllers/AdminController.cs
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

**Bug deliberado**: `AdminController` no tiene `[Authorize]` ni a nivel de clase ni de método. Mientras tanto, `MedidoresController` y `UsuariosController` SÍ lo tienen — el contraste hace que Fixi (en Paso 4 de root cause analysis) compare los tres y vea la omisión.

**Endpoints destructivos sin auth**:
- `POST /api/admin/resetear-lecturas` → borra TODAS las lecturas históricas con `ExecuteDeleteAsync`
- `DELETE /api/admin/usuarios/{id}` → elimina cualquier usuario

**Program.cs configurado con**:
- JWT Bearer auth con symmetric key (DEMO ONLY, placeholder en config)
- `UseAuthentication() + UseAuthorization()` en pipeline
- Seed on startup (`db.Database.EnsureCreated()` + `SeedData.Seed`)
- `public partial class Program { }` para `WebApplicationFactory<Program>` en tests

**JWT Key**: hardcoded como `"DEMO_ONLY_REPLACE_ME_IN_PRODUCTION_AT_LEAST_32_CHARS"` para que el build funcione zero-config. NO es secret real, es literal "DEMO_ONLY_...".

**Decisión**: NO sembrar un cuarto bug de "JWT key hardcodeada" para no muddy el signal. Los 3 bugs son claros y diferenciados.

## Outcome

6 archivos modificados/creados:
- `Domain/Models/Usuario.cs` (entidad nueva)
- `Infrastructure/EnergyTrackerDbContext.cs` (DbSet<Usuario> agregado)
- `Api/Program.cs` (rewrite completo: DI, JWT, EF, Swagger, seed)
- `Api/Controllers/MedidoresController.cs` (con `[Authorize]`)
- `Api/Controllers/UsuariosController.cs` (con `[Authorize]`)
- `Api/Controllers/AdminController.cs` (SIN `[Authorize]` — el bug)

Build: 0/0. Commit: `0516e9f`.

Próxima: [[S1-T08]] (failing tests para los 3 bugs).

## History

- `2026-04-07 00:00` · created (status: pending)
- `2026-04-07 01:30` · started (status: in-progress)
- `2026-04-07 01:45` · completed (status: done) · actual: 15m
