# HANDOFF: North Star Prompt + Audit — Continuar Sprint 2

> **Cómo usar este handoff**: En tu próxima sesión de Claude Code, empieza con:
> *"Lee `HANDOFF-NORTH-STAR.md`, luego `CLAUDE.md`, luego `kanban/BOARD.md`. Después de eso, seguimos con Sprint 2 donde íbamos — próxima tarea: `S2-T02` (instalar claude-agent-sdk)."*
>
> Generado: 2026-04-07 — al final de la sesión donde se capturó el prompt original del ingeniero de GlobalMVM y se hizo audit contra el estado actual del repo.

---

## 1. Qué pasó en la sesión anterior

El usuario (Saúl) compartió el **prompt literal** que dio Jefferson Acevedo (líder de hiperautomatización en GlobalMVM) en la reunión del 2026-04-06. Ese prompt es la especificación cruda del agente que el cliente pidió. Lo promovimos a **North Star** del proyecto:

- Replicado en `CLAUDE.md` sección "North Star Prompt" (se carga en cada sesión).
- Polished en `HANDOFF-FROM-HQ.md` línea 8 (con tildes).
- Guardado en memoria persistente (`project_north_star_prompt.md`).

Luego hicimos un audit del estado actual del repo contra las **9 capabilities no-negociables** que exige el prompt. Este documento es el resultado del audit + la lista de acciones concretas para cerrar los gaps.

---

## 2. El North Star Prompt (texto literal)

> Actúa como un agente de automatización de desarrollo de software encargado de gestionar tickets y requerimientos. Debes conectarte a fuentes de conocimiento disponibles como repositorios de código, sistemas de tickets y documentación técnica para analizar cada solicitud. Clasifica y prioriza el ticket según su tipo (bug, mejora, nueva funcionalidad), valida el código fuente existente relacionado, propone y aplica ajustes siguiendo buenas prácticas de desarrollo y estándares definidos, crea automáticamente una nueva rama con una nomenclatura adecuada, realiza los cambios necesarios en el código, ejecuta validaciones básicas, genera el commit con un mensaje claro y estructurado, y deja creado el Pull Request listo para aprobación incluyendo descripción técnica, cambios realizados y posibles impactos. No debes inventar información, si faltan datos debes indicarlo claramente y detener el flujo.

Las **9 capabilities** destiladas de ese prompt están enumeradas en `CLAUDE.md` — son el checklist contra el cual se audita cualquier decisión de diseño.

---

## 3. Estado actual del proyecto (dónde íbamos)

**Rama**: `feat/sprint-2-agent-pivot`

**Sprint 1** — ✅ **100% cerrado** (17 done, 1 cancelado)
- Demo repo `lotsofcontext/fixi-demo-dotnet` sembrado con 3 bugs (DivideByZero, N+1, Missing [Authorize])
- Work items WI-101/102/103 pre-creados
- Rehearsal GitHub (WI-101) completado con transcript en `docs/demos/run-01-github.md`
- Terraform skeleton en `terraform/`
- CLIENT-FACING.md polished con links a runs y Terraform
- S1-T15 cancelado (rehearsal ADO) — se hace contra el **agent** en S2, no contra el skill

**Sprint 2** — 🔄 **5% — recién arrancado** (1 done, 19 pending)
- ✅ `S2-T01` — agent skeleton creado (`agent/pyproject.toml`, `src/fixi_agent/`, `tests/`, `README.md`)
- 📋 **Próxima tarea**: `S2-T02` — instalar `claude-agent-sdk` + verificar import
- Quedan 19 tareas distribuidas en 4 días: bootstrap+core (D1), guardrails+CLI (D2), containerización+CI/CD (D3), rehearsal+docs (D4)
- Definition of Done: `fixi resolve --work-item <url> --repo <url>` funcional end-to-end contra `fixi-demo-dotnet`, con Dockerfile, GH Actions + Azure Pipelines ejemplos, tests, y `docs/demos/run-03-agent-cli.md` con transcript real

