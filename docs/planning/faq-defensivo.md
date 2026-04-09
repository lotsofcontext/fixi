# FAQ Defensivo — Fixi PoC vs GlobalMVM

> **Fecha**: 2026-04-08
> **Sprint**: S3 · **Task**: [[S3-T11]]
> **Fuente**: top 20 preguntas mas dificiles extraidas del [[dry-run-report|dry-run de 8 agentes simulados]] del equipo GlobalMVM.
> **Uso**: prep de la proxima reunion con GlobalMVM (entrega del PoC). Cada pregunta tiene respuesta defensiva + evidencia + estatus honesto.
> **Regla**: si no tenemos respuesta solida, lo documentamos abajo en "Preguntas que aun no sabemos responder" — honestidad > hype.

---

## Metodo de priorizacion

Las preguntas se clasifican en 3 tiers segun dificultad y frecuencia esperada:

| Tier | Criterio |
|------|----------|
| **T1 — Killer questions** | Pueden matar el PoC si no se responden. Aparecen en 3+ agentes o tocan capabilities del prompt original. |
| **T2 — Strategic questions** | No matan el PoC pero definen la forma del piloto y el modelo comercial. |
| **T3 — Tactical questions** | Detalles tecnicos y operativos que surgen una vez aceptado el PoC. |

---

## TIER 1 — Killer questions (5)

### Q1. "Quiero ver Fixi corriendo contra Azure DevOps, no GitHub. Cuando esta ese rehearsal?"

**Quien la haria**: Jefferson (principal), Jenny, Elkin, John Bairo, Victor, Joaris (implicito)
**Frecuencia**: 6 de 8 agentes la piden explicitamente.

**Respuesta defensiva**:
> "Tienen razon. El rehearsal actual es contra GitHub (WI-101 en `fixi-demo-dotnet`, Sprint 1). El codigo de integracion ADO esta 100% en `skill/SKILL.md` Paso 8 — `az repos pr create` con template de body, link del PR al Work Item con `az repos pr work-item add`, parser de fields de ADO con `az boards work-item show`. Lo que falta es correrlo punta-a-punta contra un sandbox ADO real. **Compromiso: antes de la siguiente reunion entregamos el video del rehearsal ADO con WI-102 y WI-103**. Lo que necesitamos de ustedes: un sandbox ADO accesible o un repo espejo donde podamos correr la demo sin tocar produccion."

**Evidencia que respalda**: `skill/SKILL.md` Paso 1 (parser ADO) y Paso 8 (creacion de PR). `kanban/BOARD.md` muestra S1-T13 (ADO parser) y S1-T14 (Azure Repos PR) done.
**Estatus honesto**: GAP confirmado. No hay rehearsal ADO end-to-end documentado.

---

### Q2. "Esto lo hace cualquiera con ChatGPT + Power Platform. Donde se diferencia Fixi?"

**Quien la haria**: Jefferson (literal)
**Frecuencia**: 1 agente pero es el que **dio el prompt original** — su opinion pesa mas que las otras.

**Respuesta defensiva**:
> "Jefferson, desde el respeto: lo que ChatGPT te da es el **plan**. Lo que Fixi te da es el **entregable ejecutado**. Fixi clona el repo, corre `dotnet test`, abre el PR con `az repos pr create`, y linkea el PR al Work Item. ChatGPT te da un markdown con el plan y tu lo ejecutas a mano. La diferencia en 4 puntos: (1) **ejecucion real en el repo**, no output en pantalla; (2) **guardrails auditables** — 13 reglas duras en `skill/references/guardrails.md` que Power Platform tendrias que implementar a mano con policies; (3) **corre en pipeline, no en chat** — Fixi es un CLI (`fixi resolve --work-item`) que se mete en Azure Pipelines y trabaja cuando tu no estas en la maquina; (4) **halt-and-ask auditable** — si faltan datos, Fixi se detiene y lo reporta, no inventa. Donde **NO** nos diferenciamos: la calidad del razonamiento sobre codigo es LLM. Lo que cambia es el harness alrededor. Por eso les pido verlo ejecutar, no describirlo."

