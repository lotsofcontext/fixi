"""Fixi — Autonomous issue resolution agent built on Claude Agent SDK.

Resolves tickets end-to-end from CI/CD pipelines: clones the target repo,
parses the work item, runs the agent loop with our SKILL.md as system prompt
and the 13 guardrails as PreToolUse hooks, and opens a PR.

Entry point: `fixi resolve --work-item <url> --repo <url>`
"""

__version__ = "0.1.0"
