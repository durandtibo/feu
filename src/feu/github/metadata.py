r"""Contain GitHub utility functions to get information about a single
repository."""

from __future__ import annotations

__all__ = ["fetch_github_metadata"]

import logging
from functools import lru_cache
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from feu.github.auth import build_github_headers
from feu.utils.http import fetch_data

if TYPE_CHECKING:
    from collections.abc import Mapping

logger: logging.Logger = logging.getLogger(__name__)


@lru_cache
def fetch_github_metadata(owner: str, repo: str) -> Mapping[str, Any]:
    r"""Get the GitHub repo metadata.

    The metadata is read from the GitHub API. The request is
    authenticated if the ``GITHUB_TOKEN`` environment variable is set
    (see ``build_github_headers``). The result is cached and
    read-only, so a caller cannot corrupt the cache.

    Args:
        owner: The owner of the repo.
        repo: The repo name.

    Returns:
        The repo metadata, as returned by the GitHub API, as a
            read-only mapping.

    Raises:
        RuntimeError: If the request fails or if ``requests`` is not
            installed.

    Example:
        ```pycon
        >>> from feu.github import fetch_github_metadata
        >>> metadata = fetch_github_metadata(owner="durandtibo", repo="feu")  # doctest: +SKIP

        ```
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    return MappingProxyType(fetch_data(url=url, headers=build_github_headers()))
