from __future__ import annotations

from packaging.version import Version

from feu.testing import requests_available
from feu.version import (
    fetch_latest_major_versions,
    fetch_latest_minor_versions,
    fetch_latest_stable_version,
    fetch_latest_version,
    fetch_versions,
)

# NOTE: these tests hit the real PyPI index. Bounds are asserted rather
# than exact snapshots of version lists, because upstream projects keep
# publishing new releases (e.g. a new torch/requests patch release, or a
# new gravitorch/gtaccelerate release) that would otherwise silently
# break these tests without any change to this codebase.

####################################
#     Tests for fetch_versions     #
####################################


@requests_available
def test_fetch_versions_requests() -> None:
    versions = fetch_versions("requests", lower="2.25", upper="2.30")
    assert list(versions) == sorted(versions, key=Version)
    assert all(Version("2.25") <= Version(v) < Version("2.30") for v in versions)
    assert {"2.25.0", "2.28.2"}.issubset(versions)


@requests_available
def test_fetch_versions_torch() -> None:
    versions = fetch_versions("torch", lower="2.5", upper="2.9")
    assert list(versions) == sorted(versions, key=Version)
    assert all(Version("2.5") <= Version(v) < Version("2.9") for v in versions)
    assert {"2.5.0", "2.6.0", "2.7.0"}.issubset(versions)


#################################################
#     Tests for fetch_latest_major_versions     #
#################################################


@requests_available
def test_fetch_latest_major_versions_requests() -> None:
    versions = fetch_latest_major_versions("requests", upper="2.30")
    assert list(versions) == sorted(versions, key=Version)
    assert all(Version(v) < Version("2.30") for v in versions)
    assert {"0.14.2", "1.2.3"}.issubset(versions)


@requests_available
def test_fetch_latest_major_versions_torch() -> None:
    versions = fetch_latest_major_versions("torch", upper="2.9")
    assert list(versions) == sorted(versions, key=Version)
    assert all(Version(v) < Version("2.9") for v in versions)
    assert "1.13.1" in versions


#################################################
#     Tests for fetch_latest_minor_versions     #
#################################################


@requests_available
def test_fetch_latest_minor_versions_requests() -> None:
    versions = fetch_latest_minor_versions("requests", lower="2.10", upper="2.30")
    assert list(versions) == sorted(versions, key=Version)
    assert all(Version("2.10") <= Version(v) < Version("2.30") for v in versions)
    assert {"2.10.0", "2.20.1"}.issubset(versions)


@requests_available
def test_fetch_latest_minor_versions_torch() -> None:
    versions = fetch_latest_minor_versions("torch", lower="2.0", upper="2.9")
    assert list(versions) == sorted(versions, key=Version)
    assert all(Version("2.0") <= Version(v) < Version("2.9") for v in versions)
    assert {"2.0.1", "2.5.1"}.issubset(versions)


##########################################
#     Tests for fetch_latest_version     #
##########################################


@requests_available
def test_fetch_latest_version_stable() -> None:
    version = fetch_latest_version("gravitorch")
    assert Version(version) >= Version("0.0.23")


@requests_available
def test_fetch_latest_version_dev() -> None:
    version = fetch_latest_version("gtaccelerate")
    assert Version(version) >= Version("0.0.1a6")


#################################################
#     Tests for fetch_latest_stable_version     #
#################################################


@requests_available
def test_fetch_latest_stable_version() -> None:
    version = fetch_latest_stable_version("gravitorch")
    assert Version(version) >= Version("0.0.23")
    assert not Version(version).is_prerelease
