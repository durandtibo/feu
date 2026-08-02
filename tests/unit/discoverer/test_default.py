from __future__ import annotations

from unittest.mock import patch

from feu.compat.registry import VersionRange
from feu.compat.target import Target
from feu.discoverer import CompatDiscoverer

MODULE = "feu.discoverer.default"


def test_compat_discoverer_repr() -> None:
    assert repr(CompatDiscoverer()) == "CompatDiscoverer()"


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "1.1.0": (
            "pkg-1.1.0-cp311-cp311-manylinux_2_17_x86_64.whl",
            "pkg-1.1.0-cp314-cp314t-manylinux_2_17_x86_64.whl",
        ),
        "1.1.0a1": ("pkg-1.1.0a1-cp311-cp311-manylinux_2_17_x86_64.whl",),  # pre-release, ignored
        "not-a-version": ("pkg-bad.whl",),  # invalid, ignored
    },
)
def test_discover_basic() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = CompatDiscoverer().discover("pkg", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("1.0.0", None)]}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "1.1.0": (
            "pkg-1.1.0-cp311-cp311-manylinux_2_17_x86_64.whl",
            "pkg-1.1.0-cp314-cp314t-manylinux_2_17_x86_64.whl",
        ),
    },
)
def test_discover_free_threaded() -> None:
    free_threaded_314 = Target(python_version="3.14", free_threaded=True, os="linux", arch="x86_64")
    compat = CompatDiscoverer().discover("pkg", targets=(free_threaded_314,))
    assert compat == {free_threaded_314: [VersionRange("1.1.0", None)]}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "2.0.0": ("pkg-2.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
    },
)
def test_discover_max_is_last_compatible() -> None:
    macos_arm = Target(python_version="3.11", os="macos", arch="arm64")
    compat = CompatDiscoverer().discover("pkg", targets=(macos_arm,))
    assert compat == {macos_arm: []}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "1.5.0": ("pkg-1.5.0-cp39-cp39-manylinux_2_17_x86_64.whl",),
        "2.0.0": ("pkg-2.0.0-cp39-cp39-manylinux_2_17_x86_64.whl",),
    },
)
def test_discover_upper_bound() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = CompatDiscoverer().discover("pkg", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("1.0.0", "1.0.0")]}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-py3-none-any.whl",),
        "2.0.0": ("pkg-2.0.0-py3-none-any.whl",),
    },
)
@patch(
    f"{MODULE}.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": ">=3.8", "2.0.0": ">=3.9"},
)
def test_discover_pure_python_wheel() -> None:
    linux_38 = Target(python_version="3.8", os="linux", arch="x86_64")
    linux_311 = Target(python_version="3.11", os="macos", arch="arm64")
    compat = CompatDiscoverer().discover("pkg", targets=(linux_38, linux_311))
    assert compat == {
        linux_38: [VersionRange("1.0.0", "1.0.0")],
        linux_311: [VersionRange("1.0.0", None)],
    }


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {"1.0.0": ("pkg-1.0.0-py3-none-any.whl",)},
)
@patch(f"{MODULE}.fetch_pypi_requires_python", lambda *_args: {"1.0.0": ">=3.9"})
def test_discover_pure_python_wheel_incompatible_python_version() -> None:
    py38 = Target(python_version="3.8", os="linux", arch="x86_64")
    compat = CompatDiscoverer().discover("pkg", targets=(py38,))
    assert compat == {py38: []}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
    },
)
def test_discover_arch_mismatch() -> None:
    linux_311_arm = Target(python_version="3.11", os="linux", arch="arm64")
    compat = CompatDiscoverer().discover("pkg", targets=(linux_311_arm,))
    assert compat == {linux_311_arm: []}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp314-cp314t-manylinux_2_17_x86_64.whl",),
    },
)
def test_discover_free_threaded_mismatch() -> None:
    linux_314 = Target(python_version="3.14", free_threaded=False, os="linux", arch="x86_64")
    compat = CompatDiscoverer().discover("pkg", targets=(linux_314,))
    assert compat == {linux_314: []}


@patch(f"{MODULE}.fetch_pypi_wheel_filenames", lambda *_args: {})
def test_discover_empty() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = CompatDiscoverer().discover("pkg", targets=(linux_311,))
    assert compat == {linux_311: []}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {"1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",)},
)
def test_discover_multiple_targets() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    macos_311 = Target(python_version="3.11", os="macos", arch="arm64")
    compat = CompatDiscoverer().discover("pkg", targets=(linux_311, macos_311))
    assert compat == {
        linux_311: [VersionRange("1.0.0", None)],
        macos_311: [],
    }


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-py3-none-any.whl",),
        "1.5.0": (),  # sdist-only, e.g. click 6.5
        "2.0.0": ("pkg-2.0.0-py3-none-any.whl",),
    },
)
@patch(
    f"{MODULE}.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": None, "1.5.0": None, "2.0.0": None},
)
def test_discover_sdist_only_version_falls_back_to_pure_python() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = CompatDiscoverer().discover("pkg", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("1.0.0", None)]}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "1.5.0": (),  # sdist-only, no pure-Python wheel published elsewhere
        "2.0.0": ("pkg-2.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
    },
)
def test_discover_sdist_only_version_without_pure_python_wheel_is_incompatible() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = CompatDiscoverer().discover("pkg", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("1.0.0", "1.0.0"), VersionRange("2.0.0", None)]}
