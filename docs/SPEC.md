# SPEC: Fix-Issue Agent -- Especificacion Tecnica
#spec #skill #fix-issue #fase-1

> Documento padre: [[docs/planning/PLAN-FIX-ISSUE-AGENT|PLAN]]
> Skill: [[.claude/skills/fix-issue/SKILL|fix-issue]]
> Clasificacion: [[.claude/skills/fix-issue/references/classification|Taxonomia]]
> Guardrails: [[.claude/skills/fix-issue/references/guardrails|Guardrails]]
> Fecha: 2026-04-06
> Estado: EN DESARROLLO

---

## Arquitectura

```
                            FIX-ISSUE AGENT — FLUJO COMPLETO
                            ================================

  INPUT                                                                    OUTPUT
  -----                                                                    ------
  GitHub URL ─┐                                                        ┌─> PR en GitHub
  Linear URL ─┤                                                        ├─> ACTIVO.md actualizado
  Jira URL ───┼─> [PARSE] ─> [CLASSIFY] ─> [AUTONOMY] ─> [ANALYZE] ──┼─> tasks.json entry
  #123 ───────┤       |          |             |              |        ├─> activity-log.json event
  Texto libre ┘       v          v             v              v        └─> inbox.json message
                  Solicitud   Tipo +       Nivel de     Root Cause
                  normalizada  prefix      autonomia    + plan de fix
                                                             |
                                                             v
                                              [BRANCH] ─> [IMPLEMENT] ─> [TEST] ─> [PR] ─> [TRACK]
                                                  |            |            |          |        |
                                                  v            v            v          v        v
                                              git checkout  Edit files   npm test   gh pr   triple-write
                                              -b fix/...    + commit     cargo test create  MC + ACTIVO

  ROLLBACK (si falla en cualquier paso post-branch):
  ─────────────────────────────────────────────────
  git checkout {original} && git branch -D {fix_branch}


  GUARDRAILS (verificacion continua):
  ───────────────────────────────────
  [G1] pwd != consultoria-x       [G5] branch != main/master/develop
  [G2] git repo valido             [G6] no archivos sensibles (.env, keys)
  [G3] working tree limpio         [G7] no force push
  [G4] remote = cliente correcto   [G8] >15 archivos => GUIDED

  MODOS DE AUTONOMIA:
  ───────────────────
  GUIDED ──────> aprobacion en CADA paso (default)
  CONFIRM_PLAN > aprobacion UNA vez (plan completo), luego auto
  FULL_AUTO ───> sin aprobacion (EXCEPTO security, migrations, CI/CD)
```

---

## Stack Tecnico

### Herramientas de Claude Code
| Herramienta | Uso en el skill |
|-------------|-----------------|
| `Bash` | git commands, test runners, `gh` CLI, `pwd`, deteccion de stack |
| `Grep` | Keyword search en codebase, buscar tests, buscar patterns sensibles |
| `Glob` | Encontrar archivos por patron (package.json, CLAUDE.md, test files) |
| `Read` | Leer archivos de codigo, issue bodies, configs, ACTIVO.md, JSONs de MC |
| `Edit` | Aplicar fixes al codigo, actualizar ACTIVO.md |
| `Write` | Crear archivos nuevos (tests de regresion), escribir JSONs de MC |
| `WebFetch` | Obtener contenido de Linear/Jira URLs (cuando `gh` no aplica) |

### CLIs Externos
| CLI | Uso |
|-----|-----|
| `git` | Branch management, commits, push, status, diff, remote verification |
| `gh` | GitHub issue view, PR create, PR list, repo verification |

### Archivos de Datos (Mission Control)
| Archivo | Operacion | Path |
|---------|-----------|------|
| `tasks.json` | Read + Write | `Z:\consultoria-x\mission-control\mission-control\data\tasks.json` |
| `activity-log.json` | Read + Write | `Z:\consultoria-x\mission-control\mission-control\data\activity-log.json` |
| `inbox.json` | Read + Write | `Z:\consultoria-x\mission-control\mission-control\data\inbox.json` |
| `ACTIVO.md` | Read + Edit | `Z:\consultoria-x\clientes\{cliente}\tasks\ACTIVO.md` |

---

## Especificaciones por Fase

### Fase 1: Fundamentos (MVP)

> **Scope**: GitHub Issues solamente, modo GUIDED unicamente, tracking manual (consola).
> Branch + implement + PR funcional end-to-end para un bug fix simple.

---

#### Tarea 1.1: Safety Gate (Paso 0)
**Objetivo**: Verificar que el entorno es seguro para operar antes de tocar nada.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (ya tiene la logica; esta tarea la codifica como checklist ejecutable)

- Logica (pseudocodigo):
```
function safetyGate():
  // 1. Verificar directorio
  cwd = Bash("pwd")
  if cwd contiene "consultoria-x":
    ABORT("Este skill opera en repos de clientes, no en HQ.")

  // 2. Verificar git repo
  is_git = Bash("git rev-parse --is-inside-work-tree 2>/dev/null")
  if is_git != "true":
    ABORT("No estoy en un repositorio git.")

  // 3. Verificar working tree limpio
  dirty = Bash("git status --porcelain")
  if dirty != "":
    ABORT("Hay cambios sin commitear. Stash o commit antes de continuar.")

  // 4. Identificar cliente
  if env.CURRENT_CLIENT existe:
    client = env.CURRENT_CLIENT
  else:
    client = preguntar_usuario("Para que cliente es este issue?")

  // 5. Cargar convenciones del cliente
  client_claude = Read("Z:/consultoria-x/clientes/{client}/CLAUDE.md")  // puede fallar
  repo_claude = Read("./CLAUDE.md")  // puede fallar

  // 6. Verificar remote
  remote = Bash("git remote get-url origin")
  branch = Bash("git branch --show-current")

  // 7. Presentar y esperar confirmacion
  mostrar("CONTEXTO VERIFICADO\n  Repo: {remote}\n  Branch: {branch}\n  Cliente: {client}\n  Working tree: limpio\n  Convenciones: {cargadas/no encontradas}")

  return { client, remote, branch, client_conventions, repo_conventions }
```

- Inputs: Ninguno (lee del entorno)
- Outputs: Objeto `context` con: `client`, `remote_url`, `current_branch`, `client_conventions`, `repo_conventions`
- Edge cases:
  - `pwd` es un subdirectorio de consultoria-x (ej: `consultoria-x/clientes/x/`) -- el check debe usar substring match, no equality
  - Git no esta instalado -- `git rev-parse` falla con error no-git; capturar stderr
  - Remote tiene multiples origins (origin, upstream) -- usar `origin` siempre
  - CLAUDE.md del cliente no existe -- no es blocker, continuar con defaults
  - El usuario no sabe el nombre del cliente -- listar directorios en `clientes/` como opciones

**Verificacion**:
1. Ejecutar en `Z:\consultoria-x\` -- debe abortar con mensaje claro
2. Ejecutar en un directorio no-git -- debe abortar
3. Ejecutar en un repo con cambios sin commitear -- debe abortar
4. Ejecutar en un repo limpio de cliente -- debe pasar y mostrar contexto

---

#### Tarea 1.2: Parser de GitHub Issues (Paso 1 - solo GitHub)
**Objetivo**: Parsear GitHub issue URL o shorthand (#123) y normalizar a estructura interna.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (refinar la seccion de parsing)

- Logica (pseudocodigo):
```
function parseInput(raw_input):
  // Intentar patterns en orden
  
  // Pattern 1: GitHub URL
  match = regex("github\.com/([^/]+)/([^/]+)/issues/(\d+)", raw_input)
  if match:
    owner = match[1]
    repo = match[2]
    number = match[3]
    data = Bash("gh issue view {number} --repo {owner}/{repo} --json title,body,labels,assignees,milestone,number,state")
    if data.exitCode != 0:
      // gh falla (auth, repo privado, rate limit)
      pedir_usuario("No pude acceder al issue. Pega el titulo y descripcion.")
      return parseInput(texto_pegado)  // recursion con texto libre
    json = JSON.parse(data.stdout)
    return normalizarGitHub(json, "https://github.com/{owner}/{repo}/issues/{number}")

  // Pattern 2: Shorthand #123 o GH-123
  match = regex("(?:#|GH-)(\d+)", raw_input)
  if match:
    number = match[1]
    data = Bash("gh issue view {number} --json title,body,labels,assignees,milestone,number,state")
    if data.exitCode != 0:
      ABORT("No pude acceder al issue #{number}. Verifica que estas en el repo correcto y gh esta autenticado.")
    json = JSON.parse(data.stdout)
    remote = Bash("git remote get-url origin")
    url = construirURL(remote, number)  // extraer owner/repo del remote
    return normalizarGitHub(json, url)

  // Pattern 3: Texto libre (fallback en Fase 1)
  slug = kebabCase(raw_input.split(" ").slice(0, 5).join("-"))
  date = formatDate("YYYYMMDD")
  return {
    title: raw_input.split("\n")[0].slice(0, 100),
    body: raw_input,
    external_id: "FREE-{date}-{slug}",
    labels: [],
    priority: "desconocida",
    source_type: "free-text",
    source_url: "N/A"
  }

function normalizarGitHub(json, url):
  // Mapear prioridad de labels
  priority = "desconocida"
  for label in json.labels:
    if label.name contiene "critical" or "P0": priority = "critica"
    elif label.name contiene "high" or "P1": priority = "alta"
    elif label.name contiene "medium" or "P2": priority = "media"
    elif label.name contiene "low" or "P3": priority = "baja"

  return {
    title: json.title,
    body: json.body || "(sin descripcion)",
    external_id: "GH-{json.number}",
    labels: json.labels.map(l => l.name),
    priority: priority,
    source_type: "github",
    source_url: url
  }
```

- Inputs: `raw_input` (string) -- lo que el usuario escribio o pego
- Outputs: Objeto `solicitud` normalizado:
```json
{
  "title": "string (max 100 chars)",
  "body": "string (descripcion completa)",
  "external_id": "GH-42 | FREE-20260406-slug",
  "labels": ["string"],
  "priority": "critica | alta | media | baja | desconocida",
  "source_type": "github | free-text",
  "source_url": "URL | N/A"
}
```
- Edge cases:
  - Issue body es null/vacio -- usar "(sin descripcion)" como body
  - `gh` no esta autenticado -- error code 1; pedir texto manual
  - Issue esta cerrado (state=CLOSED) -- advertir al usuario, preguntar si continuar
  - URL es de un PR, no issue (`/pull/` en vez de `/issues/`) -- detectar y avisar
  - Shorthand #123 ambiguo (no estamos en el repo correcto) -- verificar con remote URL
  - Rate limit de GitHub API -- detectar HTTP 403, sugerir esperar o pegar manualmente
  - Titulo con caracteres especiales (comillas, backticks) -- escapar para shell

**Verificacion**:
1. Input: `https://github.com/owner/repo/issues/42` -- debe extraer via `gh`
2. Input: `#42` -- debe usar repo actual
3. Input: `fix the login timeout bug on mobile` -- debe generar FREE-20260406-fix-the-login-timeout
4. Input: URL de repo privado sin auth -- debe pedir texto manual
5. Input: `https://github.com/owner/repo/pull/10` -- debe advertir que es PR, no issue

---

#### Tarea 1.3: Clasificacion basica por keywords (Paso 2)
**Objetivo**: Clasificar el issue en uno de los 7 tipos usando keyword matching.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (Paso 2 ya tiene tabla de keywords)
- Referencia: `.claude/skills/fix-issue/references/classification.md`

