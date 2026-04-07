"""Tests for fixi_agent.parser — work item URL parser."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from fixi_agent.parser import (
    SourceType,
    WorkItem,
    _extract_github_priority,
    _extract_priority_from_text,
    _map_ado_priority,
    _split_ado_tags,
    _strip_html,
    parse_work_item,
)


class TestSourceDetection:
    """Verify that each URL pattern routes to the correct source type."""

    def test_github_full_url(self) -> None:
        with patch("fixi_agent.parser._run_gh_issue_view", return_value=None):
            wi = parse_work_item("https://github.com/lotsofcontext/fixi-demo-dotnet/issues/42")
        assert wi.source_type == SourceType.github
        assert wi.external_id == "GH-42"

    def test_github_shorthand_hash(self) -> None:
        with patch("fixi_agent.parser._run_gh_issue_view", return_value=None):
            wi = parse_work_item("#123")
        assert wi.source_type == SourceType.github
        assert wi.external_id == "GH-123"

    def test_github_shorthand_gh_prefix(self) -> None:
        with patch("fixi_agent.parser._run_gh_issue_view", return_value=None):
            wi = parse_work_item("GH-456")
        assert wi.source_type == SourceType.github
        assert wi.external_id == "GH-456"

    def test_ado_full_url(self) -> None:
        with patch("fixi_agent.parser._run_az_work_item_show", return_value=None):
            wi = parse_work_item(
                "https://dev.azure.com/globalmvm/EnergySuite/_workitems/edit/4521"
            )
        assert wi.source_type == SourceType.azure_devops
        assert wi.external_id == "WI-4521"

    def test_ado_shorthand_ado(self) -> None:
        wi = parse_work_item("ADO-789")
        assert wi.source_type == SourceType.azure_devops
        assert wi.external_id == "WI-789"

    def test_ado_shorthand_wi(self) -> None:
        wi = parse_work_item("WI-101")
        assert wi.source_type == SourceType.azure_devops
        assert wi.external_id == "WI-101"

    def test_ado_shorthand_ab(self) -> None:
        wi = parse_work_item("AB#42")
        assert wi.source_type == SourceType.azure_devops
        assert wi.external_id == "WI-42"

    def test_linear_url(self) -> None:
        wi = parse_work_item("https://linear.app/myteam/issue/ENG-123")
        assert wi.source_type == SourceType.linear
        assert wi.external_id == "LINEAR-ENG-123"

    def test_jira_atlassian_url(self) -> None:
        wi = parse_work_item("https://myorg.atlassian.net/browse/PROJ-456")
        assert wi.source_type == SourceType.jira
        assert wi.external_id == "JIRA-PROJ-456"

    def test_jira_self_hosted_url(self) -> None:
        wi = parse_work_item("https://jira.mycompany.com/browse/BUG-789")
        assert wi.source_type == SourceType.jira
        assert wi.external_id == "JIRA-BUG-789"

    def test_local_file(self, tmp_path: Path) -> None:
        f = tmp_path / "WI-101-bug.md"
        f.write_text("# [BUG] Error 500\n\nDescription here.\n", encoding="utf-8")
        wi = parse_work_item(str(f))
        assert wi.source_type == SourceType.file
        assert wi.external_id == "WI-101"
        assert "[BUG] Error 500" in wi.title

    def test_free_text(self) -> None:
        wi = parse_work_item("Login fails with 500 when email contains +")
        assert wi.source_type == SourceType.free_text
        assert wi.external_id.startswith("FREE-")

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_work_item("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_work_item("   ")


class TestGitHubPriority:
    """Gap D: extract priority from GitHub labels."""

    def test_priority_critical(self) -> None:
        assert _extract_github_priority([{"name": "priority:critical"}]) == "critica"

    def test_priority_p0(self) -> None:
        assert _extract_github_priority([{"name": "P0"}]) == "critica"

    def test_priority_high(self) -> None:
        assert _extract_github_priority([{"name": "priority:high"}]) == "alta"

    def test_priority_medium(self) -> None:
        assert _extract_github_priority([{"name": "P2"}]) == "media"

    def test_priority_low(self) -> None:
        assert _extract_github_priority([{"name": "low"}]) == "baja"

    def test_no_priority_label(self) -> None:
        assert _extract_github_priority([{"name": "bug"}, {"name": "area:frontend"}]) is None

    def test_empty_labels(self) -> None:
        assert _extract_github_priority([]) is None


class TestAdoPriority:
    """Gap D: map ADO numeric priority to Spanish labels."""

    def test_priority_1(self) -> None:
        assert _map_ado_priority(1) == "critica"

    def test_priority_2(self) -> None:
        assert _map_ado_priority(2) == "alta"

    def test_priority_3(self) -> None:
        assert _map_ado_priority(3) == "media"

    def test_priority_4(self) -> None:
        assert _map_ado_priority(4) == "baja"

    def test_priority_5_unknown(self) -> None:
        assert _map_ado_priority(5) == "desconocida"

    def test_priority_none(self) -> None:
        assert _map_ado_priority(None) is None

    def test_priority_string(self) -> None:
        assert _map_ado_priority("2") == "alta"


class TestAdoTags:
    def test_split_semicolon(self) -> None:
        assert _split_ado_tags("bug; energy-suite; sprint-12") == [
            "bug", "energy-suite", "sprint-12"
        ]

    def test_empty(self) -> None:
        assert _split_ado_tags("") == []

    def test_none(self) -> None:
        assert _split_ado_tags(None) == []


class TestStripHtml:
    def test_strips_tags(self) -> None:
        assert _strip_html("<p>Hello <b>world</b></p>") == "Hello world"

    def test_empty(self) -> None:
        assert _strip_html("") == ""

    def test_none(self) -> None:
        assert _strip_html(None) == ""


class TestFileParser:
    def test_extracts_title_from_heading(self, tmp_path: Path) -> None:
        f = tmp_path / "issue.md"
        f.write_text("# My Bug Report\n\nSome details.\n", encoding="utf-8")
        wi = parse_work_item(str(f))
        assert wi.title == "My Bug Report"

    def test_extracts_id_from_content(self, tmp_path: Path) -> None:
        f = tmp_path / "issue.md"
        f.write_text("# Bug\n\nRelated: WI-101\n", encoding="utf-8")
        wi = parse_work_item(str(f))
        assert wi.external_id == "WI-101"

    def test_extracts_priority_from_table(self, tmp_path: Path) -> None:
        f = tmp_path / "issue.md"
        f.write_text("# Bug\n\n| Priority | 1 - Alta |\n", encoding="utf-8")
        wi = parse_work_item(str(f))
        assert wi.priority == "alta"

    def test_fallback_id_from_stem(self, tmp_path: Path) -> None:
        f = tmp_path / "WI-202-perf.md"
        f.write_text("Some text without explicit ID.\n", encoding="utf-8")
        wi = parse_work_item(str(f))
        assert wi.external_id == "WI-202"


class TestPriorityFromText:
    def test_spanish_priority(self) -> None:
        assert _extract_priority_from_text("Prioridad: Alta") == "alta"

    def test_english_priority(self) -> None:
        assert _extract_priority_from_text("Priority: Critical") == "critica"

    def test_ado_format(self) -> None:
        assert _extract_priority_from_text("| Priority | 1 - Alta |") == "alta"

    def test_no_priority(self) -> None:
        assert _extract_priority_from_text("Just some random text") is None
