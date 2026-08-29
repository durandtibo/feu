from __future__ import annotations

from feu.compat.interface import find_closest_version, is_valid_version
from feu.compat.target import Target
from feu.testing import requests_available

# NOTE: these tests hit the real PyPI index through the discoverer machinery.
# Bounds are asserted rather than exact snapshots, for the same reason as
# tests/integration/compat/test_matrix.py: upstream projects keep publishing
# new releases that would otherwise silently break these tests.


####################################################
#     Tests for find_closest_version/is_valid_version     #
####################################################


@requests_available
def test_find_closest_version_valid_version_is_unchanged() -> None:
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    assert find_closest_version(pkg_name="numpy", pkg_version="2.0.2", target=target) == "2.0.2"


@requests_available
def test_find_closest_version_unconfigured_package_is_unchanged() -> None:
    # feu has no registered compatibility discoverer for itself, so the
    # requested version is returned unchanged regardless of the target.
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    assert find_closest_version(pkg_name="feu", pkg_version="0.1.0", target=target) == "0.1.0"


@requests_available
def test_is_valid_version_true_for_supported_target() -> None:
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    assert is_valid_version(pkg_name="numpy", pkg_version="2.0.2", target=target)


@requests_available
def test_is_valid_version_false_for_unsupported_target() -> None:
    # numpy 1.10.4 predates cp313 wheels by several years.
    target = Target(python_version="3.13", os="linux", arch="x86_64")
    assert not is_valid_version(pkg_name="numpy", pkg_version="1.10.4", target=target)


@requests_available
def test_is_valid_version_true_for_unconfigured_package() -> None:
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    assert is_valid_version(pkg_name="feu", pkg_version="0.1.0", target=target)