- Logica (pseudocodigo):
```
// Definicion de keywords por tipo (orden = prioridad de clasificacion)
TYPES = [
  {
    type: "security",
    prefix_branch: "security/",
    prefix_commit: "fix:",
    keywords_primary: ["vulnerability", "CVE", "auth bypass", "injection", "XSS", "CSRF", "security"],
    keywords_secondary: ["exposure", "leak", "OWASP", "SQL injection", "RCE", "SSRF",
      "path traversal", "privilege escalation", "token", "session", "encryption",
      "certificate", "TLS", "SSL", "CORS", "CSP", "sanitize"],
    force_guided: true
  },
  {
    type: "bug",
    prefix_branch: "fix/",
    prefix_commit: "fix:",
    keywords_primary: ["error", "crash", "broken", "fails", "unexpected", "regression",
      "bug", "defect", "incorrect", "wrong"],
    keywords_secondary: ["doesn't work", "no funciona", "not working", "stack trace",
      "exception", "500", "404", "null pointer", "undefined", "NaN", "infinite loop",
      "race condition", "deadlock", "data loss", "corrupted"],
    force_guided: false
  },
  {
    type: "performance",
    prefix_branch: "perf/",
    prefix_commit: "perf:",
    keywords_primary: ["slow", "timeout", "memory leak", "N+1", "optimize", "latency", "performance"],
    keywords_secondary: ["bottleneck", "cache", "index", "query optimization", "lazy load",
      "pagination", "batch", "bulk", "connection pool", "rate limit", "throughput",
      "CPU usage", "OOM"],
    force_guided: false
  },
  {
    type: "feature",
    prefix_branch: "feat/",
    prefix_commit: "feat:",
    keywords_primary: ["add", "implement", "create", "new", "support", "enable", "introduce", "build"],
    keywords_secondary: ["user story", "como usuario", "as a user", "feature request",
      "enhancement", "capability", "integrate", "extend", "allow"],
    force_guided: false
  },
  {
    type: "refactor",
    prefix_branch: "refactor/",
    prefix_commit: "refactor:",
    keywords_primary: ["refactor", "clean up", "tech debt", "reorganize", "simplify",
      "extract", "rename", "restructure"],
    keywords_secondary: ["DRY", "SOLID", "decouple", "modularize", "split", "merge",
      "consolidate", "code smell"],
    force_guided: false
  },
  {
    type: "docs",
    prefix_branch: "docs/",
    prefix_commit: "docs:",
    keywords_primary: ["documentation", "README", "comment", "API docs", "changelog", "docs"],
    keywords_secondary: ["typo", "example", "tutorial", "guide", "reference", "JSDoc",
      "docstring", "swagger", "OpenAPI"],
    force_guided: false
  },
  {
    type: "chore",
    prefix_branch: "chore/",
    prefix_commit: "chore:",
    keywords_primary: ["dependency", "CI/CD", "config", "build", "tooling", "upgrade", "bump", "lint"],
    keywords_secondary: ["devDependency", "package", "version", "Dockerfile",
      "GitHub Actions", "pipeline", "formatter", "pre-commit", "gitignore"],
    force_guided: false
  }
]

function classify(solicitud):
  text = (solicitud.title + " " + solicitud.body).toLowerCase()
  scores = {}

  for type_def in TYPES:
    score = 0
    for kw in type_def.keywords_primary:
      if kw.lower() in text:
        score += 3  // primary keywords pesan mas
    for kw in type_def.keywords_secondary:
      if kw.lower() in text:
        score += 1
    scores[type_def.type] = score

  // Obtener tipo con mayor score
  // El orden en TYPES ya es la prioridad de desempate (security > bug > perf > ...)
  best = null
  best_score = 0
  for type_def in TYPES:
    if scores[type_def.type] > best_score:
      best = type_def
      best_score = scores[type_def.type]
    elif scores[type_def.type] == best_score and best_score > 0:
      // En empate, el primero en TYPES gana (prioridad por orden)
      pass  // best ya tiene prioridad

  // Si ningun keyword matcheo
  if best_score == 0:
    best = TYPES[1]  // default a "bug" (el mas comun)
    confidence = "BAJA"
  elif best_score <= 2:
    confidence = "MEDIA"
  else:
    confidence = "ALTA"

  return {
    type: best.type,
    branch_prefix: best.prefix_branch,
    commit_prefix: best.prefix_commit,
    confidence: confidence,
    force_guided: best.force_guided,
    reason: "Keywords encontrados: {lista de keywords que matchearon}"
  }
```

- Inputs: Objeto `solicitud` del Paso 1
- Outputs: Objeto `clasificacion`:
```json
{
  "type": "bug | feature | refactor | security | performance | docs | chore",
  "branch_prefix": "fix/ | feat/ | refactor/ | security/ | perf/ | docs/ | chore/",
  "commit_prefix": "fix: | feat: | refactor: | fix: | perf: | docs: | chore:",
  "confidence": "ALTA | MEDIA | BAJA",
  "force_guided": true/false,
  "reason": "string"
}
```
- Edge cases:
  - Ningun keyword matchea -- default a `bug` con confianza BAJA; el usuario puede corregir
  - Multiples tipos con mismo score -- gana el de mayor prioridad (security > bug > ...)
  - Labels del issue contienen tipo explicito (ej: label "bug") -- usar label como override con confianza ALTA
  - Titulo en espanol -- keywords incluyen variantes ES ("no funciona", "como usuario")
  - Body extremadamente largo (>5000 chars) -- truncar a primeros 2000 para clasificacion
  - Issue tiene codigo/logs que contienen keywords false-positive (ej: "error" en un log ejemplo) -- en Fase 1 se acepta; en Fase 2 se mejora con LLM classification

**Verificacion**:
1. Input: "Login fails with 500 error" -- debe clasificar como `bug` (ALTA)
2. Input: "CVE-2024-1234: XSS in profile" -- debe clasificar como `security` (ALTA)
3. Input: "Add CSV export" -- debe clasificar como `feature` (ALTA)
4. Input: "The system is fine" -- debe defaultear a `bug` (BAJA)
5. Input: "Fix auth bypass by refactoring middleware" -- debe clasificar como `security` (no refactor)

---

#### Tarea 1.4: Root Cause Analysis (Paso 4)
**Objetivo**: Encontrar la causa raiz en el codebase mediante busqueda sistematica.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (Paso 4)

