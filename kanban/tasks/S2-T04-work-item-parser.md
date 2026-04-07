---
id: S2-T04
title: Implementar parser.py (work item URL → estructura)
sprint: S2
day: 1
status: done
priority: P1
type: implementation
tags: [agent, python, parsing, day-1]
created: 2026-04-07T04:30:00
updated: 2026-04-07T07:00:00
estimated: 1h
actual: 30m
owner: claude
blocks: [S2-T06]
blocked_by: [S2-T01]
related_docs: [SPRINT-2, SKILL]
commits: []
files_touched: []
---

# S2-T04: Parser de work items

> **Sprint**: [[SPRINT-2]] · **Día**: 1 · **Status**: pending

## Contexto

Recibe una URL o referencia de work item y devuelve una estructura normalizada (title, body, external_id, labels, priority, source_type, source_url) que el agent puede procesar.

Soporta los 5 source types del [[SKILL]]:
- GitHub Issues (URL completa o `#N`)
- Azure DevOps Work Items (URL completa o `WI-N`, `ADO-N`)
- Linear (URL completa)
- Jira (URL completa)
- File path local (markdown)

## Acceptance Criteria

- [ ] `src/fixi_agent/parser.py` creado
- [ ] `class WorkItem(BaseModel)` con todos los campos normalizados
- [ ] `parse_work_item(reference: str) -> WorkItem` función principal
- [ ] Detección por regex del source_type
- [ ] Para GitHub: usa `gh issue view` subprocess (auth via GH_TOKEN env)
- [ ] Para Azure DevOps: usa `az boards work-item show` subprocess (auth via AZURE_DEVOPS_PAT env)
- [ ] Para Linear/Jira: WebFetch con fallback a manual paste
- [ ] Para file path: lee archivo local
- [ ] Tests unitarios para cada source type (con mocks de subprocess)

## Plan

```python
from pydantic import BaseModel
from enum import Enum
import re, subprocess

class SourceType(str, Enum):
    github = "github"
    azure_devops = "azure-devops"
    linear = "linear"
    jira = "jira"
    file = "file"

class WorkItem(BaseModel):
    title: str
    body: str
    external_id: str
    labels: list[str] = []
    priority: str | None = None
    source_type: SourceType
    source_url: str | None = None

GITHUB_URL = re.compile(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)")
ADO_URL = re.compile(r"dev\.azure\.com/([^/]+)/([^/]+)/_workitems/edit/(\d+)")
# ...

def parse_work_item(reference: str) -> WorkItem:
    if m := GITHUB_URL.search(reference):
        return _parse_github(m)
    if m := ADO_URL.search(reference):
        return _parse_ado(m)
    # ... etc
```

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
