"""Tests for fixi_agent.orchestrator — core agent loop."""

from __future__ import annotations

from pathlib import Path

import pytest

from fixi_agent.orchestrator import FixiOrchestrator, RunResult


class TestRunResult:
    def test_default_values(self) -> None:
        r = RunResult(success=True)
        assert r.success is True
        assert r.pr_url is None
        assert r.files_changed == []
        assert r.agent_output == ""

    def test_full_result(self) -> None:
        r = RunResult(
            success=True,
            pr_url="https://github.com/org/repo/pull/1",
            branch="fix/WI-101-bug",
            classification="bug",
            files_changed=["src/main.py"],
            duration_seconds=120.5,
            total_cost_usd=0.05,
            num_turns=15,
        )
        assert r.pr_url == "https://github.com/org/repo/pull/1"
        assert r.classification == "bug"


class TestExtractors:
    """Test the static extraction methods on FixiOrchestrator."""

    def test_extract_pr_url_github(self) -> None:
        output = "PR CREADO: https://github.com/lotsofcontext/fixi-demo-dotnet/pull/1"
        assert FixiOrchestrator._extract_pr_url(output) == \
            "https://github.com/lotsofcontext/fixi-demo-dotnet/pull/1"

    def test_extract_pr_url_ado(self) -> None:
        output = "PR: https://dev.azure.com/globalmvm/EnergySuite/pullrequest/42"
        assert FixiOrchestrator._extract_pr_url(output) == \
            "https://dev.azure.com/globalmvm/EnergySuite/pullrequest/42"

    def test_extract_pr_url_none(self) -> None:
        assert FixiOrchestrator._extract_pr_url("No PR created") is None

    def test_extract_branch_creado(self) -> None:
        output = "BRANCH CREADO: fix/WI-101-divide-by-zero"
        assert FixiOrchestrator._extract_branch(output) == "fix/WI-101-divide-by-zero"

    def test_extract_branch_checkout(self) -> None:
        output = "git checkout -b perf/WI-102-n-plus-one"
        assert FixiOrchestrator._extract_branch(output) == "perf/WI-102-n-plus-one"

    def test_extract_branch_none(self) -> None:
        assert FixiOrchestrator._extract_branch("No branch info") is None

    def test_extract_classification(self) -> None:
        output = "CLASIFICACION:\n  Tipo: bug"
        assert FixiOrchestrator._extract_classification(output) == "bug"

    def test_extract_classification_perf(self) -> None:
        output = "Tipo: performance"
        assert FixiOrchestrator._extract_classification(output) == "performance"

    def test_extract_classification_none(self) -> None:
        assert FixiOrchestrator._extract_classification("Nothing here") is None

    def test_extract_files_changed(self) -> None:
        output = (
            "- `src/Services/Calculator.cs` — fixed division\n"
            "- `tests/CalculatorTests.cs` — added regression test\n"
        )
        files = FixiOrchestrator._extract_files_changed(output)
        assert files == ["src/Services/Calculator.cs", "tests/CalculatorTests.cs"]

    def test_extract_files_deduplicates(self) -> None:
        output = (
            "- `src/main.py` — first mention\n"
            "- `src/main.py` — second mention\n"
        )
        files = FixiOrchestrator._extract_files_changed(output)
        assert files == ["src/main.py"]

    def test_extract_files_ignores_non_paths(self) -> None:
        output = "- `bug` — not a file path\n"
        assert FixiOrchestrator._extract_files_changed(output) == []


class TestBuildPrompt:
    def test_basic_prompt(self) -> None:
        from fixi_agent.parser import WorkItem, SourceType
        wi = WorkItem(
            title="Error 500 on login",
            body="Stack trace here...",
            external_id="GH-42",
            source_type=SourceType.github,
            labels=["bug"],
            priority="alta",
        )
        orch = FixiOrchestrator(work_item_ref="unused", repo_path=Path("."))
        prompt = orch._build_prompt(wi)
        assert "Error 500 on login" in prompt
        assert "GH-42" in prompt
        assert "alta" in prompt
        assert "bug" in prompt
        assert "Stack trace here..." in prompt

    def test_prompt_without_optional_fields(self) -> None:
        from fixi_agent.parser import WorkItem, SourceType
        wi = WorkItem(
            title="Simple fix",
            body="Details.",
            external_id="FREE-20260407-simple",
            source_type=SourceType.free_text,
        )
        orch = FixiOrchestrator(work_item_ref="unused", repo_path=Path("."))
        prompt = orch._build_prompt(wi)
        assert "Simple fix" in prompt
        assert "Priority" not in prompt  # no priority set
        assert "Labels" not in prompt  # no labels set


class TestOrchestratorInit:
    def test_init_with_repo_url(self) -> None:
        o = FixiOrchestrator(
            work_item_ref="WI-101",
            repo_url="https://github.com/org/repo",
        )
        assert o.repo_url == "https://github.com/org/repo"
        assert o.repo_path is None

    def test_init_with_repo_path(self) -> None:
        o = FixiOrchestrator(
            work_item_ref="WI-101",
            repo_path=Path("/tmp/my-repo"),
        )
        assert o.repo_path == Path("/tmp/my-repo")
        assert o.repo_url is None

    def test_init_defaults(self) -> None:
        o = FixiOrchestrator(work_item_ref="WI-101")
        assert o.tracking_mode == "client"
        assert o.branch is None
        assert o.max_turns is None
