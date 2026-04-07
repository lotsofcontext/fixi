"""Guardrail hooks for Fixi Agent — translates the 13 safety rules
from skill/references/guardrails.md into Claude Agent SDK PreToolUse hooks.

These hooks run BEFORE every tool call and can deny dangerous operations.
See: https://platform.claude.com/docs/en/agent-sdk/python#hooks

Usage:
    from fixi_agent.hooks import make_hooks
    options = ClaudeAgentOptions(hooks=make_hooks())
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import structlog

from claude_agent_sdk import HookContext, HookMatcher

log = structlog.get_logger()

# Patterns for sensitive files (Guardrail #7)
SENSITIVE_FILE_PATTERNS = [
    r"\.env(\..*)?$",
    r"\.env$",
    r".*credentials.*",
    r".*secret.*",
    r".*\.key$",
    r".*\.pem$",
    r".*\.pfx$",
    r".*\.p12$",
    r"id_rsa",
    r"id_ed25519",
    r"known_hosts",
]

# CI/CD pipeline files (Guardrail #8)
CICD_PATTERNS = [
    r"\.github/workflows/.*\.ya?ml$",
    r"Jenkinsfile$",
    r"\.gitlab-ci\.ya?ml$",
    r"\.circleci/config\.ya?ml$",
    r"azure-pipelines\.ya?ml$",
    r"bitbucket-pipelines\.ya?ml$",
]

# DB migration paths (Guardrail #9)
MIGRATION_PATTERNS = [
    r"migrations?/",
    r"db/migrate/",
    r"alembic/versions/",
    r"prisma/migrations/",
    r"\.sql$",
    r"schema\.prisma$",
]

# Protected branches (Guardrail #1)
PROTECTED_BRANCHES = {"main", "master", "develop"}


def _deny(reason: str) -> dict[str, Any]:
    """Return a hook deny response."""
    log.warning("guardrail.denied", reason=reason)
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"[GUARDRAIL] {reason}",
        }
    }


def _allow() -> dict[str, Any]:
    """Return an empty response (allow the tool to proceed)."""
    return {}


def _get_tool_input(input_data: dict[str, Any]) -> dict[str, Any]:
    """Extract tool_input from the hook input data."""
    return input_data.get("tool_input", {})


def _matches_any(path: str, patterns: list[str]) -> bool:
    """Check if a file path matches any of the given regex patterns."""
    path_normalized = path.replace("\\", "/")
    return any(re.search(p, path_normalized, re.IGNORECASE) for p in patterns)


# === Hook implementations ===


async def guardrail_no_main_commit(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext,
) -> dict[str, Any]:
    """Guardrail #1: NEVER commit directly to main/master/develop."""
    tool_input = _get_tool_input(input_data)
    command = tool_input.get("command", "")

    if "git commit" in command or "git merge" in command:
        # Check which branch we're on by looking at the command context
        # The agent should have already created a branch, but verify
        for branch in PROTECTED_BRANCHES:
            if f"checkout {branch}" in command or f"switch {branch}" in command:
                return _deny(
                    f"NUNCA commit directo en branch protegido '{branch}'. "
                    "Crear un feature branch primero."
                )

    return _allow()


async def guardrail_no_force_push(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext,
) -> dict[str, Any]:
    """Guardrail #2: NEVER force push."""
    tool_input = _get_tool_input(input_data)
    command = tool_input.get("command", "")

    if "git push" in command and any(
        flag in command for flag in ("--force", " -f ", " -f\n", "--force-with-lease")
    ):
        return _deny("NUNCA force push. Si push normal falla, reportar el error.")

    return _allow()


async def guardrail_sensitive_files(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext,
) -> dict[str, Any]:
    """Guardrail #7: NEVER modify sensitive files (.env, credentials, keys)."""
    tool_input = _get_tool_input(input_data)

    # Check file_path for Write/Edit tools
    file_path = tool_input.get("file_path", "")
    if file_path and _matches_any(file_path, SENSITIVE_FILE_PATTERNS):
        return _deny(
            f"NUNCA modificar archivo sensible: {file_path}. "
            "Si el fix requiere cambios en configuracion sensible, "
            "documentar como instrucciones manuales en el PR."
        )

    return _allow()


