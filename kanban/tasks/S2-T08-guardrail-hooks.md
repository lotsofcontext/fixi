---
id: S2-T08
title: Implementar 13 guardrails como PreToolUse hooks
sprint: S2
day: 2
status: done
priority: P0
type: implementation
tags: [agent, python, hooks, guardrails, day-2]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 2h
actual: ""
owner: claude
blocks: [S2-T09, S2-T12, S2-T13]
blocked_by: [S2-T07]
related_docs: [SPRINT-2, guardrails]
commits: []
files_touched: []
---

# S2-T08: Guardrails como PreToolUse hooks

> **Sprint**: [[SPRINT-2]] · **Día**: 2 · **Status**: pending

## Contexto

Traducir las **13 reglas de seguridad** de [[guardrails]] a hooks Python que se disparen antes de cada `tool_use` del agent y bloqueen operaciones prohibidas.

## Acceptance Criteria

- [ ] `src/fixi_agent/hooks.py` creado con 13 hooks (uno por regla)
- [ ] `class FixiHooks` que registra todos los hooks en un `ClaudeAgentOptions(hooks={...})`
- [ ] Cada hook devuelve `permissionDecision: deny + permissionDecisionReason` cuando aplica

### Los 13 hooks

| # | Regla | Tool matcher | Lógica |
|---|-------|--------------|--------|
| 1 | NUNCA operar en main/master/develop | `Bash` | Si comando es `git commit` y `git branch --show-current` ∈ {main,master,develop} → DENY |
| 2 | NUNCA force push | `Bash` | Si comando contiene `git push --force` o `-f` → DENY |
| 3 | NUNCA modificar fuera del repo | `Write|Edit` | Si `file_path` no está dentro de `cwd` → DENY |
| 4 | ABORT si working tree dirty | (al inicio, no hook) | Verificación pre-run |
| 5 | Verificar contexto de cliente | (al inicio) | Pre-run check |
| 6 | >15 archivos → escalar | `Edit|Write` | Track count, si > 15 → cambiar permission_mode a default |
| 7 | NUNCA tocar sensitive files | `Write|Edit|Read` | Si path matchea `*.env`, `*credentials*`, `*.key`, `*.pem`, `id_rsa` → DENY |
| 8 | NUNCA CI/CD sin GUIDED | `Edit` | Si path matchea `.github/workflows/*` o `azure-pipelines.yml` → escalar a default |
| 9 | NUNCA DB migrations sin GUIDED | `Edit` | Si path matchea `migrations/*` o `*.sql` → escalar |
| 10 | NUNCA inventar info | (LLM behavior, no hook directo) | Reflejado en system prompt |
| 11 | Rollback automático en fallo | (orchestrator level) | Try/except + git checkout master |
| 12 | Limite de tiempo root cause: 10min | (orchestrator level) | Timeout async |
| 13 | Verificar remote correcto | `Bash` | Si comando es `git push` y remote no matchea expected → DENY |

## Plan

```python
from claude_agent_sdk import HookMatcher, HookContext
from typing import Any
import re, subprocess, os
from pathlib import Path

SENSITIVE_FILE_PATTERNS = [
    r"\.env(\..*)?$",
    r".*credentials.*",
    r".*\.key$",
    r".*\.pem$",
    r".*\.pfx$",
    r"id_rsa",
    r"id_ed25519",
]

def make_hooks(repo_path: Path) -> dict:
    return {
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[guardrail_no_main, guardrail_no_force_push, guardrail_remote_check]),
            HookMatcher(matcher="Write", hooks=[guardrail_sensitive_files, guardrail_inside_repo]),
            HookMatcher(matcher="Edit", hooks=[guardrail_sensitive_files, guardrail_inside_repo, guardrail_ci_cd, guardrail_migrations]),
            HookMatcher(matcher="Read", hooks=[guardrail_sensitive_files]),
        ],
    }

async def guardrail_no_main(input_data, tool_use_id, context):
    cmd = input_data.get("tool_input", {}).get("command", "")
    if "git commit" in cmd:
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, check=True
            )
            current = result.stdout.strip()
            if current in ("main", "master", "develop"):
                return _deny(f"NUNCA commit directo en {current}")
        except subprocess.CalledProcessError:
            pass
    return {}

# ... 12 hooks más
```

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
