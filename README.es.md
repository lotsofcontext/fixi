# Fixi

> **Agente Autónomo de Resolución de Tickets** — toma un ticket, analiza el código, implementa el fix y crea un PR. De principio a fin, con humano en el loop por defecto.

Fixi automatiza el ciclo completo de resolución de un ticket: **intake → clasificación → análisis de causa raíz → branch → fix → tests → PR → tracking**. Corre como un skill de Claude Code, opera sobre cualquier lenguaje o stack, y se integra con GitHub, Azure DevOps, Jira y Linear.

El objetivo no es reemplazar desarrolladores. El objetivo es entregarles PRs listos para revisión en lugar de tickets vacíos listos para investigación.

---

## Qué hace diferente a Fixi

- **Nunca inventa información.** Si faltan datos, se detiene y pregunta. Cero causas raíz alucinadas.
- **Nunca toca `main`.** Cada fix ocurre en una rama aislada con un PR para revisión humana.
- **Solo el cambio mínimo.** Sin scope creep, sin refactoring especulativo, sin "ya que estoy aquí".
- **13 guardrails activos continuamente** — desde el Safety Gate (Paso 0) hasta la verificación pre-push.
- **Rollback automático** si cualquier paso falla.
- **3 niveles de autonomía** — `GUIDED` (default, aprobación paso a paso), `CONFIRM_PLAN` (un solo OK ejecuta todo), `FULL_AUTO` (sin interrupciones, excepto seguridad/migraciones).

---

## Flujo end-to-end

```
Ticket ──▶ Parse ──▶ Clasificar ──▶ Analizar ──▶ Branch ──▶ Fix ──▶ Tests ──▶ PR ──▶ Tracking
```

Cada paso es auditable. Cada acción es reversible. Ver [docs/diagrams.md](docs/diagrams.md) para las visualizaciones Mermaid del flujo, el árbol de clasificación, los niveles de autonomía y el pipeline de tracking.

### Las 7 clasificaciones

| Tipo | Branch prefix | Commit prefix | Cuándo usar |
|------|---------------|---------------|-------------|
| `bug` | `fix/` | `fix:` | Error, crash, regresión, comportamiento incorrecto |
| `feature` | `feat/` | `feat:` | Nueva capacidad que el sistema no tenía |
| `refactor` | `refactor/` | `refactor:` | Cambio estructural sin cambio de comportamiento |
| `security` | `security/` | `fix:` | Vulnerabilidad, CVE, auth bypass — **siempre fuerza GUIDED** |
| `performance` | `perf/` | `perf:` | Query lenta, timeout, memory leak, N+1 |
| `docs` | `docs/` | `docs:` | README, API docs, comentarios, typos |
| `chore` | `chore/` | `chore:` | Dependencias, CI/CD, config, tooling |

Prioridad cuando es ambiguo: `security > bug > performance > feature > refactor > docs > chore`. Taxonomía completa en [skill/references/classification.md](skill/references/classification.md).

---

## Agnóstico al stack

Fixi funciona con cualquier codebase que tenga código fuente y un sistema de control de versiones.

**Lenguajes**: C#/.NET · Java · Python · TypeScript · JavaScript · Go · Rust · Angular · React · y cualquier otro

**Fuentes de tickets**: GitHub Issues · Azure DevOps Work Items · Jira · Linear · descripciones en texto libre

**Plataformas de código**: GitHub · Azure Repos · GitLab

**CI/CD**: GitHub Actions · Azure Pipelines · Jenkins · GitLab CI (auto-detectados)

---

## Uso

Fixi corre como un skill de Claude Code. Instala copiando `skill/` a `.claude/skills/fix-issue/` de tu proyecto.

```bash
# URL de GitHub issue
/fix-issue https://github.com/org/repo/issues/123

# Work item de Azure DevOps
/fix-issue https://dev.azure.com/org/project/_workitems/edit/4521

# Shorthand
/fix-issue #42

# Linear / Jira
/fix-issue LINEAR-ABC-123
/fix-issue PROJ-789

# Texto libre
/fix-issue "El login falla con 500 cuando el email contiene +"
```

