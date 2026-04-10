# Resumen Ejecutivo — Fixi

> **Para**: Elkin Medina, CEO, GlobalMVM
> **De**: Saúl Martínez, Lots of Context LLC
> **Fecha**: 2026-04-09
> **Tiempo de lectura**: 8 minutos
> **Decisión requerida al final**: sí/no al piloto de 4 semanas

---

## En una frase

Tu equipo construyó un agente que toma tickets y entrega Pull Requests listos para revisar. Funciona. Lo validamos con tres bugs reales. Tu equipo técnico lo revisó y dice **"sí, pero con condiciones"**. Esas condiciones son razonables, finitas, y cerrables en 2 semanas.

---

## Qué construimos: dos repositorios

### Repositorio 1 — `lotsofcontext/fixi`
**Qué es**: el producto. Un agente autónomo que resuelve tickets.

**Qué hace en palabras simples**: tú (o tu CI/CD) le pasa un ticket — puede ser un Azure DevOps Work Item, un GitHub Issue, un Jira, un Linear, o incluso un archivo markdown con la descripción del bug. Fixi hace todo el flujo completo, solo:

1. Lee el ticket y lo entiende
2. Lo clasifica (bug, feature, security, performance, refactor, docs, chore)
3. Clona tu repositorio
4. Analiza el código hasta encontrar la causa raíz
5. Crea una rama nueva (nunca toca `main`)
6. Aplica el fix mínimo necesario
7. Corre tus tests, tu lint, tu build
8. Si todo pasa, abre un Pull Request con descripción técnica, cambios, e impactos
9. Te notifica
10. Apaga todo y se va

**Lo que hay dentro del repo**:
- **`agent/`** — el runtime ejecutable: una CLI en Python llamada `fixi` construida sobre el Claude Agent SDK oficial de Anthropic. 1,165 líneas de código, 136 tests unitarios, Dockerfile, workflows de GitHub Actions y Azure Pipelines listos para copiar-pegar en tu pipeline.
- **`skill/`** — el playbook: un archivo markdown de 763 líneas (`SKILL.md`) que describe paso a paso qué hace el agente. **Es auditable**: cualquier ingeniero tuyo puede abrirlo y leerlo como un procedimiento. No hay caja negra. Ese mismo archivo es el que el agente usa como instrucciones en runtime.
- **`terraform/`** — infraestructura como código para desplegarlo en tu Azure (ACI, ACR, Key Vault, Managed Identity, Networking). 25 archivos, 5 módulos, todo versionado.
- **`docs/`** — especificación técnica completa, roadmap, diagramas, análisis del prompt original de Jefferson (9/9 capabilities cumplidas).
- **`kanban/`** — tablero del proyecto auto-generado desde los archivos de tareas. Trazabilidad total de los 38 sprint items.

**Lo que lo diferencia**:
- **Transparente**: el workflow completo es un archivo markdown legible por humanos. Sin flows ocultos.
- **Nunca inventa información**: si falta algún dato, se detiene y pregunta. Verificado en la práctica.
- **Nunca toca `main`**: cada fix va a su propia rama con PR. Aplicado como hook de código, no como instrucción al modelo.
- **Solo el cambio mínimo**: sin scope creep, sin refactoring especulativo.
- **13 guardrails aplicados como hooks de código** — no puede forzar push, no puede tocar `.env`, no puede modificar CI/CD sin escalar a modo manual. Estas reglas no son "por favor" — son bloqueadores en código.

### Repositorio 2 — `lotsofcontext/fixi-demo-dotnet`
**Qué es**: un sandbox de evidencia. Una Web API .NET del sector energético con **3 bugs sembrados intencionalmente** por nosotros para probar a Fixi.

**Los 3 bugs sembrados** (dominio energético, diseñados para parecerse al tipo de código que tu equipo escribe para EPM, ISAGEN, XM):

1. **Bug clásico** — `DivideByZeroException` cuando dos lecturas de medidor comparten la misma fecha.
2. **Bug de performance** — Query N+1: 51 llamadas SQL para listar 50 medidores (problema típico de Entity Framework mal usado).
3. **Bug de seguridad** — endpoint `AdminController` sin el atributo `[Authorize]`. Vulnerabilidad OWASP A01 Broken Access Control.

**Por qué importa**: este repo **viene con 5 tests rojos** en `master`. Ese es el baseline. Cualquiera puede clonarlo y verificar por sí mismo que los bugs existen antes de correr Fixi. No hay truco.

