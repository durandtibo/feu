from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from packaging.version import Version

from feu.version import get_package_version

#########################################
#     Tests for get_package_version     #
#########################################


@pytest.mark.parametrize("package", ["pytest", "ruff"])
def test_get_package_version(package: str) -> None:
    assert isinstance(get_package_version(package), Version)


def test_get_package_version_missing() -> None:
    assert get_package_version("missing") is None


def test_get_package_version_value() -> None:
    with patch("feu.version.runtime.version", Mock(return_value="1.2.3")):
        assert get_package_version("my-package") == Version("1.2.3")


def test_get_package_version_not_pep440_is_none() -> None:
    # Regression test: an installed distribution whose version is not PEP 440 used to raise
    # InvalidVersion.
    with patch("feu.version.runtime.version", Mock(return_value="not-a-version")):
        assert get_package_version("my-package") is None
