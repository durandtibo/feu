from __future__ import annotations

from feu.compat import Target, find_closest_version, get_default_registry, is_valid_version

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
    assert get_default_registry().has_package("numpy")


def test_default_registry_does_not_have_unknown_package() -> None:
    """Test that the default registry does not know an unknown
    package."""
    assert not get_default_registry().has_package("not-a-real-package")
