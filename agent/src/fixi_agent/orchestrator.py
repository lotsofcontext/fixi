"""Orchestrator — wires prompts + parser + cloner + Claude Agent SDK.

This is the core of the Fixi agent. It takes a work item reference
and a repo URL, clones the repo, loads the system prompt, invokes
Claude via the Agent SDK, and captures the result.

Usage:
    from fixi_agent.orchestrator import FixiOrchestrator
    result = await FixiOrchestrator(work_item_ref, repo_url).run()
"""

from __future__ import annotations

import re
import tempfile
import time
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    query,
)

from .cloner import clone_repo
from .parser import WorkItem, parse_work_item
from .prompts import load_system_prompt

log = structlog.get_logger()


class RunResult(BaseModel):
    """Structured result of a Fixi agent run."""

    success: bool
    pr_url: str | None = None
    branch: str | None = None
    classification: str | None = None
    files_changed: list[str] = []
    duration_seconds: float = 0.0
    total_cost_usd: float | None = None
    num_turns: int = 0
    error: str | None = None
    work_item: WorkItem | None = None
    agent_output: str = ""


class FixiOrchestrator:
    """Orchestrates the full fix-issue workflow.

    1. Parse the work item reference
    2. Clone the target repo (or use local path)
    3. Load the system prompt (SKILL.md + transforms)
    4. Run the Claude agent loop
    5. Extract PR URL, branch, classification from output
    6. Return structured RunResult
    """

    def __init__(
        self,
        work_item_ref: str,
        repo_url: str | None = None,
        repo_path: Path | None = None,
        branch: str | None = None,
        tracking_mode: str = "client",
        skill_dir: Path | None = None,
        max_turns: int | None = None,
        max_budget_usd: float | None = None,
    ) -> None:
        """Initialize the orchestrator.

        Args:
            work_item_ref: URL, shorthand, file path, or free text of the work item.
            repo_url: HTTPS URL to clone. If None and repo_path is None, uses cwd.
            repo_path: Local path to the repo (skip cloning). Mutually exclusive with repo_url.
            branch: Branch to clone/checkout.
            tracking_mode: "hq", "client", or "none" — controls Paso 9.
            skill_dir: Path to skill/ directory. Auto-detected if None.
            max_turns: Max agent turns (default: SDK default).
            max_budget_usd: Max cost in USD (default: SDK default).
        """
        self.work_item_ref = work_item_ref
        self.repo_url = repo_url
        self.repo_path = repo_path
        self.branch = branch
        self.tracking_mode = tracking_mode
        self.skill_dir = skill_dir
        self.max_turns = max_turns
        self.max_budget_usd = max_budget_usd

    async def run(self) -> RunResult:
        """Execute the full workflow. Returns a structured RunResult."""
        start = time.monotonic()

        # 1. Parse work item
        log.info("orchestrator.parse_work_item", ref=self.work_item_ref)
        try:
            work_item = parse_work_item(self.work_item_ref)
        except Exception as e:
            return RunResult(
                success=False,
                error=f"Failed to parse work item: {e}",
                duration_seconds=time.monotonic() - start,
            )
        log.info(
            "orchestrator.work_item_parsed",
            title=work_item.title,
            source_type=work_item.source_type,
            external_id=work_item.external_id,
        )

        # 2. Load system prompt → write to temp file (avoids Windows
        #    command-line length limit of ~32K chars; our prompt is ~35K).
        log.info("orchestrator.load_prompt", tracking_mode=self.tracking_mode)
        system_prompt_text = load_system_prompt(
            skill_dir=self.skill_dir,
            tracking_mode=self.tracking_mode,
        )
        prompt_file = Path(tempfile.mktemp(suffix=".md", prefix="fixi-prompt-"))
        prompt_file.write_text(system_prompt_text, encoding="utf-8")
        log.info("orchestrator.prompt_written", path=str(prompt_file), chars=len(system_prompt_text))

        try:
            # system_prompt as file reference (TypedDict)
            system_prompt_ref: dict[str, str] = {"type": "file", "path": str(prompt_file)}

            # 3. Determine repo path (clone or use local)
            if self.repo_path:
                return await self._run_in_dir(self.repo_path, work_item, system_prompt_ref, start)

            if self.repo_url:
                with clone_repo(self.repo_url, branch=self.branch) as cloned_path:
                    return await self._run_in_dir(cloned_path, work_item, system_prompt_ref, start)

            # No repo specified — use current working directory
            return await self._run_in_dir(Path.cwd(), work_item, system_prompt_ref, start)
        finally:
            # Clean up temp prompt file
            prompt_file.unlink(missing_ok=True)

    async def _run_in_dir(
        self,
        repo_path: Path,
        work_item: WorkItem,
        system_prompt: dict[str, str],
        start: float,
    ) -> RunResult:
        """Run the agent inside the given repo directory."""
        log.info("orchestrator.run_agent", cwd=str(repo_path))

        # Build the initial prompt from the work item
        initial_prompt = self._build_prompt(work_item)

        # Configure the agent
        options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            allowed_tools=[
                "Read", "Write", "Edit", "Bash", "Grep", "Glob", "WebFetch",
            ],
            permission_mode="acceptEdits",
            cwd=str(repo_path),
            max_turns=self.max_turns,
            max_budget_usd=self.max_budget_usd,
        )

        # Run the agent loop and collect output
        agent_output_parts: list[str] = []
        num_turns = 0
        total_cost: float | None = None
        is_error = False
        errors: list[str] = []

        try:
            async for message in query(prompt=initial_prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if hasattr(block, "text"):
                            agent_output_parts.append(block.text)
                            # Sanitize for Windows cp1252 console logging
                            safe_text = block.text[:200].encode("ascii", "replace").decode("ascii")
                            log.debug("orchestrator.assistant_text", text=safe_text)
                        elif hasattr(block, "name"):
                            log.debug("orchestrator.tool_use", tool=block.name)

                elif isinstance(message, ResultMessage):
                    num_turns = message.num_turns
                    total_cost = message.total_cost_usd
                    is_error = message.is_error
                    if message.errors:
                        errors = message.errors
                    log.info(
                        "orchestrator.result",
                        num_turns=num_turns,
                        cost_usd=total_cost,
                        is_error=is_error,
                        stop_reason=message.stop_reason,
                    )

        except Exception as e:
            log.error("orchestrator.agent_error", error=str(e))
            return RunResult(
                success=False,
                error=f"Agent execution failed: {e}",
                work_item=work_item,
                duration_seconds=time.monotonic() - start,
            )

        agent_output = "\n".join(agent_output_parts)

        # Extract structured info from agent output
        pr_url = self._extract_pr_url(agent_output)
        branch_name = self._extract_branch(agent_output)
        classification = self._extract_classification(agent_output)
        files = self._extract_files_changed(agent_output)

        duration = time.monotonic() - start

        success = not is_error and pr_url is not None
        error_msg = "; ".join(errors) if errors else None

        result = RunResult(
            success=success,
            pr_url=pr_url,
            branch=branch_name,
            classification=classification,
            files_changed=files,
            duration_seconds=round(duration, 2),
            total_cost_usd=total_cost,
            num_turns=num_turns,
            error=error_msg,
            work_item=work_item,
            agent_output=agent_output,
        )

        log.info(
            "orchestrator.complete",
            success=success,
            pr_url=pr_url,
            duration=f"{duration:.1f}s",
            turns=num_turns,
        )

        return result

    def _build_prompt(self, work_item: WorkItem) -> str:
        """Build the initial prompt from the work item."""
        parts = [
            f"Resuelve el siguiente issue siguiendo el workflow completo "
            f"(Pasos 0 al 10 del system prompt).",
            "",
            f"**Issue**: {work_item.title}",
            f"**External ID**: {work_item.external_id}",
            f"**Source**: {work_item.source_type.value}",
        ]
        if work_item.priority:
            parts.append(f"**Priority**: {work_item.priority}")
        if work_item.labels:
            parts.append(f"**Labels**: {', '.join(work_item.labels)}")
        if work_item.source_url:
            parts.append(f"**URL**: {work_item.source_url}")
        parts.append("")
        parts.append("**Descripcion completa del issue:**")
        parts.append("")
        parts.append(work_item.body)

        return "\n".join(parts)

    @staticmethod
    def _extract_pr_url(output: str) -> str | None:
        """Extract PR URL from agent output."""
        patterns = [
            r"(https://github\.com/[^\s]+/pull/\d+)",
            r"(https://dev\.azure\.com/[^\s]+/pullrequest/\d+)",
            r"PR[:\s]+CREADO[:\s]+(https?://[^\s]+)",
            r"PR[:\s]+(https?://[^\s]+/pull/\d+)",
        ]
        for pattern in patterns:
            m = re.search(pattern, output, re.IGNORECASE)
            if m:
                return m.group(1).rstrip(")")
        return None

    @staticmethod
    def _extract_branch(output: str) -> str | None:
        """Extract branch name from agent output."""
        patterns = [
            r"BRANCH\s+CREADO[:\s]+(\S+)",
            r"Branch[:\s]+(\S+/\S+)",
            r"git checkout -b (\S+)",
        ]
        for pattern in patterns:
            m = re.search(pattern, output, re.IGNORECASE)
            if m:
                return m.group(1)
        return None

    @staticmethod
    def _extract_classification(output: str) -> str | None:
        """Extract issue classification from agent output."""
        m = re.search(r"Tipo[:\s]+(\w+)", output, re.IGNORECASE)
        return m.group(1).lower() if m else None

    @staticmethod
    def _extract_files_changed(output: str) -> list[str]:
        """Extract list of changed files from agent output."""
        files: list[str] = []
        for m in re.finditer(r"`([^`]+\.\w{1,5})`\s*[—–-]", output):
            path = m.group(1)
            if "/" in path or "\\" in path:
                files.append(path)
        return list(dict.fromkeys(files))  # deduplicate preserving order
