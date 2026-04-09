# GlobalMVM Stakeholder Review Simulation — Fixi Demo

> **Documento interno de preparación para la reunión de follow-up con GlobalMVM.**
>
> Fecha: 2026-04-09 · Versión: 1.0
>
> **Propósito**: Anticipar la reacción de cada stakeholder clave de GlobalMVM al demo de Fixi (agent Python + CLI + Sprint 2 completo) antes de la reunión real. Identificar blockers, conflictos entre stakeholders, y preparar respuestas concretas.

---

## Metodología

Se simularon **7 agentes en paralelo**, cada uno con un persona customizado al perfil real del stakeholder (extraído del handoff de la reunión del 2026-04-06). Cada agente:

1. Recibió contexto sobre su rol, background, y concerns específicos
2. Leyó un subset distinto de archivos del repo (según su ángulo de evaluación)
3. Inspeccionó los 4 PRs reales en `lotsofcontext/fixi-demo-dotnet` via `gh pr view/diff`
4. Dio feedback estructurado con: primera impresión, strengths, concerns, preguntas, verdict, y next steps

**Los 7 agentes operaron con instrucción explícita de ser críticos**, no rubber-stamp. Sus outputs son honestas simulaciones de lo que un stakeholder real con ese perfil diría.

**Limitación**: esto es una simulación basada en los perfiles del handoff. La reunión real puede tener sorpresas. Pero identifica con alta confianza **los patrones de concerns** que van a aparecer.

---

## Veredictos al vistazo

| # | Stakeholder | Rol | Verdict | Convicción |
|---|-------------|-----|---------|------------|
| 1 | **Jefferson Acevedo** | Hyperautomation Lead | ✅ **CUMPLE 9/9** | Más positivo — *"ejecutaron mi prompt literal sin interpretaciones"* |
| 2 | **Liseth Campo** | PMO / Talent | 🟡 **CAUTO SÍ** | Pilot acotado — pide playbook de adopción + career path juniors |
| 3 | **Elkin Medina** | CEO | 🟡 **GO with conditions** | Pilot en 4 semanas — necesita owner interno + rehearsal ADO + reframing |
| 4 | **Joaris Angulo** | Solutions Architect (Champion) | 🟡 **CONDITIONAL** | 2-week hardening sprint — defenderá internamente con caveats |
| 5 | **Víctor Orrego** | Director of Operations | 🟡 **YELLOW → GREEN con tasks** | TCO viable — faltan SLA, Dockerfile fix, audit trail |
| 6 | **John Bairo Gómez** | Tech Lead / Architecture | 🟡 **CONDITIONAL YES** | 4-week pilot con 3 condiciones — diffs técnicamente aprobados |
| 7 | **Liset** | Data & AI Lead | 🟡 **CONDITIONAL FIT** | DPA + governance matrix + observability antes de portfolio |

**Lectura del resultado**:
- **0 × NO rotundo** — nadie rechaza el demo
- **1 × YES sin peros** — Jefferson (quien escribió el prompt original)
- **6 × CONDITIONAL** — todos los demás piden entregables específicos antes de pilot/rollout
- **7/7 están alineados en "pilot acotado, no rollout inmediato"**

---

## Full Reviews (ordenados por nivel de entusiasmo)

### 1️⃣ Jefferson Acevedo — Hyperautomation Lead · ✅ CUMPLE (9/9)

**Quote clave**: *"Fixi no es un chatbot wrapper. Los guardrails están codificados como hooks PreToolUse, no como 'por favor evita'. Ejecutó mi especificación literal sin interpretaciones creativas."*

#### Compliance con su prompt (las 9 capabilities)

| # | Capability | Status |
|---|------------|--------|
| 1 | Conectarse a fuentes (repos + tickets + docs técnica) | ✅ |
| 2 | Clasificar Y priorizar | ✅ |
| 3 | Validar código existente | ✅ |
| 4 | Aplicar buenas prácticas + estándares definidos | ✅ |
| 5 | Crear rama con nomenclatura | ✅ |
| 6 | Validaciones básicas **en plural** (tests + lint + build) | ✅ |
| 7 | Commit estructurado | ✅ |
| 8 | PR con **3 secciones nombradas** | ✅ |
| 9 | Halt-and-ask | ✅ |

#### Comparación con Power Platform (su framework de referencia)

- **Costo**: $0.61/ticket vs. licencias por usuario + premium connectors
- **Flexibilidad**: cualquier repo (GitHub, Azure Repos, GitLab) vs. ecosistema Microsoft only
- **Auditabilidad**: SKILL.md es texto plano versionado, inspectable vs. flows visuales black-box
- **Integración CI/CD**: nativa en GitHub Actions + Azure Pipelines vs. webhook workflows separados

#### Preguntas clave que hará
1. ¿Cómo escala a 50 tickets paralelos?
2. ¿Qué pasa si el fix introduce un test rojo nuevo? (retry, rollback, halt?)
3. Si el cliente no tiene CLAUDE.md, ¿pivotea a defaults o requiere que exista?
4. ¿Cómo se configura autenticación para escribir a ACTIVO.md y Mission Control?
5. ¿Un security issue de 1 solo archivo también fuerza GUIDED?

#### Qué necesita antes de probarlo en proyecto real
- Credenciales `az` CLI + PAT configurados
- Configuración de tracking destino (ACTIVO.md spec en consultoria-x)
- Test contra WI-103 (security) primero — quiere ver el escalado a GUIDED en vivo
- Documentación de cómo personalizar SKILL.md para GlobalMVM

---

### 2️⃣ Liseth Campo Arcos — PMO / Talent · 🟡 CAUTO SÍ

**Quote clave**: *"El diseño técnico es SÓLIDO. El documento respeta developers. PERO falta toda la estrategia HUMANA de adopción. El riesgo de displacement anxiety es REAL en una org de 300+ devs con 2.8 años tenure promedio."*

#### Lo que funciona (pro-human)
- **"NO reemplaza desarrolladores — multiplica su capacidad"** (framing correcto)
- **Humans in the loop estructural**: 5 escaladores automáticos fuerzan GUIDED (security, CI/CD, >15 files, DB migrations, causa raíz ambigua)
- **Respeto por juicio de seniors**: Paso 4 espera aprobación del humano antes de implementar
- **Cero mención de displacement**: el tono es "review completos en lugar de debuggear desde cero"

