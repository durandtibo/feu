r"""Contain GitHub utility functions to get information about
repositories."""

from __future__ import annotations

__all__ = ["display_repos_summary", "fetch_github_repos"]

import logging
from functools import lru_cache
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from feu.github.auth import build_github_headers
from feu.utils.http import fetch_response

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

logger: logging.Logger = logging.getLogger(__name__)


@lru_cache
def fetch_github_repos(owner: str) -> tuple[Mapping[str, Any], ...]:
    r"""Get the metadata of all the repositories of a GitHub user or
    organization.

    The metadata is read from the GitHub API, following the
    pagination. The request is authenticated if the ``GITHUB_TOKEN``
    environment variable is set (see ``build_github_headers``). The
    result is cached and read-only: a tuple of read-only mappings.

    Args:
        owner: The owner of the repos i.e. the user or organization
            name.

    Returns:
        The metadata of each repository, as returned by the GitHub
            API, as read-only mappings.

    Raises:
        RuntimeError: If a request fails or if ``requests`` is not
            installed.

    Example:
        ```pycon
        >>> from feu.github import fetch_github_repos
        >>> repos = fetch_github_repos(owner="durandtibo")  # doctest: +SKIP

        ```
    """
    repos = []
    url = f"https://api.github.com/users/{owner}/repos"
    params = {"per_page": 100, "type": "all"}

    headers = build_github_headers()

    while url:
        response = fetch_response(url=url, headers=headers, params=params)
        page_repos = response.json()
        repos.extend(page_repos)

        # The Link header gives the URL of the next page, with the parameters.
        url = response.links.get("next", {}).get("url")
        params = None
    return tuple(MappingProxyType(repo) for repo in repos)


def display_repos_summary(repos: Sequence[Mapping[str, Any]]) -> None:
    r"""Display repository information in a readable format.

    The summary is logged at the ``INFO`` level with the logger of this
    module, so it is not visible unless logging is configured.

    Args:
        repos: List of repository dictionaries from GitHub API, as
            returned by ``fetch_github_repos``.

    Example:
        ```pycon
        >>> from feu.github import fetch_github_repos, display_repos_summary
        >>> repos = fetch_github_repos(owner="durandtibo")  # doctest: +SKIP
        >>> display_repos_summary(repos)  # doctest: +SKIP

        ```
    """
    logger.info("Total repositories: %d\n", len(repos))

    for i, repo in enumerate(repos, 1):
        logger.info("%d. %s", i, repo["name"])
        logger.info("   URL: %s", repo["html_url"])
        logger.info("   Description: %s", repo["description"] or "No description")
        logger.info(
            "   Stars: %s | Forks: %s",
            f"{repo['stargazers_count']:,}",
            f"{repo['forks_count']:,}",
        )
        logger.info("   Language: %s", repo["language"] or "Not specified")
        logger.info("   Private: %s\n", repo["private"])
