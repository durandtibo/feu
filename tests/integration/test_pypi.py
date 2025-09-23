from __future__ import annotations

import pytest

from feu.pypi import get_pypi_versions
from feu.testing import requests_available


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    get_pypi_versions.cache_clear()


#######################################
#     Tests for get_pypi_versions     #
#######################################


@requests_available
def test_get_pypi_versions_requests() -> None:
    assert "2.32.5" in set(get_pypi_versions("requests"))


@requests_available
def test_get_pypi_versions_torch() -> None:
    assert "2.8.0" in set(get_pypi_versions("torch"))