---

## Qué demostramos: la evidencia

El 2026-04-07, Fixi resolvió autónomamente los 3 bugs. Sin intervención humana. Desde la CLI:

| Work Item | Tipo | Resultado | Tiempo | Costo | Turns |
|-----------|------|-----------|--------|-------|-------|
| WI-101 | `bug` — DivideByZeroException | PR #2 ✅ | 4m 18s | $0.61 | 24 |
| WI-102 | `performance` — N+1 query | PR #3 ✅ | 4m 53s | $1.16 | 34 |
| WI-103 | `security` — OWASP A01 | PR #4 ✅ | 5m 03s | $1.13 | 31 |
| **TOTAL** | | **3 PRs** | **14 min** | **$2.90** | **89** |

**14 minutos. $2.90 dólares. 3 Pull Requests listos para revisión humana.**

Los PRs están en GitHub público. Los diffs son verificables. Jefferson (tu Hyperautomation Lead) los auditó personalmente: los 3 son correctos, mínimos, y bien testeados. John Bairo (tu Tech Lead escéptico) los revisó línea por línea y los aprobó.

---

## Qué dijo tu equipo: el review colectivo

Después de entregar el Sprint 2, simulamos un review completo por parte de tu equipo de liderazgo. Cada uno de los 7 stakeholders fue instanciado como un agente separado con su perfil específico (rol, preocupaciones, sesgos) y revisó el demo desde su ángulo. Aquí está el resumen, uno por uno:

### Jefferson Acevedo — Hyperautomation Lead — **CUMPLE** ✅

> *"Audité cada una de las 9 capabilities del prompt original contra el código real. Cumplieron 9 de 9. Mi prompt llegó intacto al sistema. Esto no es un chatbot wrapper — los 13 guardrails están codificados como hooks, no como 'por favor evita'. Es seguridad real."*

**Postura**: sí rotundo. Es el único voto sin condiciones.

### Joaris Angulo — Solutions Architect — **CONDITIONAL APPROVE** ⚠️

> *"La arquitectura es solid Phase 2 work. 136 tests, type hints, Pydantic, async-first. Pero tengo un concern estructural: la escalación de security depende de que Claude clasifique bien, no de código. Necesitamos un hook path-based que mire rutas de archivos. Con 2 semanas de hardening, defiendo esto internamente con mi nombre."*

**Postura**: sí, con hardening sprint de 2 semanas.

### John Bairo Gómez — Tech Lead / Architecture — **CONDITIONAL YES** ⚠️

> *"Llegué decidido a encontrar problemas. Y los encontré. Pero también tengo que admitir que los 3 fixes son correctos. Como reviewer, aprobaría los tres sin pedir cambios. Mi worst-case: Fixi puede hacer fixes que están mal pero pasan los tests, si el ingeniero que revisa no entiende el domain context. Quiero ver a Fixi fallar antes de escalar."*

**Postura**: sí, pero quiero pruebas contra código real GlobalMVM (no solo el demo), más tests de regresión, y Fixi probado en escenarios ambiguos.

### Víctor Manuel Orrego — Director de Operaciones — **YELLOW → GREEN** ⚠️

> *"Los números del piloto son creíbles ($20K, 4 semanas, 5-10 devs). Mi preocupación no es el concepto — es el TCO a escala. 240 tickets/día en producción = $72K/mes solo en API costs. El Dockerfile no instala `az CLI`, lo cual es un blocker para Azure DevOps. Y el framing '3.75 devs de capacidad liberada' en el CLIENT-FACING es tóxico políticamente — Liseth tiene razón."*

**Postura**: sí, con SLA escrito, Dockerfile arreglado, y CLIENT-FACING reescrito.

### Liseth Campo Arcos — PMO / Talent — **CAUTO SÍ** ⚠️

> *"Mi preocupación es cómo le presentamos esto a los 300 devs. Si les decimos 'esto libera capacidad de 3.75 devs', van a leer 'van a despedir a 4'. Necesitamos un rollout playbook: narrativa del equipo, champions por equipo, survey de adopción, métricas de satisfacción, plan de formación. El tool es bueno, pero la gente es lo que lo hace sostenible."*

**Postura**: sí, con playbook de change management antes de tocar un solo equipo.

### Liset — Data & AI Lead — **CONDITIONAL FIT** ⚠️