#### Lo que preocupa (blindspots humanos)

**Blindspot #1**: **Silencio total en change management**. No hay rollout plan, no hay champions, no hay training packet. "El doc asume que si publicas el repo, los devs la usan. Eso es un riesgo."

**Blindspot #2**: **Career path de juniors undefined**. Los juniors aprenden debugueando bugs chiquitos. Si Fixi los hace, ¿cuál es la escalera? El documento no lo dice explícitamente — aunque el skill SÍ los expone a root cause analysis + code review (skill más avanzado).

**Blindspot #3**: **Métricas peligrosas**. La frase *"equipo de 10 produce como equipo de 13-14"* **SUENA a "podríamos reducir headcount"**. Si Elkin la dice en town hall sin contexto, los devs panic.

**Blindspot #4**: **Autonomía erosionable**. FULL_AUTO existe. Bajo presión de sprints cortos, un manager lo activa sin pensar.

#### Recomendaciones concretas para el CLIENT-FACING.md

1. Eliminar el framing "3.75 devs de capacidad" — reescribir como "los devs pasan 30h/semana MÁS en architecture, mentoring, testing, innovation"
2. Agregar sección "Para los desarrolladores: cómo Fixi cambia tu día"
3. Agregar sección "Impacto en career paths para juniors" con narrativa explícita de PR review como skill
4. Agregar FAQs: "¿Esto significa que voy a perder mi empleo?"

#### Su rollout plan propuesto

| Fase | Duración | Reach | Success Criteria |
|------|----------|-------|------------------|
| Piloto cerrado | Semanas 1-2 | 1 equipo de 5-8 devs + 1 tech lead champion | Feedback, ajustes |
| Early adopters | Semanas 3-4 | 3-4 equipos | Case studies + learnings |
| Ramped | Semanas 5-8 | 50-100 devs | Self-serve con support tier |
| Mature | Semana 9+ | 300 devs | Governance clara, CONFIRM_PLAN habilitado |

#### Mensaje que daría en town hall (propuesta)
> *"Fixi es un asistente que automatiza parte del ciclo de resolución de bugs. Pero aquí está lo importante: Fixi NO despliega código. Fixi NO reemplaza reviews. Fixi crea pull requests listos para que ustedes los revisen, critiquen, y aprueben. Los juniors van a aprender a revisar código crítico más rápido. Los seniors van a tener tiempo para mentoring, arquitectura, y trabajo estratégico. No vamos a despedir a nadie. Vamos a hacer que 300 ingenieros produzcan como 350. Y eso significa que crecemos juntos."*

---

### 3️⃣ Elkin Medina — CEO · 🟡 GO with conditions

**Quote clave**: *"Veo un PoC sólido. Pero es una demo, no evidencia de producción. Me piden dinero basándose en un solo rehearsal contra un repo sembrado. Eso no me convence todavía."*

#### Lo que le convence (business angle)
- **Safety-first architecture**: nunca mergea sin review, siempre rama aislada — *"crítico para CMMI e ISO 9001 que llevamos 30 años construyendo"*
- **Stack-agnostic**: .NET, Java, Python, Angular — no requiere reconstrucción por cliente
- **ROI calculable**: 60 min ahorro/ticket × 30 tickets/semana × 10 devs = 30 horas/semana = 3.75 devs de capacidad recuperada. Pay-back <3 meses
- **Capacidad humana liberada a trabajo de valor** (architecture, mentoring, relaciones)
- **Joaris respaldando la decisión técnica** — *"si mi champion técnico dice que la arquitectura es sólida, me importa"*

#### Lo que le preocupa (business risk)
1. **Un solo rehearsal contra un repo sembrado no es evidencia** — necesita N runs contra código real
2. **Azure DevOps no probado en vivo** — 99% de GlobalMVM corre Azure DevOps. Hasta no verlo con PR linkeado a Work Item real, "para mí no existe"
3. **Mantenimiento cuando Saúl no esté** — 925 LOC de Python + 136 tests + Terraform + 3 niveles de autonomía + 13 guardrails. *"¿Mi equipo puede sostener eso?"*
4. **No hay memoria entre ejecuciones** — Fixi es stateless. Si rechazamos un PR hoy, mañana hace lo mismo. Sin feedback loop, no aprende
5. **Framing político tóxico para senior devs** — *"equipo de 10 produce como 13-14" es amenazante*
6. **Métricas de tasa de éxito inexistentes** — si la tasa de PRs aceptados sin cambios cae de 100% a 60%, el pay-back se estira de 2.8 a 5 meses

#### 5 preguntas directas que hará
1. ¿Cuándo tenemos el rehearsal de Azure DevOps vivo con métricas agregadas (media, min, max de tiempo y costo)?
2. ¿Cuándo corro Fixi contra un pedazo real de EnergySuite, no contra el demo?
3. **¿Quién mantiene Fixi cuando ustedes se van?** Necesito nombre del propietario técnico en mi equipo
4. ¿Fixi aprende de los PRs rechazados/revertidos?
5. ¿Cuál es el playbook cuando un dev senior me dice "no confío"?

#### Su pitch al board (ensayado)
> *"Agente que automatiza ticket → PR. Demo funcionó en 4 minutos por $0.61. Si tasa de éxito >80%, recuperamos 30 horas/semana en un equipo de 10 = 3.75 devs no contratados. Nunca mergea sin humano, siempre rama aislada. Piloto de 4 semanas contra un equipo chico real. Inversión: ~$5k setup + $2k/mes. Retorno mes 3: $1.6k neto. Apuesto a que sí."*

#### Qué necesita antes de mover adelante
- Rehearsal Azure DevOps documentado en video/transcript
- Métricas agregadas de los 3 tickets (no solo 1)
- Una corrida contra un pedazo real de EnergySuite
- CLIENT-FACING v4 reescrito con change management
- **Nombre del propietario técnico en GlobalMVM** (no Jefferson, no Joaris — alguien que sostiene mes 6, mes 12, mes 24)

---

### 4️⃣ Joaris Angulo — Solutions Architect / Champion · 🟡 CONDITIONAL

