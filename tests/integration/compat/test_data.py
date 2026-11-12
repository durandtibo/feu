from __future__ import annotations

import pytest

from feu.compat import (
    Target,
    UnsupportedVersionError,
    find_closest_version,
    get_default_compat_registry,
    is_valid_version,
)
from feu.testing import requests_available

###################################################
#     Tests for the shipped compatibility data    #
###################################################


def test_find_closest_version_numpy_python_39_full_target() -> None:
    """Test that a too recent numpy is clamped for a fully specified
    target."""
    target = Target(python_version="3.9", os="linux", arch="x86_64")
    assert find_closest_version("numpy", "99.0.0", target) == "2.0.2"


def test_find_closest_version_numpy_python_39_platform_unspecified() -> None:
    """Test that a too recent numpy is clamped when the platform is not
    specified."""
    assert find_closest_version("numpy", "99.0.0", Target(python_version="3.9")) == "2.0.2"


def test_find_closest_version_numpy_python_311_old_version() -> None:
    """Test that a too old numpy is raised to the oldest supported
    version when the platform is not specified."""
    assert find_closest_version("numpy", "1.0.0", Target(python_version="3.11")) == "1.23.2"


def test_is_valid_version_numpy_python_39_platform_unspecified() -> None:
    """Test that a numpy version too recent for Python 3.9 is invalid
    when the platform is not specified."""
    assert not is_valid_version("numpy", "2.3.0", Target(python_version="3.9"))


def test_default_registry_has_numpy() -> None:
    """Test that the default registry knows numpy."""
    assert get_default_compat_registry().has_package("numpy")


def test_default_registry_does_not_have_unknown_package() -> None:
    """Test that the default registry does not know an unknown
    package."""
    assert not get_default_compat_registry().has_package("not-a-real-package")


#######################################################
#     Tests for version requests on the shipped data  #
#######################################################

PY314 = Target(python_version="3.14", os="linux", arch="x86_64")
PY39 = Target(python_version="3.9", os="linux", arch="x86_64")


@pytest.mark.parametrize("request_", ["", None])
def test_is_valid_version_numpy_python_314_latest_true(request_: str | None) -> None:
    """Test that the latest version is valid on the shipped data,
    without any download."""
    assert is_valid_version("numpy", request_, PY314)


@requests_available
@pytest.mark.parametrize("request_", ["2.4.*", "2.*"])
def test_is_valid_version_numpy_python_314_wildcard_true(request_: str) -> None:
    """Test that a wildcard is matched against the releases downloaded
    from PyPI."""
    assert is_valid_version("numpy", request_, PY314)


@requests_available
def test_is_valid_version_numpy_python_314_old_wildcard_false() -> None:
    """Test that a wildcard without any compatible release is
    invalid."""
    assert not is_valid_version("numpy", "1.24.*", PY314)


@requests_available
@pytest.mark.parametrize("request_", ["2.*", ""])
def test_find_closest_version_numpy_python_314_open_request_is_returned(request_: str) -> None:
    """Test that an open-ended range returns the request itself."""
    assert find_closest_version("numpy", request_, PY314) == request_


@requests_available
def test_find_closest_version_numpy_python_39_closed_wildcard_is_resolved() -> None:
    """Test that a closed range resolves a wildcard to a concrete
    version."""
    assert find_closest_version("numpy", "1.*", PY39) == "1.26.4"


@requests_available
def test_find_closest_version_numpy_python_314_unmatched_wildcard_raises() -> None:
    """Test that a wildcard without any compatible release raises."""
    with pytest.raises(UnsupportedVersionError, match=r"matches '1\.24\.\*'"):
        find_closest_version("numpy", "1.24.*", PY314)


@requests_available
def test_get_compatible_versions_numpy_python_39_wildcard() -> None:
    """Test the compatible versions of a wildcard on the shipped
    data."""
    assert get_default_compat_registry().get_compatible_versions("numpy", PY39, "1.26.*") == [
        "1.26.0",
        "1.26.1",
        "1.26.2",
        "1.26.3",
        "1.26.4",
    ]


def test_is_valid_version_unknown_package_wildcard_false() -> None:
    """Test that a wildcard on a package without data is invalid."""
    assert not is_valid_version("not-a-real-package", "2.*", PY39)


@requests_available
def test_get_compatible_versions_numpy_is_up_to_date() -> None:
    """Test that the versions come from PyPI, not from the shipped
    data."""
    versions = get_default_compat_registry().get_compatible_versions("numpy", PY39)
    assert versions[-1] == "2.0.2"
