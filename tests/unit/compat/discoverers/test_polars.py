from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from feu.compat.discoverers import PolarsCompatDiscoverer
from feu.compat.registry import VersionRange
from feu.compat.target import Target

if TYPE_CHECKING:
    from collections.abc import Callable

MODULE = "feu.compat.discoverers.polars"


def test_polars_compat_discoverer_repr() -> None:
    assert repr(PolarsCompatDiscoverer()) == "PolarsCompatDiscoverer()"


def _fetch_wheels(polars_wheels: dict, runtime_wheels: dict) -> Callable[[str], dict]:
    def fetch(pkg_name: str) -> dict:
        return polars_wheels if pkg_name == "polars" else runtime_wheels

    return fetch


def _fetch_pin(pins: dict) -> Callable[[str, str, str], str | None]:
    def fetch(_pkg_name: str, version: str, _dependency: str) -> str | None:
        return pins.get(version)

    return fetch


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        polars_wheels={
            "0.13.4": ("polars-0.13.4-cp36-abi3-manylinux_2_12_x86_64.whl",),
        },
        runtime_wheels={},
    ),
)
def test_discover_matches_platform_wheel_directly() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = PolarsCompatDiscoverer().discover("polars", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("0.13.4", None)]}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        polars_wheels={
            "0.13.4": ("polars-0.13.4-cp36-abi3-manylinux_2_12_x86_64.whl",),
        },
        runtime_wheels={},
    ),
)
def test_discover_no_matching_platform() -> None:
    windows_311 = Target(python_version="3.11", os="windows", arch="x86_64")
    compat = PolarsCompatDiscoverer().discover("polars", targets=(windows_311,))
    assert compat == {windows_311: []}


@patch(f"{MODULE}.fetch_pypi_pinned_dependency_version", _fetch_pin({"1.36.1": "1.36.1"}))
@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        polars_wheels={"1.36.1": ("polars-1.36.1-py3-none-any.whl",)},
        runtime_wheels={
            "1.36.1": (
                "polars_runtime_32-1.36.1-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            ),
        },
    ),
)
def test_discover_matches_pinned_runtime_wheel() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = PolarsCompatDiscoverer().discover("polars", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("1.36.1", None)]}


@patch(f"{MODULE}.fetch_pypi_pinned_dependency_version", _fetch_pin({"1.36.1": "1.36.1"}))
@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        polars_wheels={"1.36.1": ("polars-1.36.1-py3-none-any.whl",)},
        runtime_wheels={
            "1.36.1": (
                "polars_runtime_32-1.36.1-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            ),
        },
    ),
)
def test_discover_no_matching_runtime_platform() -> None:
    windows_arm64 = Target(python_version="3.11", os="windows", arch="arm64")
    compat = PolarsCompatDiscoverer().discover("polars", targets=(windows_arm64,))
    assert compat == {windows_arm64: []}


@patch(f"{MODULE}.fetch_pypi_pinned_dependency_version", _fetch_pin({}))
@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        polars_wheels={"1.36.1": ("polars-1.36.1-py3-none-any.whl",)},
        runtime_wheels={},
    ),
)
def test_discover_no_pin_found() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = PolarsCompatDiscoverer().discover("polars", targets=(linux_311,))
    assert compat == {linux_311: []}


@patch(f"{MODULE}.fetch_pypi_pinned_dependency_version", _fetch_pin({"1.36.1": "1.36.1"}))
@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        polars_wheels={
            "0.13.4": ("polars-0.13.4-cp36-abi3-manylinux_2_12_x86_64.whl",),
            "1.36.1": ("polars-1.36.1-py3-none-any.whl",),
        },
        runtime_wheels={
            "1.36.1": (
                "polars_runtime_32-1.36.1-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            ),
        },
    ),
)
def test_discover_mixes_platform_and_pure_python_ranges() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = PolarsCompatDiscoverer().discover("polars", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("0.13.4", None)]}


@patch(
    f"{MODULE}.fetch_pypi_pinned_dependency_version",
    _fetch_pin({"1.36.1": "1.36.1", "1.37.0": "1.37.0"}),
)
@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        polars_wheels={
            "1.36.1": ("polars-1.36.1-py3-none-any.whl",),
            "1.37.0": ("polars-1.37.0-py3-none-any.whl",),
        },
        runtime_wheels={
            "1.36.1": (
                "polars_runtime_32-1.36.1-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            ),
            "1.37.0": (
                "polars_runtime_32-1.37.0-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            ),
        },
    ),
)
def test_discover_reuses_cached_runtime_tags_across_pure_python_versions() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = PolarsCompatDiscoverer().discover("polars", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("1.36.1", None)]}


@patch(f"{MODULE}.fetch_pypi_pinned_dependency_version", _fetch_pin({}))
@patch(f"{MODULE}.fetch_pypi_wheel_filenames", _fetch_wheels(polars_wheels={}, runtime_wheels={}))
def test_discover_no_versions() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = PolarsCompatDiscoverer().discover("polars", targets=(linux_311,))
    assert compat == {linux_311: []}