**Quote clave**: *"Solid Phase 2 work. Production-ready for internal use. NOT yet market-ready. Recommend 2-week hardening sprint before pilot."*

#### Architecture review

**Code organization**: ✅ Clean. Single responsibility per module, no circular dependencies, no god files.

**Separation of concerns**: ✅ Tight design. Orchestrator builds initial prompt manually (`_build_prompt`), which is a coupling point — regex extractors can break if Claude's output format changes.

**Python quality**: ✅ Strong. Type hints throughout, Pydantic for schemas, async-first, structured logging via structlog.

**Concern técnico**: Las regex de `_extract_pr_url()` son agresivas (4 patrones diferentes). Funcionan pero son frágiles — mejor sería pedirle a Claude que emita JSON estructurado al final.

#### Test coverage analysis

**136 unit tests pasan**. Thorough en happy paths.

**Gaps específicos identificados**:
1. Parser error paths: timeout de `gh issue view`, JSON malformado de `az boards work-item show`, repo privado sin token
2. Hooks edge cases: variantes de `git reset --hard`, false positive `.env` en `my_env_checker.py`
3. Orchestrator failure scenarios: ClaudeSDKClient exception, prompt file write failure
4. Cloner edge cases: timeout mid-transfer, lock files en Windows, tokens con chars especiales
5. **Integration testing minimal**: solo 1 smoke test. Sin test E2E de la pipeline completa (parse → clone → query → extract)

#### Análisis de los 3 PRs reales

| PR | Verdict | Notas |
|----|---------|-------|
| #2 WI-101 bug (DivideByZero) | ✅ APPROVE | Minimal, surgical. Guard clause correcto. Test proof solid |
| #3 WI-102 perf (N+1) | ✅ APPROVE WITH CAUTION | Correcto pero double `OrderByDescending()` no ideal. Query count assertion via `DbCommandInterceptor` = gold standard |
| #4 WI-103 security ([Authorize]) | ✅ APPROVE STRONGLY | Minimal, correct, reflection test + 3-scenario matrix (anon/user/admin) = security gold standard |

#### Concern estructural más importante

**Autonomy escalation for security is prompt-level, not code-enforced**.

El SKILL.md dice "Issue toca auth, payments, encryption → fuerza GUIDED". Pero el agent solo escala si **Claude mismo clasifica correctamente**. Un issue titulado "Fix login button color" podría procesarse en FULL_AUTO y modificar código de auth sin escalar.

**Mitigación propuesta**: agregar hook path-based:
```python
async def guardrail_auth_escalate(input_data, ...):
    file_path = tool_input.get("file_path", "")
    if any(segment in file_path for segment in ["auth", "security", "admin", "permission"]):
        return _deny("Security-sensitive path. Escalate to GUIDED.")
```

#### Monetización multi-cliente

| Criterio | Status actual | Necesario para EPM/ISAGEN/XM |
|----------|--------------|------------------------------|
| Skill customization | Monolithic SKILL.md | Client-specific overlays (e.g., `skill/overrides/isagen-CLAUDE.md`) |
| Repository integrations | GH + ADO | GitLab (Phase 6) |
| Tracking destinations | Mission Control (HQ-specific) | Per-client tracking connectors |
| Language | Spanish only | Bilingual (ES + EN) |
| Compliance | Logs only | Immutable audit trail, PR signing, SLAs |

#### Hardening sprint propuesto (2 semanas)

1. Integration test suite (10-15 E2E tests) — 3-5 días
2. Path-based security escalation hook — 1 día
3. Structured output del agent (JSON en vez de regex) — 2-3 días
4. Per-client config skeleton — 1-2 días
5. Tracking per-customer documentation — 2-3 días

#### Mensaje a John Bairo (su skeptic peer)
> *"John, you were right to be cautious. The architecture is sound. I found one major caveat: autonomy escalation for security relies on Claude's classification, not hard rules. With path-based checks added, I'm comfortable recommending a pilot in Q2 starting with lower-risk issues. I'm putting my name on this if we do the hardening. Not before."*

---

### 5️⃣ Víctor Manuel Orrego — Director of Operations · 🟡 YELLOW → GREEN con tasks

**Quote clave**: *"Fixi is operationally viable for a controlled pilot, but not yet for company-wide rollout. Faltan SLA, runbook, y escalation path. Si algo falla en cliente, no sé quién responde."*

#### TCO estimado — Año 1 (numbers-driven)

| Concepto | Costo mensual | Costo anual |
|----------|---------------|-------------|
| Claude API (1,000 tickets/mes) | $50-$150 | $600-$1,800 |
| Azure infra (prod) | $175 | $2,100 |
| Azure infra (dev/staging) | $40 | $480 |
| FTE soporte (0.25 FTE @ $8k/mes) | $2,000 | $24,000 |
| Onboarding 300 devs (año 1) | $125 prorrateado | $1,500 |
| Ajustes repos (CLAUDE.md, pipelines) | — | $1,000 |
| Contingencia (10%) | — | $500 |
| **TOTAL AÑO 1** | ~$2,390 | **~$30,980** |

**Año 2+ (sin onboarding)**: ~$27,480/año

**ROI vs. alternativa** (1-2 FTEs @ $50k): **4-6x**

#### Escalabilidad cliff

- **Hasta 200-300 tickets/día**: el agent corre en paralelo en runners de CI, sin problema
- **240+ tickets/día**: necesita **Azure Service Bus + worker pool**. Terraform actual NO incluye queue. **ESTO ES UN GAP**
- **GlobalMVM steady state (7,200 tickets/mes = 240/día)**: está **justo en el edge** del escalamiento simple
- **Solución**: ~40h engineering para agregar queue pattern antes de company-wide

#### Gaps críticos en Azure DevOps integration

**Fixes pequeños pero bloqueantes** (total ~8h engineering):

1. **Dockerfile NO instala `az CLI`** — actualmente solo `git`. El parser de Work Items va a fallar si corre en container sin el CLI:
   ```dockerfile
   RUN apt-get install -y azure-cli && az extension add --name azure-devops
   ```

