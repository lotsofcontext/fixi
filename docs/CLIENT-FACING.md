# Fixi — Agente Autónomo de Resolución de Tickets

> Documento para circulación interna.
> Versión: 1.0 | Fecha: 2026-04-06

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

### Ejemplo: Bug report en Azure DevOps

**Input**: Work Item #4521 — "La exportación CSV del dashboard de ventas falla con timeout cuando hay más de 10,000 registros"

**Fixi ejecuta**:

```
CONTEXTO VERIFICADO
  Repo: dev.azure.com/globalmvm/ventas-dashboard
  Branch: main
  Working tree: limpio

CLASIFICACIÓN:
  Tipo: performance
  Branch prefix: perf/
  Confianza: ALTA
  Razón: Keywords "timeout" + "10,000 registros" = performance

ROOT CAUSE ANALYSIS:
  Causa raíz: Query sin paginación en ExportService.cs:47
  carga todos los registros en memoria antes de generar CSV

  Archivos a modificar:
    1. src/Services/ExportService.cs:47-62 — agregar streaming
    2. src/Services/ExportService.cs:89 — buffer de escritura
  Riesgo: LOW

BRANCH CREADO: perf/ADO-4521-timeout-csv-export

TESTS: PASS (14 passed, 0 failed)

PR CREADO: https://dev.azure.com/globalmvm/ventas-dashboard/_git/ventas-dashboard/pullrequest/892
  Título: perf: fix CSV export timeout for large datasets
  Base: main <- perf/ADO-4521-timeout-csv-export
  Archivos: 1 modificado

FIX COMPLETE
```

**Tiempo total**: ~3 minutos (automático) + ~10 minutos (revisión humana del PR)

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
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐
│  Azure Repos  │  │    Tracking      │  │  Public /status  │
│  GitHub       │  │  (auditoría)     │  │  /verify/:id     │
└──────────────┘  └──────────────────┘  └─────────────────┘
```

---

## Infraestructura y Despliegue

Fixi se despliega como **infraestructura-como-código** (Terraform), lo cual permite:

- **Reproducibilidad**: el mismo `terraform apply` en cualquier suscripción Azure
- **Auditoría**: toda la infraestructura es versionada en Git
- **Escalabilidad**: ajustar recursos sin intervención manual
- **Aislamiento**: cada equipo o proyecto puede tener su propia instancia

### Componentes Azure

| Componente | Servicio Azure | Propósito |
|-----------|---------------|-----------|
| Agente Fixi | Azure Container Instances | Ejecución del agente |
| Registro de imágenes | Azure Container Registry | Versionado de containers |
| Configuración | Azure Key Vault | Secrets y tokens |
| Monitoreo | Azure Monitor | Logs y alertas |
| Red | Virtual Network | Aislamiento de red |

---

## Integraciones Avanzadas

### MCP Server (Machine Communication Protocol)

Fixi se expone como un servicio que otros agentes y herramientas pueden llamar programáticamente:

- Otros agentes de IA pueden enviar tickets a Fixi
- Herramientas de CI/CD pueden triggerar análisis automáticos
- Dashboards pueden consultar estado y métricas

### Verificación Pública

Cada fix ejecutado por Fixi es **públicamente verificable**:

- **`/status`** — Estado del agente, versión, capabilities, métricas
- **`/verify/:fix_id`** — Evidencia completa: PR, commits, tests, tracking

Esto permite auditoría externa y transparencia total sobre las acciones del agente.

---

## Próximos Pasos

1. **Demo técnico** — Ejecución en vivo de Fixi contra un repositorio de ejemplo con issues pre-creados
2. **Caso de uso real** — GlobalMVM provee "el chicharrón" (caso concreto) para validar contra su stack
3. **Reunión de aclaración** — Revisión técnica de resultados y ajuste de configuración
4. **Piloto** — Implementación en un proyecto real con un equipo acotado

---

## Contacto

Para preguntas técnicas o coordinación del piloto, contactar directamente al equipo de consultoría.

---

*Este documento describe las capacidades actuales y planeadas de Fixi. Algunas funcionalidades están en desarrollo activo.*
