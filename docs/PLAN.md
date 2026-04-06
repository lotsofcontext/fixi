# PLAN: Fix-Issue Agent — Agente Autonomo de Resolucion de Tickets
#plan #skill #fix-issue

> Documento padre: [[MASTERPLAN]]
> Skill: [[SKILL|fix-issue workflow]]
> Spec: [[SPEC|Especificación técnica]]
> Diagramas: [[diagrams|Diagramas Mermaid]]
> Backlog: [[BACKLOG|Items pendientes]]
> Guardrails: [[guardrails|Reglas de seguridad]]
> Clasificación: [[classification|Taxonomía de 7 tipos]]
> Fecha: 2026-04-06
> Estado: EN DESARROLLO

---

## Vision

Saul maneja 2-4 empleos remote simultaneamente. Cada empleo genera tickets: bugs, features, refactors, issues de seguridad. El ciclo clasico — leer ticket, entender codebase, encontrar causa raiz, implementar fix, crear PR, actualizar tracking — consume entre 30 minutos y 4 horas por ticket. Multiplicado por 2-4 clientes, el throughput humano es el cuello de botella.

El **fix-issue agent** convierte ese ciclo en un comando: `/fix-issue`. Claude Code recibe el ticket (GitHub, Linear, Jira, o texto libre), lo clasifica, analiza el codebase del cliente, implementa la solucion, crea branch con commits convencionales, abre PR, y actualiza el tracking en tres lugares (ACTIVO.md del cliente, Mission Control tasks.json, activity-log.json). El resultado es un PR listo para review humano en minutos en vez de horas.

Esto no es "code generation" generico. Es un agente que entiende el contexto del cliente (convenciones, stack, equipo), respeta guardrails de seguridad (nunca opera en main, nunca toca credentials, rollback automatico), y se adapta al nivel de autonomia que Saul quiera: desde paso-a-paso (GUIDED) hasta ejecucion completa sin interrupciones (FULL_AUTO).

**Impacto esperado**: 3-5x mas tickets cerrados por bloque de trabajo. Saul revisa PRs en vez de escribir codigo desde cero. El tiempo liberado se usa para meetings, code reviews de alta complejidad, y relaciones con equipos.

---

## Objetivos

1. **Reducir tiempo promedio de resolucion de tickets** de 45-120 minutos a 5-15 minutos (tiempo humano, excluyendo review)
2. **Soportar las 4 fuentes de tickets mas comunes**: GitHub Issues, Linear, Jira, y texto libre
3. **Clasificar automaticamente** cada ticket en 7 categorias (bug, feature, refactor, security, performance, docs, chore) con confianza medible
4. **Crear PRs con calidad de produccion**: branch naming correcto, commits convencionales, descripcion completa con causa raiz, testing documentado
5. **Mantener tracking sincronizado** en triple-write obligatorio: ACTIVO.md del cliente + Mission Control (tasks.json, activity-log.json, inbox.json)
6. **Operar con 3 niveles de autonomia**: GUIDED (default, paso a paso), CONFIRM_PLAN (un OK ejecuta todo), FULL_AUTO (sin interrupciones)
7. **Nunca romper nada**: rollback automatico si algo falla, escalado a GUIDED si el scope es grande, ABORT si el repo no esta limpio
8. **Respetar aislamiento de clientes**: nunca operar en consultoria-x, cargar convenciones del cliente, no mezclar contextos

---

## Fases y Tareas

### Fase 1: Fundamentos (MVP)
**Meta**: Skill funcional end-to-end para GitHub Issues con modo GUIDED.

