from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from feu.compat.discoverers import JaxCompatDiscoverer
from feu.compat.registry import VersionRange
from feu.compat.target import Target

if TYPE_CHECKING:
    from collections.abc import Callable

MODULE = "feu.compat.discoverers.jax"


def test_jax_compat_discoverer_repr() -> None:
    assert repr(JaxCompatDiscoverer()) == "JaxCompatDiscoverer()"


def _fetch(jax_wheels: dict, jaxlib_wheels: dict) -> Callable[[str], dict]:
    def fetch(pkg_name: str) -> dict:
        return jax_wheels if pkg_name == "jax" else jaxlib_wheels

    return fetch


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch(
        jax_wheels={
            "0.4.30": ("jax-0.4.30-py3-none-any.whl",),
        },
        jaxlib_wheels={
            "0.4.30": ("jaxlib-0.4.30-cp311-cp311-manylinux2014_x86_64.whl",),
        },
    ),
)
def test_discover_matches_jaxlib_wheel() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = JaxCompatDiscoverer().discover("jax", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("0.4.30", None)]}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch(
        jax_wheels={
            "0.4.30": ("jax-0.4.30-py3-none-any.whl",),
        },
        jaxlib_wheels={
            "0.4.30": ("jaxlib-0.4.30-cp311-cp311-manylinux2014_x86_64.whl",),
        },
    ),
)
def test_discover_no_matching_jaxlib_platform() -> None:
    windows_311 = Target(python_version="3.11", os="windows", arch="x86_64")
    compat = JaxCompatDiscoverer().discover("jax", targets=(windows_311,))
    assert compat == {windows_311: []}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch(
        jax_wheels={
            "0.4.30": ("jax-0.4.30-py3-none-any.whl",),
            "0.4.31": ("jax-0.4.31-py3-none-any.whl",),
        },
        jaxlib_wheels={
            "0.4.30": ("jaxlib-0.4.30-cp311-cp311-manylinux2014_x86_64.whl",),
            # jaxlib 0.4.31 dropped the linux x86_64 build for this Python version.
            "0.4.31": ("jaxlib-0.4.31-cp311-cp311-macosx_11_0_arm64.whl",),
        },
    ),
)
def test_discover_upper_bound_from_jaxlib() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    macos_311 = Target(python_version="3.11", os="macos", arch="arm64")
    compat = JaxCompatDiscoverer().discover("jax", targets=(linux_311, macos_311))
    assert compat == {
        linux_311: [VersionRange("0.4.30", "0.4.30")],
        macos_311: [VersionRange("0.4.31", None)],
    }


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    _fetch(
        jax_wheels={"0.4.30": ("jax-0.4.30-py3-none-any.whl",)},
        jaxlib_wheels={},
    ),
)
def test_discover_no_jaxlib_release() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = JaxCompatDiscoverer().discover("jax", targets=(linux_311,))
    assert compat == {linux_311: []}


@patch(f"{MODULE}.fetch_pypi_wheel_filenames", _fetch(jax_wheels={}, jaxlib_wheels={}))
def test_discover_empty() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = JaxCompatDiscoverer().discover("jax", targets=(linux_311,))
    assert compat == {linux_311: []}