- Logica (pseudocodigo):
```
function analyzeRootCause(solicitud, clasificacion, repo_conventions):
  // 4.1 Entender arquitectura
  readme = Read("./README.md") || Read("./CLAUDE.md") || null
  stack = detectStack()  // ver funcion abajo
  
  // 4.2 Extraer terminos de busqueda del issue
  search_terms = extractSearchTerms(solicitud.title, solicitud.body)
  // Heuristicas:
  //   - Error messages literales (entre comillas o backticks)
  //   - Nombres de funciones/metodos mencionados
  //   - Nombres de archivos/modulos mencionados
  //   - Nombres de componentes/endpoints
  //   - Status codes (404, 500, etc.)
  
  // 4.3 Keyword search
  candidates = {}  // { file_path: relevance_score }
  for term in search_terms:
    results = Grep(pattern=term, output_mode="files_with_matches")
    for file in results:
      if file not in IGNORED_PATTERNS:  // node_modules, .git, dist, build, vendor
        candidates[file] = (candidates[file] || 0) + 1

  // Ordenar por relevancia (mas matches = mas relevante)
  ranked_files = sort(candidates, by=value, descending)
  top_files = ranked_files.slice(0, 10)  // max 10 archivos candidatos

  // 4.4 Stack trace analysis (si hay)
  if solicitud.body contiene stack trace patterns:
    frames = parseStackTrace(solicitud.body)
    // Patrones de stack trace:
    //   JS/TS: "at FunctionName (file.ts:line:col)"
    //   Python: 'File "path.py", line N, in function'
    //   Rust: "thread 'main' panicked at 'msg', src/file.rs:line:col"
    //   Go: "goroutine N [running]:\npackage.Function()\n\tfile.go:line"
    for frame in frames:
      if fileExists(frame.file):
        Read(frame.file, offset=max(1, frame.line-10), limit=20)
        top_files.unshift(frame.file)  // stack trace frames tienen prioridad

  // 4.5 Leer archivos candidatos
  findings = []
  for file in top_files.slice(0, 5):  // leer max 5 archivos completos
    content = Read(file)
    // Buscar el area problematica
    for term in search_terms:
      lines = findLinesMatching(content, term)
      findings.push({ file, lines, context: extractSurroundingLines(content, lines, 5) })

  // 4.6 Buscar tests existentes
  test_files = Grep(pattern=getComponentName(solicitud), glob="*test*|*spec*|*_test*")
  for tf in test_files.slice(0, 3):
    Read(tf)  // entender comportamiento esperado

  // 4.7 Dependency tracing
  for file in top_files.slice(0, 3):
    imports = extractImports(file, stack)
    // Leer archivos importados que puedan ser relevantes
    for imp in imports:
      if imp in candidates:
        Read(imp)

  // 4.8 Formular hipotesis
  return {
    root_cause: "descripcion de que esta mal",
    files_to_modify: [
      { path: "src/file.ts", lines: "42-48", change: "que cambiar" }
    ],
    new_files: [
      { path: "tests/regression.test.ts", reason: "test de regresion" }
    ],
    risk: "LOW | MEDIUM | HIGH",
    risk_reason: "por que este nivel de riesgo",
    side_effects: ["lista de posibles efectos secundarios"],
    confidence: "ALTA | MEDIA | BAJA"
  }

function detectStack():
  // Deteccion en paralelo
  files = {
    "package.json": "node",
    "Cargo.toml": "rust",
    "pyproject.toml": "python",
    "setup.py": "python",
    "go.mod": "go",
    "pom.xml": "java",
    "build.gradle": "java",
    "Gemfile": "ruby",
    "composer.json": "php"
  }
  for file, stack in files:
    if Glob(file) tiene resultados:
      return stack
  return "unknown"

function extractSearchTerms(title, body):
  terms = []
  // 1. Error messages literales (entre `` o "")
  terms += regex_findall('`([^`]+)`', body)
  terms += regex_findall('"([^"]{5,80})"', body)
  // 2. Palabras clave del titulo (sin stopwords)
  stopwords = ["the", "a", "is", "in", "at", "to", "for", "of", "with", "on", "and",
               "or", "but", "not", "this", "that", "it", "when", "if", "el", "la",
               "un", "de", "en", "con", "por", "para", "que", "no", "se"]
  terms += [w for w in title.split() if w.lower() not in stopwords and len(w) > 2]
  // 3. Nombres de archivos mencionados (path-like patterns)
  terms += regex_findall('[\w/]+\.\w{1,5}', body)  // ej: src/auth.ts
  // 4. Nombres de funciones (camelCase o snake_case)
  terms += regex_findall('[a-z]+[A-Z]\w+', body)  // camelCase
  terms += regex_findall('[a-z]+_[a-z_]+', body)    // snake_case
  // Deduplicar y filtrar vacios
  return unique(terms.filter(t => t.length > 2))

// Patrones a ignorar en busquedas
IGNORED_PATTERNS = [
  "node_modules/", ".git/", "dist/", "build/", "vendor/",
  ".next/", "__pycache__/", "target/", ".venv/", "coverage/",
  "*.min.js", "*.min.css", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"
]
```

- Inputs: `solicitud`, `clasificacion`, convenciones del repo
- Outputs: Objeto `analysis` con causa raiz, archivos a modificar, riesgo, side effects
- Edge cases:
  - Codebase muy grande (>10K archivos) -- Grep con glob filters para limitar scope
  - Ningun keyword matchea en el codebase -- reportar al usuario, pedir guia
  - Stack trace apunta a node_modules/vendor -- trazar hasta el codigo del proyecto que llama
  - Multiples causas raiz candidatas -- presentar todas, pedir al usuario que elija
  - Archivos binarios en resultados de busqueda -- filtrar por extension
  - Issue es en un monorepo -- usar labels/paths mencionados para narrower scope
  - Guardrail: si mas de 15 archivos afectados, forzar GUIDED

**Verificacion**:
1. Issue con stack trace claro -- debe encontrar exactamente los archivos/lineas
2. Issue vago ("login no funciona") -- debe buscar archivos de auth/login y presentar candidatos
3. Issue en monorepo -- debe limitar busqueda al package correcto
4. Repo sin tests -- debe notar la ausencia, no fallar

---

#### Tarea 1.5: Branch Creation (Paso 5)
**Objetivo**: Crear feature branch con naming convention correcta.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (Paso 5)

- Logica (pseudocodigo):
```
function createBranch(clasificacion, solicitud, client_conventions):
  // 1. Detectar branch default
  default_branch = Bash("git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||'")
  if default_branch == "":
    // Fallback: buscar main, master, develop
    branches = Bash("git branch -r")
    for candidate in ["main", "master", "develop"]:
      if "origin/{candidate}" in branches:
        default_branch = candidate
        break
  if default_branch == "":
    ABORT("No pude detectar el branch default. Especifica manualmente.")

  // 2. Construir nombre del branch
  if client_conventions y client_conventions.branch_naming:
    // Usar convencion del cliente
    // Ej: client dice "feature/JIRA-123-description"
    branch_name = applyClientConvention(client_conventions.branch_naming, clasificacion, solicitud)
  else:
    // Default: {type_prefix}/{external_id}-{slug}
    slug = kebabCase(solicitud.title)
    slug = slug.slice(0, 40)  // max 40 chars para el slug
    slug = slug.replace(/[^a-z0-9-]/g, "")  // solo alfanumericos y guiones
    slug = slug.replace(/-+$/, "")  // quitar guiones trailing
    branch_name = "{clasificacion.branch_prefix}{solicitud.external_id}-{slug}"

  // 3. Verificar que el branch no existe
  existing = Bash("git branch --list {branch_name}")
  if existing != "":
    // Branch existe localmente -- agregar sufijo
    branch_name = "{branch_name}-v2"
  existing_remote = Bash("git ls-remote --heads origin {branch_name} 2>/dev/null")
  if existing_remote != "":
    branch_name = "{branch_name}-{timestamp_short}"

  // 4. Guardar branch original para rollback
  original_branch = Bash("git branch --show-current")

  // 5. Crear branch
  Bash("git checkout {default_branch}")
  Bash("git pull origin {default_branch}")
  Bash("git checkout -b {branch_name}")

  return { branch_name, default_branch, original_branch }
```

- Inputs: `clasificacion`, `solicitud`, `client_conventions`
- Outputs: Objeto `branch` con: `branch_name`, `default_branch`, `original_branch`
- Edge cases:
  - `origin/HEAD` no configurado (comun en clones shallow) -- fallback a buscar main/master/develop
  - Branch con ese nombre ya existe -- agregar sufijo `-v2` o timestamp
  - `git pull` falla (network, conflictos) -- reportar error, no continuar
  - Branch name resultante es invalido (chars especiales del titulo) -- sanitizar con regex
  - Titulo con caracteres unicode -- strip a ASCII en slug
  - Titulo muy largo (>100 chars) -- truncar slug a 40 chars

**Verificacion**:
1. Repo con `main` como default -- debe crear branch `fix/GH-42-descriptive-slug` desde main
2. Repo con `master` como default -- debe funcionar igual
3. Branch ya existe -- debe agregar suffix
4. Cliente con convencion custom -- debe respetar su formato

---

#### Tarea 1.6: Implementar Fix (Paso 6)
**Objetivo**: Aplicar los cambios del plan de fix al codigo y commitear.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (Paso 6)

- Logica (pseudocodigo):
```
function implementFix(analysis, clasificacion, solicitud, autonomy_level):
  files_changed = []
  
  // Para cada archivo a modificar del plan
  for change in analysis.files_to_modify:
    // Leer archivo completo
    content = Read(change.path)
    
    // En GUIDED: mostrar cambio propuesto y esperar aprobacion
    if autonomy_level == "GUIDED":
      mostrar("CAMBIO PROPUESTO en {change.path}:\n  Lineas: {change.lines}\n  Cambio: {change.description}")
      aprobacion = esperarUsuario()
      if aprobacion == "skip":
        continue
      if aprobacion == "modificar":
        // El usuario sugiere cambio diferente; aplicar su version
        change = obtenerCambioUsuario()

    // Aplicar el cambio
    Edit(file_path=change.path, old_string=change.old_code, new_string=change.new_code)
    files_changed.push(change.path)

  // Crear archivos nuevos (ej: tests de regresion)
  for new_file in analysis.new_files:
    if autonomy_level == "GUIDED":
      mostrar("ARCHIVO NUEVO: {new_file.path}\n  Contenido: {preview}")
      aprobacion = esperarUsuario()
      if aprobacion != "ok": continue
    Write(file_path=new_file.path, content=new_file.content)
    files_changed.push(new_file.path)

  // Ejecutar linter si esta configurado
  linter = detectLinter()
  if linter:
    Bash("{linter.fix_command}")  // ej: "npx eslint --fix {files}", "black {files}"

  // Guardrail: verificar que no tocamos archivos sensibles
  for file in files_changed:
    if isSensitiveFile(file):
      // Revertir cambio
      Bash("git checkout -- {file}")
      files_changed.remove(file)
      advertir("Revertido cambio en {file} -- archivo sensible.")

  // Commit
  // Commitear archivos especificos (NUNCA git add -A)
  for file in files_changed:
    Bash("git add {file}")

  // Verificar que no hay secrets en el diff
  diff = Bash("git diff --cached")
  if regex_match('0x[0-9a-fA-F]{64}', diff):
    Bash("git reset HEAD")
    ABORT("Detecte posible private key en el diff. Revisa manualmente.")

  // Construir commit message
  description = solicitud.title.slice(0, 72)
  commit_msg = "{clasificacion.commit_prefix} {description}\n\n{analysis.root_cause}\n\nFixes: {solicitud.external_id}"
  Bash('git commit -m "$(cat <<\'EOF\'\n{commit_msg}\nEOF\n)"')

  return { files_changed, commit_count: 1 }

function detectLinter():
  // Buscar linters en el proyecto
  pkg = Read("./package.json")
  if pkg:
    scripts = JSON.parse(pkg).scripts || {}
    if "lint:fix" in scripts: return { fix_command: "npm run lint:fix" }
    if "lint" in scripts: return { fix_command: "npm run lint -- --fix" }
  
  if Glob(".prettierrc*"): return { fix_command: "npx prettier --write {files}" }
  if Glob("pyproject.toml"):
    toml = Read("pyproject.toml")
    if "black" in toml: return { fix_command: "black {files}" }
    if "ruff" in toml: return { fix_command: "ruff format {files}" }
  if Glob("rustfmt.toml") or Glob("Cargo.toml"):
    return { fix_command: "cargo fmt" }
  
  return null

function isSensitiveFile(path):
  SENSITIVE = [".env", "credentials", "secret", "token", ".pem", ".key",
               ".p12", ".pfx", "id_rsa", "id_ed25519", "known_hosts"]
  for pattern in SENSITIVE:
    if pattern in path.lower():
      return true
  return false
```

- Inputs: `analysis`, `clasificacion`, `solicitud`, nivel de autonomia
- Outputs: Lista de archivos cambiados, count de commits
- Edge cases:
  - Edit falla porque `old_string` no matchea exactamente (codigo cambio desde el analisis) -- releer archivo, buscar la linea actualizada
  - Linter introduce mas cambios de los esperados -- incluir en el commit, documentar
  - Archivo es de solo lectura -- detectar error de Edit, reportar
  - Cambio requiere multiples commits logicos (ej: fix + test) -- commitear por separado
  - El usuario rechaza un cambio en GUIDED -- skip ese archivo, ajustar plan
  - Secret detectado en diff -- ABORT inmediato, revertir staging
  - Conflicto de merge despues de pull -- no deberia pasar (branch nuevo), pero si: ABORT

**Verificacion**:
1. Fix simple (1 archivo, 1 linea) -- debe editar, lint, commit en un paso
2. Fix multi-archivo -- debe editar cada uno, un commit logico
3. Usuario rechaza cambio en GUIDED -- debe skip sin romper el flujo
4. Archivo con .env detectado -- debe revertir y advertir

---

#### Tarea 1.7: Crear Pull Request (Paso 8)
**Objetivo**: Push branch y crear PR con template estructurado via `gh`.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (Paso 8)

- Logica (pseudocodigo):
```
function createPR(branch, clasificacion, solicitud, analysis, test_results):
  // Guardrail pre-push: verificar branch
  current = Bash("git branch --show-current")
  if current in ["main", "master", "develop"]:
    ABORT("Estamos en branch protegido. No se puede hacer push.")

  // Guardrail pre-push: verificar remote
  remote = Bash("git remote get-url origin")
  // No verificar match exacto -- el usuario ya confirmo en Paso 0

  // Guardrail pre-push: buscar secrets en diff completo
  full_diff = Bash("git diff {branch.default_branch}...HEAD --name-only")
  // Verificar que no haya archivos sensibles
  for file in full_diff.split("\n"):
    if isSensitiveFile(file):
      ABORT("El diff incluye archivo sensible: {file}")

  // Push
  push_result = Bash("git push -u origin {branch.branch_name}")
  if push_result.exitCode != 0:
    // NUNCA force push
    ABORT("Push fallo: {push_result.stderr}\nNO se hara force push. Resuelve manualmente.")

  // Construir body del PR
  closes_line = ""
  if solicitud.source_type == "github":
    number = solicitud.external_id.replace("GH-", "")
    closes_line = "\nCloses #{number}"

  // Construir checklist de testing
  test_checklist = ""
  if test_results.status == "PASS":
    test_checklist = "- [x] Tests existentes pasan"
  elif test_results.status == "FAIL_PREEXISTING":
    test_checklist = "- [ ] Tests existentes pasan (fallos pre-existentes documentados abajo)"
  elif test_results.status == "NO_TESTS":
    test_checklist = "- [ ] No hay infraestructura de tests"
  else:
    test_checklist = "- [x] Tests existentes pasan"

  if analysis.new_files.length > 0:
    test_checklist += "\n- [x] Tests nuevos agregados"

  // Crear PR
  pr_title = "{clasificacion.commit_prefix} {solicitud.title.slice(0, 65)}"
  
  // Construir lista de archivos cambiados
  changes_list = ""
  for change in analysis.files_to_modify:
    changes_list += "- `{change.path}` -- {change.description}\n"
  for new_file in analysis.new_files:
    changes_list += "- `{new_file.path}` -- {new_file.reason} (nuevo)\n"

  pr_body = """
## Issue

{solicitud.source_url != "N/A" ? "[{solicitud.external_id}]({solicitud.source_url})" : solicitud.external_id}: {solicitud.title}
{closes_line}

## Clasificacion

**Tipo**: {clasificacion.type}
**Riesgo**: {analysis.risk}
**Fuente**: {solicitud.source_type}

## Causa Raiz

{analysis.root_cause}

## Cambios

{changes_list}

## Testing

{test_checklist}
- [ ] Verificacion manual: {generarPasosVerificacion(solicitud, analysis)}

## Side Effects

{analysis.side_effects.length > 0 ? analysis.side_effects.join("\n- ") : "Ninguno esperado."}

---
*Generado por fix-issue skill -- revisar cuidadosamente antes de merge*
"""

  result = Bash('gh pr create --title "{pr_title}" --body "$(cat <<\'PREOF\'\n{pr_body}\nPREOF\n)"')
  
  if result.exitCode != 0:
    ABORT("gh pr create fallo: {result.stderr}")

  pr_url = result.stdout.trim()  // gh pr create imprime la URL

  return { pr_url, pr_title }
```

- Inputs: `branch`, `clasificacion`, `solicitud`, `analysis`, `test_results`
- Outputs: `{ pr_url, pr_title }`
- Edge cases:
  - `gh` no autenticado -- error en push o pr create; reportar con instrucciones de `gh auth login`
  - PR ya existe para este branch -- `gh pr create` falla; detectar y mostrar PR existente
  - Network timeout en push -- reportar, no reintentar automaticamente
  - Titulo de PR tiene caracteres que rompen shell (comillas, $) -- escapar con HEREDOC
  - El repo tiene PR template (.github/PULL_REQUEST_TEMPLATE.md) -- `gh pr create` lo detecta; nuestro body lo reemplaza
  - Issue es de otro repo (cross-repo reference) -- ajustar `Closes` syntax
  - Branch protections bloquean push -- reportar error con contexto

**Verificacion**:
1. Fix completo con tests pasando -- debe crear PR con checklist marcada
2. Fix sin tests -- debe notar en checklist
3. Push falla -- debe reportar error sin force push
4. Issue de GitHub -- debe incluir `Closes #N`
5. Texto libre -- debe omitir `Closes` line

---

#### Tarea 1.8: Output final en consola (Paso 9 simplificado)
**Objetivo**: En Fase 1, solo output en consola (sin triple-write a Mission Control ni ACTIVO.md).

**Implementacion**:
- Logica:
```
function reportCompletion(solicitud, clasificacion, branch, analysis, test_results, pr):
  output = """
FIX COMPLETE

  Issue: {solicitud.title}
  Tipo: {clasificacion.type} | Riesgo: {analysis.risk}
  Branch: {branch.branch_name}
  PR: {pr.pr_url}
  Archivos cambiados: {analysis.files_to_modify.length + analysis.new_files.length}
  Tests: {test_results.status}

  Tracking:
    [ ] ACTIVO.md (pendiente Fase 4)
    [ ] Mission Control (pendiente Fase 4)

  NEXT: Revisar el PR y asignar reviewer.
"""
  mostrar(output)
```

- Inputs: Todos los objetos de pasos anteriores
- Outputs: Output formateado en consola
- Edge cases: Ningun edge case critico -- es solo display

**Verificacion**: Ejecutar flow completo y verificar que el output tiene toda la informacion.

---

#### Tarea 1.9: Rollback (Paso 10)
**Objetivo**: Si algo falla despues de crear el branch, limpiar y volver al estado original.

**Implementacion**:
- Logica (pseudocodigo):
```
function rollback(original_branch, branch_name, failed_step, error):
  // 1. Descartar cambios no commiteados
  Bash("git checkout -- . 2>/dev/null")
  Bash("git clean -fd 2>/dev/null")  // solo en el worktree actual

  // 2. Volver al branch original
  checkout_result = Bash("git checkout {original_branch} 2>/dev/null")
  if checkout_result.exitCode != 0:
    // Si ni siquiera podemos cambiar de branch, algo grave paso
    mostrar("ROLLBACK PARCIAL: No pude volver a {original_branch}. Estado actual:\n{Bash('git status')}")
    return

  // 3. Eliminar branch del fix (solo si existe)
  Bash("git branch -D {branch_name} 2>/dev/null")

  // 4. Si el branch ya fue pusheado, NO eliminar el remote branch
  // (podria haber un PR asociado que queremos mantener como evidencia)

  // 5. Reportar
  output = """
FIX ABORTADO

  Issue: {solicitud.title}
  Fallo en: Paso {failed_step.number} - {failed_step.name}
  Error: {error}
  Rollback: Branch {branch_name} eliminado, volvimos a {original_branch}

  Recomendacion: {generarRecomendacion(failed_step, error)}
"""
  mostrar(output)

function generarRecomendacion(step, error):
  recomendaciones = {
    0: "Verifica que estas en el repo correcto y que el working tree esta limpio.",
    1: "Verifica que el issue existe y que gh esta autenticado (gh auth status).",
    2: "Clasifica el issue manualmente agregando el tipo al input.",
    4: "Revisa el issue manualmente -- puede necesitar mas contexto.",
    5: "Verifica tu conexion a git y permisos del repo.",
    6: "Aplica los cambios manualmente basandote en el analisis.",
    7: "Los tests fallaron. Revisa el output de tests para mas detalles.",
    8: "Verifica gh auth y permisos de push al repo."
  }
  return recomendaciones[step.number] || "Revisa el error y reintenta manualmente."
```

- Inputs: `original_branch`, `branch_name`, paso que fallo, error message
- Outputs: Cleanup del repo + output de error
- Edge cases:
  - El branch ya fue pusheado al remote -- NO eliminar remote branch (preservar como evidencia)
  - `git checkout` falla porque hay archivos sin trackear -- `git clean -fd` primero
  - Original branch fue eliminado (edge case extremo) -- checkout al default branch
  - Rollback mismo falla -- reportar estado actual con `git status` para debugging manual

**Verificacion**:
1. Fallo en Paso 4 (analisis) -- debe volver a branch original, eliminar fix branch
2. Fallo en Paso 8 (push) -- branch remoto no se toca
3. Doble rollback (fallo en rollback) -- debe dar informacion util para fix manual

---

### Fase 2: Multi-Source & Clasificacion Inteligente

> **Scope**: Agregar Linear y Jira como fuentes. Mejorar clasificacion con analisis semantico (LLM) ademas de keywords.

---

#### Tarea 2.1: Parser de Linear Tickets
**Objetivo**: Soportar URLs de Linear (`linear.app/.../issue/TEAM-123`) como input.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (agregar a Paso 1)

- Logica:
```
// Agregar al switch de patterns en parseInput()

// Pattern: Linear URL
match = regex("linear\.app/[^/]+/issue/([A-Z]+-\d+)", raw_input)
if match:
  ticket_id = match[1]
  // Linear no tiene CLI oficial; usar WebFetch
  page = WebFetch(raw_input)
  if page.exitCode != 0 or page contiene "Sign in":
    // Auth wall -- pedir texto manual
    pedir_usuario("No pude acceder al ticket Linear (requiere auth). Pega titulo y descripcion.")
    return parseInput(texto_pegado)
  
  // Parsear HTML/contenido de WebFetch
  title = extractFromPage(page, "title")  // heuristica: <title> o primer h1
  body = extractFromPage(page, "description")  // heuristica: main content area
  labels = extractFromPage(page, "labels")  // si visibles en la pagina
  priority = mapLinearPriority(extractFromPage(page, "priority"))
  // Linear priorities: Urgent(1), High(2), Medium(3), Low(4), No priority(0)

  return {
    title: title,
    body: body || "(sin descripcion)",
    external_id: "LINEAR-{ticket_id}",
    labels: labels,
    priority: priority,
    source_type: "linear",
    source_url: raw_input
  }

function mapLinearPriority(linear_priority):
  mapping = {
    "Urgent": "critica",
    "1": "critica",
    "High": "alta",
    "2": "alta",
    "Medium": "media",
    "3": "media",
    "Low": "baja",
    "4": "baja"
  }
  return mapping[linear_priority] || "desconocida"
```

- Inputs: URL de Linear
- Outputs: Solicitud normalizada con `source_type: "linear"`, `external_id: "LINEAR-TEAM-123"`
- Edge cases:
  - Linear detras de auth wall (lo mas comun) -- fallback a texto manual
  - WebFetch retorna HTML parcial/incompleto -- extraer lo que se pueda, pedir confirmacion
  - Ticket archivado o en proyecto privado -- mismo fallback
  - Multiple orgs en Linear (URL con workspace) -- extraer ticket ID correctamente

**Verificacion**:
1. URL de Linear publica -- debe parsear titulo y body
2. URL de Linear con auth -- debe pedir texto manual gracefully
3. Texto manual despues de fallback -- debe generar `LINEAR-TEAM-123` como external_id

---

#### Tarea 2.2: Parser de Jira Tickets
**Objetivo**: Soportar URLs de Jira (`*.atlassian.net/browse/PROJ-123` o instancias self-hosted).

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (agregar a Paso 1)

- Logica:
```
// Agregar al switch de patterns en parseInput()

// Pattern: Jira URL (Atlassian Cloud o self-hosted)
match = regex("(?:atlassian\.net|jira\.[^/]+)/browse/([A-Z]+-\d+)", raw_input)
if match:
  ticket_id = match[1]
  page = WebFetch(raw_input)
  if page.exitCode != 0 or page contiene "Log in" or page contiene "Unauthorized":
    pedir_usuario("No pude acceder al ticket Jira (requiere auth). Pega titulo y descripcion.")
    return parseInput(texto_pegado)
  
  title = extractFromPage(page, "title")
  body = extractFromPage(page, "description")
  priority = mapJiraPriority(extractFromPage(page, "priority"))
  // Jira priorities: Blocker, Critical, Major, Minor, Trivial

  return {
    title: title,
    body: body || "(sin descripcion)",
    external_id: "JIRA-{ticket_id}",
    labels: [],
    priority: priority,
    source_type: "jira",
    source_url: raw_input
  }

function mapJiraPriority(jira_priority):
  mapping = {
    "Blocker": "critica",
    "Critical": "critica",
    "Highest": "critica",
    "Major": "alta",
    "High": "alta",
    "Medium": "media",
    "Minor": "baja",
    "Low": "baja",
    "Trivial": "baja",
    "Lowest": "baja"
  }
  return mapping[jira_priority] || "desconocida"
```

- Inputs: URL de Jira
- Outputs: Solicitud normalizada con `source_type: "jira"`, `external_id: "JIRA-PROJ-123"`
- Edge cases:
  - Self-hosted Jira con dominio custom -- regex debe ser flexible
  - Jira Server vs Jira Cloud -- diferentes estructuras HTML
  - Ticket con rich text (tables, images) -- extraer solo texto plano
  - Jira con plugin de custom fields -- ignorar campos no estandar

**Verificacion**:
1. URL de Jira Cloud -- debe parsear
2. URL de Jira self-hosted -- regex debe matchear
3. Auth wall -- fallback a texto manual

---

#### Tarea 2.3: Clasificacion mejorada con LLM
**Objetivo**: Complementar keyword matching con analisis semantico del LLM para issues ambiguos.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (mejorar Paso 2)

- Logica:
```
function classifyEnhanced(solicitud):
  // Paso 1: Keyword classification (igual que Fase 1)
  keyword_result = classifyByKeywords(solicitud)

  // Paso 2: Si confianza es BAJA o MEDIA, usar analisis semantico
  if keyword_result.confidence in ["BAJA", "MEDIA"]:
    // El LLM (Claude) YA esta ejecutando este skill, asi que usamos
    // razonamiento interno para refinar la clasificacion
    // Esto no requiere API call -- el skill le pide a Claude que analice
    
    llm_analysis = """
    Analiza este issue y clasifica en EXACTAMENTE uno de estos tipos:
    - bug: comportamiento incorrecto, error, crash
    - feature: funcionalidad nueva
    - refactor: reestructuracion sin cambio de comportamiento
    - security: vulnerabilidad, auth, encryption
    - performance: lentitud, memoria, optimizacion
    - docs: documentacion
    - chore: dependencias, CI/CD, config

    Titulo: {solicitud.title}
    Descripcion: {solicitud.body}
    Labels: {solicitud.labels}

    Responde SOLO con el tipo y una razon de 1 linea.
    """
    // Claude procesa esto como parte del flujo del skill
    llm_result = { type, reason }

    // Combinar resultados
    if llm_result.type == keyword_result.type:
      // Ambos coinciden -- aumentar confianza
      return { ...keyword_result, confidence: "ALTA", reason: keyword_result.reason + " + LLM concuerda" }
    else:
      // Discrepancia -- presentar ambos al usuario
      return {
        ...keyword_result,
        confidence: "BAJA",
        reason: "Keywords sugieren {keyword_result.type}, analisis semantico sugiere {llm_result.type}. Requiere confirmacion.",
        alternative: llm_result
      }
  
  return keyword_result

  // Paso 3: Override por labels explicitos
  label_overrides = {
    "bug": "bug", "feature": "feature", "enhancement": "feature",
    "security": "security", "performance": "performance",
    "documentation": "docs", "docs": "docs",
    "dependencies": "chore", "maintenance": "chore"
  }
  for label in solicitud.labels:
    if label.lower() in label_overrides:
      return {
        type: label_overrides[label.lower()],
        confidence: "ALTA",
        reason: "Override por label explicito: {label}",
        ...getTypeConfig(label_overrides[label.lower()])
      }
```

- Inputs: Solicitud normalizada
- Outputs: Clasificacion con mayor precision y alternativas
- Edge cases:
  - LLM y keywords discrepan -- presentar ambos, el usuario decide
  - Label explicito overridea ambos -- label gana siempre
  - Issue en idioma mixto (EN/ES) -- keywords cubren ambos idiomas

**Verificacion**:
1. Issue ambiguo ("update auth to fix slow login") -- debe presentar alternativas
2. Issue con label "bug" explicito -- debe overridear con ALTA confianza
3. Issue claro -- keyword classification debe ser suficiente (ALTA)

---

### Fase 3: Autonomia y Testing

> **Scope**: Implementar modos CONFIRM_PLAN y FULL_AUTO. Agregar test runner automatico.

---

#### Tarea 3.1: Modo CONFIRM_PLAN
**Objetivo**: Presentar plan completo una vez, esperar un OK, ejecutar todo.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (Paso 3 + logica de control de flujo en todos los pasos)

- Logica:
```
function executeWithConfirmPlan(solicitud, clasificacion, analysis):
  // Presentar plan completo
  plan = """
  PLAN DE FIX (CONFIRM_PLAN mode)

  Issue: {solicitud.title} ({solicitud.external_id})
  Tipo: {clasificacion.type}
  
  1. Crear branch: {clasificacion.branch_prefix}{solicitud.external_id}-{slug}
  2. Archivos a modificar:
     {for change in analysis.files_to_modify:}
     - {change.path}:{change.lines} -- {change.description}
  3. Archivos nuevos:
     {for new_file in analysis.new_files:}
     - {new_file.path} -- {new_file.reason}
  4. Commit: {clasificacion.commit_prefix} {solicitud.title}
  5. Ejecutar tests: {detectTestRunner()}
  6. Crear PR contra {default_branch}

  Riesgo: {analysis.risk}
  Archivos afectados: {total_count}

  Aprobar este plan? (si/no/modificar)
  """
  
  respuesta = esperarUsuario()
  if respuesta == "no":
    ABORT("Plan rechazado por el usuario.")
  if respuesta == "modificar":
    // El usuario puede modificar items especificos
    plan = obtenerModificaciones()
    // Re-presentar plan modificado

  // Ejecutar todo sin mas preguntas
  createBranch(...)
  implementFix(... , autonomy_level="CONFIRM_PLAN")  // no pide aprobacion por archivo
  runTests(...)
  createPR(...)
```

- Inputs: Todos los objetos de pasos 0-4
- Outputs: Flujo ejecutado sin interrupciones despues de aprobacion
- Edge cases:
  - Usuario dice "modificar" -- permitir editar items del plan
  - Escaladores automaticos se activan mid-execution (ej: descubre que toca auth) -- forzar GUIDED
  - Error mid-execution despues de aprobacion -- rollback completo

**Verificacion**:
1. Plan aprobado -- ejecuta todo sin mas preguntas
2. Plan rechazado -- aborta limpiamente
3. Escalador se activa -- cambia a GUIDED mid-flow

---

#### Tarea 3.2: Modo FULL_AUTO
**Objetivo**: Ejecutar sin ningun prompt al usuario, excepto para issues de seguridad o migrations.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (Paso 3)

- Logica:
```
function executeFullAuto(solicitud, clasificacion, analysis):
  // Verificar escaladores ANTES de ejecutar
  escalators = checkEscalators(clasificacion, analysis)
  if escalators.length > 0:
    mostrar("FULL_AUTO desactivado por escaladores:\n{escalators.join('\n')}\nCambiando a GUIDED.")
    return executeGuided(...)  // fallback a GUIDED

  // Ejecutar todo sin preguntas
  branch = createBranch(...)
  result = implementFix(... , autonomy_level="FULL_AUTO")
  tests = runTests(...)
  
  // Si tests fallan en NUESTRO codigo, intentar fix automatico (max 1 retry)
  if tests.status == "FAIL_OUR_CODE":
    retry = autoFixTests(tests.failures, analysis)
    if retry.success:
      tests = runTests(...)
    else:
      // No pudo arreglar -- escalar a GUIDED
      mostrar("Tests fallan despues de fix. Escalando a GUIDED.")
      return handleTestFailure(...)

  pr = createPR(...)
  return { branch, result, tests, pr }

function checkEscalators(clasificacion, analysis):
  escalators = []
  if clasificacion.type == "security":
    escalators.push("Issue de seguridad -- requiere revision humana")
  if analysis.files_to_modify.any(f => isMigrationFile(f.path)):
    escalators.push("Fix toca migraciones de DB")
  if analysis.files_to_modify.any(f => isCICDFile(f.path)):
    escalators.push("Fix toca pipeline de CI/CD")
  if analysis.files_to_modify.length > 15:
    escalators.push("Fix afecta {N} archivos (>15)")
  if analysis.confidence == "BAJA":
    escalators.push("Causa raiz ambigua -- multiples candidatos")
  return escalators

function isMigrationFile(path):
  return path contiene "migration" or "alembic/versions" or "prisma/migrations" or "db/migrate"

function isCICDFile(path):
  return path contiene ".github/workflows" or "Jenkinsfile" or ".gitlab-ci"
    or ".circleci" or "azure-pipelines" or "bitbucket-pipelines"
    or "Dockerfile" or "docker-compose"
```

- Inputs: Igual que CONFIRM_PLAN
- Outputs: Ejecucion completa sin intervencion humana (si no hay escaladores)
- Edge cases:
  - Escalador descubierto mid-execution (ej: analisis revela que toca auth) -- downgrade a GUIDED
  - Tests fallan en FULL_AUTO -- un retry automatico, despues escalar
  - Network failure durante push -- rollback sin preguntar

**Verificacion**:
1. Issue simple sin escaladores -- debe ejecutar completo sin preguntas
2. Issue de security -- debe forzar GUIDED
3. Issue que toca >15 archivos -- debe forzar GUIDED
4. Tests fallan -- debe intentar 1 fix, luego escalar

---

#### Tarea 3.3: Test Runner Automatico (Paso 7)
**Objetivo**: Detectar y ejecutar tests del proyecto, interpretar resultados.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (Paso 7)

- Logica:
```
function runTests(repo_conventions):
  // 1. Detectar test runner
  runner = null

  // Prioridad 1: CLAUDE.md del repo/cliente
  if repo_conventions and repo_conventions.test_command:
    runner = { command: repo_conventions.test_command, source: "CLAUDE.md" }

  // Prioridad 2: package.json
  if !runner:
    pkg = Read("./package.json")
    if pkg:
      scripts = JSON.parse(pkg).scripts || {}
      if "test" in scripts:
        runner = { command: "npm test", source: "package.json" }
      elif "test:unit" in scripts:
        runner = { command: "npm run test:unit", source: "package.json" }

  // Prioridad 3: Makefile
  if !runner:
    makefile = Read("./Makefile")
    if makefile and "test:" in makefile:
      runner = { command: "make test", source: "Makefile" }

  // Prioridad 4: Python
  if !runner:
    if Glob("pyproject.toml") or Glob("pytest.ini") or Glob("setup.cfg"):
      runner = { command: "python -m pytest -v", source: "auto-detect" }

  // Prioridad 5: Rust
  if !runner:
    if Glob("Cargo.toml"):
      runner = { command: "cargo test", source: "auto-detect" }

  // Prioridad 6: Go
  if !runner:
    if Glob("go.mod"):
      runner = { command: "go test ./...", source: "auto-detect" }

  // Sin test runner
  if !runner:
    return { status: "NO_TESTS", command: null, output: "No se detecto infraestructura de tests." }

  // 2. Ejecutar tests
  result = Bash("{runner.command} 2>&1", timeout=300000)  // 5 min timeout
  output = result.stdout

  // 3. Interpretar resultados
  if result.exitCode == 0:
    return { status: "PASS", command: runner.command, output: output.slice(-2000) }
  
  // Tests fallaron -- determinar si es nuestro codigo o pre-existente
  // Estrategia: revisar si los tests que fallan tocan archivos que nosotros modificamos
  failed_tests = parseFailedTests(output, runner.source)
  our_files = analysis.files_to_modify.map(f => f.path)
  
  our_failures = failed_tests.filter(t => t.file in our_files or t.relates_to(our_files))
  preexisting_failures = failed_tests.filter(t => t not in our_failures)

  if our_failures.length > 0:
    return {
      status: "FAIL_OUR_CODE",
      command: runner.command,
      output: output.slice(-2000),
      our_failures: our_failures,
      preexisting_failures: preexisting_failures
    }
  else:
    return {
      status: "FAIL_PREEXISTING",
      command: runner.command,
      output: output.slice(-2000),
      preexisting_failures: preexisting_failures
    }

function parseFailedTests(output, source):
  // Parsear output de test runner para extraer tests que fallaron
  // Cada runner tiene formato diferente:
  
  // Jest/Vitest: "FAIL src/test.ts > Test Name"
  // Pytest: "FAILED tests/test_x.py::test_name"
  // Cargo test: "test module::test_name ... FAILED"
  // Go test: "--- FAIL: TestName"
  
  // Retornar lista de { test_name, file, error_message }
  // ...pattern matching por runner type...
```

- Inputs: Convenciones del repo, archivos modificados
- Outputs: Objeto `test_results` con status, command, output, desglose de failures
- Edge cases:
  - Tests toman mas de 5 minutos -- timeout, reportar como SKIP
  - Tests requieren setup (DB, Docker, env vars) -- fallan por setup; reportar como "setup required"
  - Tests pasan localmente pero runner necesita `--ci` flag -- buscar en scripts
  - No hay package.json ni Cargo.toml (proyecto sin manager) -- reportar NO_TESTS
  - Tests flaky (pasan intermitentemente) -- reportar resultado actual sin rerun

**Verificacion**:
1. Proyecto Node.js con Jest -- detecta `npm test`, ejecuta, parsea output
2. Proyecto Python con pytest -- detecta y ejecuta
3. Proyecto sin tests -- retorna NO_TESTS sin error
4. Tests fallan por codigo nuestro -- status FAIL_OUR_CODE con detalles
5. Tests fallan pre-existentes -- status FAIL_PREEXISTING, no blocker

---

### Fase 4: Tracking Triple-Write

> **Scope**: Implementar escritura simultanea a ACTIVO.md, tasks.json, activity-log.json, inbox.json.

---

#### Tarea 4.1: Write a ACTIVO.md del cliente
**Objetivo**: Actualizar el archivo de tareas activas del cliente con el issue resuelto.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (Paso 9.A)

- Logica:
```
function updateActivoMd(client, solicitud, clasificacion, pr):
  activo_path = "Z:/consultoria-x/clientes/{client}/tasks/ACTIVO.md"
  
  // Intentar leer
  content = Read(activo_path)
  
  if content == null:
    // Archivo no existe -- crear desde template
    template = Read("Z:/consultoria-x/clientes/_template/tasks/ACTIVO.md")
    content = template.replace("[CLIENTE]", client)
    // Escribir template
    Write(activo_path, content)

  // Buscar si el issue ya tiene una fila
  if solicitud.external_id in content:
    // Actualizar fila existente -- agregar PR URL a columna Notas
    // Encontrar la linea con el external_id
    Edit(
      file_path=activo_path,
      old_string="| {solicitud.external_id} |",  // buscar inicio de fila
      new_string="| {solicitud.external_id} | {solicitud.title} | {solicitud.priority} | {today} | PR: {pr.pr_url} - {clasificacion.type}: completado |"
    )
  else:
    // Agregar nueva fila a "En Progreso"
    // Buscar la tabla de "En Progreso" y agregar despues del header
    new_row = "| {solicitud.external_id} | {solicitud.title} | {solicitud.priority} | {today} | PR: {pr.pr_url} - {clasificacion.type}: completado |"
    
    Edit(
      file_path=activo_path,
      old_string="## En Progreso\n| ID | Tarea | Prioridad | Deadline | Notas |\n|----|-------|-----------|----------|-------|\n",
      new_string="## En Progreso\n| ID | Tarea | Prioridad | Deadline | Notas |\n|----|-------|-----------|----------|-------|\n{new_row}\n"
    )

  return { success: true, path: activo_path }
```

- Inputs: `client`, `solicitud`, `clasificacion`, `pr`
- Outputs: ACTIVO.md actualizado
- Edge cases:
  - ACTIVO.md no existe -- crear desde template
  - ACTIVO.md tiene formato diferente al template (usuario lo modifico) -- buscar tabla por header "En Progreso"
  - Issue ya existe en la tabla -- actualizar en vez de duplicar
  - Path del cliente no existe (`clientes/{client}/` no existe) -- crear directorio + archivos
  - Caracteres especiales en titulo que rompen tabla markdown (pipes `|`) -- escapar

**Verificacion**:
1. ACTIVO.md existe con tabla vacia -- debe agregar fila
2. ACTIVO.md no existe -- debe crear desde template y agregar fila
3. Issue ya en tabla -- debe actualizar, no duplicar

---

#### Tarea 4.2: Write a tasks.json
**Objetivo**: Crear o actualizar task en Mission Control.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (Paso 9.B)

- Logica:
```
function updateTasksJson(solicitud, clasificacion, analysis, pr, client):
  tasks_path = "Z:/consultoria-x/mission-control/mission-control/data/tasks.json"
  data = JSON.parse(Read(tasks_path))

  // Buscar task existente
  existing = data.tasks.find(t =>
    t.tags.includes(solicitud.external_id) or
    t.title.toLowerCase().includes(solicitud.title.toLowerCase().slice(0, 30)) or
    t.notes.includes(solicitud.external_id)
  )

  now = new Date().toISOString()
  
  if existing:
    // Actualizar task existente
    existing.kanban = "in-progress"
    existing.notes = (existing.notes || "") + "\n\nfix-issue: PR {pr.pr_url}"
    existing.updatedAt = now
    if !existing.tags.includes("fix-issue"):
      existing.tags.push("fix-issue")
  else:
    // Crear nueva task
    task_id = "task_{Date.now()}"
    
    // Mapear importance/urgency
    importance = "not-important"
    urgency = "not-urgent"
    if clasificacion.type in ["security", "bug"]:
      importance = "important"
    if clasificacion.type == "security" or solicitud.priority in ["critica", "alta"]:
      urgency = "urgent"

    new_task = {
      "id": task_id,
      "title": "{clasificacion.commit_prefix} {solicitud.title}",
      "description": "Issue {solicitud.external_id} - {solicitud.body.slice(0, 200)}\n\nPR: {pr.pr_url}\nCausa raiz: {analysis.root_cause.slice(0, 200)}",
      "importance": importance,
      "urgency": urgency,
      "kanban": "in-progress",
      "projectId": null,
      "milestoneId": null,
      "assignedTo": "developer",
      "collaborators": [],
      "dailyActions": [],
      "subtasks": [],
      "blockedBy": [],
      "estimatedMinutes": null,
      "actualMinutes": null,
      "acceptanceCriteria": [
        "PR merged: {pr.pr_url}",
        "Issue {solicitud.external_id} cerrado"
      ],
      "tags": [clasificacion.type, client, "fix-issue", solicitud.external_id],
      "notes": "Generado por fix-issue skill. Fuente: {solicitud.source_type}.",
      "createdAt": now,
      "updatedAt": now,
      "completedAt": null
    }
    data.tasks.push(new_task)
    task_id = new_task.id

  Write(tasks_path, JSON.stringify(data, null, 2))
  return { task_id }
```

- Inputs: `solicitud`, `clasificacion`, `analysis`, `pr`, `client`
- Outputs: tasks.json actualizado, task_id
- Edge cases:
  - tasks.json no es JSON valido -- ABORT tracking, reportar error (no romper MC data)
  - tasks.json es muy grande (>1MB) -- Read con limit, buscar eficientemente
  - Task existente con mismo titulo pero de otro cliente -- verificar client tag
  - Concurrent write (otro agente escribiendo) -- leer justo antes de escribir, minimizar ventana
  - JSON indentation inconsistente -- SIEMPRE usar 2-space indent al escribir

**Verificacion**:
1. Task no existe -- debe crear con todos los campos del schema
2. Task existe -- debe actualizar kanban y notes
3. Issue de seguridad -- importance=important, urgency=urgent
4. Issue de docs -- importance=not-important, urgency=not-urgent

---

#### Tarea 4.3: Write a activity-log.json
**Objetivo**: Registrar evento de fix completado en el activity log.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (Paso 9.B)

- Logica:
```
function updateActivityLog(solicitud, clasificacion, pr, task_id):
  log_path = "Z:/consultoria-x/mission-control/mission-control/data/activity-log.json"
  data = JSON.parse(Read(log_path))

  now = new Date().toISOString()
  event_id = "evt_{Date.now()}"

  new_event = {
    "id": event_id,
    "type": "task_created",  // o "task_updated" si task existia
    "actor": "developer",
    "taskId": task_id,
    "summary": "fix-issue: {clasificacion.commit_prefix} {solicitud.title.slice(0, 60)}",
    "details": "Issue {solicitud.external_id} resuelto via fix-issue skill.\nPR: {pr.pr_url}\nTipo: {clasificacion.type}\nFuente: {solicitud.source_type}",
    "timestamp": now
  }

  data.events.push(new_event)
  Write(log_path, JSON.stringify(data, null, 2))
  return { event_id }
```

- Inputs: `solicitud`, `clasificacion`, `pr`, `task_id`
- Outputs: activity-log.json actualizado
- Edge cases:
  - Log muy grande (miles de eventos) -- solo append, no leer entero para buscar
  - JSON parse falla -- reportar error, no perder data existente

**Verificacion**: Verificar que el evento aparece al final del array `events` con todos los campos.

---

#### Tarea 4.4: Write a inbox.json
**Objetivo**: Enviar reporte de completado al inbox de Mission Control.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (Paso 9.B)

- Logica:
```
function updateInbox(solicitud, clasificacion, analysis, pr, task_id, client):
  inbox_path = "Z:/consultoria-x/mission-control/mission-control/data/inbox.json"
  data = JSON.parse(Read(inbox_path))

  now = new Date().toISOString()
  msg_id = "msg_{Date.now()}"

  files_count = analysis.files_to_modify.length + analysis.new_files.length

  new_message = {
    "id": msg_id,
    "from": "developer",
    "to": "me",
    "type": "report",
    "taskId": task_id,
    "subject": "Fix completado: {solicitud.title.slice(0, 60)}",
    "body": "Issue {solicitud.external_id} resuelto.\n\nPR: {pr.pr_url}\nTipo: {clasificacion.type}\nRiesgo: {analysis.risk}\nArchivos modificados: {files_count}\nCliente: {client}\n\nCausa raiz: {analysis.root_cause.slice(0, 300)}",
    "status": "unread",
    "createdAt": now,
    "readAt": null
  }

  data.messages.push(new_message)
  Write(inbox_path, JSON.stringify(data, null, 2))
  return { msg_id }
```

- Inputs: Todos los datos del fix
- Outputs: inbox.json actualizado
- Edge cases:
  - Mismos que activity-log: JSON parse, append-only
  - Body muy largo -- truncar root_cause a 300 chars

**Verificacion**: Verificar que el mensaje aparece como `unread` con `type: "report"`.

---

#### Tarea 4.5: Orquestar Triple-Write
**Objetivo**: Ejecutar las 3 escrituras de forma atomica (o reportar cuales fallaron).

**Implementacion**:
- Logica:
```
function tripleWrite(client, solicitud, clasificacion, analysis, pr):
  results = {
    activo: { success: false },
    task: { success: false },
    activity: { success: false },
    inbox: { success: false }
  }

  // Escribir ACTIVO.md
  try:
    results.activo = updateActivoMd(client, solicitud, clasificacion, pr)
  catch error:
    results.activo = { success: false, error: error.message }

  // Escribir tasks.json
  try:
    results.task = updateTasksJson(solicitud, clasificacion, analysis, pr, client)
  catch error:
    results.task = { success: false, error: error.message }

  // Escribir activity-log.json (depende de task_id)
  if results.task.success:
    try:
      results.activity = updateActivityLog(solicitud, clasificacion, pr, results.task.task_id)
    catch error:
      results.activity = { success: false, error: error.message }

  // Escribir inbox.json (depende de task_id)
  if results.task.success:
    try:
      results.inbox = updateInbox(solicitud, clasificacion, analysis, pr, results.task.task_id, client)
    catch error:
      results.inbox = { success: false, error: error.message }

  // Reportar estado
  checkmarks = {
    activo: results.activo.success ? "[x]" : "[ ] FALLO: {results.activo.error}",
    task: results.task.success ? "[x]" : "[ ] FALLO: {results.task.error}",
    activity: results.activity.success ? "[x]" : "[ ] FALLO: {results.activity.error}",
    inbox: results.inbox.success ? "[x]" : "[ ] FALLO: {results.inbox.error}"
  }

  return results, checkmarks
```

- Inputs: Todos los datos del fix
- Outputs: Status de cada escritura
- Edge cases:
  - Una escritura falla pero las otras existen -- reportar parcial, no abortar
  - Task write falla -- activity y inbox no pueden continuar (dependen de task_id)
  - Todas fallan -- reportar pero el PR ya esta creado, el fix no se pierde

**Verificacion**:
1. Todo funciona -- 4 checkmarks verdes
2. ACTIVO.md falla (permisos) -- 3 verdes, 1 con error
3. tasks.json falla (JSON corrupto) -- solo ACTIVO verde, 3 con error

---

### Fase 5: Hardening & Guardrails

> **Scope**: Guardrails de seguridad, rollback robusto, edge cases, limites.

---

#### Tarea 5.1: Verificacion continua de guardrails
**Objetivo**: Implementar checks que se ejecutan ANTES de cada paso critico.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (agregar checks distribuidos)
- Referencia: `.claude/skills/fix-issue/references/guardrails.md`

- Logica:
```
function preCommitGuardrails():
  // Ejecutar ANTES de cada git commit
  
  // G1: Branch check
  branch = Bash("git branch --show-current")
  if branch in ["main", "master", "develop"]:
    ABORT("Guardrail G1: Estamos en branch protegido '{branch}'.")

  // G6: Sensitive files check
  staged = Bash("git diff --cached --name-only")
  for file in staged.split("\n"):
    if isSensitiveFile(file):
      ABORT("Guardrail G6: Archivo sensible en staging: {file}")

  // G-secrets: Secret pattern scan
  diff = Bash("git diff --cached")
  if regex_match('0x[0-9a-fA-F]{64}', diff):
    ABORT("Guardrail G-secrets: Posible private key detectada en diff.")
  if regex_match('(AKIA|ASIA)[A-Z0-9]{16}', diff):
    ABORT("Guardrail G-secrets: Posible AWS access key detectada en diff.")
  if regex_match('-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----', diff):
    ABORT("Guardrail G-secrets: Posible private key PEM detectada en diff.")

function prePushGuardrails():
  // Ejecutar ANTES de git push
  
  // G2: No force push (verificar que el comando NO tiene --force)
  // (esto es un guardrail de logica, no de runtime)

  // G5: Branch check (redundante pero critico)
  branch = Bash("git branch --show-current")
  if branch in ["main", "master", "develop"]:
    ABORT("Guardrail G5: No se puede push a branch protegido '{branch}'.")

  // G12: Remote check
  remote = Bash("git remote get-url origin")
  // El usuario ya confirmo en Paso 0; aqui re-verificamos que no cambio

  // G-files: No files outside repo
  toplevel = Bash("git rev-parse --show-toplevel")
  staged = Bash("git diff origin/{default_branch}...HEAD --name-only")
  for file in staged.split("\n"):
    full_path = resolve(toplevel, file)
    if not full_path.startsWith(toplevel):
      ABORT("Guardrail G3: Archivo fuera del repo: {file}")

function continuousGuardrails(analysis):
  // Ejecutar durante analisis y planeacion

  // G6: Limite de archivos
  if analysis.files_to_modify.length > 15:
    advertir("Guardrail G6: {N} archivos afectados (>15). Forzando GUIDED.")
    return { force_guided: true }

  // G8: CI/CD files
  cicd_files = analysis.files_to_modify.filter(f => isCICDFile(f.path))
  if cicd_files.length > 0:
    advertir("Guardrail G8: Fix modifica CI/CD ({cicd_files}). Forzando GUIDED.")
    return { force_guided: true }

  // G9: Migration files
  migration_files = analysis.files_to_modify.filter(f => isMigrationFile(f.path))
  if migration_files.length > 0:
    advertir("Guardrail G9: Fix modifica migrations ({migration_files}). Forzando GUIDED.")
    return { force_guided: true }

  return { force_guided: false }
```

- Inputs: Estado actual del repo, analysis
- Outputs: OK o ABORT con guardrail especifico
- Edge cases:
  - False positive en secret scan (ej: hash en test fixture) -- el ABORT protege; el usuario puede override
  - Regex de secrets matchea en un comentario -- mejor safe than sorry, ABORT
  - Branch protegido con nombre custom (ej: "production") -- solo checkeamos main/master/develop por ahora

**Verificacion**:
1. Commit en main -- debe ABORT
2. Push con secret en diff -- debe ABORT
3. Archivo .env en staging -- debe ABORT
4. 16 archivos afectados -- debe forzar GUIDED
5. Fix toca Dockerfile -- debe forzar GUIDED

---

#### Tarea 5.2: Rollback robusto
**Objetivo**: Mejorar rollback para manejar todos los estados intermedios posibles.

**Implementacion**:
- Archivo(s) a modificar: `.claude/skills/fix-issue/SKILL.md` (Paso 10)

- Logica:
```
function robustRollback(context):
  // Determinar que ya se hizo para decidir que limpiar
  state = {
    branch_created: context.branch_name != null,
    files_modified: context.files_changed.length > 0,
    committed: context.commit_count > 0,
    pushed: context.pushed == true,
    pr_created: context.pr_url != null,
    tracking_written: context.tracking_done == true
  }

  actions_taken = []

  // 1. Descartar cambios no commiteados
  if state.files_modified:
    Bash("git checkout -- . 2>/dev/null")
    Bash("git clean -fd 2>/dev/null")
    actions_taken.push("Cambios no commiteados descartados")

  // 2. Volver al branch original
  if state.branch_created:
    checkout = Bash("git checkout {context.original_branch} 2>&1")
    if checkout.exitCode != 0:
      // Intentar con default branch
      Bash("git checkout {context.default_branch} 2>&1")
      actions_taken.push("Volvimos a {context.default_branch} (fallback)")
    else:
      actions_taken.push("Volvimos a {context.original_branch}")

    // 3. Eliminar branch local
    Bash("git branch -D {context.branch_name} 2>/dev/null")
    actions_taken.push("Branch local {context.branch_name} eliminado")

  // 4. Si se pusheo y no se creo PR, eliminar branch remoto
  // SOLO si no hay PR (si hay PR, mantener como evidencia)
  if state.pushed and not state.pr_created:
    Bash("git push origin --delete {context.branch_name} 2>/dev/null")
    actions_taken.push("Branch remoto {context.branch_name} eliminado")

  // 5. Si se escribio tracking, revertir
  if state.tracking_written:
    // NO revertir tracking -- es evidencia del intento
    // Solo anotar que el fix fue abortado
    actions_taken.push("Tracking NO revertido (preservado como evidencia)")

  // 6. Reportar
  output = """
  FIX ABORTADO

    Issue: {context.solicitud.title}
    Fallo en: Paso {context.failed_step} - {context.failed_step_name}
    Error: {context.error_message}

    Rollback realizado:
    {for action in actions_taken:}
      - {action}

    Estado final:
      Branch actual: {Bash("git branch --show-current")}
      Working tree: {Bash("git status --porcelain") == "" ? "limpio" : "DIRTY - revisar manualmente"}

    Recomendacion: {generarRecomendacion(context.failed_step, context.error_message)}
  """
  mostrar(output)
```

- Inputs: Contexto completo del fix (que pasos se completaron)
- Outputs: Cleanup + reporte detallado
- Edge cases:
  - Branch ya fue pusheado + PR creado -- NO eliminar branch remoto (PR es evidencia)
  - Branch pusheado sin PR -- SI eliminar branch remoto
  - Rollback falla (ej: permisos) -- reportar estado actual para fix manual
  - Tracking parcial (tasks.json escrito pero inbox no) -- no intentar revertir; anotar

**Verificacion**:
1. Fallo pre-push -- limpia branch local
2. Fallo post-push sin PR -- limpia branch local Y remoto
3. Fallo post-PR -- limpia branch local, mantiene remoto + PR
4. Rollback falla -- da info suficiente para fix manual

---

#### Tarea 5.3: Timeout y limites de ejecucion
**Objetivo**: Prevenir que el skill se quede corriendo indefinidamente.

**Implementacion**:
- Logica:
```
// Limites por paso
STEP_LIMITS = {
  0: { timeout: 30000, name: "Safety Gate" },         // 30s
  1: { timeout: 30000, name: "Parse" },                // 30s
  2: { timeout: 10000, name: "Classify" },             // 10s
  3: { timeout: 5000, name: "Autonomy" },              // 5s
  4: { timeout: 600000, name: "Root Cause Analysis" }, // 10min (el mas largo)
  5: { timeout: 30000, name: "Branch" },               // 30s
  6: { timeout: 300000, name: "Implement" },           // 5min
  7: { timeout: 300000, name: "Tests" },               // 5min
  8: { timeout: 60000, name: "PR" },                   // 1min
  9: { timeout: 60000, name: "Tracking" },             // 1min
  10: { timeout: 30000, name: "Rollback" }             // 30s
}

// Limite total del skill: 30 minutos
TOTAL_LIMIT = 1800000

// Para Paso 4 (analisis):
// Si despues de ~10 min no hay causa raiz clara:
//   - Presentar hallazgos parciales
//   - Pedir guia del usuario
//   - NO intentar fixes a ciegas
```

- Edge cases:
  - Test suite tarda mas de 5 minutos -- timeout, reportar como SKIP
  - Codebase enorme (100K+ archivos) -- Grep con glob filters para limitar
  - Network lento -- push/fetch timeout; reportar sin retry infinito

**Verificacion**: Simular step que tarda mas del timeout -- debe interrumpir con reporte util.

---

#### Tarea 5.4: Logging estructurado
**Objetivo**: Mantener un log de todo lo que el skill hizo para debugging post-mortem.

**Implementacion**:
- Logica:
```
// El skill NO escribe logs a un archivo separado.
// En cambio, cada paso produce output estructurado que sirve como log.
// Si algo falla, el reporte de rollback (Paso 10) incluye toda la info.

// Formato de cada paso:
STEP_OUTPUT_FORMAT = """
[PASO {N}] {nombre} - {RESULTADO}
  Input: {resumen del input}
  Output: {resumen del output}
  Duracion: {ms}
  {Detalles adicionales si fallo}
"""

// El output final (Paso 9) consolida todo:
FINAL_OUTPUT_FORMAT = """
FIX COMPLETE / FIX ABORTADO

  Timeline:
  [00:00] Paso 0: Safety Gate -- OK (15ms)
  [00:01] Paso 1: Parse -- OK (230ms)
  [00:01] Paso 2: Classify -- OK (50ms)
  [00:01] Paso 3: Autonomy -- GUIDED (5ms)
  [00:02] Paso 4: Analysis -- OK (45000ms)
  [00:47] Paso 5: Branch -- OK (800ms)
  [00:48] Paso 6: Implement -- OK (12000ms)
  [01:00] Paso 7: Tests -- PASS (8000ms)
  [01:08] Paso 8: PR -- OK (3000ms)
  [01:11] Paso 9: Tracking -- OK (1500ms)
  Total: 71s
"""
```

- Edge cases: Ningun edge case critico -- es observabilidad pura

**Verificacion**: Ejecutar flow completo y verificar que el timeline final es correcto.

---

## Interfaces y Contratos

### Input del Skill

El skill acepta los siguientes formatos de input:

```
// GitHub Issue URL
"https://github.com/owner/repo/issues/42"

// GitHub Issue Shorthand
"#42"
"GH-42"

// Linear Ticket URL (Fase 2+)
"https://linear.app/workspace/issue/TEAM-123/issue-title"

// Jira Ticket URL (Fase 2+)
"https://company.atlassian.net/browse/PROJ-789"
"https://jira.company.com/browse/PROJ-789"

// Texto libre
"fix the login timeout bug when user has 2FA enabled"
"el dashboard muestra NaN despues de cambiar timezone"

// Combinacion (URL + contexto adicional)
"fix #42 -- el usuario reporto que pasa en Firefox pero no Chrome"
```

### Solicitud Normalizada (estructura interna)

```json
{
  "title": "string (max 100 chars)",
  "body": "string (descripcion completa, puede incluir markdown)",
  "external_id": "GH-42 | LINEAR-TEAM-123 | JIRA-PROJ-789 | FREE-20260406-slug",
  "labels": ["string"],
  "priority": "critica | alta | media | baja | desconocida",
  "source_type": "github | linear | jira | free-text",
  "source_url": "https://... | N/A"
}
```

### Clasificacion (estructura interna)

```json
{
  "type": "bug | feature | refactor | security | performance | docs | chore",
  "branch_prefix": "fix/ | feat/ | refactor/ | security/ | perf/ | docs/ | chore/",
  "commit_prefix": "fix: | feat: | refactor: | fix: | perf: | docs: | chore:",
  "confidence": "ALTA | MEDIA | BAJA",
  "force_guided": true/false,
  "reason": "string"
}
```

### Analysis (estructura interna)

```json
{
  "root_cause": "string (explicacion de 1-3 oraciones)",
  "files_to_modify": [
    {
      "path": "src/auth/login.ts",
      "lines": "42-48",
      "description": "Agregar null check antes de acceder a user.profile",
      "old_code": "const name = user.profile.name;",
      "new_code": "const name = user?.profile?.name ?? 'Unknown';"
    }
  ],
  "new_files": [
    {
      "path": "tests/auth/login.test.ts",
      "reason": "test de regresion para null profile",
      "content": "... test code ..."
    }
  ],
  "risk": "LOW | MEDIUM | HIGH",
  "risk_reason": "string",
  "side_effects": ["string"],
  "confidence": "ALTA | MEDIA | BAJA"
}
```

### Test Results (estructura interna)

```json
{
  "status": "PASS | FAIL_OUR_CODE | FAIL_PREEXISTING | NO_TESTS | SKIP | TIMEOUT",
  "command": "npm test | cargo test | ... | null",
  "output": "string (ultimas 2000 chars del output)",
  "our_failures": [{ "test_name": "string", "file": "string", "error": "string" }],
  "preexisting_failures": [{ "test_name": "string", "file": "string", "error": "string" }]
}
```

### Output del Skill (consola)

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
    [x] Activity log {event_id}
    [x] Inbox report {msg_id}

  Timeline:
    [00:00] Safety Gate -- OK
    [00:01] Parse -- OK
    ...

  NEXT: Revisar el PR y asignar reviewer.
```

### Integracion con Mission Control

#### Task entry (tasks.json)
```json
{
  "id": "task_1712419200000",
  "title": "fix: Login fails with 500 on special chars",
  "description": "Issue GH-42 - Login fails with 500 error when password contains special characters\n\nPR: https://github.com/owner/repo/pull/43\nCausa raiz: Missing input sanitization in auth middleware",
  "importance": "important",
  "urgency": "urgent",
  "kanban": "in-progress",
  "projectId": null,
  "milestoneId": null,
  "assignedTo": "developer",
  "collaborators": [],
  "dailyActions": [],
  "subtasks": [],
  "blockedBy": [],
  "estimatedMinutes": null,
  "actualMinutes": null,
  "acceptanceCriteria": [
    "PR merged: https://github.com/owner/repo/pull/43",
    "Issue GH-42 cerrado"
  ],
  "tags": ["bug", "acme-corp", "fix-issue", "GH-42"],
  "notes": "Generado por fix-issue skill. Fuente: github.",
  "createdAt": "2026-04-06T15:00:00.000Z",
  "updatedAt": "2026-04-06T15:00:00.000Z",
  "completedAt": null
}
```

#### Activity log entry (activity-log.json)
```json
{
  "id": "evt_1712419200000",
  "type": "task_created",
  "actor": "developer",
  "taskId": "task_1712419200000",
  "summary": "fix-issue: fix: Login fails with 500 on special chars",
  "details": "Issue GH-42 resuelto via fix-issue skill.\nPR: https://github.com/owner/repo/pull/43\nTipo: bug\nFuente: github",
  "timestamp": "2026-04-06T15:00:00.000Z"
}
```

#### Inbox message (inbox.json)
```json
{
  "id": "msg_1712419200000",
  "from": "developer",
  "to": "me",
  "type": "report",
  "taskId": "task_1712419200000",
  "subject": "Fix completado: Login fails with 500 on special chars",
  "body": "Issue GH-42 resuelto.\n\nPR: https://github.com/owner/repo/pull/43\nTipo: bug\nRiesgo: LOW\nArchivos modificados: 2\nCliente: acme-corp\n\nCausa raiz: Missing input sanitization in auth middleware.",
  "status": "unread",
  "createdAt": "2026-04-06T15:00:00.000Z",
  "readAt": null
}
```

---

## Flujos de Error

### Paso 0: Safety Gate
| Error | Deteccion | Accion |
|-------|-----------|--------|
| En consultoria-x | `pwd` contiene "consultoria-x" | ABORT con mensaje claro |
| No es git repo | `git rev-parse` exit code != 0 | ABORT |
| Working tree dirty | `git status --porcelain` no vacio | ABORT, sugerir stash |
| `gh` no instalado | `which gh` falla | Advertir, continuar (puede no necesitar gh) |
| Cliente desconocido | No hay CURRENT_CLIENT ni input | Preguntar, listar opciones |

### Paso 1: Parse
| Error | Deteccion | Accion |
|-------|-----------|--------|
| `gh issue view` falla (auth) | exit code 1 + "authentication" | Pedir texto manual |
| `gh issue view` falla (not found) | exit code 1 + "not found" | Verificar numero/repo |
| URL invalida (no matchea patterns) | Ningun regex matchea | Tratar como texto libre |
| WebFetch timeout | exit code != 0 despues de timeout | Pedir texto manual |
| Issue cerrado | state == "CLOSED" | Advertir, preguntar si continuar |

### Paso 2: Classify
| Error | Deteccion | Accion |
|-------|-----------|--------|
| Ningun keyword matchea | best_score == 0 | Default a "bug" con BAJA confianza |
| Multiples tipos empatados | 2+ tipos con mismo score | Usar prioridad: security > bug > ... |
| Titulo vacio | title == "" | Usar primeras palabras del body |

### Paso 4: Analysis
| Error | Deteccion | Accion |
|-------|-----------|--------|
| Ningun archivo matchea | candidates vacio | Pedir guia al usuario |
| Timeout (>10 min) | Duracion excede limite | Presentar hallazgos parciales |
| Codebase ilegible (binarios, minificado) | Archivos no parseables | Filtrar, buscar en source maps |
| Stack trace apunta a dependency | Path contiene node_modules/vendor | Trazar hasta codigo del proyecto |

### Paso 5: Branch
| Error | Deteccion | Accion |
|-------|-----------|--------|
| `git pull` falla (network) | exit code != 0 | ABORT, sugerir retry manual |
| `git pull` falla (conflictos) | exit code != 0 + "conflict" | ABORT, resolver manualmente |
| Branch name invalido | git checkout -b falla | Sanitizar nombre, reintentar |
| Default branch no detectado | Todas las heuristicas fallan | ABORT, pedir nombre manual |

### Paso 6: Implement
| Error | Deteccion | Accion |
|-------|-----------|--------|
| Edit falla (old_string no matchea) | Error de Edit tool | Releer archivo, buscar linea actualizada |
| Archivo read-only | Error de permisos | ABORT para ese archivo, reportar |
| Secret detectado en diff | Regex match en `git diff --cached` | Revertir staging, ABORT |
| Linter falla | exit code != 0 | Reportar, no bloquear (lint no es critico) |

### Paso 7: Tests
| Error | Deteccion | Accion |
|-------|-----------|--------|
| Test runner no encontrado | Todas las heuristicas fallan | Reportar NO_TESTS, continuar |
| Tests timeout | Duracion > 5 min | Reportar TIMEOUT, continuar |
| Tests fallan (nuestro codigo) | exit code != 0, fallos en nuestros archivos | Intentar fix, si no: escalar |
| Tests fallan (pre-existente) | exit code != 0, fallos en otros archivos | Documentar en PR, continuar |

### Paso 8: PR
| Error | Deteccion | Accion |
|-------|-----------|--------|
| Push falla (auth) | exit code != 0 + "auth" | Sugerir `gh auth login` |
| Push falla (branch protection) | exit code != 0 + "protected" | Reportar, sugerir admin override |
| `gh pr create` falla | exit code != 0 | Reportar error completo |
| PR ya existe | exit code != 0 + "already exists" | Mostrar PR existente |

### Paso 9: Tracking
| Error | Deteccion | Accion |
|-------|-----------|--------|
| JSON parse falla | try/catch | Reportar, NO sobrescribir archivo corrupto |
| ACTIVO.md tabla no encontrada | Tabla "En Progreso" no matchea | Agregar al final del archivo |
| Permisos de escritura | Error en Write | Reportar, el fix no se pierde (PR ya existe) |

---

## Testing del Skill

### Tests manuales (end-to-end)

#### Test E2E-1: Bug fix simple (happy path)
1. Crear repo de test con un bug conocido (ej: division by zero)
2. Crear GitHub issue describiendo el bug
3. Ejecutar `/fix-issue #1` en modo GUIDED
4. Verificar: branch creado, fix correcto, tests pasan, PR creado, tracking actualizado

#### Test E2E-2: Feature request
1. Crear issue "Add CSV export to /api/users"
2. Ejecutar `/fix-issue #2`
3. Verificar: clasificacion = feature, branch feat/, commit feat:

#### Test E2E-3: Security issue
1. Crear issue "XSS vulnerability in comment field"
2. Ejecutar `/fix-issue #3` con autonomia FULL_AUTO
3. Verificar: DEBE forzar GUIDED (escalador de security)

#### Test E2E-4: Texto libre
1. Ejecutar `/fix-issue fix the timeout in the bulk import endpoint`
2. Verificar: external_id = FREE-YYYYMMDD-..., flujo completo funciona

#### Test E2E-5: Rollback
1. Crear issue que apunta a archivo que no existe
2. Ejecutar `/fix-issue #N`
3. Verificar: falla en analisis, rollback limpio, reporte util

#### Test E2E-6: Issue en repo sin tests
1. Crear repo sin test runner
2. Ejecutar fix
3. Verificar: Tests = NO_TESTS, PR documenta la ausencia, no se bloquea

#### Test E2E-7: Multi-source (Fase 2+)
1. Probar con URL de Linear (con auth wall) -- debe pedir texto manual
2. Probar con URL de Jira -- similar

#### Test E2E-8: Triple-write (Fase 4+)
1. Ejecutar fix completo
2. Verificar ACTIVO.md tiene fila nueva
3. Verificar tasks.json tiene task nueva con todos los campos
4. Verificar activity-log.json tiene evento nuevo
5. Verificar inbox.json tiene mensaje unread

### Repo de test sugerido

Crear `Z:\test-fix-issue\` con:
```
package.json          (con jest configurado)
src/calculator.ts     (con bug: divide(a, 0) no valida)
tests/calculator.test.ts (test que pasa, falta test del bug)
README.md
.gitignore
```
Crear 3 issues en GitHub:
- #1: "Calculator crashes on divide by zero" (bug)
- #2: "Add modulo operation to calculator" (feature)
- #3: "XSS in calculator display" (security)

---

## Decisiones de Diseno

1. **GUIDED como default**: La prioridad es no romper repos de clientes. Velocidad es secundaria.
2. **Keyword classification primero, LLM segundo**: Keywords son deterministas y rapidos. LLM solo para ambiguos.
3. **Rollback preserva PRs**: Un PR creado es evidencia util, no se elimina en rollback.
4. **Triple-write es best-effort**: Si tracking falla, el fix (PR) ya existe. No se pierde trabajo.
5. **Archivos sensibles = hard abort**: Nunca tocar .env, keys, credentials. Sin excepciones.
6. **Monorepo awareness diferido**: En Fase 1, el scope es repos simples. Monorepo support es futuro.
7. **No API calls a Linear/Jira**: Dependemos de WebFetch + fallback a texto manual. APIs requieren tokens.
