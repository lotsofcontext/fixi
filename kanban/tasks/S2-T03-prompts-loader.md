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
estimated: 1h
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

El sistema prompt del agent es el contenido de `skill/SKILL.md` **transformado para modo autónomo**. La función `load_system_prompt()` NO es una concatenación pura — aplica transformaciones que adaptan el skill interactivo a un agent headless.

**Decisión de diseño** (del audit de 4 agentes paralelos, 2026-04-07): **Option 1 — dejar SKILL.md pristine, transformar en el loader**. Así SKILL.md sigue siendo válido como Claude Code skill (Sprint 1 deliverable), y el agent obtiene una variant adaptada. Ambas capas coexisten.

## Acceptance Criteria

- [ ] `src/fixi_agent/prompts.py` creado
- [ ] Función `load_system_prompt(skill_dir, tracking_mode)` que:
  - Lee `skill/SKILL.md` (path configurable, default relativo al repo root)
  - Aplica **6 transformaciones** para modo autónomo:
    1. **Preamble**: prepend "Autonomous Agent Mode" con behavioral overrides (no approval gates, pre-validated context, report to caller, failures vs warnings)
    2. **Paso 0 strip/replace**: pwd check → no-op assertion ("contexto pre-validado por orchestrator")
    3. **Paso 3 replace**: GUIDED/CONFIRM_PLAN/FULL_AUTO interactivo → FULL_AUTO estático con escalators
    4. **"Esperar confirmacion" strip**: ~9 instancias → "Proceder inmediatamente. Reportar estado."
    5. **Paso 9 condicional**: si `tracking_mode == "none"` strip entero; si `"client"` skip Mission Control; si `"hq"` full triple-write
    6. **Default GUIDED → FULL_AUTO**: invertir el default para autonomous
  - Concatena `classification.md` y `guardrails.md` como anexos (sin transformar — son reference)
  - Devuelve string listo para `ClaudeAgentOptions(system_prompt=...)`
- [ ] Parámetro `tracking_mode: str = "client"` con opciones: `"hq"`, `"client"`, `"none"`
- [ ] Test unit: prompt contiene "Autonomous Agent Mode" (preamble)
- [ ] Test unit: prompt NO contiene "Esperar confirmacion del usuario"
- [ ] Test unit: prompt NO contiene `consultoria-x` cuando `tracking_mode != "hq"`
- [ ] Test unit: prompt SÍ contiene "Paso 7: Ejecutar Validaciones Basicas" (Gap A)
- [ ] Test unit: prompt SÍ contiene "## Posibles impactos" (Gap B)
- [ ] Manejo de error si skill/SKILL.md no existe (raise con mensaje claro)
- [ ] Token estimate (~1,900) validado (contar chars / 4)

## Plan

```python
import re
from pathlib import Path

PREAMBLE = """# Autonomous Agent Mode — Fix Issue

You are running as an autonomous agent, not an interactive Claude Code skill.
There is no human user in the loop. The orchestrator invoked you with a work item.

## Behavioral Overrides

1. **No approval gates.** Do not wait for user confirmation. Proceed based on escalators (Paso 3).
2. **Escalation = explicit pause.** If guardrails trigger GUIDED (security, >15 files, ambiguous root cause, CI/CD, DB migrations): report findings in JSON and return control to caller.
3. **Context pre-validated.** Working directory, git state, and repo are verified by the orchestrator. Do not re-verify pwd or check for consultoria-x.
4. **Report via structured output.** Use JSON/markdown status blocks, not interactive "Output al usuario" directives.
5. **Failures vs warnings.** Critical errors (no git, auth failure, missing input): halt with error. Non-critical (tracking unavailable, optional linter missing): log warning and proceed.
6. **Never fabricate information.** If data is missing, halt immediately and report the gap.

---

"""

def load_system_prompt(
    skill_dir: Path | None = None,
    tracking_mode: str = "client",  # "hq" | "client" | "none"
) -> str:
    skill_dir = skill_dir or _find_skill_dir()
    skill_raw = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    classification = (skill_dir / "references" / "classification.md").read_text(encoding="utf-8")
    guardrails = (skill_dir / "references" / "guardrails.md").read_text(encoding="utf-8")

    transformed = _apply_autonomous_transforms(skill_raw, tracking_mode)

    return (
        f"{PREAMBLE}{transformed}\n\n"
        f"## Anexo: Clasificacion\n\n{classification}\n\n"
        f"## Anexo: Guardrails\n\n{guardrails}"
    )

def _apply_autonomous_transforms(skill: str, tracking_mode: str) -> str:
    # 1. Strip YAML frontmatter (agent doesn't need skill metadata)
    skill = re.sub(r"^---\n.*?\n---\n", "", skill, flags=re.DOTALL)

    # 2. Replace Paso 0 pwd check with no-op
    skill = re.sub(
        r"## Paso 0:.*?(?=\n## Paso 1)",
        "## Paso 0: Contexto Pre-validado\n\n"
        "El orchestrador ya verificó: repo git válido, working tree limpio, "
        "remote correcto, cliente identificado. Continuar directamente.\n\n---\n\n",
        skill, flags=re.DOTALL,
    )

    # 3. Replace Paso 3 interactive narrative with static FULL_AUTO
    skill = re.sub(
        r"El usuario puede cambiar nivel en cualquier momento.*?\n",
        "Nivel pre-establecido: FULL_AUTO. Solo escalar a GUIDED si los escaladores aplican.\n",
        skill,
    )

    # 4. Strip "Esperar confirmacion"
    skill = re.sub(
        r"Esperar confirmacion.*?\.\n",
        "Proceder inmediatamente. Reportar estado al caller.\n",
        skill,
    )

    # 5. Handle Paso 9 tracking based on mode
    if tracking_mode == "none":
        skill = re.sub(
            r"## Paso 9:.*?(?=## Paso 10:)",
            "## Paso 9: Tracking (SKIP — tracking_mode=none)\n\n"
            "Tracking deshabilitado por configuración. Continuar a Paso 10.\n\n---\n\n",
            skill, flags=re.DOTALL,
        )
    elif tracking_mode == "client":
        skill = re.sub(
            r"### B\. Mission Control.*?(?=### C\. Output final)",
            "### B. Mission Control\n\n"
            "[Skipped — tracking_mode=client. Solo ACTIVO.md del cliente.]\n\n",
            skill, flags=re.DOTALL,
        )

    # 6. Invert default from GUIDED to FULL_AUTO
    skill = skill.replace(
        "**Autonomia default: GUIDED**",
        "**Autonomia default: FULL_AUTO** (modo autónomo)"
    )

    return skill
```

**Nota**: las transformaciones son regex-based y deben validarse con tests unitarios. Si SKILL.md cambia de estructura (renombran Pasos, mueven secciones), los regex van a fallar — los tests lo detectarán.

**Token budget**: ~1,900 tokens antes de transformaciones, ~1,700 después (strip de Paso 0, reducción de Paso 9). Well within budget.

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
