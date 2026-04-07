# Backlog — Fixi

> Items capturados durante sesiones de desarrollo. Priorizar al inicio de cada sesión.
> Ver también: [[PLAN|Roadmap de 6 fases]], [[SPEC|Especificación técnica]], [[SPRINT-1|Sprint 1 actual]]

**Leyenda de prioridad**:
- **P0** — En ejecución ahora, bloqueando otras cosas
- **P1** — Sprint 1 (critical path al demo GlobalMVM)
- **P2** — Sprint 2 (convierte interés en contrato)
- **P3** — Deferido: nice-to-have, no bloqueante
- **done** — Completado

---

## Completados

| Date | Item | Priority |
|------|------|----------|
| 2026-04-06 | Diagramas Mermaid (P2 del handoff) | done |
| 2026-04-06 | Documento client-facing (P3 del handoff) | done |
| 2026-04-06 | PLAN.md actualizado con Fase 6 | done |
| 2026-04-06 | Backlog creado y estructurado | done |
| 2026-04-06 | README reescrito + README.es.md sync | done |
| 2026-04-06 | Obsidian wiki links en docs internos | done |

---

## Sprint 1 — Critical Path al Demo GlobalMVM (5 días)

Secuencia determinada por análisis de agentes. Objetivo: **repo cloneable que GlobalMVM pueda analizar y ejecutar**.

| # | Date | Item | Context | Priority | Status |
|---|------|------|---------|----------|--------|
| S1.1 | 2026-04-06 | Verificar contenido de `classification.md` y `guardrails.md` | Auditar que no son placeholders. SKILL.md los referencia intensivamente | P0 | pending |
| S1.2 | 2026-04-06 | Auditar wiki links — formato dual | Docs internos (PLAN, SPEC, BACKLOG) mantienen `[[wiki]]`. Client-facing (README, CLIENT-FACING, diagrams) usa links estándar para render en GitHub | P0 | pending |
| S1.3 | 2026-04-06 | Crear repo `lotsofcontext/fixi-demo-dotnet` en GitHub | Sibling de fixi, NO subdirectorio (Safety Gate). Stack: ASP.NET Core 8 | P1 | pending |
| S1.4 | 2026-04-06 | Skeleton `GMVM.EnergyTracker.Api` | Solution + 3 projects (Api, Domain, Infrastructure) + Tests. Domain: servicio de lectura de medidores (matchea sector energía GlobalMVM) | P1 | pending |
| S1.5 | 2026-04-06 | Sembrar BUG #1 — DivideByZero en CalculadoraConsumo | `CalculadoraConsumo.Calcular` usa `.Days` → crash cuando dos lecturas mismo día. Realistic bug energy sector | P1 | pending |
| S1.6 | 2026-04-06 | Sembrar PERF #2 — N+1 en MedidorService | `ListarConResumen()` query por cada medidor. 50 medidores = 51 queries | P1 | pending |
| S1.7 | 2026-04-06 | Sembrar SECURITY #3 — AdminController sin [Authorize] | OWASP A01 Broken Access Control. Fuerza GUIDED automático en Fixi | P1 | pending |
| S1.8 | 2026-04-06 | Tests que fallan para cada bug | CalculadoraConsumoTests (bug), MedidoresEndpointTests (perf guard con query counting), AdminEndpointSecurityTests (security) | P1 | pending |
| S1.9 | 2026-04-06 | Pre-crear 3 work items en `docs/issues/` | WI-101, WI-102, WI-103 en formato ADO-export markdown, bilingüe español/inglés | P1 | pending |
| S1.10 | 2026-04-06 | CLAUDE.md del demo repo | Convenciones: test commands, branch naming, commit style. Doble propósito: Fixi lo lee + template para GlobalMVM | P1 | pending |
| S1.11 | 2026-04-06 | README del demo repo (bilingüe) | Walkthrough: cómo clonar, cómo correr tests (rojos), cómo invocar Fixi contra cada issue | P1 | pending |
| S1.12 | 2026-04-06 | Rehearsal Fixi contra WI-101 (bug) → `run-01-github.md` | Transcript completo en markdown. Screenshots del PR. Evidencia diffeable | P1 | pending |
| S1.13 | 2026-04-06 | Agregar parser Azure DevOps al SKILL.md | Task 2.4 del PLAN. `az boards work-item show` + fallback WebFetch | P1 | pending |
| S1.14 | 2026-04-06 | Agregar creación de PR Azure Repos al SKILL.md | Task 6.1 del PLAN. `az repos pr create` como alternativa a `gh pr create` | P1 | pending |
| S1.15 | 2026-04-06 | Rehearsal Fixi contra WI-102 + WI-103 (ADO path) → `run-02-ado.md` | Requiere ADO sandbox. Transcript + screenshots | P1 | pending |
| S1.16 | 2026-04-06 | Terraform skeleton en `fixi/terraform/` | ACI, ACR, managed identity, networking. Solo legible, `terraform validate` limpio. NO necesita `apply` | P1 | pending |
| S1.17 | 2026-04-06 | Polish `CLIENT-FACING.md` con enlaces a runs + Terraform diagram | Es el doc que Joaris circulará. Debe apuntar a TODO | P1 | pending |
| S1.18 | 2026-04-06 | Actualizar descripción GitHub de lotsofcontext/fixi | Bloqueado: requiere `gh auth login` con cuenta lotsofcontext | P1 | blocked |

