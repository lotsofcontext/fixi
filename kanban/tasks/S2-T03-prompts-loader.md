---
id: S2-T03
title: Implementar prompts.py (loader de SKILL.md)
sprint: S2
day: 1
status: pending
priority: P0
type: implementation
tags: [agent, python, prompts, day-1]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 30m
actual: ""
owner: claude
blocks: [S2-T06]
blocked_by: [S2-T01]
related_docs: [SPRINT-2, SKILL]
commits: []
files_touched: []
---

# S2-T03: Loader de system prompt desde SKILL.md

> **Sprint**: [[SPRINT-2]] · **Día**: 1 · **Status**: pending

## Contexto

El sistema prompt del agent es el contenido completo de `skill/SKILL.md`. Esta tarea implementa el loader que lee el archivo y opcionalmente inyecta refs de classification y guardrails como anexos.

## Acceptance Criteria

- [ ] `src/fixi_agent/prompts.py` creado
- [ ] Función `load_system_prompt()` que:
  - Lee `skill/SKILL.md` (path configurable, default relativo al package)
  - Opcionalmente concatena `classification.md` y `guardrails.md` como anexos
  - Devuelve string listo para pasar a `ClaudeAgentOptions(system_prompt=...)`
- [ ] Test unit: el prompt cargado contiene "Paso 0: Verificacion de Contexto"
- [ ] Manejo de error si el archivo no existe (raise con mensaje claro)

## Plan

```python
from pathlib import Path
from importlib.resources import files

def load_system_prompt(skill_dir: Path | None = None) -> str:
    skill_dir = skill_dir or _find_skill_dir()
    skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    classification = (skill_dir / "references" / "classification.md").read_text(encoding="utf-8")
    guardrails = (skill_dir / "references" / "guardrails.md").read_text(encoding="utf-8")
    return f"{skill}\n\n## Anexo: Clasificacion\n\n{classification}\n\n## Anexo: Guardrails\n\n{guardrails}"
```

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
