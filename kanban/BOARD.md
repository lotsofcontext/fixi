# Fixi Kanban Board

> **Última actualización**: 2026-04-08 21:00:28
> **Auto-generado** por `update_board.py` — NO editar a mano.
> Ver: [[README|Cómo usar el kanban]] · [[SPRINT-1|Sprint actual]] · [[SPRINT-2|Sprint siguiente]] · [[BACKLOG|Backlog]] · [[PLAN|Roadmap]]

## Resumen

| Total | 🔄 In Progress | ⛔ Blocked | 📋 Pending | ✅ Done | 🚫 Cancelled | Progress |
|-------|----------------|------------|-------------|---------|---------------|----------|
| **50** | 0 | 0 | 0 | 49 | 1 | **100%** |

_Progress = done / (total − cancelled) = 49/49_

```
██████████████████████████████ 100%
```

## Por Sprint

| Sprint | Total | Done | In Progress | Pending | Blocked | Cancelled | Progress |
|--------|-------|------|-------------|---------|---------|-----------|----------|
| **S1** | 18 | 17 | 0 | 0 | 0 | 1 | **100%** |
| **S2** | 20 | 20 | 0 | 0 | 0 | 0 | **100%** |
| **S3** | 12 | 12 | 0 | 0 | 0 | 0 | **100%** |

## ✅ Done (49)

