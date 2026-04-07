---
id: S2-T17
title: Azure Pipelines workflow de ejemplo
sprint: S2
day: 3
status: pending
priority: P0
type: implementation
tags: [agent, ci-cd, azure-devops, day-3]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 45m
actual: ""
owner: claude
blocks: []
blocked_by: [S2-T14]
related_docs: [SPRINT-2]
commits: []
files_touched: []
---

# S2-T17: Azure Pipelines workflow de ejemplo

> **Sprint**: [[SPRINT-2]] · **Día**: 3 · **Status**: pending

## Contexto

Equivalente a [[S2-T16]] pero para Azure DevOps Pipelines. Es **el** entregable que GlobalMVM va a usar literalmente porque corren 99% en Azure DevOps.

## Acceptance Criteria

- [ ] `agent/azure-pipelines/example-fixi-resolve.yml` creado
- [ ] Trigger manual con parameters `workItemUrl`, `repoUrl`
- [ ] Container job usando `ghcr.io/lotsofcontext/fixi-agent:latest`
- [ ] Variables: `ANTHROPIC_API_KEY` y `AZURE_DEVOPS_PAT` desde Variable Group o Key Vault
- [ ] Step que ejecuta `fixi resolve --work-item $(workItemUrl) --repo $(repoUrl) --output json`
- [ ] Comentarios explicando cómo setear el Variable Group + permisos del agent
- [ ] README aparte explicando setup en una org ADO

## Plan

```yaml
parameters:
  - name: workItemUrl
    type: string
  - name: repoUrl
    type: string

trigger: none

pool:
  vmImage: ubuntu-latest

container: ghcr.io/lotsofcontext/fixi-agent:latest

steps:
  - script: |
      fixi resolve \
        --work-item "${{ parameters.workItemUrl }}" \
        --repo "${{ parameters.repoUrl }}" \
        --output json | tee result.json
    env:
      ANTHROPIC_API_KEY: $(ANTHROPIC_API_KEY)
      AZURE_DEVOPS_PAT: $(AZURE_DEVOPS_PAT)
```

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
