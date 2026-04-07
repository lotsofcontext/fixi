---
name: fix-issue
description: >
  Agente autonomo de resolucion de tickets para repos de clientes. Recibe un issue
  (GitHub URL, Linear link, Jira link, #123 shorthand, o descripcion libre), lo clasifica,
  encuentra la causa raiz en el codebase, implementa el fix, crea branch + commits + PR,
  y actualiza el tracking (ACTIVO.md + Mission Control).
  Triggers: "/fix-issue", "fix this issue", "resuelve este ticket", "fix bug", "arregla esto",
  "fix #123", "resolve issue", "tackle this ticket", o cuando el usuario pega un link de
  issue y pide resolverlo.
  IMPORTANTE: Este skill opera en repos de CLIENTES, nunca en consultoria-x.
---

# Fix Issue - Agente Autonomo de Resolucion de Tickets

Skill que automatiza el ciclo completo: intake -> clasificacion -> analisis -> fix -> PR -> tracking.

**Autonomia default: GUIDED** (aprobacion en cada paso).
El usuario puede cambiar a CONFIRM_PLAN ("rapido"/"auto") o FULL_AUTO ("full auto") en cualquier momento.

---

## Paso 0: Verificacion de Contexto (SAFETY GATE)

**OBLIGATORIO antes de cualquier accion.**

1. Ejecutar `pwd` y verificar que el directorio actual NO es `Z:\consultoria-x\`
   - Si ES consultoria-x: **ABORT** — "Este skill opera en repos de clientes, no en HQ."
2. Verificar repo git: `git rev-parse --is-inside-work-tree`
   - Si no es repo git: **ABORT** — "No estoy en un repositorio git."
3. Verificar working tree limpio: `git status --porcelain`
   - Si hay cambios: **ABORT** — "Hay cambios sin commitear. Stash o commit antes de continuar."
4. Identificar contexto de cliente:
   - Leer variable `$CURRENT_CLIENT` si existe
   - Si no existe, preguntar: "Para que cliente es este issue?"
   - Intentar leer `Z:\consultoria-x\clientes\{cliente}\CLAUDE.md` para convenciones
5. Leer CLAUDE.md del repo actual (si existe) para convenciones locales
6. Verificar remote: `git remote get-url origin` para confirmar que estamos en el repo correcto

**Output al usuario:**
```
CONTEXTO VERIFICADO
  Repo: {remote_url}
  Branch: {current_branch}
  Cliente: {client_name}
  Working tree: limpio
  Convenciones: {cargadas/no encontradas}
```

Esperar confirmacion del usuario antes de continuar.

---

## Paso 1: Parsear la Solicitud

Detectar automaticamente el formato del input:

### GitHub Issue URL
- Pattern: `github\.com/[^/]+/[^/]+/issues/\d+`
- Extraer: `gh issue view {URL} --json title,body,labels,assignees,milestone,number,state`
- Si `gh` falla (auth, repo privado): pedir al usuario que pegue el contenido

### GitHub Issue Shorthand
- Pattern: `#\d+` o `GH-\d+`
- Extraer: `gh issue view {number} --json title,body,labels,assignees,milestone,number,state`

### Linear Ticket
- Pattern: `linear\.app/.+/(issue|task)/[A-Z]+-\d+`
- Extraer: `WebFetch` del URL
- Si falla (auth wall): pedir al usuario que pegue el titulo + descripcion

### Azure DevOps Work Item
- Pattern: `dev\.azure\.com/[^/]+/[^/]+/_workitems/edit/\d+` (URL completo) y shorthand `ADO-\d+`, `WI-\d+`, o `AB#\d+`
- Extraer (preferido): usar `az` CLI con la extension `azure-devops` instalada:
  ```bash
  az boards work-item show --id {id} --output json --organization https://dev.azure.com/{org}
  ```
- Mapeo de campos del JSON de ADO a la estructura normalizada:
  - `fields["System.Title"]` -> `title`
  - `fields["System.Description"]` -> `body` (OJO: este campo viene en HTML — strip tags o avisar al usuario)
  - `fields["System.Tags"]` -> `labels` (string separado por `;`, splitear)
  - `fields["Microsoft.VSTS.Common.Priority"]` -> `priority` (1=critica, 2=alta, 3=media, 4=baja)
  - `fields["System.WorkItemType"]` -> influye en la clasificacion (Bug -> bug, User Story -> feature, Task -> chore, etc.)
  - `id` -> `external_id` como `ADO-{id}` o `WI-{id}`
  - URL original -> `source_url`
- **Fallback 1**: si `az` CLI falla o no esta configurado (sin login, sin extension `azure-devops`), intentar `WebFetch` del URL — puede fallar por auth wall
- **Fallback 2**: si `WebFetch` tambien falla, pedir al usuario que pegue el titulo + descripcion manualmente
- `source_type` debe ser `azure-devops`

### Jira Ticket
- Pattern: `atlassian\.net/browse/[A-Z]+-\d+` o `jira\..+/browse/[A-Z]+-\d+`
- Extraer: `WebFetch` del URL
- Si falla (auth wall): pedir al usuario que pegue el titulo + descripcion

### Texto Libre
- Cualquier input que no matchee los patterns anteriores
- Usar directamente como titulo + descripcion
- Generar `external_id` como `FREE-{YYYYMMDD}-{slug}`

### Normalizacion

Todo input se normaliza a esta estructura interna:
```
SOLICITUD:
  title: {titulo del issue}
  body: {descripcion completa}
  external_id: {GH-42, LINEAR-ABC-123, ADO-456, JIRA-PROJ-789, FREE-20260406-slug}
  labels: [{lista de labels/tags}]
  priority: {critica/alta/media/baja/desconocida}
  source_type: {github/linear/azure-devops/jira/free-text}
  source_url: {URL original o "N/A"}
```

**Output al usuario** — presentar la solicitud parseada y esperar confirmacion.

---

## Paso 2: Clasificar el Issue

Analizar titulo y body contra keywords para determinar tipo:

| Tipo | Branch Prefix | Commit Prefix | Keywords |
|------|--------------|---------------|----------|
| `bug` | `fix/` | `fix:` | error, crash, broken, fails, unexpected, regression, "doesn't work", "no funciona", stack trace, exception, 500, null pointer |
| `feature` | `feat/` | `feat:` | add, implement, create, new, "user story", "como usuario", support, enable, introduce |
| `refactor` | `refactor/` | `refactor:` | refactor, clean up, tech debt, reorganize, simplify, extract, rename, restructure |
| `security` | `security/` | `fix:` | vulnerability, CVE, auth bypass, injection, XSS, CSRF, exposure, leak, OWASP, security |
| `performance` | `perf/` | `perf:` | slow, timeout, memory leak, N+1, optimize, latency, bottleneck, cache, performance |
| `docs` | `docs/` | `docs:` | documentation, README, comment, API docs, changelog, typo in docs |
| `chore` | `chore/` | `chore:` | dependency, CI/CD, config, build, tooling, upgrade, bump, lint |

Si ambiguo (ej: "fix auth bypass" = security, no bug), priorizar:
`security > bug > performance > feature > refactor > docs > chore`

Ver `references/classification.md` para taxonomia completa con ejemplos.

**Output al usuario:**
```
CLASIFICACION:
  Tipo: {type}
  Branch prefix: {prefix}/
  Commit prefix: {prefix}:
  Confianza: {ALTA/MEDIA/BAJA}
  Razon: {por que se clasifico asi}
```

Esperar confirmacion. El usuario puede corregir la clasificacion.

---

## Paso 3: Determinar Nivel de Autonomia

**Default: GUIDED** — aprobacion en cada paso.

| Nivel | Activacion | Comportamiento |
|-------|-----------|----------------|
| **GUIDED** | Default | Pedir OK en: clasificacion, plan de fix, cada archivo modificado, PR, tracking |
| **CONFIRM_PLAN** | Usuario dice "rapido" o "auto" | Presentar plan completo, esperar un solo OK, ejecutar todo |
| **FULL_AUTO** | Usuario dice "full auto" | Ejecutar sin preguntar (EXCEPTO security y migrations) |

**Escaladores automaticos** (fuerzan GUIDED sin importar el nivel elegido):
- Issue toca auth, payments, encryption, o session management
- Issue requiere DB migrations
- Issue modifica CI/CD pipelines (.github/workflows/, Jenkinsfile, etc.)
- Root cause afecta >15 archivos
- Causa raiz ambigua (multiples candidatos)

El usuario puede cambiar nivel en cualquier momento: "sigue en auto" o "para, quiero revisar".

---

## Paso 4: Analisis de Codigo (Root Cause)

### 4.1 Entender la Arquitectura y Cargar Documentacion Tecnica

**Conocimiento del repo**:
- Leer `README.md`, `CLAUDE.md`, `CONTRIBUTING.md` del repo para overview y convenciones
- Detectar stack: `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `pom.xml`, `*.csproj`, `*.sln`
- Identificar estructura: monorepo vs single-repo, framework, entry points

**Documentacion tecnica relacionada al issue** (fuente de conocimiento explicita del prompt del cliente):
- Buscar archivos relevantes en `docs/`, `wiki/`, o cualquier carpeta de documentacion
- `Glob` por `**/*.md` cerca de los archivos potencialmente afectados por el issue
- Leer comentarios de codigo cercanos al area del issue (top-of-file docs, JSDoc/XMLdoc/Sphinx)
- Si el repo tiene un ADR (`docs/adr/` o `docs/decisions/`), revisar decisiones relevantes al modulo afectado
- Si el repo referencia una wiki externa en su README, intentar `WebFetch` (puede fallar por auth — anotar y continuar)

**Estandares definidos del repo** (Cap 4 del prompt: "buenas practicas y estandares definidos"):
- Cargar `.editorconfig` si existe (indentation, line endings, charset)
- Detectar configs de linter para preservar el estilo:
  - `.eslintrc*`, `eslint.config.js` → JavaScript/TypeScript
  - `pyproject.toml [tool.ruff]`, `.ruff.toml`, `.flake8` → Python
  - `.golangci.yml` → Go
  - `rustfmt.toml` → Rust
  - `.csharpierrc`, `.editorconfig` con reglas C# → .NET
- Detectar convenciones de testing (donde viven los tests, naming pattern, fixture conventions)
- Buscar `STYLE.md`, `CODING_STANDARDS.md`, `CONTRIBUTING.md` con reglas adicionales del equipo
- Cargar el `CLAUDE.md` del repo si existe (puede tener reglas especificas para agentes)

Estos hallazgos se incluyen en el contexto del analisis (Paso 4.3) y se **respetan obligatoriamente** en la implementacion (Paso 6). Si los estandares estan en conflicto entre si (ej: `.editorconfig` dice 2 espacios y `.eslintrc` dice 4), priorizar en este orden: CLAUDE.md del repo > linter config > .editorconfig > defaults del lenguaje.

### 4.2 Buscar la Causa Raiz
1. **Keyword search**: Extraer terminos clave del issue (error messages, nombres de funciones, componentes)
   - `Grep` con cada keyword en el codebase
   - Rankear archivos por relevancia (numero de matches, proximidad al area reportada)

2. **Stack trace analysis** (si hay stack trace en el issue):
   - Parsear cada frame del stack trace
   - Leer cada archivo/linea mencionado
   - Trazar desde el frame mas profundo hacia arriba

3. **Dependency tracing**:
   - Seguir imports/requires del archivo afectado
   - Mapear que otros archivos dependen del codigo afectado (reverse dependencies)

4. **Test examination**:
   - Buscar tests existentes: `Grep` para `test`, `spec`, `_test` en archivos que matcheen el componente
   - Leer tests para entender el comportamiento esperado

### 4.3 Formular Hipotesis

Crear una hipotesis especifica:
- QUE esta mal (la causa raiz exacta)
- DONDE esta (archivos y lineas)
- POR QUE ocurre (condiciones que lo triggerearon)
- COMO arreglarlo (cambios propuestos)

### 4.4 Presentar Hallazgos

```
ROOT CAUSE ANALYSIS

Issue: {title}
Tipo: {classification}
Confianza: {ALTA/MEDIA/BAJA}

Causa raiz:
  {Explicacion clara de que esta mal y por que}

Archivos a modificar:
  1. {path/to/file1.ts}:{line_start}-{line_end} — {que cambiar}
  2. {path/to/file2.ts}:{line} — {que cambiar}

Archivos nuevos (si aplica):
  - {path/to/new_test.ts} — test de regresion

Riesgo: {LOW/MEDIUM/HIGH}
  - {explicacion del nivel de riesgo}

Side effects potenciales:
  - {lista o "Ninguno esperado"}
```

En modo GUIDED: esperar aprobacion antes de proceder a implementacion.

---

## Paso 5: Crear Branch

### Detectar branch default
```bash
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||')
if [ -z "$DEFAULT_BRANCH" ]; then
  DEFAULT_BRANCH=$(git branch -r | grep -oP 'origin/\K(main|master|develop)' | head -1)
fi
```

### Naming convention
Prioridad:
1. Convencion del cliente (de su CLAUDE.md)
2. Default: `{type_prefix}/{external_id}-{slug}`

Ejemplos:
- `fix/GH-42-null-pointer-user-profile`
- `feat/LINEAR-ABC-123-add-export-csv`
- `fix/JIRA-PROJ-789-timeout-bulk-import`
- `refactor/FREE-20260406-cleanup-auth`

Slug: primeras 5-6 palabras del titulo, kebab-case, max 50 chars.

### Ejecucion
```bash
git checkout $DEFAULT_BRANCH
git pull origin $DEFAULT_BRANCH
git checkout -b {branch_name}
```

**Output al usuario:**
```
BRANCH CREADO: {branch_name}
  Base: {default_branch} (up to date)
```

---

## Paso 6: Implementar el Fix

### Reglas de implementacion
- **Cambio minimo** que resuelve el issue — nada mas, nada menos
- Seguir convenciones del repo (indentacion, naming, etc.)
- Si hay linter configurado (eslint, prettier, black, rustfmt): ejecutar despues de cambios
- NO agregar features no solicitadas
- NO refactorizar codigo que no esta relacionado con el issue
- NO agregar docstrings/comments salvo donde la logica no es obvia

### Commits
Un commit por cambio logico. Formato:
```
{commit_prefix} {descripcion concisa}

{explicacion mas larga si el fix no es obvio}

Fixes: {external_id}
```

En modo GUIDED: mostrar cada cambio al usuario antes de commitear.
En modo CONFIRM_PLAN: commitear todos los cambios segun el plan aprobado.

---

## Paso 7: Ejecutar Validaciones Basicas

El prompt del cliente exige **"validaciones basicas"** en plural (Cap 6 del North Star). Esto significa **ejecutar los 3 tipos de validacion estandar cuando esten disponibles en el repo**: tests, lint, build. Si el repo no tiene runner para una de las tres, **documentarlo en el PR como N/A — no fallar**.

### 7.1 Detectar runners disponibles

Por cada tipo de validacion, buscar en este orden y registrar el primero encontrado:

#### Tests
1. Campo "test commands" en `CLAUDE.md` del cliente o del repo
2. `package.json` → `scripts.test`, `scripts."test:unit"`, `scripts."test:integration"`
3. `Makefile` → target `test`
4. `pyproject.toml` / `pytest.ini` → pytest config
5. `Cargo.toml` → `cargo test`
6. `go.mod` → `go test ./...`
7. `*.sln` / `*.csproj` → `dotnet test`
8. `pom.xml` → `mvn test`
9. `build.gradle` / `build.gradle.kts` → `gradle test`

#### Lint
1. Campo "lint commands" en `CLAUDE.md` del cliente o del repo
2. `package.json` → `scripts.lint`, `scripts."lint:check"`
3. `.eslintrc*` / `eslint.config.js` → `npx eslint .`
4. `pyproject.toml [tool.ruff]` o `ruff.toml` → `ruff check .`
5. `.flake8` → `flake8 .`
6. `pyproject.toml [tool.black]` → `black --check .`
7. `.golangci.yml` → `golangci-lint run`
8. `rustfmt.toml` o presencia de `cargo` → `cargo fmt --check; cargo clippy --all-targets -- -D warnings` (ambos deben correr aunque uno falle — no usar `&&`)
9. `*.csproj` → `dotnet format --verify-no-changes`
10. `.editorconfig` solo (sin tool especifico) → skip lint, marcar N/A

#### Build
1. Campo "build commands" en `CLAUDE.md` del cliente o del repo
2. `package.json` → `scripts.build`
3. `Makefile` → target `build` o `all`
4. `Cargo.toml` → `cargo build --release`
5. `go.mod` → `go build ./...`
6. `*.sln` / `*.csproj` → `dotnet build`
7. `pom.xml` → `mvn compile`
8. `build.gradle` → `gradle build`

### 7.2 Ejecutar las validaciones (en orden)

Ejecutar **en este orden**: tests → lint → build. Capturar exit code y output resumido de cada una. Si una falla, **continuar con las siguientes** para tener un reporte completo, no abortar a la primera.

```bash
# Ejemplo .NET
dotnet test 2>&1 | tail -50
dotnet format --verify-no-changes 2>&1 | tail -20
dotnet build 2>&1 | tail -20

# Ejemplo Node.js
npm test 2>&1 | tail -50
npm run lint 2>&1 | tail -20
npm run build 2>&1 | tail -20

# Ejemplo Python
python -m pytest tests/ -v 2>&1 | tail -50
ruff check . 2>&1 | tail -20
# Build N/A para libs Python puras — anotar
```

### 7.3 Interpretar resultados

Por cada validacion:

| Resultado | Accion |
|-----------|--------|
| **PASS** | Continuar |
| **FAIL por nuestro codigo** | Arreglar y re-correr la validacion. Iterar hasta verde |
| **FAIL pre-existente** (estaba rojo antes del fix) | **Documentar en PR**, NO arreglar (scope creep) |
| **No hay runner detectado** | Anotar en el PR como `N/A — no detectado en el repo` |
| **No hay infraestructura** (ej: build sin compilador instalado en el sandbox) | Anotar en el PR, no bloquear |

**Regla**: si el fix introduce un **nuevo failure** en cualquiera de las 3 validaciones, hay que arreglarlo antes de crear el PR. Si los failures son pre-existentes (estaban rojos antes del fix), se documentan pero no se arreglan — eso es scope creep.

**Importante**: para verificar si un failure es "pre-existente", correr la validacion contra el branch base ANTES de crear la rama del fix (snapshot). Comparar despues.

### 7.4 Output al usuario

```
VALIDACIONES BASICAS:
  Tests:  {PASS/FAIL/N/A}  comando: `{cmd}`  resultado: {X passed, Y failed, Z skipped}
  Lint:   {PASS/FAIL/N/A}  comando: `{cmd}`  resultado: {0 errors, N warnings}
  Build:  {PASS/FAIL/N/A}  comando: `{cmd}`  resultado: {OK/{N errors}}

  {Si hay fails introducidos por el fix: explicacion + accion tomada (arreglado, escalado a usuario)}
  {Si hay fails pre-existentes: documentado para PR, no se arreglo (scope creep)}
```

---

## Paso 8: Crear Pull Request

### Detectar plataforma del remote
```bash
# Auto-detectar si el remote es Azure Repos o GitHub
REMOTE_URL=$(git remote get-url origin)
if echo "$REMOTE_URL" | grep -qE "dev\.azure\.com|visualstudio\.com"; then
  IS_AZURE_REPOS=true
else
  IS_AZURE_REPOS=false
fi
```

### Push branch
```bash
git push -u origin {branch_name}
```

### Template del body (compartido entre GitHub y Azure Repos)

El body del PR es **identico** en ambas plataformas. Tiene **las 3 secciones nombradas que el cliente exige** en Cap 8 del North Star: **descripcion tecnica**, **cambios realizados**, y **posibles impactos**. Escribirlo a un archivo temporal para reutilizarlo:

```markdown
## Issue

{Link al issue original o descripcion}

## Clasificacion

**Tipo**: {bug/feature/refactor/security/performance/docs/chore}
**Prioridad**: {critica/alta/media/baja}
**Fuente**: {github/linear/azure-devops/jira/free-text}

## Descripcion tecnica

{Que es el problema o la mejora. Si es bug: causa raiz exacta y por que ocurria.
Si es feature: por que se necesita y cual es la solucion implementada.
Si es refactor: que estructura cambia y por que mejora.
2-4 oraciones tecnicas, no marketing.}

## Cambios realizados

{Lista con bullet points, un item por archivo modificado:}
- `path/to/file.ts` — {que se cambio y por que}
- `path/to/test.ts` — {test agregado/modificado, que cubre}

## Posibles impactos

**Riesgo**: {LOW/MEDIUM/HIGH}
**Areas afectadas**: {modulos, features o subsistemas que tocan estos cambios}
**Breaking changes**: {No / Si — detalles especificos si Si}
**Side effects esperados**: {lista o "Ninguno"}
**Verificacion manual recomendada**: {pasos especificos para que el reviewer pruebe el fix}

## Validaciones ejecutadas

- **Tests**: {PASS/FAIL/N/A} — `{comando}` — {X passed, Y failed}
- **Lint**: {PASS/FAIL/N/A} — `{comando}` — {0 errors, N warnings}
- **Build**: {PASS/FAIL/N/A} — `{comando}` — {OK / {N errors}}

{Si hay fails pre-existentes (no introducidos por este PR): listarlos aqui con disclaimer}

## Tracking

- **Issue**: {external_id} ({source_url})
- **Cliente**: {client_name}
- **Clasificacion**: {type}

---
*Generado por fix-issue skill — revisar cuidadosamente antes de merge*
```

### Crear PR — GitHub (default)

```bash
if [ "$IS_AZURE_REPOS" = "false" ]; then
  gh pr create --title "{commit_prefix}: {titulo conciso}" --body "$(cat <<'EOF'
## Issue

{Link al issue original o descripcion}

## Clasificacion

**Tipo**: {bug/feature/refactor/security/performance/docs/chore}
**Prioridad**: {critica/alta/media/baja}
**Fuente**: {github/linear/azure-devops/jira/free-text}

## Descripcion tecnica

{Que es el problema o la mejora. Si es bug: causa raiz exacta y por que ocurria.
Si es feature: por que se necesita y cual es la solucion implementada.
Si es refactor: que estructura cambia y por que mejora.
2-4 oraciones tecnicas, no marketing.}

## Cambios realizados

{Lista con bullet points, un item por archivo modificado:}
- `path/to/file.ts` — {que se cambio y por que}
- `path/to/test.ts` — {test agregado/modificado, que cubre}

## Posibles impactos

**Riesgo**: {LOW/MEDIUM/HIGH}
**Areas afectadas**: {modulos, features o subsistemas que tocan estos cambios}
**Breaking changes**: {No / Si — detalles especificos si Si}
**Side effects esperados**: {lista o "Ninguno"}
**Verificacion manual recomendada**: {pasos especificos para que el reviewer pruebe el fix}

## Validaciones ejecutadas

- **Tests**: {PASS/FAIL/N/A} — `{comando}` — {X passed, Y failed}
- **Lint**: {PASS/FAIL/N/A} — `{comando}` — {0 errors, N warnings}
- **Build**: {PASS/FAIL/N/A} — `{comando}` — {OK / {N errors}}

{Si hay fails pre-existentes (no introducidos por este PR): listarlos aqui con disclaimer}

## Tracking

- **Issue**: {external_id} ({source_url})
- **Cliente**: {client_name}
- **Clasificacion**: {type}

---
*Generado por fix-issue skill — revisar cuidadosamente antes de merge*
EOF
)"
fi
```

Si el issue es de GitHub: agregar `Closes #{number}` en el body para auto-close on merge.

### Crear PR — Azure Repos (si `IS_AZURE_REPOS=true`)

```bash
if [ "$IS_AZURE_REPOS" = "true" ]; then
  # Escribir el body a un archivo temporal (az repos pr create acepta @filename)
  cat > /tmp/pr-body.md <<'EOF'
## Issue

{Link al issue original o descripcion}

## Clasificacion

**Tipo**: {bug/feature/refactor/security/performance/docs/chore}
**Prioridad**: {critica/alta/media/baja}
**Fuente**: {github/linear/azure-devops/jira/free-text}

## Descripcion tecnica

{Que es el problema o la mejora. Si es bug: causa raiz exacta y por que ocurria.
Si es feature: por que se necesita y cual es la solucion implementada.
Si es refactor: que estructura cambia y por que mejora.
2-4 oraciones tecnicas, no marketing.}

## Cambios realizados

{Lista con bullet points, un item por archivo modificado:}
- `path/to/file.ts` — {que se cambio y por que}
- `path/to/test.ts` — {test agregado/modificado, que cubre}

## Posibles impactos

**Riesgo**: {LOW/MEDIUM/HIGH}
**Areas afectadas**: {modulos, features o subsistemas que tocan estos cambios}
**Breaking changes**: {No / Si — detalles especificos si Si}
**Side effects esperados**: {lista o "Ninguno"}
**Verificacion manual recomendada**: {pasos especificos para que el reviewer pruebe el fix}

## Validaciones ejecutadas

- **Tests**: {PASS/FAIL/N/A} — `{comando}` — {X passed, Y failed}
- **Lint**: {PASS/FAIL/N/A} — `{comando}` — {0 errors, N warnings}
- **Build**: {PASS/FAIL/N/A} — `{comando}` — {OK / {N errors}}

{Si hay fails pre-existentes (no introducidos por este PR): listarlos aqui con disclaimer}

## Tracking

- **Issue**: {external_id} ({source_url})
- **Cliente**: {client_name}
- **Clasificacion**: {type}

---
*Generado por fix-issue skill — revisar cuidadosamente antes de merge*
EOF

  # Crear el PR en Azure Repos
  PR_JSON=$(az repos pr create \
    --source-branch "{branch_name}" \
    --target-branch "{default_branch}" \
    --title "{commit_prefix}: {titulo conciso}" \
    --description "@/tmp/pr-body.md" \
    --output json)

  # Extraer el URL del PR desde el campo `webUrl` del JSON
  PR_URL=$(echo "$PR_JSON" | jq -r '.webUrl // .repository.webUrl')
  PR_ID=$(echo "$PR_JSON" | jq -r '.pullRequestId')

  # Si el issue original era un ADO Work Item, linkear el PR al work item
  if [ "{source_type}" = "azure-devops" ]; then
    az repos pr work-item add --id "$PR_ID" --work-items "{wi_id}"
  fi
fi
```

**Notas sobre Azure Repos:**
- `az repos pr create` retorna JSON con el URL del PR en el campo `webUrl` — ese es el que se reporta al usuario
- Terminologia ADO: "Pull Request" (PR), "Work Item" (equivalente a issue), "Reviewer" (similar a GitHub)
- `--description "@filename"` lee el body desde un archivo (util para markdown multi-linea)
- El link PR <-> Work Item se hace con `az repos pr work-item add` despues de crear el PR

**Output al usuario:**
```
PR CREADO: {pr_url}
  Plataforma: {GitHub/Azure Repos}
  Titulo: {pr_title}
  Base: {default_branch} <- {branch_name}
  Archivos: {count} modificados
  {Si ADO y origen fue Work Item:} Work Item {wi_id} linkeado al PR
```

---

## Paso 9: Actualizar Tracking (TRIPLE-WRITE OBLIGATORIO)

**Este paso es MANDATORIO. NUNCA se salta.**

### A. ACTIVO.md del cliente

Leer `Z:\consultoria-x\clientes\{cliente}\tasks\ACTIVO.md`.
Si el archivo existe:
- Buscar si el issue ya tiene una fila (por external_id o titulo)
- Si existe: actualizar estado y agregar PR URL
- Si no existe: agregar nueva fila:
  ```
  | {external_id} | {titulo} | {priority} | {fecha} | PR: {pr_url} - {tipo}: {descripcion} |
  ```

Si el archivo NO existe: crear la estructura basica y agregar la fila.

### B. Mission Control

Leer `Z:\consultoria-x\mission-control\mission-control\data\tasks.json`.

Buscar task existente (por titulo keywords o external_id en tags/notes).
- Si encontrado: actualizar `kanban` a "in-progress", agregar note con PR URL, actualizar `updatedAt`
- Si no encontrado: crear nuevo task:
  ```json
  {
    "id": "task_{timestamp}",
    "title": "{commit_prefix}: {titulo}",
    "description": "Issue {external_id} - {body_resumen}\n\nPR: {pr_url}",
    "importance": "{importante si security/bug, no-importante si docs/chore}",
    "urgency": "{urgente si security, no-urgente para el resto}",
    "kanban": "in-progress",
    "projectId": null,
    "assignedTo": "developer",
    "tags": ["{tipo}", "{cliente}", "fix-issue"],
    "notes": "Generado por fix-issue skill",
    "createdAt": "{ISO8601}",
    "updatedAt": "{ISO8601}"
  }
  ```

Agregar evento a `activity-log.json`:
```json
{
  "id": "log_{timestamp}",
  "type": "task_created",
  "taskId": "{task_id}",
  "agentId": "developer",
  "details": "fix-issue: {titulo} - PR {pr_url}",
  "timestamp": "{ISO8601}"
}
```

Agregar reporte a `inbox.json`:
```json
{
  "id": "msg_{timestamp}",
  "type": "report",
  "from": "developer",
  "to": "me",
  "subject": "Fix completado: {titulo}",
  "body": "Issue {external_id} resuelto. PR: {pr_url}. Tipo: {tipo}. Archivos: {count}.",
  "status": "unread",
  "createdAt": "{ISO8601}"
}
```

### C. Output final en consola

```
FIX COMPLETE

  Issue: {title}
  Tipo: {type} | Riesgo: {risk}
  Branch: {branch_name}
  PR: {pr_url}
  Archivos cambiados: {count}
  Tests: {PASS/FAIL/SKIP/NO_TESTS}

  Tracking actualizado:
    [x] ACTIVO.md ({cliente})
    [x] Mission Control task {task_id}
    [x] Activity log
    [x] Inbox report

  NEXT: El developer puede ir al PR y revisar/probar.
        Asignar reviewer en {plataforma del cliente}.
```

---

## Paso 10: Cleanup y Rollback

### Si todo salio bien
- Reportar exito (Paso 9 output)
- Quedarse en el branch del fix (el usuario decide si volver a default)

### Si algo fallo mid-execution
1. Guardar el error para reportar
2. Ejecutar rollback:
   ```bash
   git checkout {original_branch}
   git branch -D {branch_name} 2>/dev/null
   ```
3. Reportar:
   ```
   FIX ABORTADO

     Issue: {title}
     Fallo en: Paso {N} - {nombre del paso}
     Error: {descripcion del error}
     Rollback: Branch {branch_name} eliminado, volvimos a {original_branch}

     Recomendacion: {que hacer para resolver manualmente}
   ```

---

## Notas de Implementacion

### Convenciones del cliente
El skill lee convenciones de estas fuentes (en orden de prioridad):
1. CLAUDE.md en el root del repo del cliente
2. `Z:\consultoria-x\clientes\{cliente}\CLAUDE.md`
3. Defaults del skill (conventional commits, kebab-case branches)

### Guardrails
Ver `references/guardrails.md` para reglas completas de seguridad.
Los guardrails mas criticos:
- NUNCA operar en main/master/develop directamente
- NUNCA force push
- ABORT si working tree dirty
- Verificar contexto de cliente
- Si >15 archivos: escalar a GUIDED
- NUNCA tocar .env, credentials, keys
- Rollback automatico si algo falla
- NUNCA inventar informacion: si faltan datos, DETENER el flujo y reportar que falta. No asumir causa raiz, impacto, o contexto sin evidencia del codigo o del issue

### Clasificacion
Ver `references/classification.md` para taxonomia detallada con keywords y ejemplos.