| ID | Task | Sprint | Estimated | Actual | Completed |
|----|------|--------|-----------|--------|-----------|
| [[S1-T01]] | Verificar contenido de classification.md y guardrails.md | S1 | 15m | 5m | 2026-04-06T21:35:00 |
| [[S1-T02]] | Audit wiki links — formato dual para client-facing vs internos | S1 | 30m | 25m | 2026-04-06T21:50:00 |
| [[S1-T03]] | Crear repo lotsofcontext/fixi-demo-dotnet en GitHub | S1 | 15m | 40m | 2026-04-06T22:30:00 |
| [[S1-T04]] | Skeleton GMVM.EnergyTracker (4 projects + config) | S1 | 45m | 25m | 2026-04-06T22:55:00 |
| [[S1-T05]] | Sembrar BUG #1 — DivideByZero en CalculadoraConsumo | S1 | 30m | 15m | 2026-04-07T01:15:00 |
| [[S1-T06]] | Sembrar PERF #2 — N+1 en MedidorService.ListarConResumen | S1 | 45m | 15m | 2026-04-07T01:30:00 |
| [[S1-T07]] | Sembrar SECURITY #3 — AdminController sin [Authorize] | S1 | 20m | 15m | 2026-04-07T01:45:00 |
| [[S1-T08]] | Tests que fallan para los 3 bugs sembrados | S1 | 1h30m | 30m | 2026-04-07T02:15:00 |
| [[S1-T09]] | Pre-crear 3 work items markdown en docs/issues/ | S1 | 1h | 25m | 2026-04-07T02:30:00 |
| [[S1-T10]] | CLAUDE.md del demo repo (convenciones .NET) | S1 | 30m | 15m | 2026-04-06T22:55:00 |
| [[S1-T11]] | README bilingüe del demo repo | S1 | 45m | 20m | 2026-04-07T03:00:00 |
| [[S1-T12]] | Rehearsal Fixi contra WI-101 → run-01-github.md | S1 | 1h30m | 3m51s | 2026-04-07T04:15:00 |
| [[S1-T13]] | Agregar parser Azure DevOps Work Items al SKILL.md | S1 | 45m | 25m | 2026-04-07T02:30:00 |
| [[S1-T14]] | Agregar Azure Repos PR creation al SKILL.md | S1 | 45m | 25m | 2026-04-07T02:30:00 |
| [[S1-T16]] | Terraform skeleton en fixi/terraform/ | S1 | 2h | 1h35m | 2026-04-07T02:35:00 |
| [[S1-T17]] | Polish CLIENT-FACING.md con links a runs y Terraform | S1 | 1h | 30m | 2026-04-07T03:30:00 |
| [[S1-T18]] | Actualizar descripción + topics del repo lotsofcontext/fixi en GitHub | S1 | 15m | 5m | 2026-04-07T00:00:00 |
| [[S2-T01]] | Crear fixi/agent/ skeleton (pyproject.toml, src, tests, README) | S2 | 30m | 15m | 2026-04-07T05:15:00 |
| [[S2-T02]] | Instalar claude-agent-sdk + verificar import | S2 | 15m | 20m | 2026-04-07T05:50:00 |
| [[S2-T03]] | Implementar prompts.py (loader de SKILL.md) | S2 | 1h | 30m | 2026-04-07T06:30:00 |
| [[S2-T04]] | Implementar parser.py (work item URL → estructura) | S2 | 1h | 30m | 2026-04-07T07:00:00 |
| [[S2-T05]] | Implementar cloner.py (git clone a tmpdir con auth) | S2 | 45m | 15m | 2026-04-07T07:15:00 |
| [[S2-T06]] | Implementar orchestrator.py (ClaudeSDKClient wrapper) | S2 | 1h |  | 2026-04-07T07:15:00 |
| [[S2-T07]] | Smoke test — orchestrator resuelve WI-101 sin hooks | S2 | 30m | 45m | 2026-04-07T08:00:00 |
| [[S2-T08]] | Implementar 13 guardrails como PreToolUse hooks | S2 | 2h |  | 2026-04-07T04:30:00 |
| [[S2-T09]] | Implementar audit log (PostToolUse hook → JSONL) | S2 | 30m |  | 2026-04-07T04:30:00 |
| [[S2-T10]] | Implementar cli.py (click) — fixi resolve | S2 | 45m |  | 2026-04-07T08:00:00 |
| [[S2-T11]] | Implementar output.py (JSON + human formatters) | S2 | 30m |  | 2026-04-07T04:30:00 |
| [[S2-T12]] | Wire CLI → orchestrator → output end-to-end | S2 | 30m |  | 2026-04-07T04:30:00 |
| [[S2-T13]] | Tests unitarios — parser, hooks, prompts | S2 | 1h30m |  | 2026-04-07T04:30:00 |
| [[S2-T14]] | Dockerfile multi-stage (Node + Claude Code + Python + fixi) | S2 | 1h30m |  | 2026-04-07T04:30:00 |
| [[S2-T15]] | docker-compose.yml para dev local | S2 | 30m |  | 2026-04-07T04:30:00 |
| [[S2-T16]] | GitHub Actions workflow de ejemplo | S2 | 45m |  | 2026-04-07T04:30:00 |
| [[S2-T17]] | Azure Pipelines workflow de ejemplo | S2 | 45m |  | 2026-04-07T04:30:00 |
| [[S2-T18]] | Rehearsal end-to-end del agent CLI vs WI-101/102/103 | S2 | 2h |  | 2026-04-07T04:30:00 |
| [[S2-T19]] | Update CLIENT-FACING.md — narrativa skill → agent | S2 | 1h |  | 2026-04-07T04:30:00 |
| [[S2-T20]] | Update PLAN.md — agent como Phase 6 central | S2 | 30m |  | 2026-04-07T04:30:00 |
| [[S3-T01]] | Crear .claude/agents/ dir para agentes de simulacion GlobalMVM | S3 | 5m | 2m | 2026-04-08T00:00:00 |
| [[S3-T02]] | Draft agente globalmvm-elkin-ceo (CEO sponsor) | S3 | 15m | 5m | 2026-04-08T00:00:00 |
| [[S3-T03]] | Draft agente globalmvm-joaris-architect (Champion Tecnico) | S3 | 15m | 5m | 2026-04-08T00:00:00 |
| [[S3-T04]] | Draft agente globalmvm-jefferson-hyperautomation (dio el prompt original) | S3 | 15m | 5m | 2026-04-08T00:00:00 |
| [[S3-T05]] | Draft agente globalmvm-liset-data-ai (Lider Datos+IA, Centro Aceleracion) | S3 | 15m | 5m | 2026-04-08T00:00:00 |
| [[S3-T06]] | Draft agente globalmvm-john-bairo-architect (escalability gatekeeper) | S3 | 15m | 5m | 2026-04-08T00:00:00 |
| [[S3-T07]] | Draft agente globalmvm-jenny-product-owner (PO Energy Suite) | S3 | 15m | 5m | 2026-04-08T00:00:00 |
| [[S3-T08]] | Draft agente globalmvm-victor-operations (ORIGINO el caso de uso) | S3 | 15m | 5m | 2026-04-08T00:00:00 |
| [[S3-T09]] | Draft agente globalmvm-carlos-regression-prevention (dev senior) | S3 | 15m | 5m | 2026-04-08T00:00:00 |
| [[S3-T10]] | Dry-run en paralelo — los 8 agentes critican Fixi PoC | S3 | 45m | 25m | 2026-04-08T00:00:00 |
| [[S3-T11]] | Generar FAQ defensivo a partir de los 8 agentes | S3 | 30m | 15m | 2026-04-08T00:00:00 |
| [[S3-T12]] | Documentar casos de uso del equipo de simulacion | S3 | 20m | 10m | 2026-04-08T00:00:00 |

## 🚫 Cancelled (1)

| ID | Task | Sprint | Reason |
|----|------|--------|--------|
| [[S1-T15]] | Rehearsal Fixi contra WI-102 y WI-103 (path Azure DevOps) | S1 | Pivot a Sprint 2: el rehearsal se hara contra el AGENT (Python Claude Agent SDK), no contra el SKILL. Validar el agent es estrategicamente mas valioso que validar el skill. |

