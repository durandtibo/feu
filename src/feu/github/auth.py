r"""Contain utilities to authenticate against the GitHub API."""

from __future__ import annotations

__all__ = ["build_github_headers"]

import os


def build_github_headers() -> dict[str, str]:
    r"""Build the HTTP headers to call the GitHub REST API.

    The ``GITHUB_TOKEN`` environment variable is used to authenticate the
    request if it is set.

    Returns:
        The HTTP headers to use to call the GitHub API.

    Example:
        ```pycon
        >>> from feu.github import build_github_headers
        >>> headers = build_github_headers()

        ```
    """
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers
