# Fixi

> **Autonomous Issue Resolution Agent** — takes a ticket, analyzes the codebase, implements the fix, and creates a PR. End-to-end, with human-in-the-loop by default.

Fixi automates the full ticket lifecycle: **intake → classification → root cause analysis → branch → fix → tests → PR → tracking**. It runs as a Claude Code skill, operates across any language or stack, and integrates with GitHub, Azure DevOps, Jira, and Linear.

The goal is not to replace developers. The goal is to hand them PRs ready for review instead of empty tickets ready for investigation.

---

## What makes Fixi different

- **Never invents information.** If data is missing, it halts and asks. No hallucinated root causes.
- **Never touches `main`.** Every fix happens on an isolated branch with a PR for human review.
- **Minimum change only.** No scope creep, no speculative refactoring, no "while I'm here" cleanups.
- **13 guardrails enforced continuously** — from Safety Gate (Paso 0) to pre-push verification.
- **Automatic rollback** if any step fails.
- **3 autonomy levels** — `GUIDED` (default, step-by-step approval), `CONFIRM_PLAN` (one-OK execution), `FULL_AUTO` (hands-free, except for security/migrations).

---

## End-to-end flow

```
Ticket ──▶ Parse ──▶ Classify ──▶ Analyze ──▶ Branch ──▶ Fix ──▶ Tests ──▶ PR ──▶ Tracking
```

Every step is auditable. Every action is reversible. See [docs/diagrams.md](docs/diagrams.md) for Mermaid visualizations of the flow, classification tree, autonomy levels, and tracking pipeline.

### The 7 classifications

| Type | Branch prefix | Commit prefix | Use when |
|------|---------------|---------------|----------|
| `bug` | `fix/` | `fix:` | Error, crash, regression, incorrect behavior |
| `feature` | `feat/` | `feat:` | New capability the system didn't have |
| `refactor` | `refactor/` | `refactor:` | Structural change without behavior change |
| `security` | `security/` | `fix:` | Vulnerability, CVE, auth bypass — **always forces GUIDED** |
| `performance` | `perf/` | `perf:` | Slow query, timeout, memory leak, N+1 |
| `docs` | `docs/` | `docs:` | README, API docs, comments, typos |
| `chore` | `chore/` | `chore:` | Dependencies, CI/CD, config, tooling |

Priority when ambiguous: `security > bug > performance > feature > refactor > docs > chore`. Full taxonomy in [skill/references/classification.md](skill/references/classification.md).

---

## Stack agnostic

Fixi works with any codebase that has source files and a version control system.

**Languages**: C#/.NET · Java · Python · TypeScript · JavaScript · Go · Rust · Angular · React · and anything else

**Ticket sources**: GitHub Issues · Azure DevOps Work Items · Jira · Linear · free-text descriptions

**Code platforms**: GitHub · Azure Repos · GitLab

**CI/CD**: GitHub Actions · Azure Pipelines · Jenkins · GitLab CI (auto-detected)

---

## Usage

Fixi runs as a Claude Code skill. Install by copying `skill/` to your project's `.claude/skills/fix-issue/`.

```bash
# GitHub issue URL
/fix-issue https://github.com/org/repo/issues/123

# Azure DevOps work item
/fix-issue https://dev.azure.com/org/project/_workitems/edit/4521

# Shorthand
/fix-issue #42

# Linear / Jira
/fix-issue LINEAR-ABC-123
/fix-issue PROJ-789

# Free text
/fix-issue "Login fails with 500 when email contains +"
```

---

## Repository structure

```
fixi/
├── README.md                   # This file
├── README.es.md                # Spanish version (bilingual sync)
├── CLAUDE.md                   # Rules for Claude Code when working on this repo
├── HANDOFF-FROM-HQ.md           # Context from GlobalMVM engagement
│
├── skill/                      # The agent itself
│   ├── SKILL.md                # Core 10-step workflow
│   └── references/
│       ├── classification.md    # 7-type taxonomy
│       └── guardrails.md        # 13 safety rules
│
└── docs/
    ├── PLAN.md                 # 6-phase roadmap (46 tasks)
    ├── SPEC.md                 # Full technical specification
    ├── diagrams.md             # 5 Mermaid diagrams
    ├── CLIENT-FACING.md        # Business-language overview
    └── planning/
        └── BACKLOG.md          # Prioritized backlog
```

---

## Roadmap

Fixi is being built in 6 phases. See [docs/PLAN.md](docs/PLAN.md) for the full roadmap and [docs/planning/BACKLOG.md](docs/planning/BACKLOG.md) for current priorities.

| Phase | Focus | Status |
|-------|-------|--------|
| **1. Fundamentos (MVP)** | GitHub Issues parser, classification, root cause, branch/commit/PR flow | Spec complete |
| **2. Multi-source + Azure DevOps** | Linear, Jira, Azure DevOps Work Items, free text, intelligent disambiguation | Spec complete |
| **3. Autonomy + Testing** | `CONFIRM_PLAN`, `FULL_AUTO`, automatic test runner detection, regression tests | Spec complete |
| **4. Triple-write tracking** | Client's ACTIVO.md + Mission Control (tasks, activity log, inbox) | Spec complete |
| **5. Hardening + Guardrails** | Rollback, scope limits, sensitive file protection, dry-run mode | Spec complete |
| **6. Ecosystem + Infra + Public Demo** | Azure IaC (Terraform), MCP Server, A2A Protocol, `/status` endpoint, self-dogfooding | Spec complete |

---

## Security

Fixi is designed for trust in production codebases:

- **Safety Gate** verifies context, repo, working tree, and client before any action
- **13 guardrails** enforced at every step — see [skill/references/guardrails.md](skill/references/guardrails.md)
- **Sensitive files protected**: `.env`, credentials, keys, certificates — never modified
- **CI/CD protection**: changes to `.github/workflows`, `azure-pipelines.yml`, etc. always force GUIDED mode
- **Scope limits**: fixes affecting >15 files auto-escalate to GUIDED
- **Audit trail**: every action logged in triple-write tracking (client state + mission control + activity log)
- **No force push. No direct commits to `main`. No bypassing of git hooks.**

---

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/PLAN.md](docs/PLAN.md) | 6-phase implementation roadmap |
| [docs/SPEC.md](docs/SPEC.md) | Full technical specification |
| [docs/diagrams.md](docs/diagrams.md) | 5 Mermaid diagrams (flow, classification, autonomy, tracking, architecture) |
| [docs/CLIENT-FACING.md](docs/CLIENT-FACING.md) | Business-language overview for stakeholders |
| [docs/planning/BACKLOG.md](docs/planning/BACKLOG.md) | Prioritized backlog |
| [skill/SKILL.md](skill/SKILL.md) | 10-step workflow definition |
| [skill/references/classification.md](skill/references/classification.md) | 7-type issue taxonomy |
| [skill/references/guardrails.md](skill/references/guardrails.md) | 13 safety rules |

---

## License

Proprietary — Lots of Context LLC · 2026
