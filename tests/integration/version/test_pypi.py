from __future__ import annotations

import pytest

from feu.testing import requests_available, requests_not_available
from feu.version import fetch_pypi_versions


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    fetch_pypi_versions.cache_clear()


#########################################
#     Tests for fetch_pypi_versions     #
#########################################


@requests_available
def test_fetch_pypi_versions_requests() -> None:
    versions = fetch_pypi_versions("requests")
    assert isinstance(versions, tuple)
    assert len(versions) >= 157
    assert "2.32.5" in versions


@requests_available
def test_fetch_pypi_versions_torch() -> None:
    versions = fetch_pypi_versions("torch")
    assert isinstance(versions, tuple)
    assert len(versions) >= 42
    assert "2.8.0" in versions


@requests_not_available
def test_fetch_pypi_versions_no_requests() -> None:
    with pytest.raises(RuntimeError, match=r"'requests' package is required but not installed."):
        fetch_pypi_versions("my_package")
