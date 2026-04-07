"""Work item parser — detects source type and normalizes to WorkItem.

Supports: GitHub Issues, Azure DevOps Work Items, Linear, Jira, local files.
Closes Gap D from the North Star audit: extracts priority from work items.

Usage:
    from fixi_agent.parser import parse_work_item
    wi = parse_work_item("https://github.com/org/repo/issues/42")
"""

from __future__ import annotations

import json
import re
import subprocess
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class SourceType(str, Enum):
    github = "github"
    azure_devops = "azure-devops"
    linear = "linear"
    jira = "jira"
    file = "file"
    free_text = "free-text"


class WorkItem(BaseModel):
    """Normalized work item structure matching SKILL.md Paso 1."""

    title: str
    body: str
    external_id: str
    labels: list[str] = []
    priority: str | None = None  # Gap D: critica/alta/media/baja/desconocida
    source_type: SourceType
    source_url: str | None = None
    raw: dict[str, Any] | None = None  # original payload for debugging


# Regex patterns for source detection
_GITHUB_URL = re.compile(
    r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/issues/(?P<number>\d+)"
)
_GITHUB_SHORT = re.compile(r"^(?:#|GH-)(?P<number>\d+)$")
_ADO_URL = re.compile(
    r"dev\.azure\.com/(?P<org>[^/]+)/(?P<project>[^/]+)/_workitems/edit/(?P<id>\d+)"
)
_ADO_SHORT = re.compile(r"^(?:ADO-|WI-|AB#)(?P<id>\d+)$", re.IGNORECASE)
_LINEAR_URL = re.compile(r"linear\.app/.+/(?:issue|task)/(?P<id>[A-Z]+-\d+)")
_JIRA_URL = re.compile(
    r"(?:atlassian\.net|jira\.[^/]+)/browse/(?P<id>[A-Z]+-\d+)"
)


def parse_work_item(reference: str) -> WorkItem:
    """Parse a work item reference into a normalized WorkItem.

    The reference can be:
    - GitHub Issue URL or #N shorthand
    - Azure DevOps Work Item URL or ADO-N/WI-N/AB#N shorthand
    - Linear URL
    - Jira URL
    - Local file path (markdown)
    - Free text (anything else)

    Args:
        reference: URL, shorthand, file path, or free text description.

    Returns:
        Normalized WorkItem with all available fields.

    Raises:
        ValueError: If the reference is empty.
    """
    reference = reference.strip()
    if not reference:
        msg = "Work item reference cannot be empty"
        raise ValueError(msg)

    # Try each detector in priority order
    if m := _GITHUB_URL.search(reference):
        return _parse_github_url(m, reference)

    if m := _GITHUB_SHORT.match(reference):
        return _parse_github_shorthand(m)

    if m := _ADO_URL.search(reference):
        return _parse_ado_url(m, reference)

    if m := _ADO_SHORT.match(reference):
        return _parse_ado_shorthand(m)

    if m := _LINEAR_URL.search(reference):
        return _parse_linear(m, reference)

    if m := _JIRA_URL.search(reference):
        return _parse_jira(m, reference)

    # Check if it's a local file
    path = Path(reference)
    if path.exists() and path.suffix in (".md", ".txt"):
        return _parse_file(path)

    # Fall back to free text
    return _parse_free_text(reference)


def _parse_github_url(m: re.Match[str], url: str) -> WorkItem:
    """Parse a full GitHub Issue URL using gh CLI."""
    number = m.group("number")
    owner = m.group("owner")
    repo = m.group("repo")

    data = _run_gh_issue_view(number, owner, repo)
    if data:
        return WorkItem(
            title=data.get("title", f"GitHub Issue #{number}"),
            body=data.get("body", ""),
            external_id=f"GH-{number}",
            labels=[l.get("name", "") for l in data.get("labels", [])],
            priority=_extract_github_priority(data.get("labels", [])),
            source_type=SourceType.github,
            source_url=url,
            raw=data,
        )

    # Fallback: minimal info from the URL
    return WorkItem(
        title=f"GitHub Issue #{number}",
        body=f"See: {url}",
        external_id=f"GH-{number}",
        source_type=SourceType.github,
        source_url=url,
    )


