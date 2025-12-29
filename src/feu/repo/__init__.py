r"""Contain functions to manage repos."""

from __future__ import annotations

__all__ = ["display_repos_summary", "fetch_github_metadata", "fetch_github_repos"]

from feu.repo.github import (
    display_repos_summary,
    fetch_github_metadata,
    fetch_github_repos,
)
