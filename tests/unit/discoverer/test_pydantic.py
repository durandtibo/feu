from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from feu.compat.registry import VersionRange
from feu.compat.target import Target
from feu.discoverer import PydanticCompatDiscoverer

if TYPE_CHECKING:
    from collections.abc import Callable

MODULE = "feu.discoverer.pydantic"


def test_pydantic_compat_discoverer_repr() -> None:
    assert repr(PydanticCompatDiscoverer()) == "PydanticCompatDiscoverer()"


def _fetch_wheels(pydantic_wheels: dict, core_wheels: dict) -> Callable[[str], dict]:
    def fetch(pkg_name: str) -> dict:
        return pydantic_wheels if pkg_name == "pydantic" else core_wheels

    return fetch


def _fetch_pin(pins: dict) -> Callable[[str, str, str], str | None]:
    def fetch(_pkg_name: str, version: str, _dependency: str) -> str | None:
        return pins.get(version)

    return fetch


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        pydantic_wheels={
            "1.10.13": (
                "pydantic-1.10.13-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            ),
        },
        core_wheels={},
    ),
)
def test_discover_v1_matches_platform_wheel_directly() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = PydanticCompatDiscoverer().discover("pydantic", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("1.10.13", None)]}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        pydantic_wheels={
            "1.10.13": (
                "pydantic-1.10.13-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            ),
        },
        core_wheels={},
    ),
)
def test_discover_v1_no_matching_platform() -> None:
    windows_311 = Target(python_version="3.11", os="windows", arch="x86_64")
    compat = PydanticCompatDiscoverer().discover("pydantic", targets=(windows_311,))
    assert compat == {windows_311: []}


@patch(f"{MODULE}.fetch_pypi_pinned_dependency_version", _fetch_pin({"2.9.0": "2.23.2"}))
@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        pydantic_wheels={"2.9.0": ("pydantic-2.9.0-py3-none-any.whl",)},
        core_wheels={
            "2.23.2": (
                "pydantic_core-2.23.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            ),
        },
    ),
)
def test_discover_v2_matches_pinned_core_wheel() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = PydanticCompatDiscoverer().discover("pydantic", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("2.9.0", None)]}


@patch(f"{MODULE}.fetch_pypi_pinned_dependency_version", _fetch_pin({"2.9.0": "2.23.2"}))
@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        pydantic_wheels={"2.9.0": ("pydantic-2.9.0-py3-none-any.whl",)},
        core_wheels={
            "2.23.2": (
                "pydantic_core-2.23.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            ),
        },
    ),
)
def test_discover_v2_no_matching_core_platform() -> None:
    windows_311 = Target(python_version="3.11", os="windows", arch="x86_64")
    compat = PydanticCompatDiscoverer().discover("pydantic", targets=(windows_311,))
    assert compat == {windows_311: []}


@patch(f"{MODULE}.fetch_pypi_pinned_dependency_version", _fetch_pin({}))
@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        pydantic_wheels={"2.9.0": ("pydantic-2.9.0-py3-none-any.whl",)},
        core_wheels={},
    ),
)
def test_discover_v2_no_pin_found() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = PydanticCompatDiscoverer().discover("pydantic", targets=(linux_311,))
    assert compat == {linux_311: []}


@patch(f"{MODULE}.fetch_pypi_pinned_dependency_version", _fetch_pin({"2.9.0": "2.23.2"}))
@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        pydantic_wheels={
            "1.10.13": (
                "pydantic-1.10.13-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            ),
            "2.9.0": ("pydantic-2.9.0-py3-none-any.whl",),
        },
        core_wheels={
            "2.23.2": (
                "pydantic_core-2.23.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            ),
        },
    ),
)
def test_discover_mixes_v1_and_v2_ranges() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = PydanticCompatDiscoverer().discover("pydantic", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("1.10.13", None)]}


@patch(
    f"{MODULE}.fetch_pypi_pinned_dependency_version",
    _fetch_pin({"2.8.0": "2.20.0", "2.9.0": "2.23.2"}),
)
@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch_wheels(
        pydantic_wheels={
            "2.8.0": ("pydantic-2.8.0-py3-none-any.whl",),
            "2.9.0": ("pydantic-2.9.0-py3-none-any.whl",),
        },
        core_wheels={
            "2.20.0": (
                "pydantic_core-2.20.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            ),
            "2.23.2": (
                "pydantic_core-2.23.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            ),
        },
    ),
)
def test_discover_multiple_v2_versions_reuse_fetched_core_wheels() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = PydanticCompatDiscoverer().discover("pydantic", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("2.8.0", None)]}


@patch(f"{MODULE}.fetch_pypi_pinned_dependency_version", _fetch_pin({}))
@patch(f"{MODULE}.fetch_pypi_wheel_filenames", _fetch_wheels(pydantic_wheels={}, core_wheels={}))
def test_discover_empty() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = PydanticCompatDiscoverer().discover("pydantic", targets=(linux_311,))
    assert compat == {linux_311: []}