def _parse_github_shorthand(m: re.Match[str]) -> WorkItem:
    """Parse #N or GH-N shorthand using gh CLI in current repo."""
    number = m.group("number")
    data = _run_gh_issue_view(number)
    if data:
        return WorkItem(
            title=data.get("title", f"Issue #{number}"),
            body=data.get("body", ""),
            external_id=f"GH-{number}",
            labels=[l.get("name", "") for l in data.get("labels", [])],
            priority=_extract_github_priority(data.get("labels", [])),
            source_type=SourceType.github,
            source_url=data.get("url"),
            raw=data,
        )

    return WorkItem(
        title=f"Issue #{number}",
        body="(Could not fetch — gh CLI failed or not authenticated)",
        external_id=f"GH-{number}",
        source_type=SourceType.github,
    )


def _parse_ado_url(m: re.Match[str], url: str) -> WorkItem:
    """Parse Azure DevOps Work Item URL using az CLI."""
    wi_id = m.group("id")
    org = m.group("org")

    data = _run_az_work_item_show(wi_id, org)
    if data:
        fields = data.get("fields", {})
        return WorkItem(
            title=fields.get("System.Title", f"ADO Work Item #{wi_id}"),
            body=_strip_html(fields.get("System.Description", "")),
            external_id=f"WI-{wi_id}",
            labels=_split_ado_tags(fields.get("System.Tags", "")),
            priority=_map_ado_priority(fields.get("Microsoft.VSTS.Common.Priority")),
            source_type=SourceType.azure_devops,
            source_url=url,
            raw=data,
        )

    return WorkItem(
        title=f"ADO Work Item #{wi_id}",
        body=f"See: {url}\n(Could not fetch — az CLI failed or not authenticated)",
        external_id=f"WI-{wi_id}",
        source_type=SourceType.azure_devops,
        source_url=url,
    )


def _parse_ado_shorthand(m: re.Match[str]) -> WorkItem:
    """Parse ADO-N, WI-N, or AB#N shorthand."""
    wi_id = m.group("id")
    return WorkItem(
        title=f"ADO Work Item #{wi_id}",
        body="(Shorthand reference — fetch content with --repo flag or paste full URL)",
        external_id=f"WI-{wi_id}",
        source_type=SourceType.azure_devops,
    )


def _parse_linear(m: re.Match[str], url: str) -> WorkItem:
    """Parse Linear URL — minimal info, body instructs to paste content."""
    issue_id = m.group("id")
    return WorkItem(
        title=f"Linear {issue_id}",
        body=f"See: {url}\n(Linear API not implemented — paste issue content if auth wall blocks access)",
        external_id=f"LINEAR-{issue_id}",
        source_type=SourceType.linear,
        source_url=url,
    )


def _parse_jira(m: re.Match[str], url: str) -> WorkItem:
    """Parse Jira URL — minimal info, body instructs to paste content."""
    issue_id = m.group("id")
    return WorkItem(
        title=f"Jira {issue_id}",
        body=f"See: {url}\n(Jira API not implemented — paste issue content if auth wall blocks access)",
        external_id=f"JIRA-{issue_id}",
        source_type=SourceType.jira,
        source_url=url,
    )