2. **Post-PR Work Item state transition** — después de que Fixi crea el PR, nadie actualiza el Work Item. Necesita script post-Fixi:
   ```yaml
   - script: |
       PR_URL=$(jq -r '.pr_url' fixi-result.json)
       WI_ID=$(jq -r '.work_item.external_id' fixi-result.json | grep -oP '\d+')
       az repos pr work-item add --id ${PR_URL##*/pull/} --work-items ${WI_ID}
       az boards work-item update --id ${WI_ID} --state "In Progress"
   ```

3. **`ACTIVO.md` no documentado** — mencionado en Paso 9 pero sin spec de formato, ubicación, o mantenedor

4. **No hay dashboard de "Fixi tickets today"** — sin visibility operacional

#### Modelo de soporte — GAP completo

**No definido**:
- SLA response time (P1, P2, P3)
- Runbook de troubleshooting
- Escalation path (Saúl → Lots of Context → Anthropic?)
- Horario de soporte (8x5, 24x7)
- Quién paga support premium si incurre cost

**Necesario antes de go-live con cliente tier-1** (ISAGEN/XM):
1. SLA written (e.g., P1=2h response, 4h resolution)
2. Runbook básico (rollback, common issues)
3. Escalation path documentado
4. Who-pays-what matrix

#### Vendor risk (Anthropic lock-in)

**Escenarios preocupantes**:
1. **Pricing 10x en 2027**: $0.61 → $6.10/ticket → $43,920/mes insostenible
2. **API deprecation**: mitigado por usar SDK oficial
3. **Claude Code CLI unavailable**: **RIESGO ALTO** — el agent depende del CLI como subprocess

**Mitigación propuesta**:
- Saúl negocia pricing commitment + volume discount con Anthropic x 2-3 años
- Contract con SLA de uptime (99.9%)
- Documentar exit strategy (cómo reemplazar Claude con alternativa)
- Feature flags para LLM provider (6 meses)

#### Recomendación a Elkin
> *"Fixi is operationally viable for a controlled pilot. Arquitectura de seguridad es buena. Integración con Azure DevOps está presente pero incompleta. SLA, runbook, escalation — no definidos. Mi recomendación: (1) piloto 1 equipo × 1 mes, (2) paralelo: Saúl cierra gaps de ops, (3) mes 3 decisión ejecutiva. Inversión total piloto: $15-20k. ROI company-wide (si sustenta): 4-6x vs. 3-5 FTEs adicionales. Not a 'trust and deploy' product. A 'pilot, learn, then decide' play."*

---

### 6️⃣ John Bairo Gómez — Tech Lead Skeptical · 🟡 CONDITIONAL YES

**Quote clave**: *"Saúl claimed 80-93% time savings. I came prepared to do the actual digging. The three fixes are genuinely good code. But I'm not convinced this is a net win at scale without addressing my concerns."*

#### Diffs analysis (PR line-by-line)

**PR #2 (WI-101 bug)**:
- Fix: guard clause `if (diasTranscurridos == 0) return deltaKwh;`
- **Verdict**: APPROVE. Correct, minimal (8 lines), resolves root cause (not symptom).
- Scope creep: zero. No refactoring adjacent, no reformatting.

**PR #3 (WI-102 perf)**:
- Fix: `.Select()` projection con correlated subqueries en vez de foreach con N queries
- **Verdict**: APPROVE WITH CAUTION. Double `OrderByDescending()` no ideal pero EF Core optimiza.
- Test con `DbCommandInterceptor` contando queries SQL: **gold standard approach**
- Scope creep: zero.

**PR #4 (WI-103 security)**:
- Fix: `[Authorize(Roles = "Admin")]` a nivel de clase
- **Verdict**: APPROVE STRONGLY. Reflection test + 3-scenario matrix (anon/user/admin) = gold standard security testing
- Scope creep: zero.

**Resumen**: *"As a code reviewer, I approve all three. The security fix is especially impressive — it's correct AND the test coverage is mature."*

#### Lo que NO le convence

1. **80-93% time savings es un single demo run de 4.3 min**. Real GlobalMVM tickets son más messy: legacy .NET Framework 4.x, business logic sin test, flaky tests, conventions que no son syntax errors

2. **"Review" step es vago sobre quién revisa**. Si un junior rubber-stamp un PR sin leerlo, automatizamos el rubber-stamp

3. **Fixi no demuestra cómo maneja ambigüedad**. Los 3 bugs del demo tenían root cause obvio. Real tickets no siempre son clean

4. **Cost-at-scale math incompleto** — excluye costo de fixing Fixi's mistakes, training time, back-and-forth

5. **El demo es PERFECTO para Fixi**: 3 seeded bugs, cada uno en single file, con tests failing claros. Real code es 500K LOC, messy business logic

#### Worst-case scenario que construyó

> *"2 AM jueves. ISAGEN tiene incidente. On-call (que no entiende el business logic) corre Fixi. Fixi ve `if (consumption < 0) consumption = 0;` y su hipótesis: 'safety net está enmascarando problema real'. Fixi remove la safety net. PR pasa tests (porque test data no triggerea negative consumption). Production breaks worse. El real problem era upstream (bad meter calibration). Fixi no entiende domain context."*

**Mitigación existente**: SKILL.md dice "deja en rama aislada, PR para revisión", pero *"el tool is only as good as el humano que revisa"*.

#### 5 preguntas difíciles que hará
1. En el smoke test de 4.3 min, ¿cuánto tiempo fue thinking vs. running tests?
2. **Show me the metrics for a FAILED run** — ¿qué pasa cuando Fixi se equivoca?
3. ¿"5-15 min review" es rubber stamp o senior engineer real?
4. ¿Cómo maneja Fixi repos sin tests?
5. ¿Cuál es el API cost real en 500K LOC repo?

#### 3 condiciones para cambiar de opinión

1. **Real-world pilot en GlobalMVM code** — 5-10 tickets reales del repo EnergyTracker, no del demo
2. **Comparación con baseline** — control group de senior engineers fixeando los mismos tickets manualmente. Medir same metrics. Si Fixi es 80% faster AND quality is equal → believe the hype. Si 80% faster BUT review time up 50% → savings evaporate
3. **Failure post-mortem** — forzar a Fixi a fallar en un ticket con ambigüedad / domain knowledge. Documentar qué salió mal y cuánto tardó en fix

