# Fixi Kanban — Sistema de Tracking

> Sistema de tracking de tareas para el desarrollo de Fixi.
> Inspirado en el patrón de [[medos]] vault, mejorado con auto-actualización e historial.
>
> Ver: [[BOARD|Tablero actual]] · [[SPRINT-1|Sprint 1]] · [[BACKLOG|Backlog completo]] · [[PLAN|Roadmap]]

---

## Filosofía

1. **Cada tarea es un archivo** en `tasks/`. La frontmatter YAML es la fuente de verdad.
2. **El tablero (`BOARD.md`) se auto-genera** desde los task files. NO se edita a mano.
3. **El historial es append-only** — cada cambio de status queda registrado en `history/YYYY-MM-DD.md`.
4. **Wiki links por ID estable** — `[[S1-T05]]` no `[[S1-T05-seed-bug]]`. Si renombras el archivo, los links no se rompen.
5. **Notas y attempts dentro del task file** — qué se intentó, qué funcionó, qué falló. Es donde vive el conocimiento.

---

## Estructura

```
kanban/
├── README.md              ← Este archivo
├── BOARD.md               ← Tablero auto-generado (NO editar)
├── update_board.py        ← Script que regenera el board
├── .state.json            ← Cache del estado previo (para detectar cambios)
├── tasks/                 ← Una tarea por archivo
│   ├── S1-T01-verify-skill-refs.md
│   ├── S1-T02-audit-wiki-links.md
│   └── ...
├── history/               ← Logs diarios append-only
│   └── 2026-04-06.md
└── _archive/              ← Tasks viejas (post-sprint cleanup)
```

---

## Cómo crear una tarea

Crear `kanban/tasks/{id}-{slug}.md` con esta frontmatter:

```yaml
---
id: S1-T05                                    # ID estable, único
title: "Sembrar BUG #1 — DivideByZero"        # Título corto
sprint: S1                                     # S0, S1, S2...
day: 1                                         # Día dentro del sprint
status: pending                                # pending|in-progress|blocked|done|cancelled
priority: P1                                   # P0|P1|P2|P3
type: implementation                           # implementation|research|docs|test|review
tags: [demo, dotnet, bug-seeded]
created: 2026-04-06T21:35:00
updated: 2026-04-06T21:35:00
estimated: 30m                                 # 5m, 1h, 2h, 1d, etc.
actual: ""                                     # se llena al completar
owner: claude
blocks: [S1-T08]                               # IDs que esta tarea bloquea
blocked_by: [S1-T04]                           # IDs que la bloquean
related_docs: [SPRINT-1, BACKLOG]              # Wiki links sin corchetes
commits: []                                    # SHAs cuando se commiteen
files_touched: []                              # Paths modificados
---

# S1-T05: Sembrar BUG #1 — DivideByZero en CalculadoraConsumo

> **Sprint**: [[SPRINT-1]] · **Día**: 1 · **Status**: pending
> **Owner**: claude · **Estimated**: 30m

## Contexto

[Descripción del por qué]

## Acceptance Criteria

- [ ] item 1
- [ ] item 2

## Plan

[Cómo se va a abordar]

## Notes & Attempts

[Append durante la ejecución: qué se probó, qué falló, decisiones]

## Outcome

[Después de completar: resultado, links a commits/PRs]

## History

- `2026-04-06 21:35` · created (status: pending)
```

---

## Workflow diario

### 1. Empezar una tarea

```bash
# Editar el task file:
#   status: pending → in-progress
#   updated: <nuevo timestamp>
#
# Agregar a "Notes & Attempts":
#   ## Iniciado 2026-04-06 22:00
#   Plan: ...

# Regenerar el board:
python kanban/update_board.py

# Commit el cambio:
git add kanban/tasks/S1-T05-*.md kanban/BOARD.md kanban/.state.json kanban/history/
git commit -m "kanban: start S1-T05"
```

### 2. Trabajar — agregar notas a "Notes & Attempts"

Cuando intentes algo, registralo en el task file. Especialmente:
- Decisiones técnicas y por qué
- Cosas que NO funcionaron
- Sorpresas o blockers descubiertos
- Links a recursos consultados

### 3. Completar una tarea

```bash
# Editar el task file:
#   status: in-progress → done
#   updated: <timestamp>
#   actual: <duración real, ej: 25m>
#   commits: [sha1, sha2]
#   files_touched: [path1, path2]
#
# Llenar la sección "Outcome":
#   ## Outcome
#   - Resultado: ...
#   - PR: ...
#   - Tests: ...

python kanban/update_board.py
git add kanban/
git commit -m "kanban: complete S1-T05"
```

### 4. Si una tarea se bloquea

```yaml
status: blocked
blocked_reason: "Esperando que GlobalMVM provea ADO sandbox"
```

---

## Status values

| Status | Cuándo usar |
|--------|------------|
| `pending` | No iniciada |
| `in-progress` | Activamente trabajando |
| `blocked` | Esperando algo externo (input, decisión, recurso) |
| `done` | Completada con criteria de aceptación cumplidas |
| `cancelled` | Decidida no hacerse — agregar `cancelled_reason` |

---

## Convenciones de IDs

- `S{sprint}-T{nn}` — formato canónico, ej: `S1-T05`
- Sprint numbering: `S0` = pre-Sprint 1, `S1` = Sprint 1 (actual), etc.
- Task numbering: empezar en `T01` por sprint, sin huecos
- Slug en filename: `S1-T05-short-description.md`

---

## Auto-actualización del board

`update_board.py` no tiene dependencias externas (Python stdlib only).

```bash
# Desde la raíz del repo:
python kanban/update_board.py

# Output:
#   Loaded N task(s)
#   Detected M status change(s):
#     S1-T05: pending → in-progress
#   History appended to kanban/history/2026-04-06.md
#   BOARD.md updated (N tasks)
```

El script:
1. Lee todos los `tasks/*.md`
2. Compara con `.state.json` para detectar cambios
3. Si hay cambios, los escribe al log diario en `history/`
4. Regenera `BOARD.md` desde cero
5. Actualiza `.state.json`

**Idempotente**: correrlo dos veces seguidas sin cambios no produce duplicados.

---

## Por qué este sistema

| Pain point en sistemas anteriores | Cómo se resuelve aquí |
|-----------------------------------|----------------------|
| Tableros que se desactualizan | Auto-generado desde task files |
| No hay historial de qué pasó | History log diario append-only |
| Status sin contexto | "Notes & Attempts" en cada task |
| Wiki links rotos al renombrar | IDs estables como wiki link target |
| No se sabe estimado vs real | Campos `estimated` y `actual` |
| Difícil saber qué se probó | Sección "Notes & Attempts" + history |

---

## Integración con Obsidian Vault

- Todos los task files tienen wiki links a docs (`[[SPRINT-1]]`, `[[BACKLOG]]`)
- Los task files mismos son link targets (`[[S1-T05]]`)
- BOARD.md y History usan wiki links — navegables desde Obsidian
- Frontmatter YAML compatible con Obsidian Dataview (queries futuras)
