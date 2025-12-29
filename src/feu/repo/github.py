r"""Contain GitHub utility functions."""

from __future__ import annotations

__all__ = ["fetch_github_metadata"]

import logging
import os
from functools import lru_cache
from typing import TYPE_CHECKING, Any

from feu.utils.http import fetch_data, fetch_response

if TYPE_CHECKING:
    from collections.abc import Sequence

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


@lru_cache
def fetch_github_repos(owner: str) -> tuple[dict[str, Any], ...]:
    r"""Get the GitHub repo metadata.

    The metadata is read from GitHub API.

    Args:
        owner: The owner of the repo.

    Returns:
        The repo metadata.

    Example:
        ```pycon
        >>> from feu.repo import fetch_github_repos
        >>> repos = fetch_github_repos(owner="durandtibo")  # doctest: +SKIP

        ```
    """
    repos = []
    url = f"https://api.github.com/users/{owner}/repos"
    params = {"per_page": 100, "type": "all"}

    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    while url:
        response = fetch_response(url=url, headers=headers, params=params)

        if response.status_code != 200:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.json())
            break

        page_repos = response.json()
        repos.extend(page_repos)

        # Get next page URL from Link header
        url = None
        params = None  # Params are included in the Link URL
        if "Link" in response.headers:
            links = response.headers["Link"]
            # Parse the Link header to find 'next' relation
            for link in links.split(","):
                if 'rel="next"' in link:
                    url = link[link.find("<") + 1 : link.find(">")]
                    break

    return tuple(repos)


def display_repos_summary(repos: Sequence[dict[str, Any]]) -> None:
    r"""Display repository information in a readable format.

    Args:
        repos: List of repository dictionaries from GitHub API.

    Example:
        ```pycon
        >>> from feu.repo import fetch_github_repos, display_repos_summary
        >>> repos = fetch_github_repos(owner="durandtibo")  # doctest: +SKIP
        >>> display_repos_summary(repos)

        ```
    """
    logger.info(f"Total repositories: {len(repos)}\n")

    for i, repo in enumerate(repos, 1):
        logger.info(f"{i}. {repo['name']}")
        logger.info(f"   URL: {repo['html_url']}")
        logger.info(f"   Description: {repo['description'] or 'No description'}")
        logger.info(f"   Stars: {repo['stargazers_count']:,} | Forks: {repo['forks_count']:,}")
        logger.info(f"   Language: {repo['language'] or 'Not specified'}")
        logger.info(f"   Private: {repo['private']}\n")