---

## Sprint 2 — Confidence Building (después del demo)

Objetivo: convertir el interés en contrato. Evidencia estadística + experiencia de un-click.

| Date | Item | Context | Priority |
|------|------|---------|----------|
| 2026-04-06 | GUIDED mode full rehearsal — 5+ runs con playbook | Joaris pidió "ingeniería y confiabilidad". Incluir 1 caso de rollback | P2 |
| 2026-04-06 | Triple-write tracking con destinos configurables | Pivotar de Mission Control específico a: ACTIVO.md + ADO Work Item state + PR comment log | P2 |
| 2026-04-06 | Azure Pipelines detection + PR comment con resultado | Cierra loop de CI/CD visibility | P2 |
| 2026-04-06 | CONFIRM_PLAN mode implementación | Skip FULL_AUTO. One-click es el money-shot del demo, menos riesgo político | P2 |
| 2026-04-06 | Conventions loader (CLAUDE.md priority chain) | Task 5.6. Demostrar con `.fixi/conventions.md` en sandbox | P2 |
| 2026-04-06 | Segundo sandbox en Java | Stack #2 de GlobalMVM. Prueba real de "stack agnostic" | P2 |

---

## Deferidos (P3) — No en critical path

Capturados pero explícitamente deprioritizados. Reactivar post-contrato o según demanda.

| Date | Item | Razón para deferir |
|------|------|--------------------|
| 2026-04-06 | Parsers Linear y Jira | GlobalMVM usa Azure DevOps. GH + ADO cubre demo |
| 2026-04-06 | FULL_AUTO mode | Políticamente riesgoso. John Bairo preocupado por resistencia de devs |
| 2026-04-06 | MCP Server — Fixi como servicio | Puro upsell. Elkin pidió repo analizable, NO servicio hosteado |
| 2026-04-06 | A2A Protocol (Agent-to-Agent) | Puro upsell. Zero demand signal |
| 2026-04-06 | Demo público con /status y /verify/:id | Presupone hosting. No es lo que Elkin pidió |
| 2026-04-06 | Self-dogfooding / Auto-healing | Narrativa cool pero no crítica. Fase 4 post-contrato |
| 2026-04-06 | Mission Control tracking específico (tasks.json, inbox) | HQ-internal. Confunde al cliente. Abstraer como "destinos configurables" |
| 2026-04-06 | Regression test generation | Impresivo pero no pedido. Roadmap bullet |
| 2026-04-06 | Dry-run mode | Nice-to-have, no demo-crítico |

---

## Notas de decisiones

**Wiki links en formato dual** (decisión 2026-04-06): los docs internos (`PLAN.md`, `SPEC.md`, `BACKLOG.md`, `skill/*`) mantienen `[[wiki links]]` porque viven en Obsidian Vault. Los docs client-facing (`README.md`, `README.es.md`, `CLIENT-FACING.md`, `diagrams.md`) usan links estándar `[texto](ruta.md)` para renderizar correctamente en GitHub.

**Demo repo separado** (decisión 2026-04-06): `fixi-demo-dotnet` será repo independiente, NO subdirectorio de fixi. Razón: Safety Gate de Fixi verifica que no operamos sobre nosotros mismos. Mezclarlos viola el mental model.

**Azure DevOps antes que Linear/Jira** (decisión 2026-04-06): GlobalMVM es 99% Azure. GH + ADO cubre el demo completo. Linear/Jira se harán post-contrato si hay demanda real.

**No hostear nada en Sprint 1** (decisión 2026-04-06): Elkin pidió "repo que ellos puedan analizar". Es read-the-repo deliverable, NO service-they-log-into. Baja la barra dramáticamente: no MCP Server, no /status público, solo un repo cloneable con evidencia.
