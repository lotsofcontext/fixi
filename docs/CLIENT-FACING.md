# Fixi — Agente Autónomo de Resolución de Tickets

> Documento para circulación interna en GlobalMVM.
> Versión: 2.0 | Fecha: 2026-04-07
>
> **Repos públicos**:
> - Skill: [github.com/lotsofcontext/fixi](https://github.com/lotsofcontext/fixi)
> - Demo cloneable: [github.com/lotsofcontext/fixi-demo-dotnet](https://github.com/lotsofcontext/fixi-demo-dotnet)

---

## Qué es Fixi

Fixi es un agente de software que **automatiza el ciclo completo de resolución de tickets**: desde que un desarrollador reporta un bug o solicita una mejora, hasta que un Pull Request verificado está listo para revisión humana.

No es un chatbot. No es un generador de código genérico. Es un **agente operacional** que entiende el contexto del proyecto, respeta las convenciones del equipo, y produce cambios auditables.

---

## Qué hace (flujo end-to-end)

```
Ticket → Clasificación → Análisis → Branch → Fix → Tests → PR → Tracking
```

1. **Recibe un ticket** de cualquier fuente: Azure DevOps Work Items, GitHub Issues, Jira, Linear, o texto libre
2. **Clasifica automáticamente** el tipo: bug, feature, refactor, seguridad, performance, documentación, o mantenimiento
3. **Analiza el código fuente** para encontrar la causa raíz — no adivina, busca evidencia en el codebase
4. **Crea una rama aislada** siguiendo las convenciones de nomenclatura del equipo
5. **Implementa el cambio mínimo necesario** respetando el estilo del proyecto
6. **Ejecuta tests** y documenta resultados
7. **Crea un Pull Request** con descripción técnica completa: causa raíz, cambios realizados, impacto potencial
8. **Actualiza el tracking** en los sistemas del equipo

**El resultado**: un PR listo para revisión humana, no código desplegado sin supervisión.

---

## Qué NO hace

- **NO despliega código en producción** — solo crea PRs para revisión
- **NO inventa información** — si faltan datos, se detiene y pregunta
- **NO modifica código fuera del alcance del ticket** — cambio mínimo, siempre
- **NO trabaja sobre main/master/develop** — siempre en rama aislada
- **NO toca archivos sensibles** (.env, credenciales, keys) — si el fix los requiere, documenta instrucciones manuales
- **NO reemplaza desarrolladores** — multiplica su capacidad

---

## Impacto en Productividad

### Tiempo por ticket (antes vs. después)

| Actividad | Sin Fixi | Con Fixi | Ahorro |
|-----------|----------|----------|--------|
| Leer y entender el ticket | 10-15 min | 0 min (automático) | 100% |
| Buscar causa raíz en el codebase | 15-60 min | 0 min (automático) | 100% |
| Implementar fix + tests | 15-120 min | 0 min (automático) | 100% |
| Crear branch, commits, PR | 5-15 min | 0 min (automático) | 100% |
| **Revisar PR** (humano) | — | 5-15 min | Nuevo paso |
| **Total tiempo humano** | **45-210 min** | **5-15 min** | **80-93%** |

### Proyección para un equipo de 10 desarrolladores

- Promedio de 3 tickets/semana por desarrollador = 30 tickets/semana
- Ahorro promedio de 60 min por ticket = **30 horas/semana recuperadas**
- Equivalente a **3.75 desarrolladores adicionales** de capacidad
- El equipo de 10 produce como equipo de 13-14

---

## Seguridad y Gobernanza

### Principios de diseño

| Principio | Implementación |
|-----------|---------------|
| **Rama aislada siempre** | Nunca toca main/master/develop. Todo cambio va a una rama dedicada |
| **PR para revisión humana** | Ningún cambio se fusiona sin aprobación de un desarrollador |
| **Nunca inventa datos** | Si falta información, se detiene y reporta qué necesita |
| **Rollback automático** | Si algo falla durante la ejecución, deshace todos los cambios |
| **Archivos sensibles protegidos** | .env, credenciales, API keys — nunca los modifica |
| **Auditable** | Cada acción queda registrada: qué hizo, por qué, cuándo, en qué archivos |
| **Escalamiento automático** | Issues de seguridad, migraciones de BD, o cambios grandes (>15 archivos) fuerzan revisión paso a paso |

### 3 niveles de autonomía

El equipo decide cuánto control quiere mantener:

1. **GUIDED** (por defecto) — Aprobación humana en cada paso
2. **CONFIRM_PLAN** — Presenta el plan completo, un "OK" ejecuta todo
3. **FULL_AUTO** — Ejecuta sin interrupciones (excepto seguridad y migraciones, que siempre piden aprobación)

---

## Compatibilidad de Stack

Fixi es **agnóstico a la tecnología**. Funciona con cualquier proyecto que tenga código fuente y un sistema de control de versiones.

### Lenguajes soportados
- C# / .NET
- Java / Spring Boot
- Python / Django / FastAPI
- JavaScript / TypeScript / Node.js
- Angular / React
- Go, Rust, y cualquier otro lenguaje con archivos de texto

### Plataformas de código
- **Azure Repos** — PRs via `az repos pr create`
- **GitHub** — PRs via `gh pr create`
- Jira, Linear (lectura de tickets)

### CI/CD
- Azure Pipelines
- GitHub Actions
- Jenkins, GitLab CI (detección automática)

### Sistemas de tickets
- Azure DevOps Work Items
- GitHub Issues
- Jira
- Linear
- Texto libre (email, chat, cualquier descripción)

---

## Cómo se ve en la práctica

Para que GlobalMVM pueda probar Fixi sin pre-requisitos, construimos un repo de demo cloneable:

> **`lotsofcontext/fixi-demo-dotnet`** — un Web API ASP.NET Core 9 para lectura de medidores de energía. Contiene **3 defectos sembrados a propósito**, uno por cada clasificación crítica de Fixi:

| # | Tipo | Work Item | Donde vive el bug | Test que falla |
|---|------|-----------|-------------------|----------------|
| 1 | `bug` | [WI-101](https://github.com/lotsofcontext/fixi-demo-dotnet/blob/master/docs/issues/WI-101-bug-lectura-negativa.md) | `Domain/Services/CalculadoraConsumo.cs` (`DivideByZeroException` cuando dos lecturas son del mismo día) | `CalculadoraConsumoTests.Calcular_DosLecturasMismoDia_NoDebeLanzarExcepcion` |
| 2 | `performance` | [WI-102](https://github.com/lotsofcontext/fixi-demo-dotnet/blob/master/docs/issues/WI-102-perf-listado-medidores.md) | `Infrastructure/Services/MedidorService.cs` (N+1 query, 51 SQL calls para 50 medidores) | `MedidoresEndpointTests.Listar_LatenciaP95_DebeSerMenorA500ms` |
| 3 | `security` | [WI-103](https://github.com/lotsofcontext/fixi-demo-dotnet/blob/master/docs/issues/WI-103-security-endpoint-admin.md) | `Api/Controllers/AdminController.cs` (sin `[Authorize]`, OWASP A01 Broken Access Control) | `AdminEndpointSecurityTests.ResetearLecturas_*` |

El dominio (lectura de medidores) matchea el sector real de GlobalMVM: clientes como **EPM, ISAGEN, XM y Veolia** aparecen en los work items con casos de uso plausibles (técnico de campo registrando lectura post-tormenta, profiling de Joaris en QA, security review de Jefferson con OWASP ZAP).

### Cómo lo pueden probar hoy

```bash
# 1. Clonar el demo
git clone https://github.com/lotsofcontext/fixi-demo-dotnet
cd fixi-demo-dotnet

# 2. Verificar que arranca y los tests fallan como esperamos
dotnet restore
dotnet build
dotnet test
# Expected: Failed: 5, Passed: 3, Total: 8 (los 5 rojos son los bugs sembrados)

# 3. En una sesión de Claude Code, invocar Fixi contra cada work item
#    /fix-issue docs/issues/WI-101-bug-lectura-negativa.md
#    /fix-issue docs/issues/WI-102-perf-listado-medidores.md
#    /fix-issue docs/issues/WI-103-security-endpoint-admin.md
```

### Lo que Fixi ejecuta (ejemplo: WI-101)

```
CONTEXTO VERIFICADO
  Repo: github.com/lotsofcontext/fixi-demo-dotnet
  Branch: master
  Working tree: limpio
  Cliente: GlobalMVM (sandbox demo)

CLASIFICACIÓN:
  Tipo: bug
  Branch prefix: fix/
  Commit prefix: fix:
  Confianza: ALTA
  Razón: Keywords "DivideByZero", "exception", "500" + stack trace en issue body

ROOT CAUSE ANALYSIS:
  Causa raíz: CalculadoraConsumo.Calcular usa (delta).Days que es 0
  cuando dos lecturas son del mismo día → división por cero.

  Archivos a modificar:
    1. src/GMVM.EnergyTracker.Domain/Services/CalculadoraConsumo.cs:17-23
       — agregar guard clause para casos sub-diarios

  Riesgo: LOW
  Tests existentes: 2 fallan (capturan el bug, pasan después del fix)

BRANCH CREADO: fix/WI-101-consumo-negativo-mismo-dia

TESTS: PASS (5 passed, 3 failed → 7 passed, 1 failed)
       — bug fix dejó solo los 3 fails de WI-102 y WI-103

PR CREADO: https://github.com/lotsofcontext/fixi-demo-dotnet/pull/1
  Título: fix: handle same-day readings in CalculadoraConsumo
  Base: master ← fix/WI-101-consumo-negativo-mismo-dia
  Archivos: 1 modificado, +5/-2 líneas

FIX COMPLETE
```

**Tiempo total**: ~3 minutos (automático) + ~5-10 minutos (revisión humana del PR).

> ⏳ Las transcripciones reales y los screenshots de los PRs creados durante los rehearsals end-to-end estarán enlazados aquí en cuanto estén disponibles: `docs/demos/run-01-github.md` y `docs/demos/run-02-ado.md`.

### El caso especial: WI-103 (security)

Cuando Fixi clasifica un issue como `security`, **automáticamente fuerza modo GUIDED**, sin importar el nivel de autonomía elegido. Esto significa que pide aprobación humana en cada paso. Es uno de los **13 guardrails** que protege contra cambios automáticos en código de seguridad sin supervisión.

Esto responde directamente a la preocupación sobre adopción y resistencia de devs: Fixi sabe **cuándo parar y pedir permiso**, no es un agente autónomo ciego.

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    FUENTES DE TICKETS                    │
│  Azure DevOps  │  GitHub  │  Jira  │  Linear  │  Texto  │
└────────┬────────┴────┬─────┴───┬────┴────┬─────┴────┬───┘
         │             │         │         │          │
         ▼             ▼         ▼         ▼          ▼
┌─────────────────────────────────────────────────────────┐
│                      FIXI AGENT                         │
│                                                         │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────┐ │
│  │  Parser   │→│ Classifier │→│ Analyzer  │→│ Fixer  │ │
│  │ Universal │  │ (7 tipos)  │  │(root cause)│ │(impl) │ │
│  └──────────┘  └───────────┘  └──────────┘  └───┬───┘ │
│                                                   │     │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────┘     │
│  │  Tester  │←─┤ PR Creator│←─┘                        │
│  └──────────┘  └───────────┘                            │
│                                                         │
│  Guardrails: 13 reglas de seguridad activas             │
│  Autonomía: GUIDED │ CONFIRM_PLAN │ FULL_AUTO           │
└─────────────────────────────┬───────────────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         ▼                                         ▼
┌──────────────────────┐              ┌──────────────────────┐
│  Azure Repos / GitHub │              │  Tracking            │
│  PRs para revisión    │              │  ACTIVO.md +         │
│  humana               │              │  Mission Control     │
└──────────────────────┘              └──────────────────────┘
```

---

## Infraestructura y Despliegue

Fixi se despliega como **infraestructura-como-código** (Terraform). El skeleton completo está en [`terraform/`](../terraform/) — 25 archivos, 5 módulos, ~1,955 líneas de HCL + Markdown, validado con `terraform validate` y `terraform fmt`.

> 📁 [`terraform/README.md`](../terraform/README.md) tiene la guía completa: arquitectura, prerequisites, setup en 6 pasos (incluyendo el bootstrap de secrets), tabla de variables, tabla de outputs, estimación de costo (~$25-30/mes dev, $150-250/mes prod), security notes, disclaimer.

**Beneficios para GlobalMVM**:

- **Reproducibilidad**: el mismo `terraform apply` en cualquier suscripción Azure
- **Auditoría**: toda la infraestructura es versionada en Git, sin ClickOps
- **Escalabilidad**: ajustar SKUs y recursos sin intervención manual
- **Aislamiento**: cada equipo o proyecto puede tener su propia instancia

### Componentes Azure (módulos Terraform)

| Componente | Servicio Azure | Módulo Terraform | Propósito |
|-----------|---------------|------------------|-----------|
| Agente Fixi | Azure Container Instances | [`modules/container_instance`](../terraform/modules/container_instance/) | Ejecución del agente como container long-running |
| Registro de imágenes | Azure Container Registry | [`modules/container_registry`](../terraform/modules/container_registry/) | Versionado de la imagen de Fixi |
| Secrets | Azure Key Vault (RBAC mode) | [`modules/key_vault`](../terraform/modules/key_vault/) | PATs de Azure DevOps, GitHub, API key de Anthropic |
| Identidad | User-Assigned Managed Identity | [`modules/managed_identity`](../terraform/modules/managed_identity/) | Pull desde ACR + lectura de secrets de KV |
| Red | Virtual Network + NSG deny-all inbound | [`modules/networking`](../terraform/modules/networking/) | Aislamiento, sin ingreso público |
| Logs | Log Analytics Workspace | (en root `main.tf`) | Diagnostics del container |

### Decisiones de seguridad clave

- **Cero secrets hardcoded** en HCL ni en tfvars committeados
- **Key Vault en modo RBAC** (no access policies), integra con PIM
- **Soft-delete + purge protection** en KV
- **NSG deny-all inbound** explícito (Fixi no expone HTTP, recibe trabajo via queue/CLI)
- **ACR admin disabled**, solo Managed Identity con `AcrPull`
- **`secret_references` output marcado `sensitive = true`**
- **`.gitignore`** bloquea state files y root-level tfvars

> Estas decisiones están documentadas en comentarios del código Terraform para que el equipo de seguridad de GlobalMVM las pueda revisar línea por línea.

---

## Integración con Azure DevOps

GlobalMVM corre 99% sobre Azure. Fixi soporta el flujo nativo de Azure DevOps:

### Lectura de Work Items
- **Pattern URL**: `dev.azure.com/{org}/{project}/_workitems/edit/{id}`
- **Shorthand**: `ADO-{id}`, `WI-{id}`, `AB#{id}`
- **Comando**: `az boards work-item show --id {id} --output json`
- **Field mapping**: `System.Title` → título, `System.Description` → body (HTML), `System.Tags` → labels, `Microsoft.VSTS.Common.Priority` → prioridad, `System.WorkItemType` → hint de clasificación
- **Fallback**: WebFetch si `az` no autenticado, input manual si todo falla

### Creación de Pull Requests
- **Auto-detección** del remote: si matchea `dev.azure.com` o `visualstudio.com` → usa `az repos pr create`
- **PR template idéntico** al de GitHub (Issue / Clasificación / Causa Raíz / Cambios / Testing)
- **Linkeo automático** PR ↔ Work Item: `az repos pr work-item add --id {pr_id} --work-items {wi_id}`
- **Si el remote no es Azure**: cae a `gh pr create` automáticamente

### Azure Pipelines
- Detección automática de `azure-pipelines.yml`
- Verifica que el pipeline corre post-push
- Documenta resultado en comments del PR

> El skill completo (10 pasos, 656 líneas) está en [`skill/SKILL.md`](../skill/SKILL.md). Las 13 reglas de seguridad están en [`skill/references/guardrails.md`](../skill/references/guardrails.md). La taxonomía de los 7 tipos está en [`skill/references/classification.md`](../skill/references/classification.md).

---

## Documentación adicional

| Documento | Para qué sirve |
|-----------|---------------|
| [README](../README.md) | Overview técnico del proyecto |
| [diagrams.md](diagrams.md) | 5 diagramas Mermaid: flujo principal, clasificación, autonomía, tracking, arquitectura de integración |
| [PLAN.md](PLAN.md) | Roadmap completo: 6 fases, 46 tareas (incluye Azure DevOps, Terraform IaC, MCP Server, demo público, self-dogfooding) |
| [SPEC.md](SPEC.md) | Especificación técnica completa |
| [SKILL.md](../skill/SKILL.md) | Workflow operacional de Fixi (10 pasos) |
| [terraform/README.md](../terraform/README.md) | Guía de despliegue en Azure |

---

## Próximos Pasos

1. ✅ **Repo cloneable entregado** — `lotsofcontext/fixi` + `lotsofcontext/fixi-demo-dotnet`, ambos públicos
2. ✅ **Terraform analizable entregado** — 25 archivos en `terraform/`, validado, documentado
3. ⏳ **Rehearsal end-to-end documentado** — pendiente: ejecución real de Fixi contra los 3 work items con transcripts en `docs/demos/`
4. ⏳ **GlobalMVM revisa los repos** — feedback técnico, preguntas, refinamientos
5. ⏳ **Caso de uso real ("el chicharrón")** — GlobalMVM provee un caso concreto de uno de sus proyectos para validar contra su stack real
6. ⏳ **Reunión de aclaración** — revisión técnica conjunta
7. ⏳ **Piloto acotado** — implementación en un proyecto real con un equipo pequeño

---

## Contacto

Para preguntas técnicas o coordinación del piloto, contactar directamente al equipo de consultoría.

---

*Este documento describe las capacidades actuales y planeadas de Fixi. La implementación está en desarrollo activo en branches públicos — el progreso se trackea en `kanban/BOARD.md` del repo principal.*
