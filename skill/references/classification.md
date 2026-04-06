# Taxonomia de Clasificacion de Issues

Referencia completa para el Paso 2 del skill fix-issue.

## Tipos y Keywords

### bug (fix/)
**Commit prefix**: `fix:`
**Descripcion**: Comportamiento incorrecto, errores, crashes, regresiones.

**Keywords primarios**: error, crash, broken, fails, unexpected, regression, bug, defect, incorrect, wrong
**Keywords secundarios**: "doesn't work", "no funciona", "not working", stack trace, exception, 500, 404, null pointer, undefined, NaN, infinite loop, race condition, deadlock, data loss, corrupted
**Contexto**: El sistema DEBERIA hacer X pero hace Y (o no hace nada).

**Ejemplos**:
- "Login fails with 500 error when password contains special characters"
- "Dashboard shows NaN for revenue after timezone change"
- "API returns 404 for existing users intermittently"

---

### feature (feat/)
**Commit prefix**: `feat:`
**Descripcion**: Funcionalidad nueva, capacidades adicionales.

**Keywords primarios**: add, implement, create, new, support, enable, introduce, build
**Keywords secundarios**: "user story", "como usuario", "as a user", feature request, enhancement, capability, integrate, extend, allow
**Contexto**: El sistema NO hace X, y queremos que lo haga.

**Ejemplos**:
- "Add CSV export to the reports page"
- "Implement OAuth2 login with Google"
- "As a user, I want to filter transactions by date range"

---

### refactor (refactor/)
**Commit prefix**: `refactor:`
**Descripcion**: Reestructuracion de codigo sin cambio de comportamiento.

**Keywords primarios**: refactor, clean up, tech debt, reorganize, simplify, extract, rename, restructure
**Keywords secundarios**: DRY, SOLID, decouple, modularize, split, merge, consolidate, migrate (code structure, not DB), "code smell"
**Contexto**: El sistema funciona correctamente pero el codigo es dificil de mantener/entender.

**Ejemplos**:
- "Extract payment logic into a dedicated service"
- "Rename UserManager to UserService for consistency"
- "Split monolithic handler into separate route files"

---

### security (security/)
**Commit prefix**: `fix:`
**Descripcion**: Vulnerabilidades, exposiciones, problemas de autenticacion/autorizacion.

**Keywords primarios**: vulnerability, CVE, auth bypass, injection, XSS, CSRF, security
**Keywords secundarios**: exposure, leak, OWASP, SQL injection, RCE, SSRF, path traversal, privilege escalation, token, session, encryption, certificate, TLS/SSL, CORS, CSP, sanitize
**Contexto**: El sistema tiene una debilidad que puede ser explotada.

**SIEMPRE modo GUIDED** sin importar el nivel de autonomia elegido.

**Ejemplos**:
- "CVE-2024-1234: XSS in user profile bio field"
- "API key exposed in client-side bundle"
- "Admin endpoints accessible without authentication"

---

### performance (perf/)
**Commit prefix**: `perf:`
**Descripcion**: Optimizaciones de velocidad, memoria, recursos.

**Keywords primarios**: slow, timeout, memory leak, N+1, optimize, latency, performance
**Keywords secundarios**: bottleneck, cache, index, query optimization, lazy load, pagination, batch, bulk, connection pool, rate limit, throughput, CPU usage, OOM
**Contexto**: El sistema funciona correctamente pero es demasiado lento o consume demasiados recursos.

**Ejemplos**:
- "Dashboard takes 30s to load with 10K+ records"
- "Memory usage grows unbounded after 24h uptime"
- "N+1 query problem in order listing endpoint"

---

### docs (docs/)
**Commit prefix**: `docs:`
**Descripcion**: Documentacion, README, comentarios, API docs.

**Keywords primarios**: documentation, README, comment, API docs, changelog, docs
**Keywords secundarios**: typo, example, tutorial, guide, reference, JSDoc, docstring, swagger, OpenAPI, migration guide
**Contexto**: El codigo esta bien pero la documentacion esta incompleta, incorrecta, o falta.

**Ejemplos**:
- "README doesn't mention the required REDIS_URL env variable"
- "API documentation missing for the /v2/users endpoint"
- "Typo in error message: 'authetication' -> 'authentication'"

---

### chore (chore/)
**Commit prefix**: `chore:`
**Descripcion**: Mantenimiento, dependencias, CI/CD, configuracion, tooling.

**Keywords primarios**: dependency, CI/CD, config, build, tooling, upgrade, bump, lint
**Keywords secundarios**: devDependency, package, version, Dockerfile, GitHub Actions, pipeline, formatter, pre-commit hook, gitignore, tsconfig, webpack, vite config
**Contexto**: No afecta funcionalidad ni documentacion, es mantenimiento de infraestructura de desarrollo.

**Ejemplos**:
- "Bump React from 18.2 to 18.3"
- "Add ESLint rule for no-unused-vars"
- "Fix Docker build failing on ARM64"

---

## Arbol de Decision para Casos Ambiguos

```
1. Menciona seguridad, auth, encryption, CVE?
   -> security (SIEMPRE priorizar)

2. Es un error/crash/comportamiento incorrecto?
   -> bug

3. Es lentitud, timeout, alto uso de recursos?
   -> performance

4. Es funcionalidad nueva que no existia?
   -> feature

5. Cambia estructura del codigo sin cambiar comportamiento?
   -> refactor

6. Solo afecta documentacion?
   -> docs

7. Es mantenimiento de deps/CI/config?
   -> chore
```

## Prioridad de Clasificacion (si multiples aplican)

`security > bug > performance > feature > refactor > docs > chore`

Ejemplo: "Fix auth bypass by refactoring session middleware" = **security** (no refactor).
Ejemplo: "Add caching to fix slow dashboard" = **performance** (no feature).
Ejemplo: "Update docs after fixing login bug" = **bug** (el fix es lo principal; docs update es secundario).
