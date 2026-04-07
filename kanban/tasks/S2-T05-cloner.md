---
id: S2-T05
title: Implementar cloner.py (git clone a tmpdir con auth)
sprint: S2
day: 1
status: pending
priority: P1
type: implementation
tags: [agent, python, git, day-1]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 45m
actual: ""
owner: claude
blocks: [S2-T06]
blocked_by: [S2-T01]
related_docs: [SPRINT-2]
commits: []
files_touched: []
---

# S2-T05: Cloner de target repo

> **Sprint**: [[SPRINT-2]] · **Día**: 1 · **Status**: pending

## Contexto

Antes de invocar al agent, hay que clonar el repo target a un tmpdir aislado. El agent va a operar dentro de ese directorio. Después de terminar, el cloner limpia el tmpdir.

## Acceptance Criteria

- [ ] `src/fixi_agent/cloner.py` creado
- [ ] `class RepoCheckout` context manager:
  - `__enter__`: crea tmpdir, ejecuta `git clone`, devuelve path
  - `__exit__`: limpia tmpdir (a menos que `keep=True`)
- [ ] Auth para GitHub via `GH_TOKEN` env var (HTTPS auth)
- [ ] Auth para Azure Repos via `AZURE_DEVOPS_PAT` env var
- [ ] Soporte para `--branch` flag (default: branch por default del repo)
- [ ] Manejo de errores: clone falla → exception clara
- [ ] Limpieza segura del tmpdir incluso si el agent crashea

## Plan

```python
import tempfile, subprocess, os, shutil
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def clone_repo(repo_url: str, branch: str | None = None, keep: bool = False):
    tmpdir = tempfile.mkdtemp(prefix="fixi-")
    try:
        url_with_auth = _inject_auth(repo_url)
        cmd = ["git", "clone", "--depth", "50", url_with_auth, tmpdir]
        if branch:
            cmd.extend(["--branch", branch])
        subprocess.run(cmd, check=True, capture_output=True)
        yield Path(tmpdir)
    finally:
        if not keep:
            shutil.rmtree(tmpdir, ignore_errors=True)

def _inject_auth(url: str) -> str:
    if "github.com" in url and (token := os.getenv("GH_TOKEN")):
        return url.replace("https://", f"https://x-access-token:{token}@")
    if "dev.azure.com" in url and (pat := os.getenv("AZURE_DEVOPS_PAT")):
        return url.replace("https://", f"https://{pat}@")
    return url
```

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