**Plus**: feedback de 3-5 senior engineers (no Joaris, no Saúl) — *"¿Confiarían el tool para critical fixes o security changes? La respuesta a esa última pregunta me dice todo."*

#### Mensaje a sus senior devs
> *"Fixi is real. Not vaporware. Three demo fixes are correct, tests solid. But this is NOT a tool that replaces your judgment — automates the boring parts so you focus on the hard parts. Pilot en non-critical tickets × 4 semanas, con 3 condiciones: (1) PR por senior antes de merge, (2) tracking de PRs que necesitan rework, (3) honestidad sobre time savings vs review overhead. If it works, great. If it doesn't, 4 weeks wasted, not $50k/year committed."*

---

### 7️⃣ Liset — Data & AI Lead / Centro de Aceleración · 🟡 CONDITIONAL FIT

**Quote clave**: *"Fixi es mucho más que una herramienta puntual. Pero no puedo aprobarla para el portafolio de IA corporativo sin cerrar los gaps de governance y data. Esto no es 'rechazo', es 'sí bajo condiciones que son estándar para cualquier herramienta de IA corporativa'."*

#### Portfolio ranking

| Criterio | Ranking |
|----------|---------|
| Valor estratégico | **ALTO** (developer productivity gain real) |
| Riesgo de implementación | **MEDIO-ALTO** (data, hallucinations, governance gaps) |
| Tiempo al valor | **SEMANAS** (MVP listo, infra en Terraform) |
| Fit con iniciativas existentes | **MEDIO** (complementario a Copilot, no conflictivo) |

#### Gaps de governance (los 3 críticos)

**GAP 1 — DPA con Anthropic no existe**

Source code, work items, git history van al Claude API. Sin contrato explícito:
- ¿Plan de Anthropic (Free/Pro/Enterprise)?
- ¿Training-on-data policy?
- ¿Data retention?
- ¿Sub-processors?

**Blocker para clientes regulados (ISAGEN, XM)**.

**GAP 2 — Data residency no soportada**

- Energy sector en Colombia puede tener requisitos regulatorios (CREG)
- Exportar source code a Anthropic (USA API) puede ser incumplimiento
- No hay mechanism para "esto no puede salir de Colombia"
- No hay regional endpoints implementados
- **Blocker para ISAGEN/XM sin conversación con legal**

**GAP 3 — Governance matrix no documentada**

- ¿Quién aprueba Fixi en un proyecto?
- ¿Hay excepciones por sector?
- ¿Resolución de disputas?
- ¿Coexistencia con Copilot, ChatGPT Enterprise?
- ¿AI Steering Committee?

#### Data leak risk — secrets históricos

**Escenario**: Dev committeó API key hace 40 commits. Nunca fue reverted. Fixi clona `--depth 50` → obtiene git history → envía a Claude API.

**Guardrail actual**: `guardrail_sensitive_files()` bloquea MODIFICACIÓN de archivos sensibles. **NO bloquea LECTURA** de archivos que ya contienen secrets.

**Solución propuesta**: integrar `git-secrets` o `truffleHog` en `clone_repo()` para detectar + redactar secrets ANTES de pasar contexto al agent.

#### Model lock-in (hardcoded a Claude)

**Costo de pivotar a GPT-5/Llama-3/local model**: ~40-60h engineering
- Prompt rewriting (SKILL.md optimizado para Claude)
- API rewriting (`claude_agent_sdk` != `openai`)
- Hook system (Claude SDK tiene PreToolUse, OpenAI no)
- Token estimation (encoding diferente)

**Mitigación propuesta**:
- Crear abstracción de `LLMProvider` interface
- Refactor orchestrator con dependency injection
- A/B test con múltiples modelos (6 meses)
- Dual-vendor soporte para Claude + OpenAI (12 meses)

#### Observabilidad central — ausente

**Como AI Lead, no puedo responder**:
- ¿Cuántos tickets resolvió Fixi esta semana?
- ¿Tasa de classification accuracy?
- ¿Cost per ticket real (no rehearsal)?
- ¿Escalation rate?
- ¿Hay bias sistemático en clasificación?

**Necesario**:
- Azure Log Analytics integration (structlog → sink)
- Dashboard Kusto/Power BI con KPIs
- Alerting (hallucination detected, escalation rate >40%, cost spike)
- Weekly report automatizado para steering committee

#### 3 entregables antes de aprobarlo para el portfolio

1. **Data Governance Policy** (crítica):
   - DPA firmado con Anthropic OU decisión documentada de non-use para clientes regulados
   - Exclusion list (ISAGEN/XM código no va a Claude)
   - Secret scanning pre-API integrado
2. **Governance Matrix** (alta):
   - Matrix de aprobación por proyecto
   - Escalation path
   - Coexistence policy con otras herramientas de IA
   - Approval by AI Steering Committee
3. **Central Observability** (alta):
   - Dashboard live en Log Analytics / Power BI
   - KPIs: fix success rate, classification accuracy, escalation rate, cost/ticket
   - Alerting + weekly report automatizado

#### Recomendación al Centro de Aceleración
> *"Fixi debe entrar al portafolio de IA de GlobalMVM, pero bajo supervisión corporativa. No como herramienta 'emergente' que cada equipo adopta ad-hoc, sino como asset estratégico gobernado centralmente. Plan: Q2 cierre DPA + governance. Q3 rollout general con observabilidad live. Q4 evaluación de impacto. Propongo que Fixi sea el primer asset del Centro de Aceleración que cumple el estándar corporativo de AI governance. Una vez listo, es nuestro modelo para lo demás."*

---

## Análisis cross-cutting

### ✅ Consenso — en qué todos (o casi todos) están de acuerdo

