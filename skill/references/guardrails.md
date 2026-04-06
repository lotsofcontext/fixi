# Guardrails de Seguridad - fix-issue

Reglas de seguridad que se verifican a lo largo de toda la ejecucion del skill.
Cualquier violacion = ABORT inmediato + rollback.

## Reglas Criticas (verificacion continua)

### 1. NUNCA operar en main/master/develop directamente
- Verificar: `git branch --show-current` != main/master/develop antes de CADA commit
- Si estamos en branch protegido: ABORT + "Debes estar en un feature branch"

### 2. NUNCA force push
- Prohibido: `git push --force`, `git push -f`, `git push --force-with-lease`
- Si push normal falla: reportar el error, NO intentar force push

### 3. NUNCA modificar archivos fuera del repo actual
- Verificar: todo path de archivo esta dentro de `$(git rev-parse --show-toplevel)`
- Excepcion UNICA: tracking files en consultoria-x (Paso 9)

### 4. ABORT si working tree esta dirty
- Verificar antes de empezar: `git status --porcelain` debe estar vacio
- Si hay cambios: "Hay cambios sin commitear. Por favor stash o commit antes de continuar."

### 5. Verificar contexto de cliente
- Confirmar que `git remote get-url origin` corresponde al cliente declarado
- Si no matchea: preguntar al usuario antes de continuar

### 6. Limite de archivos: >15 = escalar a GUIDED
- Contar archivos afectados durante analisis (Paso 4)
- Si >15: forzar modo GUIDED aunque el usuario haya pedido FULL_AUTO
- Notificar: "Este fix afecta {N} archivos. Escalando a modo GUIDED por seguridad."

### 7. NUNCA tocar archivos sensibles
Archivos prohibidos (NUNCA modificar):
- `.env`, `.env.*` (excepto `.env.example`)
- `*credentials*`, `*secret*`, `*token*`
- `*.pem`, `*.key`, `*.p12`, `*.pfx`
- `id_rsa`, `id_ed25519`, `known_hosts`
- `~/.ssh/*`, `~/.aws/*`

Si el issue REQUIERE cambios en estos archivos:
ABORT + "Este fix requiere modificar archivos sensibles. Hazlo manualmente."

### 8. NUNCA modificar CI/CD sin aprobacion GUIDED
Archivos que requieren GUIDED:
- `.github/workflows/*.yml`
- `Jenkinsfile`
- `.gitlab-ci.yml`
- `.circleci/config.yml`
- `azure-pipelines.yml`
- `bitbucket-pipelines.yml`
- `Dockerfile`, `docker-compose.yml`

Forzar GUIDED + advertir: "Este fix modifica pipeline de CI/CD. Revisemos juntos."

### 9. NUNCA modificar DB migrations sin aprobacion GUIDED
Archivos que requieren GUIDED:
- `migrations/`, `db/migrate/`
- `alembic/versions/`
- `prisma/migrations/`
- `*.sql` en directorios de migrations
- `schema.prisma` (cambios de modelo)

Forzar GUIDED + advertir: "Este fix modifica schema/migraciones de DB. Revisemos juntos."

### 10. NUNCA inventar informacion — DETENER si faltan datos
Si en CUALQUIER paso faltan datos para continuar:
- NO asumir valores, comportamientos, causa raiz, o impactos sin evidencia
- NO fabricar contexto que no este en el issue o en el codigo
- DETENER el flujo inmediatamente
- Reportar:
  ```
  FLUJO DETENIDO: Falta informacion
    Paso: {paso actual}
    Que falta: {descripcion especifica}
    Que necesito: {que debe proveer el usuario para continuar}
  ```
- Continuar SOLO cuando el usuario provea los datos faltantes
- Aplica a: descripcion del issue, causa raiz, impacto del cambio, convenciones del repo, prioridad

### 11. Rollback automatico si algo falla
Si CUALQUIER paso falla despues de crear el branch:
```bash
git checkout {original_branch}
git branch -D {fix_branch} 2>/dev/null
```
Reportar que paso fallo y por que.

### 12. Limite de tiempo para root cause: 10 minutos
Si Paso 4 (analisis) no encuentra causa raiz clara en ~10 minutos de busqueda:
- Presentar lo encontrado hasta ahora
- Pedir guia del usuario: "No encuentro causa raiz clara. Esto es lo que tengo..."
- NO intentar fixes a ciegas

### 13. Verificar remote correcto
Antes de push:
```bash
git remote get-url origin
```
Confirmar que el remote es del cliente correcto, no un fork personal o repo equivocado.

## Checklist Pre-Ejecucion

Antes de empezar el Paso 1, verificar TODO:
- [ ] pwd != consultoria-x
- [ ] git repo valido
- [ ] working tree limpio
- [ ] cliente identificado
- [ ] remote verificado
- [ ] CLAUDE.md del repo leido (si existe)

## Checklist Pre-Push

Antes del Paso 8 (crear PR):
- [ ] Branch != main/master/develop
- [ ] Todos los commits siguen conventional commits
- [ ] No hay archivos sensibles en el diff (`git diff --name-only`)
- [ ] No hay secrets en el diff (`git diff | grep -P '0x[0-9a-fA-F]{64}'`)
- [ ] Tests ejecutados (o documentado por que no)
- [ ] Remote correcto verificado