**Pivot estratégico** (commit `d045e6f`): de "Claude Code skill" a "Python agent built on Claude Agent SDK, invocable desde CI/CD". El `SKILL.md` se vuelve el `system_prompt` del agent. Los 13 guardrails se traducen a `PreToolUse` hooks. Ver `docs/planning/SPRINT-2.md` para el plan completo.

---

## 4. Audit: 9 capabilities vs estado actual

| # | Capability del prompt | Cobertura actual | Status |
|---|-----------------------|------------------|--------|
| 1 | Conectarse a fuentes de conocimiento (repos + tickets + **documentación técnica**) | Repos ✅ (cloner.py planned S2-T05). Tickets ✅ (parser GH/ADO/Linear/Jira/free text). Docs técnica ⚠️ (solo lee CLAUDE.md/README.md del target, no hay paso explícito de "load tech docs") | ⚠️ Gap parcial |
| 2 | Clasificar y **priorizar** (bug/mejora/feature) | Clasificación ✅ (7-type taxonomy en `classification.md`). Priorización ⚠️ (existe desempate por tipo pero **no lee priority field** del work item ni asigna urgencia P0/P1/P2) | ⚠️ Gap parcial |
| 3 | Validar código fuente existente relacionado | ✅ SKILL.md Paso 4 "Análisis de causa raíz" con Grep/Glob/Read | ✅ OK |
| 4 | Proponer y aplicar ajustes con buenas prácticas **y estándares definidos** | Buenas prácticas ✅ (prompt general). Estándares definidos ⚠️ (no hay paso explícito de cargar style guides, `.editorconfig`, linter configs, coding standards docs del repo target) | ⚠️ Gap parcial |
| 5 | Crear rama con nomenclatura adecuada | ✅ SKILL.md Paso 6 con prefixes del classification (`fix/`, `feat/`, `security/`, etc.) | ✅ OK |
| 6 | Ejecutar **validaciones básicas** (plural) | Tests ✅ (SKILL.md Paso 7). Lint ⚠️ (no garantizado). Build ⚠️ (no garantizado). El plural "validaciones" del prompt sugiere que se esperan los 3. | ⚠️ Gap alto |
| 7 | Commit con mensaje claro y estructurado | ✅ Conventional commits en SKILL.md Paso 8 | ✅ OK |
| 8 | PR listo con **descripción técnica + cambios realizados + posibles impactos** | ⚠️ Verificar que el template del PR del skill incluya explícitamente las 3 secciones. "Posibles impactos" probablemente falta como sección nombrada. | ⚠️ Gap probable |
| 9 | Halt-and-ask — nunca inventar | ✅ Safety Gate (Paso 0) + regla general "NEVER invent information" en CLAUDE.md | ✅ OK |

**Resumen**:
- ✅ 5 de 9 plenamente cubiertas (Cap 3, 5, 7, 9 + arquitectura)
- ⚠️ 4 de 9 con gaps parciales (Cap 1, 2, 4, 6, 8 → cuenta 5 gaps, algunos agrupados)
- 🚫 0 de 9 completamente ausentes — no hay que construir nada desde cero, solo **fortalecer** lo existente

---

## 5. Gaps concretos a cerrar (en orden de impacto)

### Gap A — Validaciones básicas en plural (Cap 6) · **IMPACTO ALTO**
**Qué**: el skill solo garantiza correr tests. El prompt dice "validaciones básicas" en plural — el cliente va a esperar mínimo **tests + lint + build**.

**Dónde cerrar**:
- `skill/SKILL.md` Paso 7: cambiar "Ejecutar tests" por "Ejecutar validaciones básicas" con auto-detección de:
  - Tests (ya existe)
  - Lint (eslint, ruff, pylint, dotnet format, golangci-lint, rubocop) — detectar por presencia de config
  - Build (npm run build, dotnet build, mvn compile, cargo build, go build) — detectar por archivos de proyecto
- `agent/src/fixi_agent/hooks.py` o nuevo módulo `validations.py`: implementar detector + runner
- Si el target repo no tiene lint/build config, **documentarlo en el PR**, no fallar

### Gap B — PR con sección "posibles impactos" (Cap 8) · **IMPACTO ALTO**
**Qué**: el prompt exige explícitamente que el PR incluya "descripción técnica, cambios realizados **y posibles impactos**". Hay que verificar que el template del PR del skill tenga las 3 secciones.

