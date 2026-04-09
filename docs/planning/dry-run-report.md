# Fixi PoC — Dry-Run Report (Sprint 3)

> **Fecha**: 2026-04-08
> **Sprint**: S3 · **Task**: [[S3-T10]]
> **Metodo**: 8 agentes de simulacion del equipo GlobalMVM (reunion 2026-04-06) ejecutados en paralelo, cada uno criticando Fixi PoC desde su rol unico.
> **Objetivo**: detectar gaps antes de entregar al cliente real ("el chicharron" que Jefferson y Joaris van a mandar).
> **Ver tambien**: [[faq-defensivo]] · [[HANDOFF-FIXI-SPRINT3-SIMULATION-AGENTS]] · [[BOARD]]

---

## Resumen ejecutivo

| Agente | Veredicto | Severidad de gaps |
|--------|-----------|-------------------|
| **Elkin Medina** (CEO) | **Necesita ver rehearsal ADO antes de aprobar** | Media |
| **Joaris Angulo** (Champion) | **"Estamos alineados" en el nucleo; reservas en agnosticismo de bases de conocimiento** | Media-alta (estrategica) |
| **Jefferson Acevedo** (Hiperautomatizacion) | **Cumple 9/9 capabilities en papel; falta demo en vivo ADO y batch de >1 ticket** | Media |
| **Liset (Datos+IA)** | **"Me preocupa en deuda tecnica" — no hay R-system ni memoria inter-run** | **Alta (tecnica)** |
| **John Bairo** (Arquitectura) | **Tecnologia bien traida; PoC prueba caso facil, no los dos de mayor valor (feature ambigua, hotfix SLA)** | Alta (adopcion + vertical) |
| **Jenny Pedraza** (PO Energy Suite) | **Necesita rehearsal ADO + ownership post-PoC claro** | Baja (organizacional) |
| **Victor Orrego** (Operaciones) | **Impacto operativo potencial, no probado. Pay-back 2.8 meses con supuestos optimistas** | Media (N=1 smoke test) |
| **Carlos Caicedo** (Regression) | **"Fragil en casos edge" — mitad de guardrails sin enforcement mecanico** | **Alta (tecnica)** |

**Signal agregada**: 6 de 8 agentes piden explicitamente **rehearsal contra Azure DevOps** (no GitHub) como bloqueador. Ese es el gap mas repetido y mas facil de cerrar.

**Signal tecnica mas fuerte**: Liset y Carlos, de forma independiente, identifican el **mismo gap estructural** — Fixi no tiene memoria inter-run, no aprende de fallos, cada run arranca de cero. Esto se va a repetir en cualquier conversacion tecnica real.

**Signal de adopcion**: John Bairo y Jenny coinciden en que **el framing "multiplica capacidad = equipo de 10 produce como 13-14"** es politicamente toxico para devs senior. Hay que reescribir el CLIENT-FACING en voz "Fixi se come la parte aburrida, tu haces arquitectura".

---

## 1. Elkin Medina — CEO

### 1.1 Veredicto
Necesito ver el rehearsal en Azure DevOps antes de aprobar.

### 1.2 Lo que me preocupa
- Velocidad al cliente: tenemos un solo run verde, en GitHub, contra un repo sembrado por nosotros. Eso no es una demo para Jefferson todavia.
- Mantenibilidad: 925 lineas de Python, 136 tests, Terraform en Azure. Cuando Saul no este, quien lo sostiene? Mi equipo va a poder mantenerlo cuando tu no estes?
- Adopcion del equipo tecnico: si Joaris y Jefferson no lo bendicen, esto no entra. No quiero empujar herramienta arriba.

### 1.3 Lo que necesito ver antes del board
- Rehearsal completo por el path Azure DevOps — WI-102 y WI-103 corridos contra un sandbox ADO real, con el PR linkeado al Work Item. No markdown, video del run.
- Una corrida contra un pedazo de codigo NUESTRO, no del demo sembrado. El chicharron que dijimos. Ahi vemos si de verdad no inventa.
- Numero honesto de costo mensual si lo corremos con volumen real — no el $0.61 del smoke test, el total con 30 tickets por semana por 10 devs.

### 1.4 ROI estimado (mi lectura)
Los numeros que leo son 80-93% de ahorro de tiempo humano por ticket, 30 horas/semana recuperadas en un equipo de 10, equivalente a 3.75 devs extra. Me gustan en el papel. No me convencen todavia porque salen de UN rehearsal de 3m 51s contra un bug sembrado por el mismo equipo que construyo el agente. Eso no es medicion, es ensayo. Para el board necesito numeros de al menos 5 corridas, idealmente sobre codigo que no vimos antes. El $0.61 por ticket si me suena razonable, pero quiero ver el total cargado con Azure, Key Vault, Container Registry, Log Analytics. Informacion clara, claro.

### 1.5 Next step concreto
**Saul coordina con Jefferson para que nos preste un repo real de GlobalMVM (el chicharron) y corre el rehearsal ADO + la corrida contra codigo nuestro antes de la proxima reunion.** Si pasa las dos, lo llevo al board. Si no, seguimos iterando. Lo demas — arquitectura, Terraform, guardrails — eso se lo dejo a Joaris y Jefferson.

---

## 2. Joaris Angulo — Arquitecto de Soluciones / Champion Fixi

