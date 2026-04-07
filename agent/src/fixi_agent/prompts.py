"""System prompt loader for Fixi Agent.

Reads skill/SKILL.md and applies 6 transformations to adapt the
interactive Claude Code skill into an autonomous agent prompt.
SKILL.md stays pristine (valid for interactive use); the loader
produces the agent-mode variant at runtime.

Usage:
    from fixi_agent.prompts import load_system_prompt
    prompt = load_system_prompt(skill_dir=Path("skill/"))
"""

from __future__ import annotations

import re
from pathlib import Path

PREAMBLE = """\
# Autonomous Agent Mode — Fix Issue

You are running as an autonomous agent, not an interactive Claude Code skill.
There is no human user in the loop. The orchestrator (CI/CD pipeline or CLI)
invoked you with a work item URL and a target repo.

## Behavioral Overrides

1. **No approval gates.** Do not wait for user confirmation after each step.
   Proceed based on escalators (Paso 3). If no escalator triggers, execute
   the full workflow without stopping.

2. **Escalation = explicit pause.** If a guardrail triggers GUIDED mode
   (security issues, >15 files, ambiguous root cause, CI/CD changes, DB
   migrations): report findings in structured output and return control to
   the caller. Do NOT continue autonomously in that case.

3. **Context is pre-validated.** The orchestrator has verified: working
   directory is a clean git repo, remote is correct, client context is
   identified. Do not re-verify pwd or check for consultoria-x.

4. **Report via structured output.** Use JSON or markdown status blocks.
   Do not use interactive "Output al usuario" formatting or wait for input.

5. **Failures vs warnings.** Critical errors (no git, auth failure, missing
   required input): halt with error code. Non-critical issues (tracking
   system unavailable, optional linter missing): log as WARNING and proceed.

6. **Never fabricate information.** If required data is missing (issue title,
   description, repo context), halt immediately and report what's missing.
   Do not guess or assume.

---

"""


def load_system_prompt(
    skill_dir: Path | None = None,
    tracking_mode: str = "client",
) -> str:
    """Load SKILL.md as an autonomous agent system prompt.

    Applies 6 transformations to adapt the interactive Claude Code skill
    for headless, CI/CD-triggered execution.

    Args:
        skill_dir: Path to the skill/ directory containing SKILL.md and
            references/. If None, auto-detected relative to this file
            (assumes repo layout: agent/src/fixi_agent/prompts.py →
            ../../skill/).
        tracking_mode: Controls Paso 9 (tracking) behavior:
            - "hq": full triple-write (ACTIVO.md + Mission Control)
            - "client": only ACTIVO.md, skip Mission Control
            - "none": skip Paso 9 entirely

    Returns:
        Complete system prompt string ready for ClaudeAgentOptions.

    Raises:
        FileNotFoundError: If SKILL.md or reference files don't exist.
        ValueError: If tracking_mode is not one of "hq", "client", "none".
    """
    if tracking_mode not in ("hq", "client", "none"):
        msg = f"tracking_mode must be 'hq', 'client', or 'none', got '{tracking_mode}'"
        raise ValueError(msg)

    skill_dir = skill_dir or _find_skill_dir()
    skill_path = skill_dir / "SKILL.md"
    classification_path = skill_dir / "references" / "classification.md"
    guardrails_path = skill_dir / "references" / "guardrails.md"

    for path in (skill_path, classification_path, guardrails_path):
        if not path.exists():
            msg = f"Required file not found: {path}. Is skill_dir correct? Got: {skill_dir}"
            raise FileNotFoundError(msg)

    skill_raw = skill_path.read_text(encoding="utf-8")
    classification = classification_path.read_text(encoding="utf-8")
    guardrails = guardrails_path.read_text(encoding="utf-8")

    transformed = _apply_autonomous_transforms(skill_raw, tracking_mode)

    return (
        f"{PREAMBLE}{transformed}\n\n"
        f"## Anexo: Clasificacion de Issues\n\n{classification}\n\n"
        f"## Anexo: Guardrails de Seguridad\n\n{guardrails}"
    )


def _find_skill_dir() -> Path:
    """Auto-detect skill/ directory relative to the repo root.

    Walks up from this file's location looking for a directory that
    contains skill/SKILL.md. Typical layout:
        repo/
        ├── agent/src/fixi_agent/prompts.py  (this file)
        └── skill/SKILL.md
    """
    current = Path(__file__).resolve().parent
    for _ in range(10):
        candidate = current / "skill" / "SKILL.md"
        if candidate.exists():
            return current / "skill"
        current = current.parent

    msg = (
        "Could not find skill/SKILL.md by walking up from "
        f"{Path(__file__).resolve().parent}. Pass skill_dir= explicitly."
    )
    raise FileNotFoundError(msg)


def _apply_autonomous_transforms(skill: str, tracking_mode: str) -> str:
    """Apply 6 transformations to convert interactive skill → autonomous prompt."""

    # 1. Strip YAML frontmatter (agent doesn't need skill metadata triggers)
    skill = re.sub(r"^---\n.*?\n---\n", "", skill, count=1, flags=re.DOTALL)

    # 2. Replace Paso 0 (pwd check → pre-validated no-op)
    skill = re.sub(
        r"## Paso 0:.*?(?=\n## Paso 1)",
        (
            "## Paso 0: Contexto Pre-validado\n\n"
            "El orchestrador ya verifico: repo git valido, working tree limpio, "
            "remote correcto, cliente identificado. No re-verificar.\n\n"
            "Convenciones del repo: leer CLAUDE.md, README.md, CONTRIBUTING.md "
            "del directorio actual si existen.\n\n---\n\n"
        ),
        skill,
        count=1,
        flags=re.DOTALL,
    )

    # 3. Replace Paso 3 interactive narrative → static FULL_AUTO
    skill = re.sub(
        r"El usuario puede cambiar nivel en cualquier momento.*?\.\n",
        (
            "Nivel pre-establecido: FULL_AUTO. "
            "Solo escalar a GUIDED si los escaladores automaticos aplican.\n"
        ),
        skill,
    )

    # 4. Strip all "Esperar confirmacion" approval gates (~9 instances)
    skill = re.sub(
        r"Esperar confirmacion[^\n]*\.\n",
        "Proceder inmediatamente. Reportar estado al caller.\n",
        skill,
    )

    # 5. Handle Paso 9 tracking based on mode
    if tracking_mode == "none":
        skill = re.sub(
            r"## Paso 9:.*?(?=## Paso 10:)",
            (
                "## Paso 9: Tracking (DESHABILITADO)\n\n"
                "tracking_mode=none. Paso 9 omitido por configuracion.\n"
                "El PR creado en Paso 8 es el unico artefacto de tracking.\n\n"
                "---\n\n"
            ),
            skill,
            count=1,
            flags=re.DOTALL,
        )
    elif tracking_mode == "client":
        skill = re.sub(
            r"### B\. Mission Control.*?(?=### C\. Output final)",
            (
                "### B. Mission Control\n\n"
                "[Omitido — tracking_mode=client. "
                "Solo ACTIVO.md del cliente se actualiza.]\n\n"
            ),
            skill,
            count=1,
            flags=re.DOTALL,
        )

    # 6. Invert default autonomy from GUIDED to FULL_AUTO
    skill = skill.replace(
        "**Autonomia default: GUIDED**",
        "**Autonomia default: FULL_AUTO** (modo autonomo)",
    )

    return skill


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for mixed English/Spanish."""
    return len(text) // 4