**Evidencia que respalda**: `docs/CLIENT-FACING.md` metricas smoke test (4.3 min, $0.61 USD, PR #1 real). `agent/README.md` use case. `skill/references/guardrails.md` las 13 reglas.
**Estatus honesto**: defendible con evidencia real, pero **requiere mostrar el rehearsal en vivo** para ser creible.

---

### Q3. "Cuando Saul no este, quien sostiene esto? Mi equipo podra mantenerlo?"

**Quien la haria**: Elkin, Jenny, Victor (implicito)
**Frecuencia**: 3 agentes, 2 de ellos en puestos de decision final.

**Respuesta defensiva**:
> "Pregunta justa. Fixi esta disenado especificamente para ser mantenible sin vendor lock-in en la persona: (1) **el workflow de 10 pasos es texto plano en markdown** (`skill/SKILL.md`, no es codigo compilado — cualquier arquitecto de GlobalMVM puede leerlo, entenderlo, y modificarlo; (2) **el agent runtime son ~925 lineas de Python** (`agent/src/fixi_agent/`) con 136 unit tests y comentarios explicativos; (3) **el Terraform esta modularizado** en 5 componentes estandar de Azure que su equipo de plataforma ya conoce; (4) **los guardrails son markdown + hooks Python** inspeccionables. **Propuesta concreta**: durante el piloto hacemos 2 sesiones de handoff tecnico con Joaris y el owner tecnico que ustedes designen — una sobre el skill, otra sobre el agent + guardrails. Dejamos un CLAUDE.md del repo con instrucciones de mantenimiento. Si ustedes quieren, firmamos SLA de soporte de 6 meses mientras el equipo se apropia."

**Evidencia que respalda**: `agent/README.md` y `agent/pyproject.toml`. `skill/SKILL.md` es markdown. `terraform/` tiene 5 modulos claros.
**Estatus honesto**: defendible. La arquitectura es genuinamente inspeccionable. El gap es que el handoff tecnico no esta documentado todavia — hay que escribir una guia de mantenimiento.

---

### Q4. "El $0.61 y los 4.3 min son de un solo ticket. Donde estan las metricas sobre volumen real?"

**Quien la haria**: Victor, Elkin, Jefferson, Joaris
**Frecuencia**: 4 agentes, todos pidiendo explicitamente N>1.

**Respuesta defensiva**:
> "Tienen razon, esos numeros son N=1 sobre WI-101 en el smoke test del 2026-04-07. Hoy no tenemos estadistica, tenemos una corrida verde. **Compromiso concreto para la siguiente entrega**: correr los 3 work items sembrados (WI-101 bug, WI-102 performance, WI-103 security) como batch y reportar metricas agregadas — tiempo promedio, costo promedio, archivos modificados promedio, tasa de exito. Si quieren ir un paso mas, repetir cada uno 3 veces para medir varianza (9 corridas en total). Antes de firmar piloto formal — el piloto de 4 semanas que proponemos — ahi es donde se mide la tasa de exito real: `(PRs aceptados sin cambios) / (PRs totales)`. **Sin esa metrica, cualquier proyeccion de ROI es papel, estamos de acuerdo**. Victor, tu observacion del 100% exito asumido en el CLIENT-FACING es correcta — lo vamos a corregir en la v4 con escenarios pesimista/realista/optimista."

**Evidencia que respalda**: `docs/CLIENT-FACING.md` seccion smoke test. `docs/planning/dry-run-report.md` seccion 7 (calculo de Victor).
**Estatus honesto**: GAP confirmado. El smoke test es N=1. **Accion inmediata**: correr batch de 3 tickets antes de la proxima reunion.

---

### Q5. "Como evitas que Fixi rompa codigo que ya funciona? Los 13 guardrails son suficientes?"

**Quien la haria**: Carlos (principal), Joaris (implicito en "agnosticismo"), Liset (implicito en "deuda tecnica"), Jenny (implicito en "que no rompa lo que ya funciona en produccion")
**Frecuencia**: 4 agentes, Carlos con analisis linea por linea.

**Respuesta defensiva**:
> "Carlos, tu analisis es el que mas me hace trabajar. Voy a separar la respuesta en dos partes porque tiene dos niveles distintos:
>
> **Lo que Fixi hace HOY para no romper codigo existente**:
> (1) Rama aislada siempre (guardrail #1, nunca commit a main); (2) cambio minimo por diseno (Paso 6); (3) escalacion forzada a GUIDED cuando >15 archivos, security, migrations, o CI/CD; (4) rollback automatico si cualquier paso falla (Paso 10 + guardrail #11); (5) el agente corre en un tempdir propio por invocacion, aislado del filesystem del developer; (6) el PR va a review humano — no hay auto-merge por diseno.
>
> **Lo que tu identificaste correctamente como gap**:
> (1) Varios guardrails (#1, #3, #4, #6, #11) viven en el prompt, no en hooks mecanicos. Si el modelo se salta la instruccion bajo presion, no hay red de seguridad. **Vamos a moverlos a hooks Python en Sprint 4**. (2) No hay snapshot pre-fix de tests para comparar nuevo-vs-pre-existente — esa es exactamente la debilidad del Paso 7.3. **Accion: implementarlo antes de la siguiente entrega**. (3) No hay hook que deniega `Edit` sobre archivos de test (tu edge case 7 — agente borra test que 'fallaba por su culpa'). **Nuevo hook en `hooks.py`**. (4) No hay lock por repo path — race entre agentes paralelos. **Sprint 4**.
>
> Carlos, la lista de 8 edge cases que mandaste la vamos a meter como test fixtures de regression del propio Fixi. Es el trabajo mas valioso que salio del dry-run."

**Evidencia que respalda**: `skill/references/guardrails.md` + `agent/src/fixi_agent/hooks.py` + `agent/tests/unit/test_hooks.py`. Analisis de Carlos en `docs/planning/dry-run-report.md` seccion 8.
**Estatus honesto**: los gaps que Carlos identifico son **reales y documentables**. La defensa no es negarlos, es tener un plan creible para cerrarlos en Sprint 4 y mostrarlo por escrito.

---

## TIER 2 — Strategic questions (8)

### Q6. "Como escalas esto a clientes con stacks diferentes — agnosticismo real?"

**Quien la haria**: Joaris (principal), Jefferson
**Respuesta defensiva**:
> "En el eje tecnologia, Fixi ya es agnostico: el Paso 4.1 detecta .NET, Node, Python, Rust, Go, Java/Maven/Gradle. El Paso 7 corre tests/lint/build segun el runner que encuentre. El skill es texto plano, se adapta por cliente con un CLAUDE.md propio. **Lo que NO es agnostico todavia**: conectores a librerias cerradas del cliente (nugets privados, Azure Artifacts, JFrog) y RAG sobre documentacion fuera del repo (Confluence, SharePoint, ADRs externos). Esos son los 2 trabajos que Joaris identifico para cerrar Nivel 4. Proposal: el modelo de negocio es skill + agent reutilizables (IP), y capa de adaptacion por cliente (conectores + base de conocimiento) — como Joaris lo planteo en la reunion, 'los conectores y las bases de conocimiento son lo que diferencia'."

**Evidencia**: `skill/SKILL.md` Paso 4.1 (stack detection). `docs/planning/dry-run-report.md` seccion 2.2.
**Estatus**: cubierto en el eje tecnico, gap confirmado en el eje de bases de conocimiento externas.

---

### Q7. "En que Nivel de IA (1-4) esta Fixi hoy, y que falta para llegar a Nivel 4?"

**Quien la haria**: Joaris (su marca personal)
**Respuesta defensiva**:
> "Nivel 3 con rozando Nivel 4. Esta en Nivel 3 porque ya ejecuta el ciclo completo sin supervision humana — recibe work item, parsea, clasifica, analiza, crea rama, implementa, corre validaciones, abre PR — con guardrails auditables y prueba real (PR #1 del demo en 3m51s, $0.61). **Falta para Nivel 4**: (a) RAG sobre base de conocimiento del cliente, (b) MCP servers por cliente para exponer fuentes internas (ADO boards, artifact feeds, runbooks) de forma estandarizada, (c) memoria inter-run para aprender de fallos, (d) adapter para librerias cerradas del cliente, (e) telemetria agregada multi-cliente para cobrar por valor. Los primeros 3 son Sprint 4. Los ultimos 2 son Sprint 5-6."

**Evidencia**: Framework de niveles esta en `.claude/agents/globalmvm-joaris-architect.md`. Gaps documentados en `docs/planning/dry-run-report.md` seccion 2.5.
**Estatus**: defendible con roadmap concreto.

---

### Q8. "Cuanto cuesta mantener esto a un ano? Dame el TCO honesto."

**Quien la haria**: Jefferson, Victor, Elkin
**Respuesta defensiva**:
> "Tres componentes:
> (1) **API Anthropic**: ~$950-$2,000/ano para 10 devs a 129 tickets/mes. Escenario pesimista si los tickets son mas complejos que el smoke test: hasta $4k/ano. El $0.61/ticket del smoke test es un piso, no el piso garantizado.
> (2) **Mantenimiento del agente**: ~$24,000/ano (0.4 FTE sosteniendo prompts, ajustando clasificadores, patcheando guardrails cuando cambien las librerias del cliente). Esto lo puede hacer alguien de GlobalMVM si decidimos hacer handoff tecnico en vez de SLA.
> (3) **Infra Azure**: ~$1,800-$3,000/ano segun CLIENT-FACING (ACI + ACR + Key Vault + VNet + Log Analytics).
>
> **TCO estimado: $28k-$32k/ano** para 10 devs. Contra $43k de ahorro bruto proyectado (con supuestos optimistas), margen positivo pero ajustado. **Factor critico**: si la tasa de exito del agente es 60%, el margen desaparece. Por eso insisto en el piloto de 4 semanas con medicion real antes de expandir."

**Evidencia**: `docs/planning/dry-run-report.md` seccion 7.3 (Victor's ROI) y 7.5 (TCO). `docs/CLIENT-FACING.md`.
**Estatus**: numeros de Victor son el escenario defendible. Hay que agregarlos al CLIENT-FACING v4.

---

### Q9. "Como manejas la adopcion del equipo de devs? Mis senior no van a adoptar esto por miedo."

**Quien la haria**: John Bairo (principal)
**Respuesta defensiva**:
> "John, este es el trabajo mas importante que sacaste del dry-run. El framing del CLIENT-FACING actual ('multiplica capacidad, 10 devs producen como 13') es contraproducente y lo vamos a reescribir. El framing correcto es **'Fixi se come la parte aburrida para que tu hagas arquitectura'**. Para los dos perfiles que identificaste:
>
> **Dev senior que resiste por temor a ser reemplazado**: Fixi hace bugs de 1-3 archivos con stack trace claro — el trabajo que ellos tampoco quieren hacer. Libera su tiempo para arquitectura, diseno, mentoring. El PR todavia tiene que ser revisado por un humano — el senior es ese humano, y su valor sube, no baja.
>
> **Dev que resiste por desconocimiento**: training. Compromiso: durante el piloto, 2 workshops de 1 hora — (1) como Fixi trabaja, que hace y que NO hace, (2) como revisar un PR de Fixi de forma eficiente. Demo en vivo.
>
> **Playbook de 'que hacer cuando el PR de Fixi es incorrecto'**: lo vamos a escribir antes de la siguiente entrega. Debe incluir: (a) como rechazar el PR con feedback estructurado, (b) que info capturar para que Fixi no vuelva a cometer el mismo error (input al R-system de Sprint 4), (c) como escalar a humano cuando Fixi se atasca 2 veces en el mismo ticket.
>
> Este trabajo es de narrativa, no de ingenieria. Y no lo vamos a subestimar."

**Evidencia**: Analisis de John Bairo en `docs/planning/dry-run-report.md` seccion 5.2.
**Estatus**: gap confirmado. **Accion inmediata**: reescribir CLIENT-FACING v4 con framing corregido.

---

### Q10. "Dame una matriz de decision: cuando Fixi SI y cuando NO?"

**Quien la haria**: John Bairo (literal, lo pidio en la reunion real)
**Respuesta defensiva**:
> "Esta es la primera iteracion de la matriz. Las dos celdas con `?` son gaps reales que no se pueden responder sin evidencia que todavia no tenemos:

| Caso | Fixi SI | Fixi NO | Razon |
|---|---|---|---|
| Bug con stack trace claro, 1-3 archivos | SI | | Paso 4.2 analiza stack trace directo, FULL_AUTO seguro |
| Perf localizada (N+1, timeout) | SI | | WI-102 del demo, clasificacion `performance` |
| Security (auth, injection, CVE) | | NO autonomo | Guardrail fuerza GUIDED |
| DB migrations / schema changes | | NO | Guardrail #9 fuerza GUIDED |
| Refactor >15 archivos / cross-module | | NO | Guardrail #6 degrada a GUIDED |
| Tickets sin repro steps ni evidencia | | NO | Guardrail #10 halt-and-ask |
| Feature nueva con diseno pendiente | **?** | **?** | Gap: no hay evidencia en el PoC |
| Hotfix en produccion con SLA minutos | **?** | **?** | Gap: no hay test de carga ni SLO definido |
| Repo sin tests existentes | SI con disclaimer | | Paso 7 acepta N/A, riesgo medio |
| Monorepo con pipelines compartidos | | NO | Guardrail #8 + limite vertical |

> Los dos `?` son candidatos a validacion en el piloto. Si ustedes nos dan un caso de feature ambigua y un caso de hotfix con SLA durante el piloto, los medimos. Hasta entonces, honestamente no los sabemos."

**Evidencia**: John Bairo seccion 5.3 del dry-run report. Guardrails en `skill/references/guardrails.md`.
**Estatus**: matriz completable. **Accion**: agregar al CLIENT-FACING v4 como seccion propia.

---

### Q11. "Como sincronizas dos runs paralelos sobre el mismo repo? Hay lock?"

**Quien la haria**: Liset (literal)
**Respuesta defensiva**:
> "Hoy el aislamiento es por tempdir — cada invocacion clona el repo a un directorio temporal unico con `tempfile.mkdtemp(prefix='fixi-')`, entonces dos agentes no pisan el mismo filesystem. Guardrail #4 aborta si working tree esta dirty al arrancar. **Pero**, como Liset identifico correctamente, **no hay lock optimista a nivel de repo o modulo**. Si dos agentes crean branches desde el mismo SHA y tocan el mismo archivo, el segundo PR va a tener merge conflicts. La sincronizacion queda en manos del reviewer humano. **Gap Sprint 4**: (a) lock file por repo path (file-lock o distributed lock), (b) `git fetch` + re-check del HEAD del base branch antes del push — si el base cambio, rebase o regenerar el fix. Liset, si tienes experiencia con file-lock distribuido en su stack, nos interesa ese input."

**Evidencia**: `agent/src/fixi_agent/cloner.py` (tempdir clone). Liset seccion 4.3 del dry-run report.
**Estatus**: gap confirmado. Sprint 4.

---

### Q12. "Como se integra Fixi con el Centro de Aceleracion y el trabajo de Carlos (regression prevention)?"

**Quien la haria**: Liset (principal), Carlos (implicito)
**Respuesta defensiva**:
> "Hoy no se integra — esa es la verdad. Fixi hoy escribe su tracking a `consultoria-x/mission-control/` que es el sistema interno del vendor. Si GlobalMVM adopta Fixi, el Paso 9 (triple-write) se debe reescribir hacia el Centro de Aceleracion y sus dashboards. **Propuesta concreta**: (a) hook `PreToolUse` que llame al agente de regression-prevention de Carlos antes de cualquier `Edit` — el match natural que Liset senalo, (b) hook `PostRun` que escriba outcome del PR a un store compartido con el Centro de Aceleracion, (c) RAG que consulte la base de conocimiento del Centro antes de Paso 4 (analisis). Esto es arquitectura conjunta — no lo decidimos solos, lo disenamos con Liset y Carlos."

**Evidencia**: Liset seccion 4.4 del dry-run report.
**Estatus**: no integrado hoy. Es oportunidad, no bloqueador — pero debe documentarse.

---

### Q13. "Como impacta esto a Energy Suite y a los clientes finales (EPM, ISAGEN, XM, Veolia)?"

**Quien la haria**: Jenny (principal)
**Respuesta defensiva**:
> "Jenny, en corto: **los clientes finales no deberian notar nada**, y eso es el objetivo. Si lo notan, algo salio mal. Los candidatos naturales en Energy Suite son los que tu identificaste: bugs reportados por soporte, deuda tecnica acumulada, correcciones cosmeticas. **Features nuevas no** — esas requieren conversacion con el cliente, no solo un ticket bien redactado. Para el lado de compliance: Fixi deja audit trail completo (triple-write en Paso 9) — quien pidio el cambio (work item), quien lo aprobo (reviewer del PR), contra que ticket (link PR↔WI). Para CMMI e ISO 9001 eso es defendible ante auditoria externa — el proceso es trazable de punta a punta, con evidencia en git history, ADO work items, y el inbox de Mission Control. **Lo que falta** es un playbook formal de 'como auditar PRs generados por agente' — eso lo podemos escribir antes del piloto con input de tu equipo de calidad."

**Evidencia**: `skill/SKILL.md` Paso 9 (triple-write). Jenny seccion 6.2 del dry-run report.
**Estatus**: defendible con accion pendiente (playbook de auditoria externa).

---

## TIER 3 — Tactical questions (7)

### Q14. "Quien es el product owner de Fixi una vez Saul se va?"

**Quien la haria**: Jenny (literal)
**Respuesta defensiva**: "Propuesta 3 roles: (a) **sponsor ejecutivo** (Elkin), (b) **owner tecnico** — el arquitecto que GlobalMVM designe (sugerencia: Joaris), (c) **champion del equipo piloto** — quien lo va a usar dia a dia (sugerencia: un team lead). El API key y centro de costos quedan bajo el owner tecnico. Cada rol queda documentado en el CLIENT-FACING v4."
**Estatus**: gap. Sprint 3 en CLIENT-FACING v4.

---

### Q15. "Fixi genera tests nuevos o solo corre los existentes?"

**Quien la haria**: Victor (literal, del paso 5 de su caso original)
**Respuesta defensiva**: "Hoy el SKILL.md dice 'archivos nuevos (si aplica): test de regresion' en el Paso 4.4 — o sea, **puede** generar tests nuevos si el fix lo amerita (ej: test de regresion para un bug). Pero la palabra 'si aplica' es ambigua. **Compromiso**: en la proxima entrega, aclarar en el SKILL.md la regla explicita: 'si el fix es un bug, generar al menos un test de regresion que falle en main y pase en la rama del fix'. Y mostrarlo en el rehearsal batch de 3 tickets."
**Estatus**: PARCIAL en docs. Accion: hacer la regla explicita y demostrarla.

---

### Q16. "Tienes rate limiting propio? Que pasa si lanzo 50 Fixi en paralelo?"

**Quien la haria**: John Bairo (principal)
**Respuesta defensiva**: "Hoy no hay rate limiting propio. Dependemos del rate limit del provider (Anthropic API) y del git host (GitHub/ADO). Para concurrencia alta se necesitan 3 cosas: (a) semaforo en el entry point del CLI, (b) backoff exponencial en cada call, (c) queue externa (Azure Storage Queue o Service Bus) entre el pipeline y el agente. **Sprint 4**. Para el piloto de 4 semanas no es bloqueador — arrancamos con concurrencia 1-3 para medir varianza antes de subir."
**Estatus**: gap. Sprint 4.

---

### Q17. "Que pasa con idempotencia? Si proceso el mismo work item dos veces, abre dos PRs?"

**Quien la haria**: John Bairo (implicito), Liset (implicito)
**Respuesta defensiva**: "Hoy **no hay check de idempotencia**. Si se corre `fixi resolve --work-item WI-123` dos veces, abriria dos branches y dos PRs con sufijos diferentes. **Propuesta Sprint 4**: antes del Paso 5 (crear branch), query al platform (`gh pr list --search WI-123` o `az repos pr list --query`) y si ya hay un PR abierto asociado al work item, abortar con mensaje 'este WI ya tiene PR abierto — usar --force si queres reabrir'."
**Estatus**: gap. Sprint 4.

---

### Q18. "Que hace Fixi con repos sin tests existentes? Es ciego para el reviewer."

**Quien la haria**: Carlos (implicito)
**Respuesta defensiva**: "El Paso 7 detecta runners de test y si no encuentra ninguno, marca el resultado como `N/A — no detectado en el repo` en el PR. El reviewer ve explicitamente que no hay validacion automatica. **Riesgo medio**, como bien dice John Bairo en la matriz de decision. **Mitigacion posible**: si el repo no tiene tests, Fixi puede proponer un archivo de test con el mismo fix — el reviewer decide si lo acepta. Hoy no lo hace automaticamente. Sprint 4 candidato si resulta relevante en el piloto."
**Estatus**: cubierto parcialmente. Riesgo documentado.

---

### Q19. "Los 925 LOC del agente — como los vamos a auditar de seguridad?"

**Quien la haria**: Carlos, Joaris (implicito)
**Respuesta defensiva**: "El codigo es Python estandar, publico en github.com/lotsofcontext/fixi, con 136 unit tests, linter ruff estricto, y mypy strict. Para auditoria formal proponemos: (a) pasar `bandit` y `semgrep` contra `agent/src/`, (b) revisar manualmente los hooks de `hooks.py` con el equipo de Carlos, (c) scan de dependencias con `pip-audit`. Los resultados se entregan como parte del piloto. Si GlobalMVM tiene un proceso de appsec interno que quiere aplicar, tambien funcionamos con eso."
**Estatus**: defendible. Accion: correr bandit + semgrep + pip-audit antes de la proxima reunion.

---

### Q20. "Que sobra del PoC actual que se puede cortar para no distraer?"

**Quien la haria**: Jefferson (literal, "eso sobra")
**Respuesta defensiva**: "Jefferson, coincido parcialmente. Lo que **sobra para el PoC** y lo guardamos para piloto: (a) los 5 modulos Terraform (ACR + Key Vault + VNet + ACI + Managed Identity, 1,955 lineas HCL) — para demostrar el PoC basta `docker run` con env vars; (b) MCP Server y A2A del roadmap expandido — los mencionamos como Sprint 5+ pero no los empujamos en el PoC. Lo que **NO** sobra: los 13 guardrails (son diferenciador vs ChatGPT), los 10 pasos del SKILL (son el contrato con tu prompt), y los 136 unit tests (son prueba de calidad del runtime). **Compromiso**: en la entrega del PoC, el deck y la demo solo tocan el flujo ticket-a-PR. Todo lo demas queda en el repo como roadmap, no en el pitch."
**Estatus**: alineable con Jefferson.

---

## Preguntas que AUN no sabemos responder

Honestidad > hype. Estas son las preguntas que **no tenemos respuesta solida todavia** y vamos a marcar explicitamente como gap:

### GAP-1. "Cual es la tasa de exito real de Fixi sobre tickets de produccion?"
**Estatus**: no medida. Necesitamos piloto de 4 semanas. **Honestidad**: no vamos a inventar un numero.

### GAP-2. "Fixi escala a un monorepo de 500k lineas?"
**Estatus**: no probado. El guardrail #6 (>15 archivos → GUIDED) lo bloquea por diseno. Hay que medir si el bloqueo se dispara en 20%, 40%, u 80% de los tickets reales — eso define si Fixi es util o no en monorepos reales.

### GAP-3. "Fixi puede manejar features con diseno ambiguo?"
**Estatus**: no probado. Celda `?` de la matriz de decision. **Honestidad**: no sabemos como reacciona a ambiguedad de producto. Probable hipotesis: se detiene en halt-and-ask (guardrail #10) porque falta "causa raiz clara", que es lo correcto pero deja el ticket sin resolver.

### GAP-4. "Como se comporta Fixi en un hotfix con SLA de minutos bajo presion?"
**Estatus**: no probado. Otra celda `?`. El smoke test de 4.3 min suena bien en abstracto, pero nunca se corrio bajo carga ni con interrupciones.

### GAP-5. "Cual es la tasa de falsos positivos del linter cuando Fixi corre `--fix`?"
**Estatus**: no medida. Carlos identifico esto como caso edge #4. Accion planeada: cambiar `--fix` a `--check` en Paso 7 como quick fix Sprint 3, eliminando el riesgo.

### GAP-6. "El R-system / memoria inter-run realmente reduce errores repetidos?"
**Estatus**: no implementado. Sprint 4. Hasta que exista, Fixi repetira los mismos errores de criterio que cometio el mes anterior.

### GAP-7. "Fixi funciona contra un repo privado de GlobalMVM con librerias cerradas (nugets internos, artifact feeds)?"
**Estatus**: no probado. Joaris lo marco como gap para Nivel 4. Sprint 5.

---

## Uso del FAQ en la reunion real

**Antes de la reunion**:
- Saul se lee las 20 respuestas de corrido (~15 min).
- Para cada Q, identifica 1-2 quotes clave que pueda decir sin leer del papel.
- Para los GAPs, decidir de antemano cuales se admiten publicamente y cuales se guardan para privado.

**Durante la reunion**:
- Si aparece una Q del Tier 1, responderla con la estructura (evidencia + accion concreta).
- Si aparece una Q que esta en GAPs, **decirla como gap** — no inventar. "Eso no lo sabemos todavia, aqui esta el plan para medirlo".
- Si aparece una Q **no cubierta**, anotarla y agregarla a este FAQ para la siguiente iteracion.

**Despues de la reunion**:
- Actualizar este FAQ con: (a) preguntas nuevas que surgieron, (b) reacciones reales vs simuladas, (c) correcciones a los perfiles de `.claude/agents/`.

---

*Sprint 3 · [[S3-T11]] · Ver [[dry-run-report|dry-run report completo]] para el contexto de cada pregunta.*