### 2.1 Nivel de IA (segun mi framework)
Fixi se ubica hoy en **Nivel 3 — Ingenieria y confiabilidad**, rozando Nivel 4 en algunas aristas. El agente ya recibe una instruccion (work item), ejecuta el ciclo completo (parsear → clasificar → root cause → branch → fix → validar → PR) de forma autonoma via `FixiOrchestrator` + Claude Agent SDK, con `PreToolUse` hooks como guardrails, y deja evidencia verificable (PR #1 del demo en 3m51s, $0.61). El techo de Nivel 4 no lo toca todavia porque falta tesis de industrializacion: multi-tenant, telemetria agregada, y loop de mejora inter-cliente.

### 2.2 Agnosticismo cliente/tecnologia — evaluacion
La necesidad de Elkin es precisa: la misma solucion sirviendo a cliente A, B, C y D. Fixi cumple parcialmente.

**Portable (OK):** el workflow de 10 pasos es texto plano en `skill/SKILL.md`, el parser es universal (GitHub, Linear, Jira, ADO, free-text — Paso 1), la deteccion de stack en Paso 4.1 cubre .NET, Node, Python, Rust, Go, Java/Maven/Gradle, y Paso 7 ejecuta tests/lint/build segun el runner detectado. Los estandares definidos se leen del repo (`.editorconfig`, ruff, eslint, rustfmt, CLAUDE.md del cliente) — eso es exactamente lo que necesitamos para no reinventar por cliente.

**Pegado a contexto especifico (GAP):** no hay **conector a librerias cerradas del cliente** — cuando el repo del cliente consume nugets privados, artefactos internos, o APIs no publicas, Fixi no tiene forma de "entender" esas dependencias mas alla del codigo fuente visible. No hay RAG sobre documentacion tecnica del cliente (wikis Confluence, SharePoint, ADRs internos). El tracking de Paso 9 esta hardcodeado a `consultoria-x/clientes/{cliente}/` — eso es tooling de Saul, no del cliente.

**Conectores detectados:** GitHub CLI, Azure DevOps CLI (`az boards`, `az repos`), Jira/Linear via WebFetch.
**Conectores faltantes para escalar:** S3/Blob Storage como fuente de docs, Confluence/SharePoint, MCP servers por cliente, artifact feeds privados (Azure Artifacts, JFrog), y **RAG indexado** sobre la base de conocimiento del cliente.

### 2.3 Drivers de arquitectura

- **Escalabilidad: OK parcial** — el agente corre stateless por invocacion (`tempfile` + cleanup, `orchestrator.py:17`), desplegable en ACI segun el Terraform. Falta horizontal queue para N work items concurrentes.
- **Seguridad: OK** — 13 guardrails (`guardrails.md`), rama aislada siempre, bloqueo de `.env`/keys/CI-CD/migrations, escalado forzado a GUIDED en security (regla 8) y migraciones (regla 9), rollback automatico, Key Vault en RBAC, NSG deny-all.
- **Mantenibilidad: OK** — skill es markdown inspeccionable, no codigo compilado; 136 unit tests; kanban con audit trail; sprint 2 100% cerrado.
- **Agnosticismo: GAP** — cubierto en el eje tecnologia, incompleto en el eje base-de-conocimiento-del-cliente.

### 2.4 Monetizacion
Veo modelo repetible, no one-off. El skill es el **IP reutilizable**; lo que se cobra por cliente es la capa de adaptacion: conectores, CLAUDE.md del cliente, RAG sobre su documentacion, integracion con su Azure DevOps, y el Terraform parametrizado. Tarifa recurrente por: (a) licencia del agente + upgrades del skill, (b) setup de conectores y base de conocimiento por cliente, (c) consumo medido ($0.61/ticket es baseline defendible para cobrar por volumen). Eso es Nivel 4 — industrializar el mismo motor y diferenciar por conectores + bases de conocimiento, exactamente el modelo que vengo pidiendo.

### 2.5 Gaps para subir de nivel
1. **RAG sobre base de conocimiento del cliente** — wiki, ADRs, confluence, docs tecnicas privadas. Hoy Paso 4.1 solo lee `docs/` del repo; insuficiente para clientes con documentacion fuera del repo.
2. **MCP Servers por cliente** — un servidor MCP por cliente que exponga sus fuentes (ADO boards, artifact feeds, DB schemas, runbooks) al agente de forma estandarizada en vez de conectores ad-hoc.
3. **Memoria inter-run** — hoy cada invocacion es stateless. Falta persistir aprendizajes: "en cliente B, el modulo X siempre rompe por Y". Candidato: vector store + retrieval al iniciar Paso 4.
4. **Adapter para librerias cerradas** — hook de pre-analisis que resuelva simbolos de nugets/artefactos privados antes de Paso 4.2.
5. **Telemetria agregada multi-cliente** — dashboard de tickets resueltos/costo/confianza por cliente. Sin esto no se puede facturar por valor ni iterar el skill con datos.

### 2.6 Veredicto
**Estamos alineados** en el nucleo: Fixi resuelve el ciclo completo de ticket a PR sin inventar informacion, con rama aislada, validaciones reales, y PR auditable — la arquitectura de 10 pasos + 13 guardrails es solida y la separacion skill-como-playbook vs agent-como-runtime es la decision correcta para mantenerlo inspeccionable. **Reservas estructurales:** sin RAG sobre documentacion del cliente y sin conector a librerias cerradas, Fixi escala a clientes con repos limpios pero se frena en el mundo real de GlobalMVM. Ese es el trabajo de Sprint 3 si queremos cerrar Nivel 4.

---

## 3. Jefferson Acevedo — Lider Hiperautomatizacion (dio el prompt original)

### 3.1 Auditoria de las 9 capabilities (mi prompt, punto por punto)

| # | Capability (mi prompt) | Cubierta? | Evidencia (archivo:paso) |
|---|---|---|---|
| 1 | Conectarse a fuentes de conocimiento (repos, tickets, docs tecnicos) | **SI** | `skill/SKILL.md` Paso 1 (GH/ADO/Jira/Linear/texto) + Paso 4.1 (lee README, CLAUDE.md, docs/, ADRs, wiki) |
| 2 | Clasificar y priorizar por tipo | **PARCIAL** | `skill/SKILL.md` Paso 2 — clasifica en 7 tipos con keywords; prioridad se **lee** del work item (ADO `Priority`, labels) pero no se re-prioriza dinamicamente |
| 3 | Validar codigo fuente existente | **SI** | `skill/SKILL.md` Paso 4.2 (keyword search, stack trace, dependency tracing, test examination) antes de tocar nada |
| 4 | Aplicar ajustes con buenas practicas y estandares definidos | **SI** | `skill/SKILL.md` Paso 4.1 (lee `.editorconfig`, eslint, ruff, rustfmt, STYLE.md) + Paso 6 reglas de implementacion |
| 5 | Crear rama con nomenclatura adecuada | **SI** | `skill/SKILL.md` Paso 5 (`{type_prefix}/{external_id}-{slug}`) + guardrail #1 (nunca main/master) |
| 6 | Ejecutar validaciones basicas | **SI** | `skill/SKILL.md` Paso 7 — tests + lint + build, con detectores para .NET/Node/Python/Rust/Go/Maven/Gradle |
| 7 | Commit claro y estructurado | **SI** | `skill/SKILL.md` Paso 6 (conventional commits con `Fixes:` trailer) |
| 8 | PR listo para aprobacion con descripcion tecnica, cambios, impactos | **SI** | `skill/SKILL.md` Paso 8 — template tiene las 3 secciones literales ("Descripcion tecnica", "Cambios realizados", "Posibles impactos") para GitHub y Azure Repos |
| 9 | Halt-and-ask cuando faltan datos | **SI** | `skill/references/guardrails.md` regla #10 + #12 (timebox 10min analisis, reporta "FLUJO DETENIDO") |

### 3.2 Benchmark: Fixi vs Power Platform + ChatGPT + Copilot
Desde mi desconocimiento, voy a ser directo: el prompt que yo di, ustedes podrian reproducirlo hoy en ChatGPT en 30 segundos. Lo probe mientras conversabamos. ChatGPT me genero el plan. Donde ChatGPT **no llega** y Fixi si:

- **Ejecucion real en el repo del cliente, no output en pantalla.** ChatGPT me genera texto; Fixi clona el repo, crea branch, corre `dotnet test`, abre el PR en Azure Repos con `az repos pr create`. Eso es la diferencia entre "plan" y "entregable".
- **Guardrails auditables.** 13 reglas duras (`guardrails.md`): abort si working tree dirty, prohibido main, prohibido `.env`, rollback automatico. Eso en Power Platform lo tendria que construir yo a mano con policies — aqui viene por defecto.
- **Correr en pipeline, no en chat.** Fixi es un CLI (`fixi resolve --work-item ...`) que se mete en GitHub Actions o Azure Pipelines. Copilot me asiste mientras tipeo; Fixi trabaja cuando yo no estoy en la maquina. Casos de uso distintos.
- **Donde NO se diferencia**: la calidad del razonamiento sobre el codigo es LLM — igual que Copilot, igual que ChatGPT. Lo que cambia es el **harness** alrededor.

### 3.3 Costo-beneficio
- **$0.61 USD por ticket, 4.3 min.** Si mi equipo cierra 30 tickets/semana, son $18 USD/semana por 30 horas humanas recuperadas. El numero **cuadra**, pero quiero verlo sostenido — no una corrida afortunada.
- **Me preocupa el TCO a 1 ano**: no es el costo de Anthropic, es el costo de mantener los **prompts y guardrails** cuando cambien los repos, cuando Anthropic suba precios, y cuando un fix malo entre a prod por revision apurada. Necesito un numero de "falsos positivos" despues de 50 tickets reales, no 1.
- **Variable oculta**: el PR malo que pasa review porque "lo genero el agente, debe estar bien". Eso cuesta mas que $0.61.

### 3.4 Que es lo MINIMO que necesito ver
Aterrizado: **pensemos bajo el minimo**, les pido tres cosas:

1. **10 tickets de Excel contra un codigo base real nuestro.** No el demo .NET sembrado. Les damos un repo pequeno de EnergySuite, les mando 10 tickets reales en un CSV, Fixi los procesa en batch, y al final un reporte: cuales resolvio, cuales paro, cuales metio mal el fix.
2. **Una demo en vivo de `fixi resolve` contra Azure DevOps** — no contra GitHub. 99% de nosotros corre en ADO. El rehearsal ADO esta pendiente en el BOARD (S1-T15 cancelado, S2-T18 en GitHub). Eso **lo quiero ver con mis ojos**.
3. **Un ticket donde Fixi se detenga y diga "me falta informacion"**. Quiero confirmar que el halt-and-ask funciona en la practica, no solo en el guardrail.

### 3.5 Que sobra
- **Terraform con 5 modulos en Azure** (Container Instances, ACR, Key Vault, VNet, Managed Identity, ~1,955 lineas HCL). Para un PoC — **eso sobra**. Un `docker run` con las env vars me basta. El IaC lo veo cuando pasemos a piloto.
- **El MCP Server y A2A del roadmap expandido** — sobra para esta fase. Primero demuestrenme que 10 tickets corren limpios, despues hablamos de protocolos.

### 3.6 Que falta
- **Capability #2 (priorizar)**: Fixi **lee** la prioridad del work item, no la re-calcula contra el resto del backlog. Si me llegan 10 tickets el lunes, no me dice cual atacar primero. Eso no es lo que yo pedi literalmente, pero lo asumi implicito.
- **El rehearsal contra Azure DevOps con `az repos pr create` real**. El codigo esta en `SKILL.md` Paso 8, pero no lo he visto corriendo end-to-end. Hasta no verlo, para mi es **NO VISTO**.
- **Metricas sobre mas de 1 ticket.** El smoke test de $0.61 y 4.3 min es UN ticket (WI-101). Necesito el numero de los 3 tickets sembrados, minimo.

### 3.7 Veredicto
Desde mi desconocimiento: Fixi **cumple las 9 capabilities en papel**, y en el unico rehearsal documentado (WI-101, GitHub) demuestra que el arco completo funciona — parse → clasifica → rama → fix → tests → PR → tracking en 4.3 min y 61 centavos. Eso es respetable y es mas de lo que ChatGPT solo me da. Pero esto no me alcanza para firmar un piloto todavia. Lo que necesito en la siguiente iteracion, en este orden: (1) el rehearsal ADO con `az repos pr create` corriendo en vivo, (2) los 3 tickets del demo corridos en batch con las metricas agregadas, no 1, y (3) un halt-and-ask real en pantalla donde Fixi diga "no tengo datos, paro aca". Con esas tres cosas aterrizo el business case. Sin eso, sigue siendo un PoC bonito que no se diferencia lo suficiente de lo que puedo armar en Power Platform + ChatGPT en una tarde. **Mientras conversabamos, yo ya tengo mi plan de trabajo — lo que necesito es ver a Fixi ejecutarlo, no describirlo.**

---

## 4. Liset — Lider Datos+IA / Centro de Aceleracion

### 4.1 Sustainability tecnica
**Depende-de-que.** Tiene bases solidas pero veo gaps que pueden acumular deuda rapido:

- El skill se auto-impone "cambio minimo, nada mas, nada menos" (Paso 6) y tiene guardrail de ">15 archivos = escalar a GUIDED". Eso controla el blast radius — bien.
- Pero el agente **no tiene un modelo de lo que ya toco antes** en ese repo. Cada run arranca desde cero con `tempfile.mkdtemp(prefix="fixi-")` y `git clone --depth 50`. Si el mismo modulo recibe 20 fixes en 6 meses, nadie esta midiendo si la entropia del codigo sube. No hay metricas de duplicacion, acoplamiento, ni drift arquitectonico post-fix.
- Los estandares los carga del repo (`.editorconfig`, eslint, ruff, etc.) — eso tiene sentido. Pero "respetar el linter" no es lo mismo que "respetar la intencion arquitectonica del modulo". Ahi es donde tipicamente se genera deuda silenciosa.

### 4.2 Memoria y aprendizaje (R-system check)
**No encontre nada parecido a R.** Lo revise explicitamente:

- `grep -ri "memory|learning|reinforcement|retrospective"` en `agent/` → cero matches.
- El `orchestrator.py` usa `structlog` para logging operacional pero no persiste aprendizajes entre runs. El `RunResult` tiene `total_cost_usd`, `num_turns`, `files_changed` — metricas de ejecucion, no de calidad.
- `cloner.py` clona a tmpdir y hace `shutil.rmtree` al terminar. Todo contexto se tira.
- No hay RAG sobre PRs historicos, no hay vector store de "fixes rechazados por review", no hay un feedback loop del reviewer humano de vuelta al agente.

**Lo que falta explicitamente**: un store de iteraciones calificadas (PR merged / PR rejected / PR revert) que alimente el prompt del proximo run. Sin eso, Fixi va a cometer el mismo error de criterio 50 veces si el equipo no lo atrapa cada vez en review. Eso es exactamente lo que el R evita en nuestro stack.

### 4.3 Sincronizacion con repos
Debil. Lo que encontre:

- `clone_repo()` hace shallow clone (`--depth 50`) a un tmpdir unico por run — eso da aislamiento entre runs paralelos (dos agentes no pisan el mismo filesystem).
- Guardrail #4 aborta si working tree esta dirty al inicio.
- Paso 5 hace `git pull origin {default_branch}` antes de crear la rama.
- **Pero no hay logica de "el base branch cambio mientras yo analizaba"**. Si dos agentes analizan el mismo modulo en paralelo y ambos crean branches desde el mismo SHA, el segundo PR va a tener merge conflicts o, peor, va a sobreescribir intencion del primero. No veo un `git fetch` + re-check del HEAD antes del push, ni lock optimista por archivo.
- No hay coordinacion entre instancias del agente. Si orquestan N workers contra la misma cola de tickets, la sincronizacion queda en manos del reviewer humano.

### 4.4 Conexion con iniciativas internas de GlobalMVM
- **Centro de Aceleracion**: no duplica nada visible, pero tampoco se integra. Fixi hoy escribe tracking a `consultoria-x/mission-control/tasks.json` (el sistema interno del vendor), no al nuestro. Si lo adoptamos habria que reescribir Paso 9 hacia nuestros dashboards.
- **Trabajo de Carlos (regression prevention)**: **se complementa, no compite** — y es precisamente donde falta integracion. Fixi aplica el fix, Carlos previene que ese fix rompa lineas funcionando. Pero Fixi no consulta a Carlos antes de commitear. Un hook `PreToolUse` que llame al regression-prevention agent antes del `Edit` seria el match natural.
- **Azure DevOps**: **solido**. Detecta `dev.azure.com`, usa `az boards work-item show`, linkea PR ↔ Work Item con `az repos pr work-item add`, mapea campos de ADO (System.Title, Priority, WorkItemType). Es la integracion mas madura que tiene.

### 4.5 Preguntas que aun no tengo claro
1. Como sincronizas dos runs concurrentes sobre el mismo repo? Hay lock a nivel de modulo o es el reviewer el que hace merge?
2. Como evitas que Fixi repita el mismo error de criterio dos semanas despues? Donde vive la memoria post-PR-review?
3. El `RunResult` captura el outcome, pero que pasa con los PRs rechazados o revertidos — alimentan algo, o se pierden?
4. Un hook de pre-commit que consulte al agente de Carlos antes de cada `Edit` — viable en el SDK actual, o requiere refactor del loop?
5. Los 136 unit tests cubren el orquestador, pero hay alguna metrica de **calidad del fix** medida a posteriori (bugs reabiertos, revertidos, touched-again)?

### 4.6 Veredicto
El core workflow y los guardrails tienen sentido — Paso 0, hooks PreToolUse, escalacion automatica a GUIDED en security/migrations, rollback automatico, todo eso es higiene solida. **La integracion con Azure DevOps tambien tiene sentido**, es concreta y usable hoy. Pero **esto me preocupa en deuda tecnica**: sin R-system, sin memoria entre runs, y sin sincronizacion optimista contra el repo base, cada fix es un evento aislado. A 50 tickets por mes durante un ano son 600 fixes sin aprendizaje acumulado — el agente no va a ser mejor en el mes 12 que en el mes 1. Antes de ir a piloto real yo exigiria, minimo: (a) un store de outcomes post-review que alimente el prompt, (b) un hook que conecte con el regression agent de Carlos, y (c) logica de re-fetch del base branch antes del push. Sin eso es automatizacion, no aprendizaje.

---

## 5. John Bairo Gomez — Arquitecto (escalability + adopcion)

### 5.1 Escalabilidad horizontal y vertical
**Horizontal**: Veo que el agente es un binario que se lanza desde un pipeline (GitHub Actions / Azure Pipelines) y cada invocacion clona el repo a un temp dir propio. En teoria puedo tirar 50 agentes en paralelo porque cada uno vive en su runner aislado, pero los gates reales que veo son cuatro y ninguno esta resuelto en los docs. **Uno**, rate limits del provider (Anthropic API) y del git host — si 50 agentes abren 50 PRs al mismo tiempo contra el mismo repo, Azure DevOps y GitHub me van a tirar throttling y no veo en `guardrails.md` una estrategia de backoff ni cola. **Dos**, el costo: $0.61 por ticket × 30 tickets/semana × 10 devs = ~$180/semana solo en un equipo, y GlobalMVM tiene decenas de equipos. No hay matriz de costo proyectada. **Tres**, git conflicts: el Paso 5 hace `git pull origin master` y crea branch, pero si 50 agentes corren contra el mismo repo y el mismo modulo, los PRs van a pisarse en review — no vi lock de modulos ni deteccion de colision entre tickets in flight. **Cuatro**, autenticacion: cada runner necesita PAT de Azure DevOps con permisos de escritura, y multiplicar esos tokens es un problema de gobernanza que el Key Vault Terraform soluciona pero no documenta para N instancias concurrentes.

**Vertical**: Aqui me preocupa mas. El guardrail #6 dice textual: ">15 archivos = escalar a GUIDED". Eso significa que Fixi, por diseno, **no resuelve solo** tickets que tocan 50 archivos o refactors de monorepo. Se vuelve un asistente que pide OK en cada paso, no un agente autonomo. Para un monorepo real de GlobalMVM (EnergySuite tiene modulos C#, Angular, pipelines compartidos) eso significa que Fixi sirve para el 60-70% de tickets chicos y se degrada al resto. Ademas el guardrail #12 pone un limite de 10 minutos para root cause — un monorepo grande no se analiza en 10 minutos. Ese techo vertical no esta dimensionado en el `CLIENT-FACING.md` y deberia estarlo.

### 5.2 Adopcion humana — el problema que MAS me importa
Saul, este es el que me quita el sueno, no el de blockchain. Veo en `CLIENT-FACING.md` frases como "multiplica capacidad" y "equipo de 10 produce como equipo de 13-14" — eso es exactamente el mensaje que hace que un dev senior se sienta amenazado, y no vi en ningun lado una seccion sobre **manejo del cambio**. Mi gente mayor no va a adoptar una herramienta que le diga "ahora produces como 1.3 devs" porque oyen "estas a 0.3 de ser prescindible". Preguntas que necesito que respondas antes del piloto: que hace Fixi **por** el dev que lo haga quererlo (no solo cumplir una orden del arquitecto), como entrena al dev junior sin que copie PRs a ciegas, donde esta el playbook de "que hacer cuando el PR de Fixi es incorrecto" (no lo encontre), y como vamos a manejar al dev que resiste por desconocimiento versus el que resiste por temor — son dos problemas distintos con dos soluciones distintas. El framing tiene que ser "Fixi se come la parte aburrida, tu haces arquitectura" no "Fixi te hace 30% redundante".

### 5.3 Matriz de decision (primera iteracion)

| Caso | Fixi SI | Fixi NO | Razon |
|---|---|---|---|
| Bug con stack trace claro, 1-3 archivos | SI | | Paso 4.2 analiza stack trace directo, modo FULL_AUTO seguro |
| Perf (N+1, timeout localizado) | SI | | Precedente: WI-102 del demo, clasificacion `performance` resuelta |
| Security (auth, injection, CVE) | | NO autonomo | Guardrail fuerza GUIDED — util pero **no ahorra tiempo senior**, solo lo asiste |
| DB migrations / schema changes | | NO | Guardrail #9 fuerza GUIDED explicito |
| Refactor >15 archivos / cross-module | | NO | Guardrail #6 degrada a GUIDED, pierde el valor de autonomia |
| Tickets sin repro steps ni evidencia | | NO | Guardrail #10 (halt-and-ask) — Fixi se detiene, no adivina |
| Feature nueva con diseno de producto pendiente | ? | ? | No vi evidencia de como maneja ambiguedad de diseno. Marco **?** hasta que Saul muestre un caso |
| Hotfix en produccion con SLA de minutos | ? | ? | 4.3 min de ejecucion + review humano suena bien, pero no vi test de carga ni SLO definido. **?** |
| Tickets en repo sin tests existentes | SI con disclaimer | | Paso 7 acepta N/A, pero el reviewer queda ciego — riesgo medio |
| Monorepo con pipelines compartidos | | NO | Guardrail #8 fuerza GUIDED en CI/CD, + limitante vertical |

Las dos celdas con **?** son el gap mas grande: feature nueva y hotfix productivo. Son exactamente los dos casos donde un agente tiene mas valor de negocio y donde el repo no tiene evidencia aun.

### 5.4 Alta transaccionalidad — scorecard

| Aspecto | Estado | Evidencia |
|---|---|---|
| Reintentos | **Parcial** | Paso 7 reintenta validaciones hasta verde, pero no vi retry policy para API de Anthropic ni para `gh`/`az` CLI |
| Rollback automatico | **SI** | Guardrail #11 + Paso 10 — borra branch y vuelve al original si falla cualquier paso |
| Observabilidad / logging | **Parcial** | Hook `PostToolUse` → JSONL (S2-T09 hecho), pero no vi integracion con App Insights ni dashboard |
| Rate limiting propio | **NO** | No vi semaforo ni throttle del lado del agente. Es el gate mas fuerte para concurrencia alta |
| Idempotencia | **NO documentada** | Si el mismo WI se procesa dos veces, que pasa? No vi check de "este WI ya tiene PR abierto" |
| Audit trail | **SI** | Triple-write (ACTIVO.md + Mission Control + inbox) del Paso 9 |

Para alta transaccionalidad real necesito rate limiting, idempotencia y metricas exportadas. Hoy Fixi esta en 3/6.

### 5.5 Redirect
Saul — vi en `docs/CLIENT-FACING.md` bastante enfasis en Terraform (25 archivos, 5 modulos, ~$25-30/mes). Eso esta bien pero **mi foco no es ese**. Mi foco es adopcion humana y matriz de decision. La infra la revisa Joaris o el equipo de plataforma. Cuando volvamos a revisar el PoC, partamos por los dos **?** de la matriz y por la tabla de manejo del cambio para devs senior — no por el HCL.

### 5.6 Veredicto
Fixi es una tecnologia bien traida: los 13 guardrails, la clasificacion, el halt-and-ask y el rollback automatico me dan confianza de que no es un agente ciego, y el smoke test de 4.3 minutos sobre WI-101 es prueba real, no demo. **Pero hoy no la estoy metiendo a la fuerza — la estoy metiendo incompleta.** El PoC prueba el caso facil (bug localizado con stack trace) y no prueba los dos casos de mayor valor (feature con ambiguedad, hotfix bajo SLA) ni responde la pregunta de adopcion. Mi recomendacion: piloto acotado en un equipo chico, con las dos celdas **?** como hipotesis a validar, y un playbook de manejo del cambio escrito **antes** de que anunciemos Fixi al resto de los equipos. Sin esos dos, el tooling es bueno y el rollout fracasa.

---

## 6. Jenny Pedraza — PO Energy Suite

### 6.1 Impacto en Energy Suite
Candidatos claros en mi backlog: bugs reportados por soporte (lecturas raras en calculadora de consumo, timeouts en reportes), deuda tecnica acumulada de los ultimos sprints, correcciones cosmeticas y de textos. Features no las metiria a un agente todavia — las features nuestras requieren conversacion con el cliente, no solo un ticket bien redactado.

Bloqueos que veo: Energy Suite tiene partes heredadas donde el "codigo relacionado" no esta obvio ni para un humano senior. Ahi Fixi va a tener que detenerse y preguntar mucho — lo cual esta bien, pero hay que medirlo antes de prometer los numeros del CLIENT-FACING.

### 6.2 Impacto en clientes finales
EPM, ISAGEN, XM y Veolia no deberian notar nada distinto — y eso es exactamente lo que quiero. Si lo notan, algo salio mal.

Lo que me importa es el lado de compliance. Nosotros trabajamos bajo CMMI y ISO 9001 como cultura de casa. Un PR generado por agente tiene que dejar trazabilidad clara de quien pidio el cambio, quien lo aprobo, y contra que ticket. El doc habla de audit trail y de que nunca se mergea sin revision humana — bien. Pero antes de pilotearlo con codigo que termina tocando facturacion de EPM, quiero ver como se documenta eso para una auditoria externa.

### 6.3 Ownership post-implementacion
Esta es mi pregunta de siempre y no la veo resuelta en el doc. Cuando Saul entrega el PoC: quien opera Fixi? Quien responde cuando un PR del agente rompe produccion? Quien paga el Anthropic API key y bajo que centro de costos? Quien decide el nivel de autonomia por proyecto?

El CLIENT-FACING lista "proximos pasos" pero no lista un dueno. Necesito que eso quede explicito antes del piloto — idealmente no soy yo, porque mi foco es Energy Suite, no una plataforma interna de devtools.

### 6.4 Integracion con roadmap existente
No tengo evidencia en los docs de como Fixi se conecta con nuestro roadmap de Energy Suite. El doc describe la herramienta, no su encaje en nuestros flujos de Azure DevOps reales, ni en los ceremoniales del equipo (refinement, planning, retro). Eso lo veo mejor en la reunion de aclaracion.

### 6.5 Veredicto breve
**Necesito dos cosas para poder evaluarlo**: (1) el rehearsal por el path Azure DevOps — nosotros corremos sobre ADO, el de GitHub me sirve poco; (2) un dueno claro post-PoC. Con eso hablamos de piloto acotado, probablemente en un proyecto que no toque facturacion de clientes.

---

## 7. Victor Orrego — Director de Operaciones (origen del use case)

### 7.1 Mi caso original — cubierto?

| Paso | Cubierto | Evidencia |
|------|----------|-----------|
| 1. Llega requerimiento / incidente | SI | CLIENT-FACING.md: Azure DevOps, GitHub Issues, Jira, Linear, texto libre |
| 2. Tipificar / categorizar | SI | README: taxonomia 7 tipos, prioridad security>bug>perf>feat>refactor>docs>chore |
| 3. Identificar repositorio de codigo | SI | CLIENT-FACING: "Analiza el codigo fuente para encontrar la causa raiz - no adivina" |
| 4. Modificar el codigo necesario | SI | CLIENT-FACING: "Implementa el cambio minimo necesario". WI-101 demo: +5/-2 lineas, 1 archivo |
| 5. Hacer los test cases | **PARCIAL** | CLIENT-FACING: "Ejecuta tests y documenta". Corre tests existentes. NO queda claro si **genera nuevos** test cases — solo los corre |
| 6. Dejar PR listo para aprobacion | SI | PR `fixi-demo-dotnet#1` real, rehearsal 2026-04-07, 3m 51s |

**Veredicto del checklist: 5.5/6.** El paso 5 necesita aclaracion — yo pedi "hacer los test cases", no solo correrlos.

### 7.2 Numeros — yo vivo de numeros

| Metrica | Valor declarado | Mi evaluacion |
|---------|----------------|---------------|
| Tiempo humano por ticket (sin Fixi) | 45-210 min | **Creible**. Rango amplio, honesto |
| Tiempo humano por ticket (con Fixi) | 5-15 min review | **Creible** si el PR viene limpio |
| Ahorro promedio | 60 min/ticket | **Optimista**. Toman el midpoint del rango bajo. Pido ver distribucion real |
| Costo por ticket | $0.61 USD | **Creible pero N=1**. Un solo smoke test no es estadistica |
| Tiempo agente | 4.3 min (o 3m 51s) | **Creible pero N=1** |
| Proyeccion 30h/semana | 30 tickets x 60 min | **Exagerado**. Asume 100% exito. Sin tasa de rechazo de PR, el numero es papel |
| "3.75 devs equivalentes" | Derivado | **Necesito evidencia**. Depende del 60min que no esta validado |

**Gap critico: no hay tasa de exito del agente.** Si 30% de los PRs los rechaza el reviewer y toca rehacer, el ahorro cae a ~40 min/ticket, no 60.

### 7.3 Calculo propio — ROI 3 / 6 / 12 meses

Supuestos:
- 10 devs x 3 tickets/sem x 4.3 sem = **129 tickets/mes**
- Ahorro 60 min = 129 horas/mes (**SUPUESTO**: asume tasa exito 100%)
- FTE Colombia $4,500/mes / 160h = **$28/hora**
- Ahorro bruto = 129h x $28 = **$3,612/mes**
- API Anthropic: 129 x $0.61 = **$79/mes** (**SUPUESTO**: costo smoke test aplica a todos los casos)
- Mantenimiento Saul: **$2,000/mes** (estimado conservador, 0.4 FTE)
- Training inicial: $3,000 one-time (mes 1)

| Horizonte | Ahorro bruto | Costo API | Mant. | Training | **Neto** |
|-----------|-------------|-----------|-------|----------|----------|
| 3 meses | $10,836 | $237 | $6,000 | $3,000 | **+$1,599** |
| 6 meses | $21,672 | $474 | $12,000 | $3,000 | **+$6,198** |
| 12 meses | $43,344 | $948 | $24,000 | $3,000 | **+$15,396** |

**Pay-back: ~2.8 meses** en el escenario optimista. Si la tasa de exito cae a 60%, pay-back se estira a ~5 meses. Si cae a 40%, no hay ROI.

### 7.4 Capacity de devs liberada
Con los supuestos arriba (100% exito, 60 min/ticket): **129 h/mes liberadas = 0.8 FTEs equivalentes** sobre un equipo de 10. El cliente-facing dice 3.75 devs — **eso asume 30h/semana continuas, no 129h/mes**. Matematica inconsistente o yo leyendo mal el periodo.

**Conclusion honesta: entre 0.8 y 3.75 FTEs liberados, dependiendo de como se mida. Necesito piloto de 4 semanas con tasa de exito medida para darte el numero real.**

### 7.5 TCO anual
- **API Anthropic**: ~$950-$2,000/ano (depende de volumen real y tokens por ticket, $0.61 es smoke test controlado)
- **Mantenimiento Saul**: ~$24,000/ano (0.4 FTE sosteniendo el agente, parchando clasificadores, ajustando guardrails)
- **Training + onboarding + infra Azure** (ACI/KV/ACR segun Terraform): ~$3,000-$6,000/ano

**TCO estimado: $28k-$32k/ano** para 10 devs. Contra $43k de ahorro bruto = margen ajustado pero positivo.

### 7.6 Veredicto operacional
Veo impacto operativo **potencial**, no probado. Los numeros del smoke test son N=1 sobre un bug sembrado a proposito en un repo demo — no es evidencia de produccion. El pay-back de 2.8 meses depende de una tasa de exito del 100% que nadie ha medido. Lo que yo necesito para firmar: **piloto controlado de 4 semanas con 1 equipo de 5 devs sobre un repo real de GlobalMVM, midiendo (a) tasa de PRs aceptados sin cambios, (b) tiempo medio de review humano, (c) costo API real por ticket, (d) tickets escalados por falta de datos**. Sin esos 4 numeros no autorizo expansion. El paso 5 de mi caso original ("hacer los test cases") me preocupa — quiero confirmar en vivo si Fixi **genera** tests nuevos o solo corre los existentes. Siguiente validacion: piloto real, no mas demos.

---

## 8. Carlos Caicedo — Dev Senior / Regression Prevention

### 8.1 Los 13 guardrails — evaluacion honesta
- G1 (NUNCA main/master/develop): **DEBIL** — el hook solo chequea `"checkout main"` dentro del mismo comando. Si el agente ya esta parado en `main` (porque Paso 0 no se ejecuto o el working tree chequeo se salto), `git commit` pasa sin que el hook lo detecte. El hook nunca corre `git branch --show-current`.
- G2 (NUNCA force push): **OK** — cubre `--force`, `-f`, `--force-with-lease`.
- G3 (NUNCA modificar fuera del repo): **DEBIL** — no veo hook que compare el `file_path` contra `git rev-parse --show-toplevel`. El SDK tiene `cwd`, pero si el agente escribe un path absoluto fuera de esa raiz, nada lo para.
- G4 (ABORT si working tree dirty): **DEBIL** — esto vive en el prompt (Paso 0), no hay hook. Si el modelo se salta el Paso 0 bajo presion, no hay red de seguridad mecanica.
- G5 (verificar contexto de cliente): N/A para mi rama.
- G6 (limite >15 archivos → GUIDED): **DEBIL** — no veo enforcement en hooks ni conteo en `orchestrator.py`. Es una instruccion al modelo, nada mas. El modelo decide cuando escalar.
- G7 (NUNCA archivos sensibles): **OK** — `SENSITIVE_FILE_PATTERNS` cubre bien, y el propio test file admite el falso positivo aceptable en `.env.example` (prefieren ser conservadores, me parece bien).
- G8 (NUNCA CI/CD sin GUIDED): **DEBIL** — el hook deniega directo, no "escala a GUIDED". Eso rompe el flujo cuando el fix legitimamente necesita tocar el pipeline. El prompt dice "forzar GUIDED", el hook dice "deny". No matchea.
- G9 (NUNCA DB migrations sin GUIDED): **DEBIL** — mismo problema que G8. Tambien, `\.sql$` en `MIGRATION_PATTERNS` matchea CUALQUIER `.sql`, no solo migrations. Un seed file o query de reporte queda bloqueado.
- G10 (NUNCA inventar info): N/A para mi rama, pero apunto que esto vive 100% en el prompt, sin enforcement mecanico.
- G11 (rollback automatico): **DEBIL** — esta en el prompt (Paso 10), pero no veo logica de cleanup en `orchestrator.py`. Si el proceso muere a mitad de camino, la rama queda huerfana y el `tempfile.mktemp` tampoco se borra (tiene `finally` para eso, pero no para el git state).
- G12 (10 min root cause): N/A para mi rama.
- G13 (verificar remote): **DEBIL** — el hook solo logea, no verifica. El comentario en el codigo lo admite literalmente: "we can't fully verify the remote in a hook".

### 8.2 Casos edge que los 13 guardrails NO cubren

**Caso edge 1: Cambio pasa tests locales pero rompe consumidores downstream**
El repo cambiado es una libreria publicada, o un paquete interno que otros modulos consumen por version pinned. Fixi corre `npm test` y ve verde, pero no sabe de los 12 proyectos que la importan.
*Mitigacion*: detectar `package.json` con `"main"/"exports"` o artefactos publicables y marcar riesgo automatico HIGH + bloquear FULL_AUTO.

**Caso edge 2: Private API tocada, otro modulo la usa por reflexion/DI**
Fixi renombra un metodo "privado" porque nadie lo importa directamente. Pero otro modulo lo resuelve por string (DI container, reflexion .NET, `getattr` en Python, anotaciones Spring). Los tests del modulo tocado pasan. Los del consumidor estallan en runtime.
*Mitigacion*: grep del nombre del simbolo como string literal en todo el repo antes de renombrar.

**Caso edge 3: Dos Fixi corren en paralelo sobre el mismo repo**
Dos tickets se disparan al mismo tiempo. Ambos hacen `git checkout default && git pull`, ambos crean ramas, y el segundo puede pisar el working tree del primero. No veo lockfile ni flock en `orchestrator.py`, y el clone es a `tempfile` pero si alguien pasa `--repo-path` local, colision garantizada.
*Mitigacion*: file lock por repo path, o forzar clone a tempdir siempre.

**Caso edge 4: Linter "arregla" y rompe semantica**
El agente corre `ruff check --fix` o `dotnet format` despues del cambio. El autofix toca un archivo NO relacionado con el issue (un import reordenado, un `==` → `is`) y rompe comportamiento sutil. El diff del PR ahora tiene ruido + un bug nuevo.
*Mitigacion*: correr linter solo sobre los archivos cambiados por el fix, no sobre `.` completo. Y NUNCA `--fix`, solo `--check`.

**Caso edge 5: Tests flakeados pasan por suerte**
Fixi ve tests verdes y asume OK. Pero los tests son flaky (race, timing, orden) y el verde es casualidad. El fix introdujo una regression que aparece 1 de cada 5 corridas.
*Mitigacion*: correr la suite afectada 3 veces antes de PR. Si hay diferencia, flag.

**Caso edge 6: Snapshot de "pre-existente fails" se toma en la rama equivocada**
Paso 7.3 dice "correr validacion contra branch base antes de crear la rama del fix para comparar". No veo esto implementado en ningun lado — ni en SKILL.md como comando concreto, ni en orchestrator. Si no se hace, "pre-existente vs nuevo" es opinion del modelo.
*Mitigacion*: snapshot real en Paso 0, guardar JSON con pass/fail por test. Comparar en Paso 7.

**Caso edge 7: Agente borra un test que "fallaba por su culpa"**
Edge clasico de RL mal alineado: el modelo aprende que "test rojo = malo" y en vez de arreglar el codigo borra o skipea el test. Nada en los hooks bloquea `Edit` sobre un archivo `test_*.py` o `*_test.go`.
*Mitigacion*: hook que deniega DELETE/skip/xfail en archivos de test salvo que el usuario lo apruebe explicito.

**Caso edge 8: `.sql` no-migration bloqueado**
Ya mencionado en G9. Un seed, un fixture, un query de reporte en `sql/reports/top_users.sql` queda bloqueado aunque nada tenga que ver con un schema change.
*Mitigacion*: reducir el pattern a `migrations?/.*\.sql$` y `alembic/.*\.sql$`, no `\.sql$` pelado.

### 8.3 Regression tests del propio Fixi
Revise `agent/tests/unit/`. Hay 5 archivos: `test_hooks.py`, `test_orchestrator.py`, `test_parser.py`, `test_prompts.py`, `test_cloner.py`.

**Que cubren bien**:
- Patterns regex de sensitive files / CI-CD / migrations (unit tests aislados)
- Deny/allow de cada hook individual con inputs mockeados
- Extractors del orchestrator (PR URL, branch, classification, files) via regex sobre strings de output
- `make_hooks()` estructura

**Que NO cubren**:
- **Integracion end-to-end**: no hay un test que corra el orchestrator completo contra un repo dummy y verifique que no toco nada fuera de scope
- **Race conditions / concurrencia**: zero tests multi-proceso o multi-thread
- **Regression del propio agente**: no hay un "fixture de regresiones conocidas"
- **Falsos positivos del linter**: nada testea el flujo de "ruff --fix metio basura"
- **Escape del tempdir**: no hay test de "agente intenta escribir fuera de `cwd`"
- **Rollback real**: zero tests de "agente crasheo mid-fix, el branch se limpio"

Los tests actuales son basicamente unit tests de pattern matching. Sirven, pero no protegen del happy-path breaking que me preocupa.

### 8.4 Quien revisa el PR
Respuesta corta: **nadie automaticamente**.

Lo que encontre: el agente crea el PR con `gh pr create` o `az repos pr create`, escribe el body con template, y termina con "NEXT: El developer puede ir al PR y revisar/probar. Asignar reviewer en {plataforma del cliente}". La asignacion del reviewer es manual, post-facto, a criterio del humano que ve el output.

No veo: default reviewer configurado por cliente, CODEOWNERS check antes de push, branch protection rules verification, bloqueo de auto-merge.

En FULL_AUTO un PR puede quedar abierto sin reviewer asignado y, si el repo del cliente tiene auto-merge por labels, se mergea solo. Eso es un escenario real que hay que documentar o bloquear.

### 8.5 Conexion con mi trabajo (R-system / RL)
**Fixi no aprende de fallos pasados.** No encontre: archivo de "fallos conocidos" / rejection memory, embeddings o lookup de "PRs rechazados con razon X", tabla de classifications que fallaron antes, sistema de scoring por iteracion, feedback loop del reviewer humano hacia el agente.

Cada run de Fixi es estatico: lee SKILL.md, corre, genera PR, muere. Si ayer Fixi clasifico mal un ticket como `refactor` cuando era `security`, manana lo vuelve a hacer identico. Si ayer `ruff --fix` rompio un archivo, manana lo romperia igual.

Donde lo meteria: un hook `SessionEnd` (o equivalente) que escriba un JSON con (work_item, classification, files_changed, tests_passed, reviewer_verdict_if_any) a un store persistente. Y un hook `SessionStart` que lea ese store y lo inyecte en el prompt como "contexto de errores pasados en este repo". Sin eso, Fixi es un pez con memoria de 3 segundos.

### 8.6 Veredicto
**Esto lo veo fragil en casos edge.** Los guardrails que existen estan bien pensados para amenazas obvias (secrets, force push, `rm -rf`, pipes a bash) y la cobertura unit de los patterns regex es decente. Pero la mitad de los 13 guardrails son instrucciones al prompt sin enforcement mecanico, varios hooks tienen un comentario en el propio codigo admitiendo que no verifican lo que deberian (G13 literal: "can't fully verify"), y los tres vectores que mas me preocupan — race entre agentes paralelos, consumidores downstream sin tests, y autolinter rompiendo semantica — no tienen ni hook ni test ni mencion en SKILL.md. Sumado a que no hay reviewer automatico asignado y cero memoria de fallos pasados, Fixi hoy es un agente que puede hacer el happy path perfecto y romper produccion en el dia que el ticket no sea un bug aislado de un solo archivo. Antes del PoC con Saul yo pediria: (a) snapshot real pre-fix de tests para comparar, (b) lock por repo path, (c) hook que deniegue deletes/skips en archivos de test, (d) linter solo sobre archivos tocados y sin `--fix`, (e) algun store minimo de regresiones para empezar a alimentar RL despues.

---

## Consolidated Findings

### Patrones que aparecen en 3+ agentes

#### 1. Rehearsal Azure DevOps es bloqueador universal (Elkin, Joaris implicito, Jefferson, Jenny, Victor, John Bairo)
**6 de 8 agentes** piden explicitamente ver el flujo Fixi → Azure DevOps corriendo en vivo antes de firmar cualquier cosa. El rehearsal actual es en GitHub (WI-101 en `fixi-demo-dotnet`). El handoff original de Sprint 1 tenia la tarea S1-T15 (rehearsal ADO con WI-102/WI-103) pero fue cancelada.

**Accion**: resucitar S1-T15 o crear S3-T13 para "rehearsal ADO end-to-end contra sandbox real". Esto cierra 6 de 8 objeciones de golpe.

#### 2. N=1 en metricas (Elkin, Jefferson, Victor, Joaris implicito)
El costo $0.61 y los 4.3 min son de UN solo ticket. Ningun numero proyectado es defendible contra alguien que sepa estadistica.

**Accion**: correr los 3 work items sembrados (WI-101, WI-102, WI-103) como batch y reportar metricas agregadas (media, min, max, std). Idealmente correr cada uno 3 veces para detectar varianza.

#### 3. Falta memoria inter-run / R-system (Liset, Carlos, Joaris lo pide como gap de Nivel 4)
**Tres agentes tecnicos independientes** identifican el mismo gap: Fixi es stateless por invocacion. No hay store de outcomes, no hay feedback loop del reviewer humano. "Pez con memoria de 3 segundos" (Carlos).

**Accion**: este es trabajo de Sprint 4. Diseno: hook `SessionEnd` → JSONL local + S3/Blob opcional con `(work_item, classification, files_changed, tests_passed, reviewer_verdict)`. Hook `SessionStart` retrieve-top-K contra este store para inyectar contexto de runs previos en el mismo repo.

#### 4. Adopcion humana no esta resuelta (John Bairo explicito, Jenny implicito, Elkin en "que va a mantenerlo cuando Saul no este")
El framing del CLIENT-FACING ("multiplica capacidad = equipo de 10 produce como 13-14") es politicamente toxico para devs senior. No hay playbook de "que hacer cuando el PR de Fixi es incorrecto". No hay seccion de manejo del cambio.

**Accion**: reescribir `docs/CLIENT-FACING.md` v4 con framing "Fixi se come la parte aburrida, tu haces arquitectura", agregar seccion "Playbook de manejo del cambio", documentar los 2 escenarios de resistencia (desconocimiento vs temor) y sus respuestas. **NO es trabajo de ingenieria — es trabajo de narrativa y debe hacerse antes de la proxima entrega**.

#### 5. Ownership post-PoC (Jenny, Elkin, Victor implicito)
Quien mantiene Fixi cuando Saul no este? Quien paga la API key? Quien decide el nivel de autonomia por proyecto?

**Accion**: agregar seccion "Modelo operativo post-entrega" al CLIENT-FACING, con propuesta explicita de 3 roles: (a) sponsor ejecutivo, (b) owner tecnico, (c) champion del equipo piloto.

### Gaps tecnicos concretos (de Liset + Carlos + John Bairo)

| # | Gap | Severidad | Sprint sugerido |
|---|-----|-----------|-----------------|
| 1 | G1-G4, G6, G8-G11, G13: enforcement vive en prompt, no en hook | Alta | S4 (reforzar hooks) |
| 2 | No lock por repo path — race entre agentes paralelos | Alta | S4 |
| 3 | No snapshot pre-fix de tests para comparar "nuevo vs pre-existente" | Alta | S4 |
| 4 | Hook que deniega delete/skip/xfail en archivos de test | Media | S4 |
| 5 | Linter solo sobre archivos tocados + NUNCA `--fix` | Media | S3 quick fix |
| 6 | No hay reviewer automatico asignado (CODEOWNERS / default reviewer) | Media | S4 |
| 7 | Rate limiting propio (Anthropic API + git host) | Media | S4 |
| 8 | Idempotencia: check "este WI ya tiene PR abierto" | Media | S4 |
| 9 | Retry policy para `gh`/`az` CLI | Baja | S4 |
| 10 | Integracion App Insights / dashboard exportado | Baja | S5 |

### Gaps estrategicos (de Joaris)

| # | Gap | Severidad | Sprint sugerido |
|---|-----|-----------|-----------------|
| 1 | RAG sobre base de conocimiento del cliente (wiki, ADRs, Confluence) | Alta | S4-S5 |
| 2 | MCP Servers por cliente (ADO boards, artifact feeds, DB schemas) | Media | S5 |
| 3 | Adapter para librerias cerradas del cliente (nugets privados) | Media | S5 |
| 4 | Telemetria agregada multi-cliente | Baja | S6 |

---

## Gap Analysis vs las 9 capabilities del prompt de Jefferson

Basado en la auditoria de Jefferson (seccion 3.1), con comentarios de los otros agentes:

| # | Capability | Cubierta? | Nota consolidada |
|---|---|---|---|
| 1 | Fuentes de conocimiento | **SI** | Jefferson OK. Joaris senala que falta RAG sobre docs del cliente **fuera** del repo (wiki, Confluence, ADRs externos). |
| 2 | Clasificar y priorizar | **PARCIAL** | Jefferson: Fixi lee la prioridad del work item, no la re-prioriza contra el resto del backlog. Si llegan 10 tickets el lunes, no dice cual atacar primero. |
| 3 | Validar codigo existente | **SI** | Jefferson OK. Carlos agrega que "validar" solo cubre el archivo tocado, no consumidores downstream. |
| 4 | Ajustes con buenas practicas y estandares | **SI** | Jefferson OK. Liset senala que "respetar linter" ≠ "respetar intencion arquitectonica". |
| 5 | Crear rama con nomenclatura | **SI** | Jefferson OK. Carlos senala que G1 es debil — si el agente ya esta en main, el hook no lo detecta. |
| 6 | Validaciones basicas | **SI** | Jefferson OK. Carlos: no hay snapshot pre-fix → "nuevo vs pre-existente" es opinion del modelo. |
| 7 | Commit claro | **SI** | Unanime. Sin objeciones. |
| 8 | PR con descripcion tecnica, cambios, impactos | **SI en template, NO VISTO en vivo para ADO** | Jefferson y Jenny: quieren verlo corriendo contra `az repos pr create` real. |
| 9 | Halt-and-ask | **SI en docs, NO VISTO en vivo** | Jefferson: "quiero confirmar que el halt-and-ask funciona en la practica, no solo en el guardrail". |

**Lectura**: Fixi cumple 9/9 **en documentacion y codigo**, pero 2 de las 9 (capabilities 8 y 9) no han sido demostradas en vivo contra Azure DevOps ni en un caso de halt-and-ask real. Esa es la siguiente entrega.

---

## Acciones prioritarias para la proxima entrega a GlobalMVM

### P0 — bloqueadores (hacer antes de la proxima reunion)

1. **Rehearsal ADO end-to-end** — WI-102 + WI-103 contra sandbox ADO, con `az repos pr create` real, PR linkeado al Work Item, video del run. Cierra 6/8 objeciones.
2. **Batch de 3 tickets** — correr WI-101, WI-102, WI-103 (los 3 sembrados) en la misma corrida. Reportar metricas agregadas: tiempo promedio, costo promedio, files_changed promedio, confianza promedio.
3. **Demo de halt-and-ask en vivo** — crear un WI deliberadamente ambiguo (sin repro steps) y mostrar que Fixi lo detecta y se detiene.
4. **Reescribir CLIENT-FACING v4** con:
   - Framing "Fixi se come la parte aburrida"
   - Seccion "Playbook de manejo del cambio"
   - Seccion "Modelo operativo post-entrega" (ownership)
   - Numeros corregidos: usar el batch de 3 tickets, no el N=1 de smoke test

### P1 — refuerzos tecnicos que se pueden hacer rapido

5. **Snapshot pre-fix de tests** — implementar en Paso 0 del SKILL.md, guardar JSON con pass/fail por test, comparar en Paso 7. Resuelve el gap de Carlos #6.
6. **Linter solo sobre archivos tocados, sin `--fix`** — quick fix en Paso 7 del SKILL. Resuelve gap de Carlos #4.
7. **Hook que deniega delete/skip/xfail en archivos de test** — nuevo hook en `hooks.py`. Resuelve gap de Carlos #7.
8. **Conteo mecanico de archivos afectados** — mover el guardrail #6 ">15 archivos" del prompt a un hook real que cuente `files_changed` post-fix. Resuelve gap de Carlos #1-G6.

### P2 — Sprint 4 candidates

9. Memoria inter-run (R-system minimo): hook `SessionEnd` + store JSONL
10. RAG sobre docs del cliente (wiki/Confluence/ADRs)
11. Lock por repo path + re-fetch del base branch antes de push
12. Rate limiting propio + idempotencia check

---

## Notas de metodo

- Los 8 agentes corrieron en paralelo via `general-purpose` subagent con briefing completo desde `.claude/agents/globalmvm-*.md`.
- Cada uno tuvo acceso de solo lectura al repo `Z:\fixi\` y al handoff source.
- **No son las personas reales** — son simulaciones basadas en UNA reunion (2026-04-06). Veredictos tipo "Jefferson dijo X" en este report deben leerse como "el agente Jefferson-simulado dijo X basado en el transcript del 2026-04-06".
- Los hallazgos deben validarse contra reacciones reales de GlobalMVM en la siguiente reunion. Los perfiles de los agentes deben actualizarse despues.

---

*Dry-run ejecutado 2026-04-08 · Sprint 3 · [[S3-T10]] · Ver [[faq-defensivo]] para las 20 preguntas mas dificiles derivadas de este ejercicio.*
