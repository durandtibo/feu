r"""Contain GitHub utility functions to get information about a single
repository."""

from __future__ import annotations

__all__ = ["fetch_github_metadata"]

import logging
from functools import lru_cache
from typing import Any

from feu.github.auth import build_github_headers
from feu.utils.http import fetch_data

logger: logging.Logger = logging.getLogger(__name__)


@lru_cache
def fetch_github_metadata(owner: str, repo: str) -> dict[str, Any]:
    r"""Get the GitHub repo metadata.

    The metadata is read from GitHub API.

    Args:
        owner: The owner of the repo.
        repo: The repo name.

    Returns:
        The repo metadata.

    Example:
        ```pycon
        >>> from feu.github import fetch_github_metadata
        >>> metadata = fetch_github_metadata(owner="durandtibo", repo="feu")  # doctest: +SKIP

        ```
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    return fetch_data(url=url, headers=build_github_headers())
