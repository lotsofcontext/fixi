# Fixi

Autonomous issue resolution agent. Takes a ticket (GitHub Issue, Azure DevOps Work Item, Jira, Linear, or free text), analyzes the codebase, implements the fix, and creates a PR — end to end.

## What it does

1. **Parse** — Accepts GitHub URLs, Linear links, Jira links, `#123` shorthand, or plain text descriptions
2. **Classify** — Bug, feature, refactor, security, performance, docs, or chore
3. **Analyze** — Root cause analysis via keyword search, stack trace parsing, dependency tracing
4. **Branch** — Creates branch with proper naming (`fix/123-description`, `feat/456-new-feature`)
5. **Implement** — Minimal, focused changes following conventional commits
6. **Test** — Auto-detects test runner and validates changes
7. **PR** — Creates pull request with full technical description, changes, and impact analysis
8. **Track** — Updates tracking systems (triple-write: source, git, mission control)

## Safety

- Human-in-the-loop by default (GUIDED mode)
- Never invents information — halts if data is missing
- Never modifies code outside the scope of the ticket
- Automatic rollback on failure
- 13 guardrails enforced at every step

## Structure

```
fixi/
├── README.md
├── CLAUDE.md
├── skill/
│   ├── SKILL.md              # Core agent workflow (10 steps)
│   └── references/
│       ├── classification.md  # Issue type taxonomy & decision tree
│       └── guardrails.md      # Safety rules & rollback procedures
└── docs/
    ├── PLAN.md                # Implementation roadmap (5 phases, 36 tasks)
    └── SPEC.md                # Technical specification (pseudocode, schemas)
```

## Usage

Fixi runs as a Claude Code skill. Install by copying the `skill/` directory to your project's `.claude/skills/fix-issue/`.

```
/fix-issue https://github.com/org/repo/issues/123
/fix-issue LINEAR-123
/fix-issue "Login page throws 500 error when email contains +"
```

## Stack Agnostic

Works with any language and platform: C#/.NET, Java, Python, TypeScript, Angular, React. Supports GitHub, Azure DevOps, Jira, and Linear as ticket sources.

## License

Proprietary — Lots of Context LLC
