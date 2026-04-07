"""Repo cloner — clones target repo to a temp directory with auth.

Handles authentication for GitHub (GH_TOKEN) and Azure DevOps
(AZURE_DEVOPS_PAT) via URL injection. Cleans up on exit.

Usage:
    from fixi_agent.cloner import clone_repo

    with clone_repo("https://github.com/org/repo") as repo_path:
        # repo_path is a Path to the cloned dir
        run_agent(repo_path)
    # tmpdir is cleaned up automatically
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import structlog

log = structlog.get_logger()


@contextmanager
def clone_repo(
    repo_url: str,
    branch: str | None = None,
    keep: bool = False,
    depth: int = 50,
) -> Generator[Path, None, None]:
    """Clone a repo to a temp directory, yield its path, clean up on exit.

    Args:
        repo_url: HTTPS URL of the repo to clone.
        branch: Branch to checkout (default: repo's default branch).
        keep: If True, do not delete the tmpdir on exit (useful for debugging).
        depth: Shallow clone depth (default 50 commits for reasonable git log).

    Yields:
        Path to the cloned repository root.

    Raises:
        RuntimeError: If git clone fails.
    """
    tmpdir = tempfile.mkdtemp(prefix="fixi-")
    log.info("cloner.start", repo_url=repo_url, tmpdir=tmpdir, branch=branch)

    try:
        url_with_auth = _inject_auth(repo_url)
        cmd = ["git", "clone", "--depth", str(depth), url_with_auth, tmpdir]
        if branch:
            cmd.extend(["--branch", branch])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            stderr = result.stderr.strip()
            # Sanitize: don't leak auth tokens in error messages
            stderr = _sanitize_output(stderr, repo_url)
            log.error("cloner.failed", returncode=result.returncode, stderr=stderr)
            msg = f"git clone failed (exit {result.returncode}): {stderr}"
            raise RuntimeError(msg)

        log.info("cloner.success", path=tmpdir)
        yield Path(tmpdir)

    finally:
        if keep:
            log.info("cloner.kept", path=tmpdir)
        else:
            shutil.rmtree(tmpdir, ignore_errors=True)
            log.info("cloner.cleaned", path=tmpdir)


def _inject_auth(url: str) -> str:
    """Inject auth tokens into HTTPS URLs from environment variables.

    Supports:
    - GitHub: GH_TOKEN env var → x-access-token auth
    - Azure DevOps: AZURE_DEVOPS_PAT env var → PAT auth
    - Other: returns URL unchanged

    SECURITY: tokens are injected into the URL for git clone only.
    They are NEVER logged or returned to the caller.
    """
    if "github.com" in url:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if token:
            return url.replace("https://", f"https://x-access-token:{token}@")

    if "dev.azure.com" in url or "visualstudio.com" in url:
        pat = os.environ.get("AZURE_DEVOPS_PAT")
        if pat:
            return url.replace("https://", f"https://{pat}@")

    return url


def _sanitize_output(text: str, original_url: str) -> str:
    """Remove auth tokens from error messages to prevent leaking credentials."""
    # Remove any token that might appear in git error messages
    for var in ("GH_TOKEN", "GITHUB_TOKEN", "AZURE_DEVOPS_PAT"):
        token = os.environ.get(var)
        if token and token in text:
            text = text.replace(token, "***")

    # Also clean the authenticated URL if it leaked
    auth_url = _inject_auth(original_url)
    if auth_url != original_url and auth_url in text:
        text = text.replace(auth_url, original_url)

    return text
