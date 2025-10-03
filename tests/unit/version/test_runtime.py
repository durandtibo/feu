from __future__ import annotations

import pytest
from packaging.version import Version

from feu.versio import get_package_version, get_python_major_minor


@pytest.fixture(autouse=True)
def _reset() -> None:
    get_python_major_minor.cache_clear()


#########################################
#     Tests for get_package_version     #
#########################################


@pytest.mark.parametrize("package", ["pytest", "ruff"])
def test_get_package_version(package: str) -> None:
    assert isinstance(get_package_version(package), Version)


def test_get_package_version_missing() -> None:
    assert get_package_version("missing") is None


############################################
#     Tests for get_python_major_minor     #
############################################


def test_get_python_major_minor() -> None:
    isinstance(get_python_major_minor(), str)