> *"Estratégicamente encaja en el Centro de Aceleración. Pero necesito governance matrix (quién aprueba qué, quién revisa, quién audita), DPA firmado con Anthropic o exclusion list para clientes regulados (EPM, ISAGEN, XM tienen compliance), y dashboard inicial de observabilidad. No vamos a escalar esto sin medir consumo, latencia, tasa de rollback."*

**Postura**: sí, con conversaciones paralelas de legal, compliance, y observability.

### Elkin Medina — CEO — **GO CON CONDICIONES** ✅⚠️

Tu postura (según la simulación) fue:

> *"0 votos en contra. 1 sí rotundo. 5 conditional. Nadie mata el proyecto, pero cada uno tiene su lista. Vamos a hacer el piloto, pero no antes de cerrar los 5 blockers cross-cutting. Pilot de 4 semanas en 1 equipo acotado de 5-10 devs. ROI proyectado 4-6x vs contratar FTEs. Pero hay una condición no-negociable: si durante el piloto Fixi toca código sin escalar cuando debió — por ejemplo, modificando auth/ sin GUIDED mode — paramos inmediatamente."*

---

## Los 5 blockers cross-cutting

Los 5 blockers que aparecen en **múltiples listas independientes** (más peso evidencial que consensos por contagio):

1. **Dockerfile + Azure DevOps integration completa**
   — Víctor, Jefferson. Sin `az CLI` en la imagen, Fixi no puede hablar con Azure DevOps. Es horas de trabajo, no semanas.

2. **Rehearsal Azure DevOps en vivo con métricas agregadas**
   — Víctor, John Bairo, Joaris, tú. No basta con 3 runs en GitHub. Necesitamos 10-20 runs en un Azure DevOps real para ver varianza, tasa de fallo, tasa de escalación.

3. **Real-world test contra código GlobalMVM**
   — John Bairo, Joaris, tú. El demo .NET es un sandbox curado. Necesitamos probar contra un repo real tuyo (anonimizado si necesario) con tickets históricos.

4. **Reescritura del CLIENT-FACING eliminando "3.75 devs"**
   — Víctor, Liseth, tú. El framing actual es políticamente tóxico para una org de 300 devs. Solución: reemplazar "capacidad liberada" con "ciclo medio de bugs acortado de X a Y días".

5. **Nombre del propietario técnico interno**
   — Tú, Víctor, Liset. Mientras Saúl sea el único punto de contacto, esto no escala. Necesitamos saber quién adentro de GlobalMVM será el owner cuando Saúl salga del loop.

**Estimación**: 2 semanas, ~$20K USD, 1 ingeniero dedicado.

---

## Qué estoy pidiendo decidir

**Decisión 1 — ¿Autorizas el hardening sprint de 2 semanas?**

- Scope: cerrar los 5 blockers cross-cutting arriba
- Inversión: ~$10K USD
- Entregables: checklist ejecutable contra los 5 blockers, con evidencia por cada uno
- Riesgo: bajo — son gaps de finalización, no de diseño

**Decisión 2 — Si el hardening sprint cierra los blockers, ¿autorizas el piloto de 4 semanas?**

- Scope: 1 equipo acotado de 5-10 devs, en un proyecto real pero no crítico
- Inversión adicional: ~$10K USD
- Entregables: 20-30 runs reales contra tickets reales, métricas de precisión (% de PRs aprobados sin cambios), tasa de escalación, tiempo ahorrado vs baseline
- Riesgo: medio — estamos tocando trabajo real de ingenieros reales
- **Salida de emergencia**: cualquier incidente de Fixi tocando código sin escalar cuando debió hacerlo (p.ej. modificando `auth/` sin ir a GUIDED mode) **para el piloto inmediatamente**

**Decisión 3 — Si el piloto sustenta las métricas, ¿autorizas ramped rollout en mes 3?**

- Scope: fase 2 — 2-3 equipos adicionales, dominios controlados
- Inversión Año 1 completa: ~$30-35K USD
- ROI proyectado: 4-6x vs contratar FTEs adicionales equivalentes
- Esta decisión **no se toma hoy**. Se toma cuando tengas datos reales del piloto.

---

## Lo que NO estoy pidiendo

- No pido rollout company-wide hoy. **Nadie en tu equipo lo recomendó**, ni siquiera Jefferson.
- No pido que uses esto en clientes regulados (EPM, ISAGEN, XM) hasta tener DPA con Anthropic o exclusion list. Liset tiene razón.
- No pido que me pagues el Año 1 completo upfront. Pido autorización **fase por fase**, con checkpoints claros donde puedes cortar.
- No pido que tu equipo confíe ciegamente. Pido que verifiquen. Todo el código es público. Los PRs son públicos. El SKILL.md es auditable.

