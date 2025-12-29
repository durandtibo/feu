r"""Contain GitHub utility functions to sort repositories."""

from __future__ import annotations

__all__ = ["sort_repos_by_full_name", "sort_repos_by_name"]

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

logger: logging.Logger = logging.getLogger(__name__)


def sort_repos_by_name(
    repos: Sequence[dict[str, Any]], *, reverse: bool = False
) -> list[dict[str, Any]]:
    r"""Sort repositories by name.

    Args:
        repos: List of repository dictionaries from GitHub API.
        reverse: If True, sort in descending order. Defaults to False.

    Returns:
        List of repository dictionaries sorted by name in ascending order
            (or descending if reverse=True).

    Examples:
        ```pycon
        >>> from feu.github import sort_repos_by_name
        >>> repos = [{"name": "zoo"}, {"name": "alpha"}]
        >>> sort_repos_by_name(repos)
        [{'name': 'alpha'}, {'name': 'zoo'}]
        >>> sort_repos_by_name(repos, reverse=True)
        [{'name': 'zoo'}, {'name': 'alpha'}]

        ```
    """
    return sorted(repos, key=lambda x: x["name"], reverse=reverse)


def sort_repos_by_full_name(
    repos: Sequence[dict[str, Any]], *, reverse: bool = False
) -> list[dict[str, Any]]:
    r"""Sort repositories by full name.

    Args:
        repos: List of repository dictionaries from GitHub API.
        reverse: If True, sort in descending order. Defaults to False.

    Returns:
        List of repository dictionaries sorted by full name in ascending order
            (or descending if reverse=True).

    Examples:
        ```pycon
        >>> from feu.github import sort_repos_by_name
        >>> repos = [{"full_name": "owner/zoo"}, {"full_name": "owner/alpha"}]
        >>> sort_repos_by_name(repos)
        [{'name': 'owner/alpha'}, {'name': 'owner/zoo'}]
        >>> sort_repos_by_name(repos, reverse=True)
        [{'name': 'owner/zoo'}, {'name': 'owner/alpha'}]

        ```
    """
    return sorted(repos, key=lambda x: x["full_name"], reverse=reverse)
