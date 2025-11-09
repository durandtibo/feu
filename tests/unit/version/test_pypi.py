from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from feu.testing import requests_available
from feu.version import get_pypi_versions


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    get_pypi_versions.cache_clear()


#######################################
#     Tests for get_pypi_versions     #
#######################################


@requests_available
def test_get_pypi_versions() -> None:
    mock = Mock(
        return_value=Mock(
            json=Mock(return_value={"releases": {"1.2.0": None, "1.2.3": None, "2.0.0": None}})
        )
    )
    with patch("feu.version.pypi.requests.get", mock):
        assert get_pypi_versions("my_package") == ("1.2.0", "1.2.3", "2.0.0")
        mock.assert_called_once_with(url="https://pypi.org/pypi/my_package/json", timeout=10)


@requests_available
def test_get_pypi_versions_reverse() -> None:
    mock = Mock(
        return_value=Mock(
            json=Mock(return_value={"releases": {"1.2.0": None, "1.2.3": None, "2.0.0": None}})
        )
    )
    with patch("feu.version.pypi.requests.get", mock):
        assert get_pypi_versions("my_package", reverse=True) == ("2.0.0", "1.2.3", "1.2.0")
        mock.assert_called_once_with(url="https://pypi.org/pypi/my_package/json", timeout=10)


@patch("feu.imports.is_requests_available", lambda: False)
def test_get_pypi_versions_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        get_pypi_versions("my_package")
