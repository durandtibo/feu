from __future__ import annotations

from unittest.mock import patch

from feu.compat.discoverers import DuckdbCompatDiscoverer
from feu.compat.registry import VersionRange
from feu.compat.target import Target

MODULE = "feu.compat.discoverers.duckdb"


def test_duckdb_compat_discoverer_repr() -> None:
    assert repr(DuckdbCompatDiscoverer()) == "DuckdbCompatDiscoverer()"


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "0.0.0": ("duckdb-0.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "1.0.0": ("duckdb-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
    },
)
def test_discover_ignores_0_0_0_version() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = DuckdbCompatDiscoverer().discover("duckdb", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("1.0.0", None)]}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {"0.0.0": ("duckdb-0.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",)},
)
def test_discover_only_0_0_0_version() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = DuckdbCompatDiscoverer().discover("duckdb", targets=(linux_311,))
    assert compat == {linux_311: []}


@patch(f"{MODULE}.fetch_pypi_wheel_filenames", lambda *_args: {})
def test_discover_empty() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = DuckdbCompatDiscoverer().discover("duckdb", targets=(linux_311,))
    assert compat == {linux_311: []}
