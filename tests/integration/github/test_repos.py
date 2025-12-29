from __future__ import annotations

import pytest

from feu.github import fetch_github_repos
from feu.testing import requests_available, requests_not_available


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    fetch_github_repos.cache_clear()


########################################
#     Tests for fetch_github_repos     #
########################################


@requests_available
def test_fetch_github_repos() -> None:
    repos = fetch_github_repos(owner="durandtibo")
    assert isinstance(repos, tuple)
    assert len(repos) > 0
    assert isinstance(repos[0], dict)


@requests_not_available
def test_fetch_github_repos_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_github_repos(owner="durandtibo")