| # | Tema | Quiénes lo dijeron |
|---|------|--------------------|
| 1 | **Pilot acotado, NO rollout inmediato** | 7/7 |
| 2 | **Necesitamos un owner interno en GlobalMVM (no Saúl)** | Elkin, Víctor, Liset |
| 3 | **Azure DevOps no probado en vivo es un gap crítico** | Elkin, Jefferson, Joaris, Víctor |
| 4 | **Un solo rehearsal no es evidencia estadística** | Elkin, John Bairo, Joaris |
| 5 | **Los 3 PRs técnicamente son correctos** | Jefferson, Joaris, John Bairo |
| 6 | **13 Guardrails como hooks es el patrón correcto** | Jefferson, Joaris, John Bairo, Liseth, Liset |
| 7 | **SKILL.md auditable es un diferenciador vs Power Platform** | Jefferson, Joaris, Liset |
| 8 | **PR template con 3 secciones nombradas es excelente** | Jefferson, Joaris, John Bairo, Liseth |
| 9 | **Real-world pilot contra código GlobalMVM, no demo** | Elkin, John Bairo, Joaris |
| 10 | **SLA/runbook/escalation no definidos** | Víctor, Elkin, Liset |

### ⚠️ Conflictos entre stakeholders

#### Conflicto #1 — Velocidad de rollout

| Stakeholder | Posición |
|-------------|----------|
| **Elkin (CEO)** | Pilot 4 semanas, ROI mes 3 → crecimiento rápido |
| **Liseth (PMO)** | Fase 1 = 2 semanas, fase 4 = semana 9+, company-wide = mes 12 |
| **Víctor (Ops)** | Rollout escalonado mes 1-12 con métricas por fase |
| **John Bairo** | 4-week pilot con control group baseline |

**Tension**: CEO quiere velocidad → PMO/Ops/Tech quieren cautela. La reunión real va a tener este debate.

**Respuesta preparada**: proponer un pilot de 4 semanas (satisface a Elkin) pero con criterios de éxito de Liseth/Víctor (dev satisfaction, quality metrics, feedback de peers). Si pasa, escalado mes 3-6 fase-por-fase.

#### Conflicto #2 — Niveles de autonomía aceptables

| Stakeholder | Posición |
|-------------|----------|
| **Jefferson** | FULL_AUTO default + escalators actuales OK |
| **Joaris** | Path-based security checks code-enforced, no solo prompt |
| **John Bairo** | GUIDED para critical tickets, nunca FULL_AUTO sin supervisión |
| **Liseth** | GUIDED por defecto FOREVER, CONFIRM_PLAN con aprobación de tech lead, FULL_AUTO raro |

**Tension**: Jefferson está cómodo con el diseño actual. Joaris/John Bairo/Liseth quieren más barreras.

**Respuesta preparada**: implementar el path-based escalation hook que propone Joaris. En el pilot, **default a GUIDED**. Documentar política de gobernanza (cuándo se puede cambiar a CONFIRM_PLAN/FULL_AUTO, quién aprueba).

#### Conflicto #3 — Framing del CLIENT-FACING

| Stakeholder | Posición |
|-------------|----------|
| **Víctor** | "Framing político tóxico para devs senior" |
| **Liseth** | "3.75 devs de capacidad' SUENA a 'podríamos reducir headcount'" |
| **Elkin** | "Reframing del CLIENT-FACING con change management" |
| **Jefferson, Joaris** | No objetan el framing |

**Tension**: 3 stakeholders independientemente llegaron a la misma preocupación sobre la frase.

**Respuesta preparada**: reescribir la sección de "Proyección para equipo de 10 desarrolladores" para eliminar cualquier implicación de "reducción de headcount" y reemplazar con "30 horas/semana recuperadas para architecture, mentoring, innovation".

#### Conflicto #4 — "Production ready" threshold

| Stakeholder | Posición |
|-------------|----------|
| **Jefferson** | Ready AHORA para PoC |
| **Joaris** | 2-week hardening sprint |
| **John Bairo** | 4-week pilot con 3 condiciones |
| **Víctor** | YELLOW → GREEN con SLA + Azure DevOps fixes |
| **Liset** | Conditional fit con DPA + governance + observability |

**Convergencia**: todos coinciden en que **algo** falta antes de "full deploy", pero difieren en QUÉ falta. El hardening sprint de Joaris cubre parcialmente lo de John Bairo y Víctor. Lo de Liset es más independiente (governance, no técnico).

---

## Issues técnicos específicos identificados (action items)

### 🔴 CRÍTICOS (bloqueadores)

| # | Issue | Quién lo dijo | Esfuerzo | Owner |
|---|-------|---------------|----------|-------|
| 1 | **Dockerfile no instala `az CLI` + `azure-devops` extension** | Víctor | 15 min | Saúl |
| 2 | **DPA con Anthropic inexistente** (bloquea clientes regulados) | Liset | Legal + 1 semana | Saúl + Legal |
| 3 | **Escalación de security es prompt-level, no code-enforced** | Joaris | 1 día (agregar hook) | Saúl |
| 4 | **SLA + runbook + escalation path no definidos** | Víctor, Elkin | 1 semana (docs) | Saúl |
| 5 | **No hay owner técnico interno en GlobalMVM** | Elkin, Víctor, Liset | Decisión ejecutiva | Elkin |
| 6 | **Azure DevOps no probado en vivo** | Elkin, Jefferson, Víctor, Joaris | 4 horas (setup sandbox ADO + run) | Saúl |

### 🟡 ALTOS (antes de rollout wider)

| # | Issue | Quién lo dijo | Esfuerzo |
|---|-------|---------------|----------|
| 7 | **Secret scanning pre-API (git-secrets/truffleHog)** | Liset | 1 día |
| 8 | **Integration tests (10-15 E2E)** | Joaris, John Bairo | 3-5 días |
| 9 | **Structured JSON output del agent (no regex)** | Joaris | 2-3 días |
| 10 | **Central observability dashboard** | Liset, Víctor | 3-5 días |
| 11 | **Governance matrix + steering committee** | Liset | 1 semana docs |
| 12 | **Real-world test contra código GlobalMVM** | Elkin, John Bairo, Joaris | 1-2 días |
| 13 | **Post-PR Work Item state transition (ADO)** | Víctor | 2 horas |
| 14 | **ACTIVO.md spec documentada** | Víctor | 2 horas |
| 15 | **Rollout playbook de change management** | Liseth, Víctor | 1 semana docs |
| 16 | **Reframing del CLIENT-FACING.md v4** | Liseth, Víctor, Elkin | 2 horas |

### 🟢 MEDIOS (antes de company-wide)

