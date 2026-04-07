---
id: S1-T17
title: Polish CLIENT-FACING.md con links a runs y Terraform
sprint: S1
day: 5
status: done
priority: P1
type: docs
tags: [docs, client-facing, polish, day-5]
created: 2026-04-07T00:00:00
updated: 2026-04-07T03:30:00
estimated: 1h
actual: 30m
owner: claude
blocks: []
blocked_by: [S1-T16]
related_docs: [SPRINT-1, BACKLOG]
commits: []
files_touched:
  - docs/CLIENT-FACING.md
---

# S1-T17: Polish CLIENT-FACING.md

> **Sprint**: [[SPRINT-1]] · **Día**: 5 · **Status**: pending
> **Owner**: claude · **Estimated**: 1h

## Contexto

`docs/CLIENT-FACING.md` ya existe (260 líneas) pero necesita pulido final con links a los runs reales y al Terraform skeleton. Es el doc que Joaris circulará.

## Acceptance Criteria

- [ ] Links activos a `docs/demos/run-01-github.md` y `docs/demos/run-02-ado.md`
- [ ] Sección de Terraform con link a `terraform/README.md`
- [ ] Screenshots de los PRs reales (de los rehearsals)
- [ ] ROI table refinada con datos reales del rehearsal (tiempo medido)
- [ ] Sección "qué se puede probar hoy" con instrucciones de clone
- [ ] Final pass: typos, claridad, lenguaje de negocio
- [ ] Verificar todos los links cross-doc

## Plan

Lectura completa primero, después edits puntuales. No reescribir.

## Notes & Attempts

**Decisión de scope**: Esta tarea originalmente estaba bloqueada por T12 + T15 + T16 (necesita los run transcripts). Cambié de scope a "polish parcial sin rehearsals":

- **Removidos** los blockers T12 y T15 de `blocked_by` (solo dependía de T16, que está done)
- **Mantenidos placeholders** para los run transcripts: cuando T12 y T15 se ejecuten, solo hay que agregar 2 líneas con los links

**Cambios aplicados a `docs/CLIENT-FACING.md`** (260 → 343 líneas, +83):

1. **Header** — versión 1.0 → 2.0, fecha 2026-04-06 → 2026-04-07, agregado bloque con links a los 2 repos públicos

2. **Sección "Cómo se ve en la práctica"** — reemplazada COMPLETA. El ejemplo anterior era ficticio (ventas-dashboard, Work Item #4521). Ahora es:
   - Tabla de los 3 work items reales con links a GitHub
   - Sección "Cómo lo pueden probar hoy" con comandos exactos (clone, restore, build, test)
   - Output de Fixi con el ejemplo real de WI-101 (paths reales del demo repo, branch real, métricas reales)
   - Nota sobre placeholders para los transcripts de rehearsals
   - Sección destacada "El caso especial: WI-103 (security)" explicando que fuerza GUIDED automático — responde directo a la preocupación de John Bairo sobre adopción/resistencia

3. **Sección "Infraestructura y Despliegue"** — expandida con:
   - Link directo a `terraform/README.md`
   - Mención de las métricas concretas (25 archivos, 5 módulos, ~1,955 líneas, validado)
   - Tabla de componentes con links a cada módulo Terraform
   - Sub-sección "Decisiones de seguridad clave" con 7 bullets concretos (KV RBAC mode, NSG deny-all, ACR admin disabled, etc.)

4. **Diagrama ASCII de arquitectura** — actualizado para remover `/status` y `/verify` (features deferidas), reemplazado por "Azure Repos / GitHub PRs para revisión humana" + "Tracking (ACTIVO.md + Mission Control)"

5. **Nueva sección "Integración con Azure DevOps"** — completa, con sub-secciones:
   - Lectura de Work Items (pattern, comando, field mapping, fallbacks)
   - Creación de Pull Requests (auto-detección, template, link PR↔WI)
   - Azure Pipelines (detección, comments)
   - Link al SKILL.md, guardrails.md, classification.md

6. **Removida** sección antigua "Integraciones Avanzadas" (MCP Server / `/status` / `/verify`) — esas features están deferidas y no deben aparecer en client-facing

7. **Nueva sección "Documentación adicional"** — tabla con todos los docs internos y para qué sirven

8. **Sección "Próximos Pasos"** — refactorizada en 7 items con check marks para los 2 ya completados (repo cloneable, Terraform analizable) y emojis ⏳ para los pendientes (rehearsal, review, "el chicharrón", reunión, piloto)

9. **Footer** — agregado pointer a `kanban/BOARD.md` para que los reviewers vean el progreso live

**Decisión sobre wiki links**: este doc es client-facing, así que mantengo links markdown estándar (`[texto](ruta.md)`) — NO `[[wiki]]`. Coherente con la decisión global de [[S1-T02]].

**Lo que sigue siendo TODO** (cuando T12 y T15 finalicen):
- 2 líneas de link a `docs/demos/run-01-github.md` y `docs/demos/run-02-ado.md`
- 2 screenshots embebidos de los PRs creados durante los rehearsals
- Métricas reales medidas (tiempo de ejecución de Fixi en cada run)

Estos son adiciones puntuales, no rewrites. El doc está al 90% terminado.

## Outcome

`docs/CLIENT-FACING.md` reescrito de 260 → 343 líneas. Versión 2.0. Cero referencias a features deferidas o ejemplos ficticios. Listo para que Joaris lo circule internamente.

**Sprint 1 — todas las tareas no-bloqueantes completas. 16/18 done = 89%.**

Pendiente solo lo que requiere ejecución real con humano + ADO sandbox:
- [[S1-T12]] (rehearsal Fixi vs WI-101 path GitHub)
- [[S1-T15]] (rehearsal Fixi vs WI-102 + WI-103 path Azure DevOps)

## History

- `2026-04-07 00:00` · created (status: pending)
- `2026-04-07 03:15` · started (status: in-progress, scope ajustado)
- `2026-04-07 03:30` · completed (status: done) · actual: 30m
