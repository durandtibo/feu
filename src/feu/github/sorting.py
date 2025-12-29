r"""Contain GitHub utility functions to sort repositories."""

from __future__ import annotations

__all__ = ["sort_repos_by_key"]

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

logger: logging.Logger = logging.getLogger(__name__)


def sort_repos_by_key(
    repos: Sequence[dict[str, Any]], *, key: str, reverse: bool = False
) -> list[dict[str, Any]]:
    """Sort repositories by a given key.

    Repositories without the key are placed at the end in their
    original order.

    Args:
        repos: List of repository dictionaries from GitHub API.
        key: Key to sort.
        reverse: If True, sort in descending order. Defaults to False.

    Returns:
        List of repository dictionaries sorted in ascending order
        (or descending if reverse=True). Repositories without the key appear
        at the end in their original order.

    Examples:
        ```pycon
        >>> from feu.github import sort_repos_by_key
        >>> repos = [{"name": "zoo"}, {"name": "alpha"}, {"id": 1}]
        >>> sort_repos_by_key(repos, key="name")
        [{'name': 'alpha'}, {'name': 'zoo'}, {'id': 1}]
        >>> sort_repos_by_key(repos, key="name", reverse=True)
        [{'name': 'zoo'}, {'name': 'alpha'}, {'id': 1}]

        ```
    """
    repos_with_name = [repo for repo in repos if key in repo]
    repos_without_name = [repo for repo in repos if key not in repo]

    sorted_repos = sorted(repos_with_name, key=lambda x: x[key], reverse=reverse)
    return sorted_repos + repos_without_name