| # | Issue | Quién lo dijo |
|---|-------|---------------|
| 17 | Azure Queue + worker pool para escalabilidad >240 tickets/día | Víctor |
| 18 | Model diversification (LLMProvider abstraction) | Liset |
| 19 | Data residency controls (regional endpoints) | Liset |
| 20 | Junior career path document | Liseth |
| 21 | Coexistence policy con Copilot + ChatGPT Enterprise | Liset |
| 22 | Cost tracking dashboard | Víctor |
| 23 | Memory/feedback loop entre runs | Elkin |

---

## Strengths reconocidos (los 10 más mencionados)

1. **SKILL.md auditable y versionable** — el diferenciador clave vs Power Platform (Jefferson, Joaris, Liset)
2. **13 Guardrails como code hooks, no prompts** — safety real, no "prayer" (todos)
3. **Los 3 PRs son correctos, mínimos, bien testeados** (Jefferson, Joaris, John Bairo)
4. **PR template con 3 secciones nombradas** (descripción técnica, cambios, impactos) — todos
5. **Respect for human review** — nunca mergea sin aprobación (Liseth, Elkin)
6. **No-fabrication rule enforcement** — el demo lo demostró marcando AC como N/A (Jefferson, Liseth)
7. **Architecture sólida** — separation of concerns, type hints, Pydantic, async (Joaris)
8. **IaC via Terraform** — 25 archivos, validable, reproducible (Víctor, Joaris)
9. **Stack agnostic** — .NET, Java, Python, Angular (Elkin, Jefferson)
10. **Demo con clientes reales de GlobalMVM** — EPM, ISAGEN, XM, Veolia en work items (Liseth)

---

## Plan de acción priorizado (antes de la reunión real)

### Semana 1 — blockers críticos

- [ ] **Fix Dockerfile**: agregar `az CLI` + `azure-devops` extension (Saúl, 15 min)
- [ ] **Designar owner interno**: Saúl pide a Elkin que nombre técnico de GlobalMVM que sostiene Fixi (Saúl → Elkin)
- [ ] **Path-based security hook**: agregar `guardrail_auth_escalate` (Saúl, 1 día)
- [ ] **SLA + runbook draft**: P1 response 2h, P2 4h, rollback procedure (Saúl, 1 día)
- [ ] **Reframing CLIENT-FACING.md v4**: eliminar "3.75 devs de capacidad" (Saúl, 2 horas)

### Semana 2 — real evidence

- [ ] **Setup ADO sandbox**: org throwaway, PAT, mirror de fixi-demo-dotnet (Saúl, 2 horas)
- [ ] **Rehearsal ADO live**: correr agent contra los 3 WIs en ADO path (Saúl, 1 hora)
- [ ] **Transcript run-02-ado.md**: documentar metrics agregadas (media, min, max) (Saúl, 2 horas)
- [ ] **Real code test**: pedir a Joaris/Jefferson un pedazo real de EnergyTracker o similar + correr agent (Saúl + champion)
- [ ] **Conversación con Anthropic**: DPA negotiation + pricing commitment (Saúl → Anthropic sales)

### Semana 3 — governance

- [ ] **Governance matrix draft**: template para aprobación de Fixi en proyectos (Saúl + Liset)
- [ ] **Rollout playbook draft**: fases, champions, training packet (Saúl + Liseth)
- [ ] **Failure post-mortem**: forzar a Fixi a fallar en ticket ambiguo, documentar (Saúl + John Bairo)
- [ ] **Peer feedback**: conversar con 3-5 senior engineers de GlobalMVM (no Joaris, no Jefferson) (Saúl)

---

## Meeting preparation guide

### Qué esperar de cada stakeholder

**Elkin (CEO)** abrirá preguntando por **ROI y timeline**. Su primera pregunta será probablemente: *"¿En 4 semanas podemos tener un pilot produciendo valor medible?"*. Respuesta preparada: "Sí, con pilot acotado en 1 equipo. Hay 6 gaps críticos que cerramos en semana 1-2. Semana 3-4 es el pilot en vivo."

**Jefferson (Hyperautomation)** será **el campeón técnico** en la sala. No necesita convencimiento — ya dio su visto bueno (9/9 capabilities). Úsalo como aliado para contestar preguntas técnicas.

**Joaris (Architect)** va a pedir detalles de **integration testing** y **security escalation**. Presentar el hook path-based que agregaste. Si pregunta por structured JSON output, dile que es roadmap Sprint 3.

**John Bairo (Skeptical)** va a ser **el más duro** — preguntas sobre failure modes, real world pilot, peer feedback. Respuesta preparada: propón exactamente sus 3 condiciones (real pilot + baseline comparison + failure post-mortem).

**Víctor (Ops)** va a preguntar por **SLA, TCO, escalabilidad**. Tener el TCO year-1 listo ($30K), el SLA draft, y el gap del Dockerfile ya arreglado.

**Liseth (PMO)** va a preguntar por **change management, juniors, framing**. Mostrar el CLIENT-FACING v4 reframeado. Presentar el rollout playbook.

**Liset (Data & AI)** va a preguntar por **DPA, data residency, governance, observability**. Tener la conversación de DPA con Anthropic en progreso. Governance matrix draft listo.

### Las 10 preguntas que casi seguro vas a recibir

1. "¿Quién mantiene Fixi cuando Lots of Context no esté?" → **Owner técnico interno**
2. "¿Dónde está el rehearsal de Azure DevOps en vivo?" → **Semana 2 run-02-ado.md**
3. "¿El DPA con Anthropic está firmado?" → **En conversación, contingency: exclusion list**
4. "¿Cómo evitan que Fixi modifique auth code sin escalar?" → **Hook path-based ya agregado**
5. "¿Cuál es el SLA cuando Fixi falla en cliente?" → **P1 2h, P2 4h, runbook documentado**
6. "¿A qué volumen se rompe?" → **240 tickets/día sin queue; Phase 6 agrega Azure Service Bus**
7. "¿Corrieron Fixi contra nuestro código real o solo demo?" → **Real code test semana 2**
8. "¿Qué pasa si los devs lo rechazan?" → **Rollout playbook + GUIDED default + champions**
9. "¿Cuánto cuesta 12 meses?" → **$30K año 1, $27K año 2+, 4-6x ROI vs FTEs**
10. "¿Cómo medimos éxito del pilot?" → **% PRs merged sin cambios >80%, NPS dev >7/10, zero prod incidents**