async def guardrail_cicd_escalate(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext,
) -> dict[str, Any]:
    """Guardrail #8: CI/CD changes require GUIDED mode (escalate)."""
    tool_input = _get_tool_input(input_data)

    file_path = tool_input.get("file_path", "")
    if file_path and _matches_any(file_path, CICD_PATTERNS):
        return _deny(
            f"Modificar pipeline CI/CD ({file_path}) requiere modo GUIDED. "
            "En modo autonomo, documentar el cambio necesario en el PR "
            "como instruccion manual."
        )

    return _allow()


async def guardrail_migration_escalate(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext,
) -> dict[str, Any]:
    """Guardrail #9: DB migrations require GUIDED mode (escalate)."""
    tool_input = _get_tool_input(input_data)

    file_path = tool_input.get("file_path", "")
    if file_path and _matches_any(file_path, MIGRATION_PATTERNS):
        return _deny(
            f"Modificar migration/schema ({file_path}) requiere modo GUIDED. "
            "En modo autonomo, documentar la migracion necesaria en el PR."
        )

    return _allow()


async def guardrail_dangerous_bash(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext,
) -> dict[str, Any]:
    """Combined bash guardrails: no rm -rf, no git reset --hard, etc."""
    tool_input = _get_tool_input(input_data)
    command = tool_input.get("command", "")

    dangerous_substrings = [
        ("rm -rf /", "Borrar raiz del filesystem"),
        ("git reset --hard", "Reset destructivo de git"),
        ("git clean -fd", "Limpieza destructiva de archivos untracked"),
        ("DROP TABLE", "Borrar tabla de base de datos"),
        ("DROP DATABASE", "Borrar base de datos"),
        ("chmod 777", "Permisos abiertos a todos"),
    ]

    for pattern, reason in dangerous_substrings:
        if pattern.lower() in command.lower():
            return _deny(f"Comando peligroso bloqueado: {reason} ({pattern})")

    # Pipe-to-shell patterns (regex — handles "curl <url> | bash")
    if re.search(r"\|\s*(bash|sh|zsh)\b", command):
        return _deny("Ejecucion de codigo remoto via pipe a shell")

    return _allow()


async def guardrail_verify_remote(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext,
) -> dict[str, Any]:
    """Guardrail #13: Verify remote before push."""
    tool_input = _get_tool_input(input_data)
    command = tool_input.get("command", "")

    # We can't fully verify the remote in a hook (would need subprocess),
    # but we can at least log pushes for audit
    if "git push" in command:
        log.info("guardrail.push_detected", command=command[:100])

    return _allow()


# === Hook registration ===


def make_hooks() -> dict[str, list[HookMatcher]]:
    """Create the full set of guardrail hooks for ClaudeAgentOptions.

    Returns a dict compatible with ClaudeAgentOptions(hooks=...).
    """
    return {
        "PreToolUse": [
            # Bash hooks (Guardrails #1, #2, #13 + dangerous commands)
            HookMatcher(
                matcher="Bash",
                hooks=[
                    guardrail_no_main_commit,
                    guardrail_no_force_push,
                    guardrail_dangerous_bash,
                    guardrail_verify_remote,
                ],
            ),
            # Write hooks (Guardrails #7, #8, #9)
            HookMatcher(
                matcher="Write",
                hooks=[
                    guardrail_sensitive_files,
                    guardrail_cicd_escalate,
                    guardrail_migration_escalate,
                ],
            ),
            # Edit hooks (same as Write)
            HookMatcher(
                matcher="Edit",
                hooks=[
                    guardrail_sensitive_files,
                    guardrail_cicd_escalate,
                    guardrail_migration_escalate,
                ],
            ),
        ],
    }
