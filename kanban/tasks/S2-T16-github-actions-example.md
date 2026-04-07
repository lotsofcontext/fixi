---
id: S2-T16
title: GitHub Actions workflow de ejemplo
sprint: S2
day: 3
status: done
priority: P0
type: implementation
tags: [agent, ci-cd, github-actions, day-3]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 45m
actual: ""
owner: claude
blocks: [S2-T18]
blocked_by: [S2-T14]
related_docs: [SPRINT-2]
commits: []
files_touched: []
---

# S2-T16: GitHub Actions workflow de ejemplo

> **Sprint**: [[SPRINT-2]] · **Día**: 3 · **Status**: pending

## Contexto

Workflow .yml que demuestra cómo usar Fixi como step en una pipeline real. Es el "money shot" del demo: GlobalMVM lo copia a sus workflows y empieza a usar Fixi.

## Acceptance Criteria

- [ ] `agent/.github/workflows/example-fixi-resolve.yml` creado
- [ ] Trigger: `workflow_dispatch` (manual) con inputs `work_item_url` y `repo_url`
- [ ] Job que:
  - Usa `lotsofcontext/fixi-agent:latest` como container
  - Setea ANTHROPIC_API_KEY desde secrets
  - Setea GH_TOKEN desde `secrets.GITHUB_TOKEN`
  - Ejecuta `fixi resolve --work-item ${{ inputs.work_item_url }} --repo ${{ inputs.repo_url }} --output json`
  - Captura el output JSON y lo expone como step output
- [ ] Comentarios en el yml explicando cada sección
- [ ] Documentar setup de secrets en README

## Plan

```yaml
name: Fixi Resolve Issue
on:
  workflow_dispatch:
    inputs:
      work_item_url:
        description: 'Work item URL (GitHub Issue, ADO Work Item, etc.)'
        required: true
      repo_url:
        description: 'Target repo URL'
        required: true

jobs:
  resolve:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/lotsofcontext/fixi-agent:latest
    steps:
      - name: Resolve issue
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          fixi resolve \
            --work-item "${{ inputs.work_item_url }}" \
            --repo "${{ inputs.repo_url }}" \
            --output json > result.json
          cat result.json
```

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
