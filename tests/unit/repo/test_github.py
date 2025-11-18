from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from feu.repo import get_github_metadata
from feu.testing import requests_available


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    get_github_metadata.cache_clear()


#########################################
#     Tests for get_github_metadata     #
#########################################


@requests_available
def test_get_github_metadata() -> None:
    mock = Mock(
        return_value=Mock(json=Mock(return_value={"name": "feu", "owner": {"login": "durandtibo"}}))
    )
    with patch("feu.version.pypi.requests.get", mock):
        assert get_github_metadata(owner="durandtibo", repo="feu") == {
            "name": "feu",
            "owner": {"login": "durandtibo"},
        }
        mock.assert_called_once_with(url="https://api.github.com/repos/durandtibo/feu", timeout=10)


@patch("feu.imports.is_requests_available", lambda: False)
def test_get_github_metadata_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        get_github_metadata(owner="my_name", repo="my_package")
