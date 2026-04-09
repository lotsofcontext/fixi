# Fixi

> **Agente autónomo de resolución de tickets** — resuelve tickets end-to-end desde tu pipeline de CI/CD. Se invoca desde la CLI, devuelve un Pull Request.

```bash
fixi resolve \
  --work-item https://dev.azure.com/globalmvm/EnergySuite/_workitems/edit/4521 \
  --repo https://dev.azure.com/globalmvm/EnergySuite/_git/energy-tracker
```

Fixi recibe un work item (GitHub Issue, Azure DevOps Work Item, Jira, Linear, o texto libre), clona el repo target, ejecuta un workflow de 10 pasos — parsear, clasificar, analizar causa raíz, branch, fix, validar, PR — y entrega un Pull Request listo para revisión humana. Autónomo. Auditable. Con 13 reglas de seguridad aplicadas como código.

El objetivo no es reemplazar desarrolladores. El objetivo es entregarles PRs listos para revisar en lugar de tickets vacíos listos para investigar.

---

## Funciona. Acá está la evidencia.

El 2026-04-07 Fixi resolvió autónomamente tres bugs sembrados intencionalmente en un repo .NET de demo — uno de bug, uno de performance, uno de seguridad. Cada ejecución: clona repo, encuentra causa raíz, fixea, valida, abre PR. Sin intervención humana.