def _parse_file(path: Path) -> WorkItem:
    """Parse a local markdown file as a work item."""
    content = path.read_text(encoding="utf-8")
    # Extract title from first heading or first line
    title_match = re.match(r"^#\s+(.+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem

    # Try to extract external ID from filename or content
    id_match = re.search(r"WI-\d+|GH-\d+|ADO-\d+|LINEAR-[A-Z]+-\d+|JIRA-[A-Z]+-\d+", content)
    if not id_match:
        id_match = re.search(r"WI-\d+|GH-\d+|ADO-\d+", path.stem)
    external_id = id_match.group(0) if id_match else f"FILE-{path.stem}"

    # Try to extract priority from content
    priority = _extract_priority_from_text(content)

    return WorkItem(
        title=title,
        body=content,
        external_id=external_id,
        priority=priority,
        source_type=SourceType.file,
        source_url=str(path.resolve()),
    )


def _parse_free_text(text: str) -> WorkItem:
    """Parse free text as a work item."""
    from datetime import datetime

    slug = re.sub(r"[^a-z0-9]+", "-", text[:50].lower()).strip("-")
    date_str = datetime.now().strftime("%Y%m%d")

    return WorkItem(
        title=text[:200],
        body=text,
        external_id=f"FREE-{date_str}-{slug}",
        source_type=SourceType.free_text,
    )


# --- CLI helpers ---


def _run_gh_issue_view(
    number: str, owner: str | None = None, repo: str | None = None
) -> dict[str, Any] | None:
    """Run gh issue view and return parsed JSON, or None on failure."""
    cmd = ["gh", "issue", "view", number, "--json",
           "title,body,labels,assignees,milestone,number,state,url"]
    if owner and repo:
        cmd.extend(["--repo", f"{owner}/{repo}"])
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=30,
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        return None


def _run_az_work_item_show(wi_id: str, org: str | None = None) -> dict[str, Any] | None:
    """Run az boards work-item show and return parsed JSON, or None on failure."""
    cmd = ["az", "boards", "work-item", "show", "--id", wi_id, "--output", "json"]
    if org:
        cmd.extend(["--organization", f"https://dev.azure.com/{org}"])
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=30,
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        return None


# --- Field extractors ---


def _extract_github_priority(labels: list[dict[str, Any]]) -> str | None:
    """Extract priority from GitHub labels like priority:high, P1, etc."""
    for label in labels:
        name = label.get("name", "").lower()
        if "priority" in name or name in ("p0", "p1", "p2", "p3", "critical", "high", "medium", "low"):
            if any(x in name for x in ("critical", "p0")):
                return "critica"
            if any(x in name for x in ("high", "p1", "alta")):
                return "alta"
            if any(x in name for x in ("medium", "p2", "media")):
                return "media"
            if any(x in name for x in ("low", "p3", "baja")):
                return "baja"
    return None


def _map_ado_priority(priority: int | str | None) -> str | None:
    """Map ADO Microsoft.VSTS.Common.Priority (1-4) to Spanish labels."""
    if priority is None:
        return None
    try:
        p = int(priority)
    except (ValueError, TypeError):
        return None
    return {1: "critica", 2: "alta", 3: "media", 4: "baja"}.get(p, "desconocida")


def _split_ado_tags(tags: str | None) -> list[str]:
    """Split ADO semicolon-separated tags into a list."""
    if not tags:
        return []
    return [t.strip() for t in tags.split(";") if t.strip()]


def _strip_html(html: str | None) -> str:
    """Basic HTML tag stripping for ADO System.Description."""
    if not html:
        return ""
    return re.sub(r"<[^>]+>", "", html).strip()


def _extract_priority_from_text(text: str) -> str | None:
    """Try to extract priority from markdown content (e.g., work item files)."""
    # Look for "Priority" field in markdown table or header
    m = re.search(
        r"(?:priority|prioridad)[:\s|]*\s*(?:\d\s*[-–]\s*)?(\w+)",
        text,
        re.IGNORECASE,
    )
    if not m:
        return None
    val = m.group(1).lower()
    if val in ("1", "critica", "critical"):
        return "critica"
    if val in ("2", "alta", "high"):
        return "alta"
    if val in ("3", "media", "medium"):
        return "media"
    if val in ("4", "baja", "low"):
        return "baja"
    return None
