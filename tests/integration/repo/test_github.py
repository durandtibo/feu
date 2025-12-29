from __future__ import annotations

import pytest

from feu.repo import fetch_github_metadata
from feu.testing import requests_available, requests_not_available


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    fetch_github_metadata.cache_clear()


###########################################
#     Tests for fetch_github_metadata     #
###########################################


@requests_available
def test_fetch_github_metadata_feu() -> None:
    metadata = fetch_github_metadata(owner="durandtibo", repo="feu")
    assert isinstance(metadata, dict)
    assert metadata["name"] == "feu"
    assert metadata["owner"]["login"] == "durandtibo"


@requests_available
def test_fetch_github_metadata_pytorch() -> None:
    metadata = fetch_github_metadata(owner="pytorch", repo="pytorch")
    assert isinstance(metadata, dict)
    assert metadata["name"] == "pytorch"
    assert metadata["owner"]["login"] == "pytorch"


@requests_not_available
def test_fetch_github_metadata_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_github_metadata(owner="durandtibo", repo="feu")