**Dónde cerrar**:
- `skill/SKILL.md` Paso 9: verificar el PR description template. Debe tener 3 secciones nombradas:
  1. **Descripción técnica** (qué es el bug/feature, causa raíz)
  2. **Cambios realizados** (archivos modificados, por qué)
  3. **Posibles impactos** (áreas afectadas, riesgos, breaking changes, qué probar)
- Si alguna falta, agregar al template + actualizar `docs/demos/run-01-github.md` con un ejemplo del nuevo formato

### Gap C — Estándares definidos del repo target (Cap 4) · **IMPACTO MEDIO**
**Qué**: el skill lee `CLAUDE.md` del target, pero no explícitamente busca `.editorconfig`, linter configs, style guides en `docs/`, o convenciones del repo. El cliente tiene estándares internos que esperan que el agente respete.

**Dónde cerrar**:
- `skill/SKILL.md` Paso 0 o Paso 3: añadir sub-step "Cargar estándares del repo":
  - `CLAUDE.md`, `CONTRIBUTING.md`, `STYLE.md`, `.editorconfig`
  - Configs de linter detectadas
  - Convenciones en `docs/` si existen
- Incluir lo encontrado en el system context para el agent

### Gap D — Priority field del work item (Cap 2) · **IMPACTO MEDIO**
**Qué**: Azure DevOps work items tienen campo `Microsoft.VSTS.Common.Priority`. GitHub Issues tienen labels como `priority:high`. El skill no los lee ni los usa.

**Dónde cerrar**:
- `agent/src/fixi_agent/parser.py` (S2-T04): extraer `priority` como campo normalizado de la estructura del work item
- Incluir priority en el análisis y en el PR description
- No cambia el flujo — es informativo

### Gap E — Documentación técnica como fuente explícita (Cap 1) · **IMPACTO BAJO-MEDIO**
**Qué**: el prompt menciona "documentación técnica" como fuente de conocimiento explícita, al mismo nivel que repos y tickets. Actualmente es implícito (el agente puede leer con Read/Glob pero no hay garantía).

**Dónde cerrar**:
- `skill/SKILL.md` Paso 4 (análisis): añadir sub-step "Buscar documentación técnica relacionada":
  - `README.md`, `docs/**/*.md`, wikis si están clonados
  - Comentarios en el código cercano al issue
- Opcional: detectar si el repo tiene una carpeta `docs/` o `wiki/` y priorizarla

---

## 6. Cómo integrar los fixes al Sprint 2 (sin romper el plan)

Los gaps se pueden cerrar **dentro de las tareas existentes de Sprint 2**, no necesitan tareas nuevas. Propuesta de integración:

| Gap | Integrar en | Cómo |
|-----|-------------|------|
| A (validaciones plural) | **S2-T06 (orchestrator)** + **S2-T08 (guardrail hooks)** | Añadir a SKILL.md Paso 7 que el agent debe auto-detectar lint/build además de tests. Opcionalmente crear un módulo `validations.py` en el agent. |
| B (impactos en PR) | **S2-T03 (prompts loader)** | Al cargar SKILL.md como system_prompt, primero **actualizar SKILL.md Paso 9** con el template de PR de 3 secciones. El loader ya cargará la versión actualizada. |
| C (estándares del repo) | **S2-T06 (orchestrator)** | Antes de hacer `query()`, inyectar en el contexto inicial los contenidos de `CLAUDE.md`, `CONTRIBUTING.md`, `.editorconfig` si existen en el target repo. |
| D (priority field) | **S2-T04 (parser)** | Añadir campo `priority` a la estructura normalizada del work item. Extraerlo de ADO `fields["Microsoft.VSTS.Common.Priority"]` y GH labels `priority:*`. |
| E (docs técnica explícita) | **S2-T03 (prompts loader)** | Añadir a SKILL.md Paso 4 un sub-step "buscar docs técnica" antes de generar tasks nuevas. |