| # | Tarea | Descripcion | Entregable | Dependencia |
|---|-------|-------------|------------|-------------|
| 1.1 | Safety Gate (Paso 0) | Implementar verificacion de contexto: detectar que no estamos en consultoria-x, confirmar repo git, working tree limpio, identificar cliente, leer convenciones locales | Paso 0 del skill funcionando con ABORT correcto en cada caso | - |
| 1.2 | Parser de GitHub Issues | Implementar parsing de URLs de GitHub Issues (`github.com/.../issues/N`) y shorthands (`#N`, `GH-N`) usando `gh issue view` con fallback a input manual | Solicitud normalizada con title, body, external_id, labels, priority, source_type, source_url | 1.1 |
| 1.3 | Clasificacion basica por keywords | Implementar tabla de clasificacion con 7 tipos (bug, feature, refactor, security, performance, docs, chore) basada en matching de keywords contra titulo y body | Clasificacion con tipo, branch prefix, commit prefix, nivel de confianza (ALTA/MEDIA/BAJA), y razon | 1.2 |
| 1.4 | Analisis de causa raiz | Implementar busqueda de causa raiz: keyword search en codebase, analisis de stack traces, dependency tracing, examinacion de tests existentes | Hipotesis estructurada: QUE esta mal, DONDE, POR QUE, COMO arreglarlo, archivos a modificar, nivel de riesgo | 1.3 |
| 1.5 | Creacion de branch y commits | Implementar creacion de branch con naming convention (`{prefix}/{external_id}-{slug}`), checkout desde branch default, commits con formato convencional y referencia al issue | Branch creado, commits atomicos, formato correcto | 1.4 |
| 1.6 | Implementacion del fix | Implementar la logica de edicion de codigo: cambio minimo necesario, respetar convenciones del repo, ejecutar linter si existe, un commit por cambio logico | Archivos modificados y commiteados con mensajes correctos | 1.5 |
| 1.7 | Creacion de PR via `gh` | Implementar creacion de PR con template completo: seccion de issue, clasificacion, causa raiz, cambios por archivo, checklist de testing, tracking info | PR creado en GitHub con URL devuelta al usuario | 1.6 |
| 1.8 | Flujo GUIDED completo | Integrar todos los pasos con puntos de aprobacion: confirmacion despues de parseo, clasificacion, plan de fix, cada archivo modificado, PR, y tracking | Ejecucion end-to-end con aprobacion humana en cada paso | 1.7 |

---

