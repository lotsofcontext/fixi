# Fixi

> **Autonomous issue resolution agent** — resolve tickets end-to-end from your CI/CD pipeline. Invoke from the CLI, get a Pull Request back.

```bash
fixi resolve \
  --work-item https://dev.azure.com/globalmvm/EnergySuite/_workitems/edit/4521 \
  --repo https://dev.azure.com/globalmvm/EnergySuite/_git/energy-tracker
```

Fixi takes a work item (GitHub Issue, Azure DevOps Work Item, Jira, Linear, or free text), clones the target repo, runs a 10-step workflow — parse, classify, analyze root cause, branch, fix, validate, PR — and hands you a Pull Request ready for review. Autonomous. Auditable. With 13 safety guardrails enforced as code.

The goal is not to replace developers. The goal is to hand them PRs ready for review instead of empty tickets ready for investigation.

---

## It works. Here's the evidence.

On 2026-04-07 Fixi autonomously resolved three intentionally-seeded bugs in a demo .NET repo — one bug, one performance issue, one security vulnerability. Each run: clone repo, find root cause, fix, validate, open PR. Zero human intervention.

| Work Item | Type | PR | Duration | Cost | Turns |
|-----------|------|-----|----------|------|-------|
| [WI-101](https://github.com/lotsofcontext/fixi-demo-dotnet/blob/master/docs/issues/WI-101-bug-lectura-negativa.md) | `bug` — DivideByZeroException | [#2](https://github.com/lotsofcontext/fixi-demo-dotnet/pull/2) | 4m 18s | $0.61 | 24 |
| [WI-102](https://github.com/lotsofcontext/fixi-demo-dotnet/blob/master/docs/issues/WI-102-perf-listado-medidores.md) | `performance` — N+1 query | [#3](https://github.com/lotsofcontext/fixi-demo-dotnet/pull/3) | 4m 53s | $1.16 | 34 |
| [WI-103](https://github.com/lotsofcontext/fixi-demo-dotnet/blob/master/docs/issues/WI-103-security-endpoint-admin.md) | `security` — OWASP A01 | [#4](https://github.com/lotsofcontext/fixi-demo-dotnet/pull/4) | 5m 03s | $1.13 | 31 |

**Totals**: 14 minutes, $2.90 USD, 89 turns, 3 PRs. Clone the [demo repo](https://github.com/lotsofcontext/fixi-demo-dotnet), read the PRs, inspect the diffs. The evidence is verifiable.

---

## Two layers

Fixi is built in two layers that can be understood and audited independently:

### 🧠 Layer 1 — The playbook (`skill/SKILL.md`)

A human-readable markdown file that defines the 10-step workflow: intake, classification, root cause analysis, branching, fix, validations, PR creation, tracking, cleanup. 763 lines of plain text that any engineer can read, audit, and modify. Versioned in git. No black box.

This is the **"what to do"**. It's also the system prompt the agent uses at runtime — one source of truth, no drift.

### 🤖 Layer 2 — The deployable runtime (`agent/`)

A Python CLI (`fixi`) built on the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python). It:

- Loads the playbook as a system prompt with 6 autonomous-mode transformations (strips interactive approval gates, inverts default to FULL_AUTO, etc.)
- Parses work item references into a normalized structure (6 source types supported)
- Clones the target repo with auth injection (GH_TOKEN, AZURE_DEVOPS_PAT)
- Invokes the agent loop with 13 guardrails enforced as `PreToolUse` hooks
- Extracts the PR URL, branch, classification, files changed from the output
- Returns structured JSON for CI/CD consumption

This is the **"how to execute it without a human in the loop"**. 1,165 lines of Python. 136 unit tests.

---

## Quick start

### Install

```bash
git clone https://github.com/lotsofcontext/fixi
cd fixi/agent
python -m venv venv
source venv/bin/activate      # or: venv\Scripts\activate on Windows
pip install -e .
fixi check                    # verify Claude Code CLI, git, auth tokens
```

### Resolve an issue

```bash
# Azure DevOps Work Item
fixi resolve \
  --work-item https://dev.azure.com/org/project/_workitems/edit/4521 \
  --repo https://dev.azure.com/org/project/_git/my-repo

# GitHub Issue
fixi resolve \
  --work-item https://github.com/org/repo/issues/42 \
  --repo https://github.com/org/repo

# Local markdown file (for testing)
fixi resolve \
  --work-item docs/issues/WI-101-bug.md \
  --repo-path ./my-local-repo

# JSON output for CI/CD parsing
fixi resolve --work-item <url> --repo <url> --output json
```

### Required environment variables

```bash
export ANTHROPIC_API_KEY=sk-ant-...          # required
export GH_TOKEN=ghp_...                       # for GitHub repos
export AZURE_DEVOPS_PAT=...                   # for Azure Repos
```

---

## CI/CD integration

Fixi is designed to run as a step in your existing pipeline. Copy-paste examples:

### GitHub Actions

[`agent/.github/workflows/example-fixi-resolve.yml`](agent/.github/workflows/example-fixi-resolve.yml) — manual trigger with `workflow_dispatch`, installs the CLI, runs against a work item, uploads result as artifact, writes step summary.

### Azure DevOps Pipelines

[`agent/azure-pipelines/example-fixi-resolve.yml`](agent/azure-pipelines/example-fixi-resolve.yml) — parameters for `workItemUrl` and `repoUrl`, uses a Variable Group `fixi-secrets` for `ANTHROPIC_API_KEY` and `AZURE_DEVOPS_PAT`.

### Docker

[`agent/Dockerfile`](agent/Dockerfile) — multi-stage build (Node + Claude Code CLI + Python + Fixi) targeting ~1.5 GB. [`agent/docker-compose.yml`](agent/docker-compose.yml) for local dev.

---

## What makes Fixi different

- **Transparent**: the playbook is a markdown file you can read line-by-line. No black box flows, no hidden prompts.
- **Never invents information.** If data is missing, it halts and asks. Verified on the WI-101 run where Fixi marked acceptance criteria as N/A rather than fabricate evidence.
- **Never touches `main`.** Every fix is an isolated branch with a PR for human review. Guardrail-enforced.
- **Minimum change only.** No scope creep, no speculative refactoring, no "while I'm here" cleanups. Verified on all 3 PRs (max 9 lines changed).
- **13 guardrails as code hooks**, not prompts — `PreToolUse` blockers that can't be argued with. See [`agent/src/fixi_agent/hooks.py`](agent/src/fixi_agent/hooks.py).
- **Auto-escalation**: security issues, DB migrations, CI/CD changes, >15 files, or ambiguous root cause all force GUIDED mode regardless of the caller's autonomy setting.
- **3 autonomy levels**: `GUIDED` (approval at every step), `CONFIRM_PLAN` (one-OK execution), `FULL_AUTO` (hands-free). Default is FULL_AUTO for CLI; agent auto-drops to GUIDED when escalators fire.

---

## The 7 classifications

Fixi assigns one of these types based on keywords + work item context:

| Type | Branch prefix | Commit prefix | Use when |
|------|---------------|---------------|----------|
| `bug` | `fix/` | `fix:` | Error, crash, regression, incorrect behavior |
| `feature` | `feat/` | `feat:` | New capability the system didn't have |
| `refactor` | `refactor/` | `refactor:` | Structural change without behavior change |
| `security` | `security/` | `fix:` | Vulnerability, CVE, auth bypass — **always forces GUIDED** |
| `performance` | `perf/` | `perf:` | Slow query, timeout, memory leak, N+1 |
| `docs` | `docs/` | `docs:` | README, API docs, comments, typos |
| `chore` | `chore/` | `chore:` | Dependencies, CI/CD, config, tooling |

Priority when ambiguous: `security > bug > performance > feature > refactor > docs > chore`. Full taxonomy in [`skill/references/classification.md`](skill/references/classification.md).

---

## Stack agnostic

Fixi works with any codebase that has source files and version control.

**Languages**: C#/.NET · Java · Python · TypeScript · JavaScript · Go · Rust · Angular · React — and anything else

**Ticket sources**: GitHub Issues · Azure DevOps Work Items · Jira · Linear · local markdown files · free-text descriptions

**Code platforms**: GitHub · Azure Repos · GitLab

**CI/CD**: GitHub Actions · Azure Pipelines · Jenkins · GitLab CI (auto-detected)

**Validations**: tests, lint, and build runners auto-detected per language (dotnet, npm, pytest, cargo, go, maven, gradle, ruff, eslint, etc.)

---

## Security by design

- **Safety Gate** verifies context, repo, working tree, and client before any action
- **13 guardrails** enforced at every tool use as `PreToolUse` hooks — see [`skill/references/guardrails.md`](skill/references/guardrails.md) for the spec and [`agent/src/fixi_agent/hooks.py`](agent/src/fixi_agent/hooks.py) for the implementation
- **Sensitive files protected**: `.env`, credentials, keys, certificates — never modified, never read into the prompt
- **CI/CD protection**: changes to `.github/workflows`, `azure-pipelines.yml`, `Jenkinsfile`, etc. force GUIDED mode
- **DB migration protection**: changes to `migrations/`, `alembic/`, `prisma/`, `*.sql` force GUIDED
- **Scope limits**: fixes affecting >15 files auto-escalate to GUIDED
- **Auth token sanitization**: secrets are stripped from all logs and error messages
- **No force push. No direct commits to `main`. No bypassing git hooks.**

---

## Repository structure

```
fixi/
├── README.md                   # This file
├── README.es.md                # Spanish version (bilingual sync)
├── CLAUDE.md                   # North Star Prompt + rules for Claude Code
├── HANDOFF-FROM-HQ.md          # Context from GlobalMVM engagement
├── HANDOFF-NORTH-STAR.md       # Audit vs 9 non-negotiable capabilities
│
├── agent/                      # 🤖 The deployable runtime
│   ├── src/fixi_agent/
│   │   ├── cli.py              # CLI entry point (fixi resolve, fixi check)
│   │   ├── orchestrator.py     # Core agent loop (Claude Agent SDK integration)
│   │   ├── prompts.py          # Loads SKILL.md with 6 autonomous transforms
│   │   ├── parser.py           # Multi-source work item parser (Gap D priority)
│   │   ├── cloner.py           # git clone with auth injection
│   │   └── hooks.py            # 13 guardrails as PreToolUse hooks
│   ├── tests/                  # 136 unit tests + integration smoke test
│   ├── .github/workflows/      # GitHub Actions workflow example
│   ├── azure-pipelines/        # Azure DevOps Pipelines example
│   ├── Dockerfile              # Multi-stage build (Node + Python + Claude Code)
│   ├── docker-compose.yml      # Local dev
│   └── pyproject.toml          # Package config
│
├── skill/                      # 🧠 The playbook (human-readable)
│   ├── SKILL.md                # 10-step workflow (763 lines)
│   └── references/
│       ├── classification.md   # 7-type taxonomy
│       └── guardrails.md       # 13 safety rules
│
├── terraform/                  # Azure IaC skeleton (25 files, 5 modules)
│   ├── main.tf
│   ├── modules/
│   │   ├── container_instance/ # ACI running Fixi
│   │   ├── container_registry/ # ACR for the image
│   │   ├── key_vault/          # Secrets (API keys, PATs)
│   │   ├── managed_identity/   # UAMI with least privilege
│   │   └── networking/         # VNet + NSG (deny-all inbound)
│   └── README.md
│
├── kanban/                     # Self-updating project board
│   ├── BOARD.md                # Auto-generated (do not edit)
│   ├── tasks/                  # Individual task files (source of truth)
│   ├── history/                # Append-only daily transition logs
│   └── update_board.py         # Regenerate board from task files
│
└── docs/
    ├── PLAN.md                 # 6-phase roadmap (46 tasks)
    ├── SPEC.md                 # Full technical specification
    ├── diagrams.md             # 5 Mermaid diagrams
    ├── CLIENT-FACING.md        # Business-language overview (v3.0)
    ├── globalmvm-review-simulation.md  # 7-stakeholder review simulation
    └── planning/
        ├── BACKLOG.md
        ├── SPRINT-1.md
        └── SPRINT-2.md
```

---

## Status

Both development sprints are **complete**.

| Sprint | Scope | Status |
|--------|-------|--------|
| **Sprint 1** | Skill workflow (10 steps), classification taxonomy, guardrails spec, demo repo with seeded bugs, Terraform skeleton, client-facing docs | ✅ **100%** (17/17 tasks) |
| **Sprint 2** | Python agent on Claude Agent SDK, CLI, 13 guardrails as hooks, 6-source parser, Dockerfile, GH Actions + Azure Pipelines workflows, 136 unit tests, 3 real PRs as evidence | ✅ **100%** (20/20 tasks) |

See [`kanban/BOARD.md`](kanban/BOARD.md) for the full auto-generated board and [`docs/planning/SPRINT-1.md`](docs/planning/SPRINT-1.md) / [`docs/planning/SPRINT-2.md`](docs/planning/SPRINT-2.md) for per-sprint plans.

---

## Documentation

| Document | Purpose |
|----------|---------|
| [`skill/SKILL.md`](skill/SKILL.md) | The 10-step workflow — also loaded as the agent's system prompt |
| [`skill/references/classification.md`](skill/references/classification.md) | 7-type issue taxonomy with keywords and decision tree |
| [`skill/references/guardrails.md`](skill/references/guardrails.md) | 13 safety rules spec |
| [`agent/README.md`](agent/README.md) | Agent package overview |
| [`docs/CLIENT-FACING.md`](docs/CLIENT-FACING.md) | Business-language overview for stakeholders (v3.0) |
| [`docs/diagrams.md`](docs/diagrams.md) | 5 Mermaid diagrams (flow, classification, autonomy, tracking, architecture) |
| [`docs/PLAN.md`](docs/PLAN.md) | 6-phase implementation roadmap |
| [`docs/SPEC.md`](docs/SPEC.md) | Full technical specification |
| [`docs/globalmvm-review-simulation.md`](docs/globalmvm-review-simulation.md) | Simulated review from 7 stakeholder personas |
| [`terraform/README.md`](terraform/README.md) | Azure deployment guide |
| [`HANDOFF-NORTH-STAR.md`](HANDOFF-NORTH-STAR.md) | Audit of the 9 non-negotiable capabilities from the client's original prompt |

---

## The demo sandbox

[`lotsofcontext/fixi-demo-dotnet`](https://github.com/lotsofcontext/fixi-demo-dotnet) — ASP.NET Core 9 Web API (`GMVM.EnergyTracker`) with 3 intentionally-seeded bugs in the energy sector domain:

- **Bug** (`CalculadoraConsumo.cs`): `DivideByZeroException` when two meter readings share the same date
- **Performance** (`MedidorService.cs`): N+1 query — 51 SQL calls for 50 meters
- **Security** (`AdminController.cs`): Missing `[Authorize]` attribute (OWASP A01 Broken Access Control)

The repo ships with 5 failing tests on `master` — that's the baseline. Run `fixi resolve` against any of the three work items in `docs/issues/` and watch the tests turn green as PRs are created.

---

## License

Proprietary — Lots of Context LLC · 2026
