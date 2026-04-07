# Fixi Agent

> Autonomous issue resolution agent built on the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python). Resolves tickets end-to-end from CI/CD pipelines: clones the target repo, parses the work item, runs the agent loop, opens a PR.

Fixi is the **deployable runtime** for the [`fix-issue` workflow](../skill/SKILL.md). The skill (`SKILL.md`) is the human-readable playbook; the agent is the program that executes that playbook autonomously, without a human inside an interactive Claude Code session.

---

## Use case

```bash
fixi resolve \
  --work-item https://dev.azure.com/globalmvm/EnergySuite/_workitems/edit/4521 \
  --repo https://dev.azure.com/globalmvm/EnergySuite/_git/energy-tracker
```

What happens:

1. Parses the work item URL → detects source (GitHub Issue, Azure DevOps, Jira, Linear, file)
2. Fetches the work item content (`gh issue view`, `az boards work-item show`, `WebFetch`, or local file)
3. Clones the target repo to a temp directory
4. Initializes a `ClaudeSDKClient` with:
   - **system_prompt** = the contents of [`skill/SKILL.md`](../skill/SKILL.md)
   - **tools** = `Read, Write, Edit, Bash, Grep, Glob, WebFetch`
   - **permission_mode** = `acceptEdits` (autonomous)
   - **hooks** = the [13 guardrails](../skill/references/guardrails.md) as `PreToolUse` blockers
5. Runs the agent loop with the work item as the initial prompt
6. Captures branch, commits, PR URL from the agent output
7. Cleans up the temp directory
8. Returns a result (JSON for CI/CD, human-readable for terminal)

Designed to run as a step in **GitHub Actions** or **Azure DevOps Pipelines**.

---

## Status

🚧 **Sprint 2 in progress** — see [`docs/planning/SPRINT-2.md`](../docs/planning/SPRINT-2.md) for the full plan.

This README will be expanded as the agent matures. For now, this is the project skeleton.

---

## Local development (when implemented)

```bash
cd agent
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install -e .[dev]

# Verify Claude Code CLI is installed (the SDK wraps it)
claude --version

# Run tests
pytest

# Run CLI
fixi --help
```

## Architecture

See [`docs/planning/SPRINT-2.md`](../docs/planning/SPRINT-2.md) for the architecture diagram and component breakdown.

## License

Proprietary — Lots of Context LLC · 2026