---

## Estructura del repositorio

```
fixi/
├── README.md                   # Versión en inglés
├── README.es.md                # Este archivo
├── CLAUDE.md                   # Reglas para Claude Code al trabajar en este repo
├── HANDOFF-FROM-HQ.md           # Contexto de la interacción con GlobalMVM
│
├── skill/                      # El agente
│   ├── SKILL.md                # Workflow de 10 pasos
│   └── references/
│       ├── classification.md    # Taxonomía de 7 tipos
│       └── guardrails.md        # 13 reglas de seguridad
│
└── docs/
    ├── PLAN.md                 # Roadmap de 6 fases (46 tareas)
    ├── SPEC.md                 # Especificación técnica completa
    ├── diagrams.md             # 5 diagramas Mermaid
    ├── CLIENT-FACING.md        # Resumen en lenguaje de negocio
    └── planning/
        └── BACKLOG.md          # Backlog priorizado
```

---

## Roadmap

Fixi se construye en 6 fases. Ver [docs/PLAN.md](docs/PLAN.md) para el roadmap completo y [docs/planning/BACKLOG.md](docs/planning/BACKLOG.md) para las prioridades actuales.

| Fase | Foco | Estado |
|------|------|--------|
| **1. Fundamentos (MVP)** | Parser de GitHub Issues, clasificación, causa raíz, flujo branch/commit/PR | Spec completa |
| **2. Multi-source + Azure DevOps** | Linear, Jira, Azure DevOps Work Items, texto libre, desambiguación inteligente | Spec completa |
| **3. Autonomía + Testing** | `CONFIRM_PLAN`, `FULL_AUTO`, detección automática de test runner, tests de regresión | Spec completa |
| **4. Triple-write tracking** | ACTIVO.md del cliente + Mission Control (tasks, activity log, inbox) | Spec completa |
| **5. Hardening + Guardrails** | Rollback, límites de scope, protección de archivos sensibles, dry-run mode | Spec completa |
| **6. Ecosistema + Infra + Demo Público** | Azure IaC (Terraform), MCP Server, A2A Protocol, endpoint `/status`, self-dogfooding | Spec completa |

---

## Seguridad

Fixi está diseñado para operar sobre codebases de producción con confianza:

- **Safety Gate** verifica contexto, repo, working tree y cliente antes de cualquier acción
- **13 guardrails** aplicados en cada paso — ver [skill/references/guardrails.md](skill/references/guardrails.md)
- **Archivos sensibles protegidos**: `.env`, credenciales, keys, certificados — nunca se modifican
- **Protección de CI/CD**: cambios en `.github/workflows`, `azure-pipelines.yml`, etc. siempre fuerzan modo GUIDED
- **Límites de scope**: fixes que afectan >15 archivos auto-escalan a GUIDED
- **Audit trail**: cada acción registrada en el tracking triple-write (estado del cliente + mission control + activity log)
- **Sin force push. Sin commits directos a `main`. Sin bypass de git hooks.**

---

## Documentación

| Documento | Propósito |
|-----------|-----------|
| [docs/PLAN.md](docs/PLAN.md) | Roadmap de implementación de 6 fases |
| [docs/SPEC.md](docs/SPEC.md) | Especificación técnica completa |
| [docs/diagrams.md](docs/diagrams.md) | 5 diagramas Mermaid (flujo, clasificación, autonomía, tracking, arquitectura) |
| [docs/CLIENT-FACING.md](docs/CLIENT-FACING.md) | Resumen en lenguaje de negocio para stakeholders |
| [docs/planning/BACKLOG.md](docs/planning/BACKLOG.md) | Backlog priorizado |
| [skill/SKILL.md](skill/SKILL.md) | Definición del workflow de 10 pasos |
| [skill/references/classification.md](skill/references/classification.md) | Taxonomía de 7 tipos de issue |
| [skill/references/guardrails.md](skill/references/guardrails.md) | 13 reglas de seguridad |

---

## Licencia

Propietario — Lots of Context LLC · 2026
