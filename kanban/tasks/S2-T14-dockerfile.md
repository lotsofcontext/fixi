---
id: S2-T14
title: Dockerfile multi-stage (Node + Claude Code + Python + fixi)
sprint: S2
day: 3
status: pending
priority: P1
type: implementation
tags: [agent, docker, deployment, day-3]
created: 2026-04-07T04:30:00
updated: 2026-04-07T04:30:00
estimated: 1h30m
actual: ""
owner: claude
blocks: [S2-T15, S2-T16, S2-T17]
blocked_by: [S2-T12]
related_docs: [SPRINT-2]
commits: []
files_touched: []
---

# S2-T14: Dockerfile multi-stage

> **Sprint**: [[SPRINT-2]] · **Día**: 3 · **Status**: pending

## Contexto

Docker image que empaca Python + Node + Claude Code CLI + fixi-agent. Multi-stage para minimizar tamaño.

## Acceptance Criteria

- [ ] `agent/Dockerfile` con stages:
  - `node-stage`: instala Node 22 LTS y Claude Code CLI
  - `python-stage`: builds wheel del agent
  - `final`: junta ambos en `python:3.12-slim-bookworm`
- [ ] Imagen final < 1.5 GB
- [ ] `docker run -e ANTHROPIC_API_KEY=... fixi-agent fixi version` funciona
- [ ] Variables de entorno documentadas en comentarios
- [ ] Working dir `/workspace`, agent corre como usuario non-root

## Plan

```dockerfile
FROM node:22-slim AS node-base
RUN npm install -g @anthropic-ai/claude-code

FROM python:3.12-slim-bookworm AS python-build
WORKDIR /build
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir build && python -m build --wheel

FROM python:3.12-slim-bookworm
COPY --from=node-base /usr/local/bin/node /usr/local/bin/node
COPY --from=node-base /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/@anthropic-ai/claude-code/cli.js /usr/local/bin/claude

COPY --from=python-build /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

RUN useradd -m -u 1000 fixi
USER fixi
WORKDIR /workspace

ENTRYPOINT ["fixi"]
CMD ["--help"]
```

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 04:30` · created (status: pending)
