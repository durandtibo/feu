r"""Contain GitHub utility functions."""

from __future__ import annotations

__all__ = ["fetch_github_metadata"]

import os
from functools import lru_cache
from typing import Any

from feu.utils.http import fetch_data


@lru_cache
def fetch_github_metadata(owner: str, repo: str) -> dict[str, Any]:
    r"""Get the GitHub repo metadata.

    The metadata is read from GitHub API.

    Args:
        owner: The owner of the repo.
        repo: The repo name.

    Returns:
        The repo metadata.

    Example usage:

    ```pycon

    >>> from feu.repo import fetch_github_metadata
    >>> metadata = fetch_github_metadata(owner="durandtibo", repo="feu")  # doctest: +SKIP

    ```
    """
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"https://api.github.com/repos/{owner}/{repo}"
    return fetch_data(url=url, headers=headers)