### Fase 2: Multi-Source y Clasificacion Inteligente
**Meta**: Soporte para Linear, Jira, Azure DevOps, texto libre. Clasificacion con confianza porcentual y desambiguacion.
Ver: [[diagrams#2. Árbol de Clasificación|Diagrama de clasificación]]

| # | Tarea | Descripcion | Entregable | Dependencia |
|---|-------|-------------|------------|-------------|
| 2.1 | Parser de Linear tickets | Implementar parsing de URLs de Linear (`linear.app/.../issue/ABC-123`) con WebFetch y fallback a input manual cuando hay auth wall | Solicitud normalizada desde Linear con misma estructura que GitHub | Fase 1 completada |
| 2.2 | Parser de Jira tickets | Implementar parsing de URLs de Jira (`atlassian.net/browse/PROJ-123`) con WebFetch y fallback a input manual cuando hay auth wall | Solicitud normalizada desde Jira con misma estructura que GitHub | Fase 1 completada |
| 2.3 | Parser de texto libre | Implementar intake de descripcion libre sin URL: generar external_id (`FREE-{YYYYMMDD}-{slug}`), extraer titulo y body, inferir labels y prioridad del texto | Solicitud normalizada desde texto libre | Fase 1 completada |
| 2.4 | Parser de Azure DevOps Work Items | Implementar parsing de URLs de Azure DevOps (`dev.azure.com/{org}/{project}/_workitems/edit/{id}`) via `az boards work-item show` con fallback a WebFetch o input manual. Mapear fields de ADO (System.Title, System.Description, System.Tags) a estructura normalizada | Solicitud normalizada desde Azure DevOps con misma estructura que GitHub | Fase 1 completada |
| 2.5 | Deteccion automatica de formato | Implementar dispatcher que detecte automaticamente el tipo de input (GitHub URL, GitHub shorthand, Linear URL, Jira URL, Azure DevOps URL, texto libre) por regex matching y rutee al parser correcto | Unico punto de entrada que funciona con cualquier formato | 2.1, 2.2, 2.3, 2.4 |
| 2.6 | Clasificacion con confianza porcentual | Evolucionar la clasificacion de ALTA/MEDIA/BAJA a porcentaje numerico basado en: cantidad de keywords matcheados, presencia de stack traces, labels del issue, contexto del repo | Confianza expresada como 0-100% con umbral configurable para pedir confirmacion | 2.5 |
| 2.7 | Desambiguacion inteligente | Implementar logica para casos ambiguos (ej: "fix auth bypass" = security no bug): prioridad por severidad, preguntas dirigidas al usuario cuando confianza < 70% | Clasificacion correcta en casos edge con interaccion minima | 2.6 |
| 2.8 | Documento de referencia de clasificacion | Crear `references/classification.md` con taxonomia completa: keywords por tipo, ejemplos reales, casos edge documentados, reglas de prioridad entre tipos | Documento de referencia que el skill consulta para clasificar — ver [[classification]] | 2.7 |

---

### Fase 3: Autonomia y Testing
**Meta**: Modos CONFIRM_PLAN y FULL_AUTO funcionales. Deteccion y ejecucion automatica de tests.
Ver: [[diagrams#3. Niveles de Autonomía|Diagrama de autonomía]]

| # | Tarea | Descripcion | Entregable | Dependencia |
|---|-------|-------------|------------|-------------|
| 3.1 | Modo CONFIRM_PLAN | Implementar flujo donde el skill presenta el plan completo (clasificacion + causa raiz + archivos a modificar + estrategia de fix) y ejecuta todo con un solo OK del usuario | Flujo de un-solo-click que ejecuta pasos 4-8 sin interrupciones adicionales | Fase 2 completada |
| 3.2 | Modo FULL_AUTO | Implementar flujo sin interrupciones donde el skill ejecuta todo desde parseo hasta PR sin pedir confirmacion. Mantener escaladores automaticos que fuercen GUIDED (security, migrations, CI/CD, >15 archivos, causa raiz ambigua) | Ejecucion completa sin interaccion humana excepto en casos de riesgo | 3.1 |
| 3.3 | Deteccion automatica de test runner | Implementar deteccion del framework de testing del repo: buscar en CLAUDE.md, package.json (scripts.test), Makefile, pyproject.toml, Cargo.toml, go.mod. Soportar al menos Node/Jest, Python/pytest, Rust/cargo-test, Go | Test runner detectado y comando de ejecucion determinado automaticamente | Fase 2 completada |
| 3.4 | Ejecucion e interpretacion de tests | Implementar ejecucion de tests post-fix con interpretacion de resultados: tests pasan (continuar), fallan en nuestro codigo (arreglar), fallan pre-existentes (documentar en PR), no hay tests (notar en PR) | Tests ejecutados con resultado interpretado y accion tomada automaticamente | 3.3 |
| 3.5 | Generacion de test de regresion | Cuando el fix es non-trivial y no hay test que cubra el caso, generar un test de regresion que reproduzca el bug original y verifique que el fix lo resuelve | Test de regresion commiteado junto con el fix cuando aplique | 3.4 |
| 3.6 | Cambio dinamico de nivel de autonomia | Implementar que el usuario pueda cambiar nivel mid-execution: "sigue en auto", "para, quiero revisar", "rapido". El skill ajusta sin reiniciar el flujo | Transiciones fluidas entre GUIDED, CONFIRM_PLAN, y FULL_AUTO en cualquier momento | 3.2 |

---

### Fase 4: Tracking Triple-Write
**Meta**: Actualizacion obligatoria y confiable de ACTIVO.md + Mission Control (tasks.json, activity-log.json, inbox.json).
Ver: [[diagrams#4. Flujo de Triple-Write (Tracking)|Diagrama de triple-write]]

| # | Tarea | Descripcion | Entregable | Dependencia |
|---|-------|-------------|------------|-------------|
| 4.1 | Lectura y update de ACTIVO.md | Implementar lectura de `Z:\consultoria-x\clientes\{cliente}\tasks\ACTIVO.md`, busqueda por external_id o titulo, actualizacion de filas existentes o insercion de nuevas con formato correcto | ACTIVO.md actualizado con fila del issue y PR URL | Fase 1 completada |
| 4.2 | Creacion de ACTIVO.md si no existe | Cuando el archivo ACTIVO.md no existe para el cliente, crear la estructura basica (headers de tabla, formato correcto) y agregar la primera fila | Estructura de ACTIVO.md creada automaticamente para clientes nuevos | 4.1 |
| 4.3 | Update de Mission Control tasks.json | Implementar lectura de `mission-control/mission-control/data/tasks.json`, busqueda de task existente (por keywords o external_id en tags), actualizacion de kanban a "in-progress" con note de PR, o creacion de task nuevo con campos completos | Task en Mission Control creado o actualizado con PR URL | 4.1 |
| 4.4 | Escritura en activity-log.json | Implementar append de evento a `mission-control/mission-control/data/activity-log.json` con tipo "task_created", taskId, agentId "developer", details con titulo y PR URL, timestamp ISO8601 | Evento de actividad registrado en el log | 4.3 |
| 4.5 | Escritura en inbox.json | Implementar append de reporte a `mission-control/mission-control/data/inbox.json` con tipo "report", from "developer", to "me", subject y body descriptivos, status "unread" | Reporte en inbox para que Saul lo vea en Mission Control | 4.4 |
| 4.6 | Validacion de triple-write | Implementar verificacion post-escritura: confirmar que los 3 destinos fueron actualizados correctamente. Si alguno falla, reintentar una vez. Si sigue fallando, reportar cuales se actualizaron y cuales no (nunca silenciar errores) | Reporte de tracking con checkmarks por cada destino actualizado | 4.5 |
| 4.7 | Output final consolidado | Implementar el bloque de output final (FIX COMPLETE) que resume: issue, tipo, riesgo, branch, PR URL, archivos cambiados, resultado de tests, estado de tracking con checkmarks | Resumen ejecutivo impreso al final de cada ejecucion | 4.6 |

---

### Fase 5: Hardening y Guardrails
**Meta**: Seguridad robusta, rollback automatico, limites de scope, documentacion de referencia.
Ver: [[guardrails|13 reglas de seguridad]]

| # | Tarea | Descripcion | Entregable | Dependencia |
|---|-------|-------------|------------|-------------|
| 5.1 | Rollback automatico | Implementar rollback completo cuando algo falla mid-execution: guardar branch original, eliminar branch del fix, restaurar working tree, reportar en que paso fallo y que hacer manualmente | Rollback ejecutado automaticamente con reporte de fallo | Fases 1-4 completadas |
| 5.2 | Guardrails de scope | Implementar limites: si el analisis detecta >15 archivos afectados, escalar a GUIDED. Si la causa raiz es ambigua (multiples candidatos), escalar a GUIDED. Si el issue toca archivos protegidos (.env, credentials, keys), ABORT con explicacion | Escalado automatico que previene cambios de alto riesgo sin supervision | 5.1 |
| 5.3 | Proteccion de branches criticas | Implementar verificacion de que NUNCA se opera directamente en main, master, o develop. NUNCA force push. NUNCA push a branches protegidas. ABORT inmediato si se detecta intento | Bloqueo total de operaciones destructivas en branches criticas | 5.2 |
| 5.4 | Guardrails de seguridad de codigo | Implementar que el skill NUNCA modifique archivos .env, credentials, API keys, tokens. Si el fix requiere cambios en configuracion sensible, documentar en PR como instrucciones manuales | Archivos sensibles nunca tocados, instrucciones claras cuando se necesitan cambios manuales | 5.3 |
| 5.5 | Documento de guardrails | Crear `references/guardrails.md` con todas las reglas de seguridad documentadas: que se puede hacer, que NO se puede hacer, condiciones de escalado, condiciones de ABORT | Documento de referencia consultable por el skill y por Saul | 5.4 |
| 5.6 | Respeto de convenciones del cliente | Implementar carga de convenciones en orden de prioridad: CLAUDE.md del repo > CLAUDE.md del cliente en consultoria-x > defaults del skill. Aplicar convenciones a branch naming, commit format, estilo de PR | Convenciones del cliente siempre respetadas sobre los defaults | 5.5 |
| 5.7 | Manejo de errores de `gh` CLI | Implementar fallbacks para cuando `gh` falla: auth expirada, repo privado sin acceso, rate limiting, network errors. En cada caso, dar instruccion clara al usuario o pedir input manual | Experiencia robusta que no se rompe por problemas de autenticacion o red | 5.6 |
| 5.8 | Dry-run mode | Implementar modo `--dry-run` que ejecuta analisis y presenta plan completo sin hacer ningun cambio en el repo. Util para evaluar un ticket antes de comprometerse a resolverlo | Reporte completo de que haria el skill sin ejecutar cambios | 5.7 |

---

### Fase 6: Ecosistema, Infraestructura y Demo Publico
**Meta**: Fixi deployable en Azure, expuesto via MCP, descubrible via A2A, con demo publico verificable y capacidad de auto-mejora.
Ver: [[diagrams#5. Arquitectura de Integración|Diagrama de arquitectura]], [[BACKLOG|Items de backlog relacionados]]

| # | Tarea | Descripcion | Entregable | Dependencia |
|---|-------|-------------|------------|-------------|
| 6.1 | Azure DevOps PR creation | Implementar creacion de PRs via `az repos pr create` como alternativa a `gh pr create`. Detectar automaticamente si el remote es Azure Repos o GitHub y usar el CLI correcto. Branch naming compatible con convenciones Azure Repos | PRs creados en Azure Repos con el mismo template y calidad que GitHub | Fase 2 (parser ADO) |
| 6.2 | Azure Pipelines integration | Detectar `azure-pipelines.yml` como CI/CD. Verificar que pipeline corre post-push. Documentar resultado de pipeline en PR comments | Integracion con Azure Pipelines para validacion automatica post-push | 6.1 |
| 6.3 | Terraform — Azure Container Instances | Modulos Terraform para deployar Fixi como container en Azure: ACI, Container Registry, networking, managed identity. Variables para org-specific config | `terraform/` con modulos listos para `terraform apply` | Fases 1-5 estables |
| 6.4 | Terraform — Azure DevOps Project | Terraform para configurar Azure DevOps project: service connections, pipelines, repos, work item queries que alimenten a Fixi | Proyecto ADO configurado via IaC | 6.3 |
| 6.5 | MCP Server — Fixi como servicio | Exponer Fixi como MCP server con tools: `parse-issue`, `classify`, `analyze`, `implement`, `create-pr`. Autenticacion via tokens. Schema JSON para cada tool | MCP server funcional que otros agentes pueden llamar | Fases 1-5 estables |
| 6.6 | Agent Card (A2A discovery) | Publicar agent card en formato estandar: nombre, capabilities, endpoint, protocolo, autenticacion requerida. Endpoint `/.well-known/agent.json` | Fixi descubrible por otros agentes via A2A protocol | 6.5 |
| 6.7 | Demo publico — /status endpoint | Endpoint publico GET `/status` que retorna: version, capabilities, uptime, fixes recientes (count), health. Pagina HTML con visualizacion del estado | Endpoint publico para que GlobalMVM verifique operacion | 6.3 |
| 6.8 | Demo publico — /verify/:fix_id | Endpoint publico GET `/verify/:fix_id` que muestra: PR link, commits, archivos modificados, resultado de tests, evidencia de tracking. Todas las acciones del agente son auditables | Verificacion publica de cada fix ejecutado | 6.7 |
| 6.9 | Self-dogfooding — auto-analisis | Configurar Fixi para analizar su propio repo: linting, test failures, code smells generan issues automaticos. Fixi ejecuta `/fix-issue` contra sus propios tickets | Fixi mejora su propio codigo de forma autonoma | Fases 1-5 estables |
| 6.10 | Self-dogfooding — guardrails de recursion | Implementar limites para evitar loops infinitos en self-dogfooding: max fixes por dia, cooldown entre ejecuciones, no crear issues sobre issues que acaba de crear, human review gate para self-fixes | Guardrails que previenen runaway behavior | 6.9 |

---

## Criterios de Exito

El proyecto esta completo cuando se cumplan TODAS estas condiciones:

1. **End-to-end funcional**: `/fix-issue` resuelve un GitHub Issue real de un repo de cliente, desde URL hasta PR creado, en menos de 5 minutos de tiempo humano
2. **Multi-source**: El skill acepta tickets de GitHub, Linear, Jira, Azure DevOps, y texto libre sin configuracion adicional
3. **Clasificacion correcta**: En 10 tickets de prueba variados, la clasificacion automatica es correcta en al menos 8 (80% accuracy)
4. **Triple-write consistente**: Despues de cada ejecucion, ACTIVO.md, tasks.json, activity-log.json, e inbox.json estan actualizados correctamente
5. **Rollback confiable**: Si se fuerza un fallo en cualquier paso (3 al 8), el rollback deja el repo exactamente como estaba antes
6. **Zero incidents de seguridad**: En 20 ejecuciones de prueba, nunca se opera en main, nunca se tocan credentials, nunca se opera en consultoria-x
7. **3 niveles de autonomia**: GUIDED, CONFIRM_PLAN, y FULL_AUTO funcionan correctamente con transiciones mid-execution
8. **Convenciones respetadas**: PRs y commits siguen las convenciones del cliente cuando existen, y los defaults del skill cuando no
9. **Azure DevOps funcional**: Fixi crea PRs en Azure Repos y parsea Work Items de Azure DevOps correctamente
10. **Deployable via IaC**: `terraform apply` deploya Fixi en Azure sin intervencion manual
11. **MCP Server operativo**: Otro agente puede llamar a Fixi via MCP y recibir resultado estructurado
12. **Demo publico verificable**: `/status` y `/verify/:fix_id` accesibles y mostrando data real

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| **Fix incorrecto en FULL_AUTO** — el agente implementa un cambio que introduce un nuevo bug | Alta | Alto | Tests obligatorios post-fix. Escaladores automaticos para security, migrations, y scope grande. PR siempre requiere review humano antes de merge. Dry-run mode para tickets riesgosos |
| **Causa raiz mal identificada** — el agente arregla el sintoma en vez de la causa | Media | Alto | Presentar hipotesis estructurada con evidencia antes de implementar. En GUIDED mode, Saul valida la hipotesis. Clasificar confianza del analisis |
| **Tracking desincronizado** — alguno de los 3 destinos de tracking no se actualiza | Media | Medio | Validacion post-escritura con reintento. Reporte explicito de que se actualizo y que no. Nunca silenciar errores de tracking |
| **Repo sin tests** — no hay forma de verificar que el fix no rompe nada | Alta | Medio | Documentar en PR que no hay tests. Generar test de regresion cuando sea posible. No bloquear el fix por falta de tests existentes |
| **Auth de `gh` o `az` expirada** — el CLI falla en operaciones criticas | Media | Medio | Fallback a input manual del usuario. Instrucciones claras para re-autenticar. Detectar el error antes de hacer cambios. Soportar ambos CLIs |
| **Conflicto de contexto** — el skill se ejecuta accidentalmente en el repo equivocado | Baja | Critico | Safety Gate (Paso 0) es OBLIGATORIO y no se puede saltear. Verificacion de remote URL, confirmacion de cliente, ABORT si algo no cuadra |
| **Scope creep en el fix** — el agente modifica mas de lo necesario | Media | Medio | Regla de "cambio minimo". Guardrail de >15 archivos escala a GUIDED. No refactorizar codigo no relacionado. No agregar features no solicitadas |
| **Convenciones del cliente desconocidas** — primer ticket en un repo nuevo sin CLAUDE.md documentado | Alta | Bajo | Defaults sensatos (conventional commits, kebab-case branches). Detectar convenciones existentes del historial de git. Preguntar en GUIDED mode |
| **Self-dogfooding loop infinito** — Fixi crea issue, lo arregla, el arreglo crea otro issue, repite | Media | Alto | Max fixes por dia, cooldown entre ejecuciones, no crear issues sobre issues recien creados, human review gate para self-fixes. Ver [[guardrails]] |
| **MCP Server expuesto sin auth** — acceso no autorizado al agente | Media | Critico | Token-based auth obligatorio. Rate limiting. Audit log de todas las llamadas. Whitelist de callers si es posible |

---

## Timeline Estimado

Las fases no tienen fechas fijas. El orden de magnitud relativo es:

| Fase | Esfuerzo Relativo | Prerequisito | Notas |
|------|-------------------|-------------|-------|
| **Fase 1**: Fundamentos (MVP) | Referencia base (1x) | Skill borrador ya existe | La mas critica. Debe funcionar end-to-end con GitHub Issues antes de avanzar |
| **Fase 2**: Multi-Source y Clasificacion | ~0.7x de Fase 1 | Fase 1 completada | Parsers son independientes entre si (paralelizables). Incluye Azure DevOps |
| **Fase 3**: Autonomia y Testing | ~0.8x de Fase 1 | Fase 2 completada | CONFIRM_PLAN es relativamente simple. FULL_AUTO con escaladores requiere mas cuidado |
| **Fase 4**: Tracking Triple-Write | ~0.5x de Fase 1 | Fase 1 completada (paralelizable con 2 y 3) | Lectura/escritura de JSON y Markdown |
| **Fase 5**: Hardening y Guardrails | ~0.6x de Fase 1 | Fases 1-4 completadas | Rollback y guardrails son criticos para confianza |
| **Fase 6**: Ecosistema e Infra | ~1.5x de Fase 1 | Fases 1-5 estables | Azure IaC, MCP Server, A2A, demo publico, self-dogfooding. Es la mas grande pero modular |

**Nota**: Fase 4 puede desarrollarse en paralelo con Fases 2 y 3 ya que solo depende de Fase 1. Fase 6 es modular: cada tarea (Terraform, MCP, demo) puede desarrollarse independientemente.

**Velocidad esperada**: Con Claude Code asistiendo, cada fase deberia completarse en 1-3 sesiones de trabajo enfocado. El MVP (Fase 1) es la prioridad absoluta — todo lo demas se construye sobre eso.

**Deliverable GlobalMVM**: Para la demo, se necesitan como minimo Fases 1-2 funcionales + Fase 6 tareas 6.1-6.4 (Azure) + 6.7-6.8 (demo publico). Ver [[BACKLOG]] para tracking.

---

## Documentos Relacionados

- [[MASTERPLAN]] — Plan maestro del Proyecto Hydra (fases 0-5)
- [[SKILL|fix-issue SKILL.md]] — Workflow de 10 pasos (el COMO)
- [[SPEC|Especificacion tecnica]] — Spec completa (2,356+ lineas)
- [[diagrams|Diagramas Mermaid]] — 5 diagramas: flujo, clasificacion, autonomia, tracking, arquitectura
- [[classification|Taxonomia]] — 7 tipos de issues con keywords y decision tree
- [[guardrails|Guardrails]] — 13 reglas de seguridad
- [[BACKLOG|Backlog]] — Items pendientes priorizados
- [[CLIENT-FACING|Doc para GlobalMVM]] — Documento client-facing (en desarrollo)
- [[HANDOFF-FROM-HQ|Handoff]] — Contexto de la reunion con GlobalMVM
