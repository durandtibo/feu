r"""Contain GitHub utility functions."""

from __future__ import annotations

__all__ = ["get_github_metadata"]

import os
from functools import lru_cache

from feu.imports import (
    check_requests,
    check_urllib3,
    is_requests_available,
    is_urllib3_available,
)

if is_requests_available():  # pragma: no cover
    import requests
    from requests.adapters import HTTPAdapter

if is_urllib3_available():  # pragma: no cover
    from urllib3.util.retry import Retry


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
    check_urllib3()
    session = requests.Session()

    retry = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)

    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        resp = session.get(url=url, timeout=10, headers=headers)
        resp.raise_for_status()
    except requests.exceptions.Timeout as exc:
        msg = "GitHub API request timed out"
        raise RuntimeError(msg) from exc
    except requests.exceptions.RequestException as exc:
        msg = f"Network or HTTP error: {exc}"
        raise RuntimeError(msg) from exc

    try:
        return resp.json()
    except ValueError as exc:
        msg = "Invalid JSON received from GitHub"
        raise RuntimeError(msg) from exc
