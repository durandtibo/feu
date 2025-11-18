r"""Contain GitHub utility functions."""

from __future__ import annotations

__all__ = ["get_github_metadata"]

from functools import lru_cache

from feu.imports import check_requests, is_requests_available

if is_requests_available():  # pragma: no cover
    import requests


@lru_cache
def get_github_metadata(owner: str, repo: str) -> dict:
    r"""Get the GitHub repo metadata.

    The metadata is read from GitHub API.

    Args:
        owner: The owner of the repo.
        repo: The repo name.

    Returns:
        The repo metadata.

    Example usage:

    ```pycon

    >>> from feu.repo import get_github_metadata
    >>> metadata = get_github_metadata(owner="durandtibo", repo="feu")  # doctest: +SKIP

    ```
    """
    check_requests()
    return requests.get(url=f"https://api.github.com/repos/{owner}/{repo}", timeout=10).json()