**Orden recomendado**:
1. **Primero** (antes de S2-T03): actualizar `skill/SKILL.md` con los cambios de Gaps A, B, C, E. Esto es un commit de "fortalecimiento del SKILL.md contra el North Star Prompt" que no rompe nada.
2. **Luego** seguir con S2-T02..S2-T20 normal, porque el loader de prompts (S2-T03) ya cargará el SKILL.md fortalecido.
3. **S2-T04 (parser)** añade el campo `priority` (Gap D).
4. **S2-T06 (orchestrator)** inyecta estándares del repo (Gap C).

Estimado adicional para cerrar los gaps: **~2h** distribuidas sobre las tareas existentes. No mueve el Definition of Done del Sprint 2.

---

## 7. Next actions concretas para la próxima sesión

En orden de ejecución:

1. **Leer**: `CLAUDE.md` (North Star Prompt está arriba del todo), `kanban/BOARD.md`, `docs/planning/SPRINT-2.md` (plan completo del sprint), `skill/SKILL.md` (el workflow que se va a fortalecer).

2. **Preguntar a Saúl**: *"¿Cerramos los 5 gaps del audit primero (estimado ~2h, commit de fortalecimiento de SKILL.md + ajustes a S2-T04/T06), o arrancamos directo con S2-T02 y vamos cerrando gaps on-the-fly cuando toque cada tarea?"*

3. **Si Saúl dice "cierra los gaps primero"**:
   - Crear branch `feat/sprint-2-north-star-fortify` (o quedarse en `feat/sprint-2-agent-pivot`)
   - Editar `skill/SKILL.md`: Paso 7 (validaciones plural), Paso 9 (PR 3 secciones), Paso 4 (docs técnica explícita), Paso 0/3 (estándares del repo)
   - Actualizar `docs/demos/run-01-github.md` si el template de PR cambia (para consistencia)
   - Commit: `refactor(skill): fortify workflow against GlobalMVM north star prompt`
   - Luego empezar S2-T02 normalmente

4. **Si Saúl dice "integra on-the-fly"**:
   - Arrancar S2-T02 (instalar `claude-agent-sdk`) siguiendo el kanban workflow mandatorio (editar task file → in-progress → `python kanban/update_board.py` → commit)
   - Tener a la vista los 5 gaps del audit y cerrarlos cuando caiga la tarea relacionada (ver tabla §6)

5. **Kanban workflow** (mandatorio, ver `CLAUDE.md`): cada tarea de Sprint 2 debe actualizar el task file en `kanban/tasks/`, correr `python kanban/update_board.py`, y commit del task file + BOARD + .state.json + history.

6. **No olvidar**:
   - `NEVER` commit a `main`
   - `NEVER` invent information — halt and ask
   - Commits granulares (un commit por unidad lógica)
   - `python` en Windows (no `python3`)
   - Docs internos con `[[wiki links]]`, client-facing con markdown estándar

---

## 8. Referencias rápidas

| Archivo | Contenido |
|---------|-----------|
| `CLAUDE.md` | Reglas del proyecto + **North Star Prompt arriba del todo** + 9 capabilities |
| `HANDOFF-FROM-HQ.md` | Context original de GlobalMVM (reunión 2026-04-06) |
| `docs/planning/SPRINT-2.md` | Plan completo del Sprint 2 (pivot a Python agent) |
| `docs/planning/BACKLOG.md` | Backlog priorizado |
| `kanban/BOARD.md` | Board auto-generado — NO editar a mano |
| `kanban/tasks/S2-*.md` | Task files individuales — source of truth |
| `skill/SKILL.md` | 10-step workflow (será fortalecido) |
| `skill/references/classification.md` | 7-type taxonomy |
| `skill/references/guardrails.md` | 13 safety rules |
| `agent/` | Python agent scaffold (S2-T01 done) |
| `agent/pyproject.toml` | Package config |
| `docs/SPEC.md` | Full technical spec |
| `docs/diagrams.md` | 5 Mermaid diagrams |
| `docs/CLIENT-FACING.md` | Doc para GlobalMVM |

---

**FIN DEL HANDOFF**. Saúl, este doc es self-contained — puedes pegar "lee HANDOFF-NORTH-STAR.md" en la próxima sesión y Claude tendrá todo el contexto para retomar.