### Lo que NO hay que decir

- ❌ *"Fixi reemplaza desarrolladores"* (Liseth va a quemar todo)
- ❌ *"Equipo de 10 produce como 13-14"* (mismo problema — Víctor + Liseth lo flaggearon)
- ❌ *"Es solo instalarlo y corre"* (todos saben que no es verdad)
- ❌ *"Funciona con cualquier repo"* (John Bairo va a pedir evidencia)
- ❌ *"Nunca tiene bugs"* (cero credibilidad)

### Lo que SÍ hay que enfatizar

- ✅ *"Los 3 PRs reales que pueden clonar y revisar línea por línea"* (concrete evidence)
- ✅ *"SKILL.md es texto plano versionado — pueden auditar cada paso"* (transparency diff vs Power Platform)
- ✅ *"13 guardrails como hooks ejecutables, no como prayers"* (security story)
- ✅ *"Humans in the loop estructural — nunca mergea sin review"* (dignidad dev)
- ✅ *"Pilot de 4 semanas con criterios de éxito medibles"* (concrete ask, not vague)
- ✅ *"Jefferson ya validó las 9 capabilities de su prompt"* (internal champion validation)

---

## Appendix A — Matriz de votos en una sola imagen

```
                   Jeff  Liseth  Elkin  Joaris  Víctor  JohnB  Liset
                   ----  ------  -----  ------  ------  -----  -----
Technical ready?   ✅    —       🟡     🟡      🟡      🟡     🟡
Business ready?    —     🟡      🟡     —       🟡      🟡     🟡
Ops ready?         —     🟡      🟡     —       🟡      —      🟡
Governance ready?  —     🟡      —      —       —       —      🔴
                   
Overall verdict    ✅    🟡      🟡     🟡      🟡      🟡     🟡
```

**Leyenda**: ✅ = listo · 🟡 = conditional · 🔴 = blocker · — = no evaluado desde ese ángulo

**0 × 🔴 rojos en overall verdict** — nadie rechaza. **1 × ✅ verde + 6 × 🟡 yellow** — el demo es defensible pero necesita condiciones para avanzar.

## Appendix B — Cost summary (consolidado de todas las reviews)

**Inversión requerida (pre-pilot)**:
- Semana 1-2 hardening (Saúl): ~60h engineering ≈ $6K
- DPA negotiation (legal): ~$2K
- ADO sandbox + rehearsal: ~$200 (API costs + time)
- Governance + rollout docs: ~$2K
- **Total pre-pilot**: ~$10-12K

**Pilot (4 semanas, 1 equipo de 5-8 devs, ~30 tickets)**:
- Claude API: ~$50
- Ops overhead (Víctor): 40h ≈ $4K
- Training + support (Liseth): 20h ≈ $2K
- Saúl on-call: 20h ≈ $2K
- **Total pilot**: ~$8K

**TOTAL a decidir "go / no-go" post-pilot**: **~$20K**

**Year 1 full (si pilot es exitoso)**:
- Claude API + Azure infra: ~$5K/año
- 0.25 FTE ops: ~$24K/año
- Onboarding 300 devs: ~$1.5K
- **Total Year 1**: ~$30-35K

**ROI vs. alternative (3-5 FTEs @ $50K c/u)**: **4-6x**

---

## Appendix C — Conversaciones 1:1 preparadas

### Si Elkin te corre aparte: *"¿En qué vamos a invertir realmente?"*
> *"$10-12K hardening + $8K pilot = $20K para decidir. Si pasa, Year 1 es $30-35K. ROI 4-6x si reemplaza trabajo de 0.5-1 FTE. Si no pasa, perdimos $20K — menos que un mes de un dev senior."*

### Si John Bairo te enfrenta: *"¿Funciona contra código real o solo el demo?"*
> *"Esa es exactamente la pregunta que queremos responder en semana 2. Pide a tu equipo un ticket real — non-critical, repo con tests. Fixi corre, nosotros documentamos el resultado (éxito o fracaso). Si Fixi falla, aprendemos por qué. Si funciona, tenemos evidencia. Ambos outcomes son valiosos."*

### Si Liseth te pregunta: *"¿Cómo protegemos a los juniors?"*
> *"Los juniors aprenden diferente. En lugar de 2 horas debugueando, 10 minutos revisando PRs completas con root cause ya identificada. Es skill más avanzada, no menos. Pero sí, necesitamos un rollout playbook que lo haga explícito. Lo tengo draft para semana 3 — te pido que lo revises y co-autorees."*

### Si Liset te corre aparte: *"¿Los clientes regulados pueden usar esto?"*
> *"Hoy, sin DPA con Anthropic, no. Estoy en conversación con su sales team esta semana. Hay dos paths: (1) DPA estándar de enterprise, (2) exclusion list — ISAGEN y XM quedan fuera hasta que tengamos el DPA. Cualquiera es aceptable para empezar el pilot en un cliente non-regulated."*

### Si Víctor pregunta: *"¿Quién responde cuando esto se rompe?"*
> *"P1 respuesta 2h, P2 4h, P3 1 día. Primario: Saúl (horario oficina ET). Secundario: Lots of Context eng team (on-call rotation). Escalation a Anthropic si es issue del SDK. Runbook draft lo tengo — te pido que lo revises antes del pilot."*

### Si Jefferson te felicita: *"Cumpliste mi prompt al detalle"*
> *"Gracias Jefferson. Eso lo quiero en la próxima reunión — tu voz como co-autor del requerimiento tiene peso. ¿Podrías presentar la validación 9/9 vos mismo? Yo te backup en lo técnico."*

---

**FIN DEL DOCUMENTO**

> **Nota de Saúl al equipo**: Este documento es una simulación, no la reunión real. Los patrones de concerns son sólidos pero el humano real puede sorprender. Úsalo como **mapa**, no como **guion**. Adapta según la energía de la sala.
>
> El objetivo de la reunión real no es "vender" el demo. Es **obtener compromiso para un pilot de 4 semanas**, con los 6 blockers de semana 1-2 resueltos antes. Si salimos con ese compromiso, esta sprint fue un éxito.
