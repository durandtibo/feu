from __future__ import annotations

from unittest.mock import patch

from feu.compat.discovery import (
    DEFAULT_PYTHON_VERSIONS,
    DEFAULT_TARGETS,
    discover_compat,
    discover_compat_targets,
)
from feu.compat.registry import UNSUPPORTED
from feu.compat.target import Target


@patch(
    "feu.compat.discovery.fetch_pypi_requires_python",
    lambda *_args: {
        "1.0.0": ">=3.6",
        "1.5.0": ">=3.8",
        "2.0.0": ">=3.9",
        "2.1.0": ">=3.9",
        "2.1.0a1": ">=3.9",  # pre-release, should be ignored
        "not-a-version": ">=3.9",  # invalid, should be ignored
    },
)
def test_discover_compat() -> None:
    compat = discover_compat("my_package", python_versions=("3.8", "3.9", "3.10"))
    assert compat == {
        "3.8": {"min": "1.0.0", "max": "1.5.0"},
        "3.9": {"min": "1.0.0", "max": None},
        "3.10": {"min": "1.0.0", "max": None},
    }


@patch(
    "feu.compat.discovery.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": ">=3.9", "2.0.0": ">=3.9"},
)
def test_discover_compat_no_compatible_version() -> None:
    compat = discover_compat("my_package", python_versions=("3.7",))
    assert compat == {"3.7": {"min": UNSUPPORTED, "max": UNSUPPORTED}}


@patch(
    "feu.compat.discovery.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": None, "2.0.0": None},
)
def test_discover_compat_no_requires_python() -> None:
    compat = discover_compat("my_package", python_versions=("3.9",))
    assert compat == {"3.9": {"min": "1.0.0", "max": None}}


@patch(
    "feu.compat.discovery.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": "invalid specifier!!", "2.0.0": ">=3.9"},
)
def test_discover_compat_invalid_specifier() -> None:
    compat = discover_compat("my_package", python_versions=("3.5",))
    assert compat == {"3.5": {"min": "1.0.0", "max": "1.0.0"}}


@patch("feu.compat.discovery.fetch_pypi_requires_python", lambda *_args: {})
def test_discover_compat_empty() -> None:
    compat = discover_compat("my_package", python_versions=("3.9",))
    assert compat == {"3.9": {"min": UNSUPPORTED, "max": UNSUPPORTED}}


def test_discover_compat_default_python_versions() -> None:
    with patch(
        "feu.compat.discovery.fetch_pypi_requires_python",
        lambda *_args: {"1.0.0": None},
    ):
        compat = discover_compat("my_package")
    assert set(compat.keys()) == {"3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15"}


##############################################
#     Tests for DEFAULT_TARGETS              #
##############################################


def test_default_targets_shape() -> None:
    assert len(DEFAULT_TARGETS) == len(DEFAULT_PYTHON_VERSIONS) * 2 * 3 * 2
    assert all(isinstance(target, Target) for target in DEFAULT_TARGETS)
    assert all(target.os is not None and target.arch is not None for target in DEFAULT_TARGETS)


##############################################
#     Tests for discover_compat_targets      #
##############################################


@patch(
    "feu.compat.discovery.fetch_pypi_wheel_filenames",
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
def test_discover_compat_targets_basic() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(linux_311,))
    assert compat == {linux_311: {"min": "1.0.0", "max": None}}


@patch(
    "feu.compat.discovery.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "1.1.0": (
            "pkg-1.1.0-cp311-cp311-manylinux_2_17_x86_64.whl",
            "pkg-1.1.0-cp314-cp314t-manylinux_2_17_x86_64.whl",
        ),
    },
)
def test_discover_compat_targets_free_threaded() -> None:
    free_threaded_314 = Target(
        python_version="3.14", free_threaded=True, os="linux", arch="x86_64"
    )
    compat = discover_compat_targets("pkg", targets=(free_threaded_314,))
    assert compat == {free_threaded_314: {"min": "1.1.0", "max": None}}


@patch(
    "feu.compat.discovery.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "2.0.0": ("pkg-2.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
    },
)
def test_discover_compat_targets_max_is_last_compatible() -> None:
    macos_arm = Target(python_version="3.11", os="macos", arch="arm64")
    compat = discover_compat_targets("pkg", targets=(macos_arm,))
    assert compat == {macos_arm: {"min": UNSUPPORTED, "max": UNSUPPORTED}}


@patch(
    "feu.compat.discovery.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "1.5.0": ("pkg-1.5.0-cp39-cp39-manylinux_2_17_x86_64.whl",),
        "2.0.0": ("pkg-2.0.0-cp39-cp39-manylinux_2_17_x86_64.whl",),
    },
)
def test_discover_compat_targets_upper_bound() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(linux_311,))
    assert compat == {linux_311: {"min": "1.0.0", "max": "1.0.0"}}


@patch("feu.compat.discovery.fetch_pypi_wheel_filenames", lambda *_args: {})
def test_discover_compat_targets_empty() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(linux_311,))
    assert compat == {linux_311: {"min": UNSUPPORTED, "max": UNSUPPORTED}}


@patch(
    "feu.compat.discovery.fetch_pypi_wheel_filenames",
    lambda *_args: {"1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",)},
)
def test_discover_compat_targets_multiple_targets() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    macos_311 = Target(python_version="3.11", os="macos", arch="arm64")
    compat = discover_compat_targets("pkg", targets=(linux_311, macos_311))
    assert compat == {
        linux_311: {"min": "1.0.0", "max": None},
        macos_311: {"min": UNSUPPORTED, "max": UNSUPPORTED},
    }