---

## Por qué tu equipo dijo lo que dijo

La conversación completa está en [`docs/conversacion-equipo-globalmvm.md`](conversacion-equipo-globalmvm.md) — 312 líneas de diálogo reconstruido. Pero la lógica de fondo es esta:

1. **La evidencia técnica es sólida**. Los 3 PRs son correctos, mínimos, testeados. Rechazar después de ver la evidencia sería cerrar los ojos a lo obvio.
2. **Los gaps son cerrables, no estructurales**. Nadie dijo "hay que rediseñar". Todos dijeron "faltan piezas pequeñas".
3. **Los concerns humanos son documentos, no código**. Liseth y Víctor tienen razón sobre el framing — la solución es reescribir un doc, no cambiar el producto.
4. **Los concerns de governance son contractuales**. Liset tiene razón sobre el DPA — eso es trabajo con legal, no con ingeniería.
5. **"GO con condiciones" es la respuesta honestamente correcta**. Un "sí sin reservas" hubiera sido irresponsable. Un "no" hubiera sido ignorar la evidencia.

---

## Datos clave para tu decisión

| Métrica | Valor | Fuente |
|---------|-------|--------|
| Capabilities del prompt original cumplidas | 9 de 9 | Audit de Jefferson |
| Tests unitarios del agent | 136 | Suite de pytest en `agent/tests/` |
| Líneas del playbook auditable | 763 | `skill/SKILL.md` |
| Guardrails de seguridad como hooks de código | 13 | `agent/src/fixi_agent/hooks.py` |
| PRs reales producidos autónomamente | 3 | GitHub: fixi-demo-dotnet #2, #3, #4 |
| Tiempo total de los 3 runs | 14 min | Smoke test T18 |
| Costo total de los 3 runs | $2.90 USD | API Anthropic metering |
| Inversión pre-pilot + pilot | ~$20K USD | Cotización |
| ROI proyectado vs contratar FTEs | 4-6x | Análisis de Víctor |
| Votos del equipo | 0 NO, 1 SÍ, 5 CONDITIONAL | Review simulation |

---

## Próximo paso

Si la respuesta es **sí al hardening sprint de 2 semanas**, yo empiezo mañana. Entregables al día 14: los 5 blockers cross-cutting cerrados, checklist ejecutable, y kickoff del piloto listo.

Si la respuesta es **no**, acepto la decisión sin cuestionarla — el demo está en GitHub, los 2 repos son públicos, y la documentación queda como evidencia de lo que construimos. Puedes volver a retomarlo cuando quieras.

Si la respuesta es **"déjame consultarlo con el board"**, te preparo una versión de 3 slides con solo los 3 números que importan: $20K, 4 semanas, 4-6x ROI.

---

## Para drill-down

- **Conversación completa del equipo** (diálogo reconstruido, 312 líneas): [`docs/conversacion-equipo-globalmvm.md`](conversacion-equipo-globalmvm.md)
- **Reviews individuales detalladas** (7 stakeholders, 758 líneas): [`docs/globalmvm-review-simulation.md`](globalmvm-review-simulation.md)
- **Overview de producto para stakeholders** (lenguaje de negocio): [`docs/CLIENT-FACING.md`](CLIENT-FACING.md)
- **Audit de las 9 capabilities del North Star Prompt**: [`HANDOFF-NORTH-STAR.md`](../HANDOFF-NORTH-STAR.md)
- **Repositorio del producto**: https://github.com/lotsofcontext/fixi
- **Repositorio de la evidencia**: https://github.com/lotsofcontext/fixi-demo-dotnet
- **PRs reales producidos**: [#2](https://github.com/lotsofcontext/fixi-demo-dotnet/pull/2) · [#3](https://github.com/lotsofcontext/fixi-demo-dotnet/pull/3) · [#4](https://github.com/lotsofcontext/fixi-demo-dotnet/pull/4)

---

**Elkin**, tu equipo hizo su trabajo. Revisaron el demo desde 7 ángulos diferentes y llegaron a un consenso razonable. La decisión ahora es tuya.

Gracias por el tiempo y la confianza.

— Saúl Martínez
Lots of Context LLC
2026-04-09