| Work Item | Tipo | PR | Duración | Costo | Turns |
|-----------|------|-----|----------|-------|-------|
| [WI-101](https://github.com/lotsofcontext/fixi-demo-dotnet/blob/master/docs/issues/WI-101-bug-lectura-negativa.md) | `bug` — DivideByZeroException | [#2](https://github.com/lotsofcontext/fixi-demo-dotnet/pull/2) | 4m 18s | $0.61 | 24 |
| [WI-102](https://github.com/lotsofcontext/fixi-demo-dotnet/blob/master/docs/issues/WI-102-perf-listado-medidores.md) | `performance` — N+1 query | [#3](https://github.com/lotsofcontext/fixi-demo-dotnet/pull/3) | 4m 53s | $1.16 | 34 |
| [WI-103](https://github.com/lotsofcontext/fixi-demo-dotnet/blob/master/docs/issues/WI-103-security-endpoint-admin.md) | `security` — OWASP A01 | [#4](https://github.com/lotsofcontext/fixi-demo-dotnet/pull/4) | 5m 03s | $1.13 | 31 |

**Totales**: 14 minutos, $2.90 USD, 89 turns, 3 PRs. Clona el [repo demo](https://github.com/lotsofcontext/fixi-demo-dotnet), lee los PRs, inspecciona los diffs. La evidencia es verificable.

---

## Dos capas

Fixi está construido en dos capas que pueden entenderse y auditarse de forma independiente:

### 🧠 Capa 1 — El playbook (`skill/SKILL.md`)

Un archivo markdown human-readable que define el workflow de 10 pasos: intake, clasificación, análisis de causa raíz, ramificación, fix, validaciones, creación de PR, tracking, cleanup. 763 líneas de texto plano que cualquier ingeniero puede leer, auditar, y modificar. Versionado en git. Sin caja negra.

Es el **"qué hacer"**. También es el system prompt que el agent usa en runtime — una sola fuente de verdad, sin drift.

### 🤖 Capa 2 — El runtime deployable (`agent/`)

Una CLI Python (`fixi`) construida sobre el [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python). Hace:

- Carga el playbook como system prompt con 6 transformaciones de modo autónomo (elimina approval gates interactivos, invierte default a FULL_AUTO, etc.)
- Parsea referencias de work items a una estructura normalizada (6 tipos de fuentes soportadas)
- Clona el repo target con inyección de auth (GH_TOKEN, AZURE_DEVOPS_PAT)
- Invoca el agent loop con 13 guardrails aplicados como `PreToolUse` hooks
- Extrae PR URL, branch, clasificación, archivos modificados del output
- Devuelve JSON estructurado para consumo desde CI/CD

Es el **"cómo ejecutarlo sin humano en el loop"**. 1,165 líneas de Python. 136 tests unitarios.

---

## Quick start

### Instalar

```bash
git clone https://github.com/lotsofcontext/fixi
cd fixi/agent
python -m venv venv
source venv/bin/activate      # o: venv\Scripts\activate en Windows
pip install -e .
fixi check                    # verifica Claude Code CLI, git, auth tokens
```

### Resolver un issue

```bash
# Azure DevOps Work Item
fixi resolve \
  --work-item https://dev.azure.com/org/project/_workitems/edit/4521 \
  --repo https://dev.azure.com/org/project/_git/my-repo

# GitHub Issue
fixi resolve \
  --work-item https://github.com/org/repo/issues/42 \
  --repo https://github.com/org/repo

# Archivo markdown local (para testing)
fixi resolve \
  --work-item docs/issues/WI-101-bug.md \
  --repo-path ./my-local-repo

# Output JSON para CI/CD
fixi resolve --work-item <url> --repo <url> --output json
```

### Variables de entorno requeridas

```bash
export ANTHROPIC_API_KEY=sk-ant-...          # requerido
export GH_TOKEN=ghp_...                       # para repos GitHub
export AZURE_DEVOPS_PAT=...                   # para Azure Repos
```

---

## Integración CI/CD

Fixi está diseñado para correr como un step en tu pipeline existente. Ejemplos copy-paste:

### GitHub Actions

[`agent/.github/workflows/example-fixi-resolve.yml`](agent/.github/workflows/example-fixi-resolve.yml) — trigger manual con `workflow_dispatch`, instala la CLI, corre contra un work item, sube resultado como artifact, escribe step summary.

### Azure DevOps Pipelines

[`agent/azure-pipelines/example-fixi-resolve.yml`](agent/azure-pipelines/example-fixi-resolve.yml) — parámetros `workItemUrl` y `repoUrl`, usa un Variable Group `fixi-secrets` para `ANTHROPIC_API_KEY` y `AZURE_DEVOPS_PAT`.

### Docker

[`agent/Dockerfile`](agent/Dockerfile) — build multi-stage (Node + Claude Code CLI + Python + Fixi) apuntando a ~1.5 GB. [`agent/docker-compose.yml`](agent/docker-compose.yml) para dev local.

---

## Qué hace diferente a Fixi

- **Transparente**: el playbook es un archivo markdown que podés leer línea por línea. Sin flows black-box, sin prompts ocultos.
- **Nunca inventa información.** Si faltan datos, se detiene y pregunta. Verificado en el run de WI-101 donde Fixi marcó acceptance criteria como N/A en lugar de fabricar evidencia.
- **Nunca toca `main`.** Cada fix es un branch aislado con PR para revisión humana. Guardrail-enforced.
- **Solo el cambio mínimo.** Sin scope creep, sin refactoring especulativo, sin "ya que estoy aquí". Verificado en los 3 PRs (máx 9 líneas cambiadas).
- **13 guardrails como code hooks**, no como prompts — bloqueadores `PreToolUse` que no se pueden discutir. Ver [`agent/src/fixi_agent/hooks.py`](agent/src/fixi_agent/hooks.py).
- **Escalación automática**: security, migraciones de DB, cambios CI/CD, >15 archivos, o causa raíz ambigua fuerzan modo GUIDED sin importar el nivel de autonomía del caller.
- **3 niveles de autonomía**: `GUIDED` (aprobación en cada paso), `CONFIRM_PLAN` (un OK ejecuta todo), `FULL_AUTO` (sin interrupciones). Default CLI es FULL_AUTO; el agent baja a GUIDED cuando los escaladores disparan.

---

## Las 7 clasificaciones

Fixi asigna uno de estos tipos basándose en keywords + contexto del work item:

| Tipo | Branch prefix | Commit prefix | Cuándo usar |
|------|---------------|---------------|-------------|
| `bug` | `fix/` | `fix:` | Error, crash, regresión, comportamiento incorrecto |
| `feature` | `feat/` | `feat:` | Nueva capacidad que el sistema no tenía |
| `refactor` | `refactor/` | `refactor:` | Cambio estructural sin cambio de comportamiento |
| `security` | `security/` | `fix:` | Vulnerabilidad, CVE, auth bypass — **siempre fuerza GUIDED** |
| `performance` | `perf/` | `perf:` | Query lenta, timeout, memory leak, N+1 |
| `docs` | `docs/` | `docs:` | README, API docs, comentarios, typos |
| `chore` | `chore/` | `chore:` | Dependencias, CI/CD, config, tooling |

Prioridad cuando es ambiguo: `security > bug > performance > feature > refactor > docs > chore`. Taxonomía completa en [`skill/references/classification.md`](skill/references/classification.md).

---

## Agnóstico al stack

Fixi funciona con cualquier codebase que tenga código fuente y control de versiones.

**Lenguajes**: C#/.NET · Java · Python · TypeScript · JavaScript · Go · Rust · Angular · React — y cualquier otro

**Fuentes de tickets**: GitHub Issues · Azure DevOps Work Items · Jira · Linear · archivos markdown locales · descripciones en texto libre

**Plataformas de código**: GitHub · Azure Repos · GitLab

**CI/CD**: GitHub Actions · Azure Pipelines · Jenkins · GitLab CI (auto-detectados)

**Validaciones**: runners de tests, lint, y build auto-detectados por lenguaje (dotnet, npm, pytest, cargo, go, maven, gradle, ruff, eslint, etc.)

---

## Seguridad por diseño

- **Safety Gate** verifica contexto, repo, working tree, y cliente antes de cualquier acción
- **13 guardrails** aplicados en cada tool use como `PreToolUse` hooks — ver [`skill/references/guardrails.md`](skill/references/guardrails.md) para el spec y [`agent/src/fixi_agent/hooks.py`](agent/src/fixi_agent/hooks.py) para la implementación
- **Archivos sensibles protegidos**: `.env`, credenciales, keys, certificados — nunca se modifican, nunca se leen al prompt
- **Protección CI/CD**: cambios en `.github/workflows`, `azure-pipelines.yml`, `Jenkinsfile`, etc. fuerzan modo GUIDED
- **Protección de migraciones**: cambios en `migrations/`, `alembic/`, `prisma/`, `*.sql` fuerzan GUIDED
- **Límites de scope**: fixes que afectan >15 archivos auto-escalan a GUIDED
- **Sanitización de auth tokens**: los secrets se quitan de todos los logs y error messages
- **Sin force push. Sin commits directos a `main`. Sin bypass de git hooks.**

---

## Estructura del repositorio

```
fixi/
├── README.md                   # En inglés
├── README.es.md                # Este archivo
├── CLAUDE.md                   # North Star Prompt + reglas para Claude Code
├── HANDOFF-FROM-HQ.md          # Contexto de la interacción con GlobalMVM
├── HANDOFF-NORTH-STAR.md       # Audit vs las 9 capabilities no-negociables
│
├── agent/                      # 🤖 El runtime deployable
│   ├── src/fixi_agent/
│   │   ├── cli.py              # Entry point CLI (fixi resolve, fixi check)
│   │   ├── orchestrator.py     # Core agent loop (integración Claude Agent SDK)
│   │   ├── prompts.py          # Carga SKILL.md con 6 autonomous transforms
│   │   ├── parser.py           # Parser multi-source de work items (Gap D priority)
│   │   ├── cloner.py           # git clone con inyección de auth
│   │   └── hooks.py            # 13 guardrails como PreToolUse hooks
│   ├── tests/                  # 136 unit tests + integration smoke test
│   ├── .github/workflows/      # Ejemplo de GitHub Actions workflow
│   ├── azure-pipelines/        # Ejemplo de Azure DevOps Pipeline
│   ├── Dockerfile              # Build multi-stage (Node + Python + Claude Code)
│   ├── docker-compose.yml      # Dev local
│   └── pyproject.toml          # Config del paquete
│
├── skill/                      # 🧠 El playbook (human-readable)
│   ├── SKILL.md                # Workflow de 10 pasos (763 líneas)
│   └── references/
│       ├── classification.md   # Taxonomía de 7 tipos
│       └── guardrails.md       # 13 reglas de seguridad
│
├── terraform/                  # IaC skeleton para Azure (25 archivos, 5 módulos)
│   ├── main.tf
│   ├── modules/
│   │   ├── container_instance/ # ACI corriendo Fixi
│   │   ├── container_registry/ # ACR para la imagen
│   │   ├── key_vault/          # Secrets (API keys, PATs)
│   │   ├── managed_identity/   # UAMI con least privilege
│   │   └── networking/         # VNet + NSG (deny-all inbound)
│   └── README.md
│
├── kanban/                     # Tablero de proyecto auto-actualizable
│   ├── BOARD.md                # Auto-generado (no editar)
│   ├── tasks/                  # Archivos individuales de tareas (source of truth)
│   ├── history/                # Logs diarios append-only
│   └── update_board.py         # Regenera el board desde los task files
│
└── docs/
    ├── PLAN.md                 # Roadmap de 6 fases (46 tareas)
    ├── SPEC.md                 # Especificación técnica completa
    ├── diagrams.md             # 5 diagramas Mermaid
    ├── CLIENT-FACING.md        # Overview para stakeholders (v3.0)
    ├── globalmvm-review-simulation.md  # Simulación de review con 7 stakeholders
    └── planning/
        ├── BACKLOG.md
        ├── SPRINT-1.md
        └── SPRINT-2.md
```

---

## Estado

Ambos sprints de desarrollo están **completos**.

| Sprint | Scope | Estado |
|--------|-------|--------|
| **Sprint 1** | Skill workflow (10 pasos), taxonomía de clasificación, spec de guardrails, demo repo con bugs sembrados, Terraform skeleton, docs client-facing | ✅ **100%** (17/17 tareas) |
| **Sprint 2** | Python agent sobre Claude Agent SDK, CLI, 13 guardrails como hooks, parser de 6 fuentes, Dockerfile, workflows GH Actions + Azure Pipelines, 136 unit tests, 3 PRs reales como evidencia | ✅ **100%** (20/20 tareas) |

Ver [`kanban/BOARD.md`](kanban/BOARD.md) para el board auto-generado y [`docs/planning/SPRINT-1.md`](docs/planning/SPRINT-1.md) / [`docs/planning/SPRINT-2.md`](docs/planning/SPRINT-2.md) para los planes por sprint.

---

## Documentación

| Documento | Propósito |
|-----------|-----------|
| [`skill/SKILL.md`](skill/SKILL.md) | El workflow de 10 pasos — también se carga como system prompt del agent |
| [`skill/references/classification.md`](skill/references/classification.md) | Taxonomía de 7 tipos con keywords y árbol de decisión |
| [`skill/references/guardrails.md`](skill/references/guardrails.md) | Spec de las 13 reglas de seguridad |
| [`agent/README.md`](agent/README.md) | Overview del paquete agent |
| [`docs/CLIENT-FACING.md`](docs/CLIENT-FACING.md) | Overview en lenguaje de negocio para stakeholders (v3.0) |
| [`docs/diagrams.md`](docs/diagrams.md) | 5 diagramas Mermaid (flujo, clasificación, autonomía, tracking, arquitectura) |
| [`docs/PLAN.md`](docs/PLAN.md) | Roadmap de implementación de 6 fases |
| [`docs/SPEC.md`](docs/SPEC.md) | Especificación técnica completa |
| [`docs/globalmvm-review-simulation.md`](docs/globalmvm-review-simulation.md) | Review simulada desde 7 personas stakeholders |
| [`terraform/README.md`](terraform/README.md) | Guía de despliegue en Azure |
| [`HANDOFF-NORTH-STAR.md`](HANDOFF-NORTH-STAR.md) | Audit de las 9 capabilities no-negociables del prompt original del cliente |

---

## El sandbox de demo

[`lotsofcontext/fixi-demo-dotnet`](https://github.com/lotsofcontext/fixi-demo-dotnet) — Web API ASP.NET Core 9 (`GMVM.EnergyTracker`) con 3 bugs sembrados intencionalmente en el dominio del sector energético:

- **Bug** (`CalculadoraConsumo.cs`): `DivideByZeroException` cuando dos lecturas de medidor comparten la misma fecha
- **Performance** (`MedidorService.cs`): Query N+1 — 51 llamadas SQL para 50 medidores
- **Security** (`AdminController.cs`): Falta el atributo `[Authorize]` (OWASP A01 Broken Access Control)

El repo viene con 5 tests rojos en `master` — ese es el baseline. Corré `fixi resolve` contra cualquiera de los tres work items en `docs/issues/` y mirá los tests pasando a verde mientras se crean los PRs.

---

## Licencia

Propietario — Lots of Context LLC · 2026
