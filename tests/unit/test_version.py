from packaging.version import Version

from feu import get_package_version

#########################################
#     Tests for get_package_version     #
#########################################


def test_get_package_version() -> None:
    assert isinstance(get_package_version("pytest"), Version)


def test_get_package_version_missing() -> None:
    assert get_package_version("missing") is None
