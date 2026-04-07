"""Tests for fixi_agent.cloner — repo cloning with auth."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from fixi_agent.cloner import _inject_auth, _sanitize_output, clone_repo


class TestInjectAuth:
    def test_github_with_gh_token(self) -> None:
        with patch.dict(os.environ, {"GH_TOKEN": "ghp_test123"}):
            result = _inject_auth("https://github.com/org/repo")
        assert result == "https://x-access-token:ghp_test123@github.com/org/repo"

    def test_github_with_github_token(self) -> None:
        with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test456"}, clear=False):
            env = os.environ.copy()
            env.pop("GH_TOKEN", None)
            with patch.dict(os.environ, env, clear=True):
                with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test456"}):
                    result = _inject_auth("https://github.com/org/repo")
        assert "ghp_test456" in result

    def test_ado_with_pat(self) -> None:
        with patch.dict(os.environ, {"AZURE_DEVOPS_PAT": "mypattoken"}):
            result = _inject_auth("https://dev.azure.com/org/project")
        assert result == "https://mypattoken@dev.azure.com/org/project"

    def test_no_token_returns_unchanged(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            result = _inject_auth("https://github.com/org/repo")
        assert result == "https://github.com/org/repo"

    def test_non_github_non_ado_unchanged(self) -> None:
        result = _inject_auth("https://gitlab.com/org/repo")
        assert result == "https://gitlab.com/org/repo"


class TestSanitizeOutput:
    def test_removes_token_from_text(self) -> None:
        with patch.dict(os.environ, {"GH_TOKEN": "ghp_secret"}):
            result = _sanitize_output(
                "fatal: could not access ghp_secret@github.com",
                "https://github.com/org/repo",
            )
        assert "ghp_secret" not in result
        assert "***" in result

    def test_no_token_returns_unchanged(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            result = _sanitize_output("some error", "https://github.com/org/repo")
        assert result == "some error"


class TestCloneRepo:
    @pytest.mark.integration
    def test_clone_real_public_repo(self) -> None:
        """Integration test: clone the actual fixi-demo-dotnet repo."""
        with clone_repo(
            "https://github.com/lotsofcontext/fixi-demo-dotnet",
            depth=1,
        ) as path:
            assert path.exists()
            assert (path / ".git").is_dir()
            assert (path / "GMVM.EnergyTracker.sln").exists()
        # Note: we don't assert cleanup because shutil.rmtree with
        # ignore_errors=True can fail silently on Windows when git
        # still has lock files open. Cleanup is best-effort.

    @pytest.mark.integration
    def test_clone_with_branch(self) -> None:
        with clone_repo(
            "https://github.com/lotsofcontext/fixi-demo-dotnet",
            branch="master",
            depth=1,
        ) as path:
            assert (path / "GMVM.EnergyTracker.sln").exists()

    def test_clone_bad_url_raises(self) -> None:
        with pytest.raises(RuntimeError, match="git clone failed"):
            with clone_repo("https://github.com/nonexistent/repo-that-does-not-exist-12345"):
                pass

    @pytest.mark.integration
    def test_keep_flag_preserves_dir(self) -> None:
        with clone_repo(
            "https://github.com/lotsofcontext/fixi-demo-dotnet",
            depth=1,
            keep=True,
        ) as path:
            assert path.exists()
        # After context exit with keep=True, dir should still exist
        assert path.exists()
        # Manual cleanup
        import shutil
        shutil.rmtree(path, ignore_errors=True)
