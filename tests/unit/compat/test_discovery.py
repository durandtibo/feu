from __future__ import annotations

from unittest.mock import patch

import pytest

from feu.compat.discovery import (
    DEFAULT_TARGETS,
    discover_compat,
    discover_compat_targets,
    show_compat_targets,
)
from feu.compat.registry import VersionRange
from feu.compat.target import Target
from feu.testing import rich_available

MODULE = "feu.compat.discovery"


@patch(
    f"{MODULE}.fetch_pypi_requires_python",
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
        "3.8": [VersionRange("1.0.0", "1.5.0")],
        "3.9": [VersionRange("1.0.0", None)],
        "3.10": [VersionRange("1.0.0", None)],
    }


@patch(
    f"{MODULE}.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": ">=3.9", "2.0.0": ">=3.9"},
)
def test_discover_compat_no_compatible_version() -> None:
    compat = discover_compat("my_package", python_versions=("3.7",))
    assert compat == {"3.7": []}


@patch(
    f"{MODULE}.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": None, "2.0.0": None},
)
def test_discover_compat_no_requires_python() -> None:
    compat = discover_compat("my_package", python_versions=("3.9",))
    assert compat == {"3.9": [VersionRange("1.0.0", None)]}


@patch(
    f"{MODULE}.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": "invalid specifier!!", "2.0.0": ">=3.9"},
)
def test_discover_compat_invalid_specifier() -> None:
    compat = discover_compat("my_package", python_versions=("3.5",))
    assert compat == {"3.5": [VersionRange("1.0.0", "1.0.0")]}


@patch(f"{MODULE}.fetch_pypi_requires_python", lambda *_args: {})
def test_discover_compat_empty() -> None:
    compat = discover_compat("my_package", python_versions=("3.9",))
    assert compat == {"3.9": []}


def test_discover_compat_default_python_versions() -> None:
    with patch(
        f"{MODULE}.fetch_pypi_requires_python",
        lambda *_args: {"1.0.0": None},
    ):
        compat = discover_compat("my_package")
    assert set(compat.keys()) == {"3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15"}


##############################################
#     Tests for DEFAULT_TARGETS              #
##############################################


def test_default_targets_shape() -> None:
    assert len(DEFAULT_TARGETS) == 60
    assert all(isinstance(target, Target) for target in DEFAULT_TARGETS)
    assert all(target.os is not None and target.arch is not None for target in DEFAULT_TARGETS)


##############################################
#     Tests for discover_compat_targets      #
##############################################


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
def test_discover_compat_targets_basic() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(linux_311,))
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
def test_discover_compat_targets_free_threaded() -> None:
    free_threaded_314 = Target(python_version="3.14", free_threaded=True, os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(free_threaded_314,))
    assert compat == {free_threaded_314: [VersionRange("1.1.0", None)]}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "2.0.0": ("pkg-2.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
    },
)
def test_discover_compat_targets_max_is_last_compatible() -> None:
    macos_arm = Target(python_version="3.11", os="macos", arch="arm64")
    compat = discover_compat_targets("pkg", targets=(macos_arm,))
    assert compat == {macos_arm: []}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "1.5.0": ("pkg-1.5.0-cp39-cp39-manylinux_2_17_x86_64.whl",),
        "2.0.0": ("pkg-2.0.0-cp39-cp39-manylinux_2_17_x86_64.whl",),
    },
)
def test_discover_compat_targets_upper_bound() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(linux_311,))
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
def test_discover_compat_targets_pure_python_wheel() -> None:
    linux_38 = Target(python_version="3.8", os="linux", arch="x86_64")
    linux_311 = Target(python_version="3.11", os="macos", arch="arm64")
    compat = discover_compat_targets("pkg", targets=(linux_38, linux_311))
    assert compat == {
        linux_38: [VersionRange("1.0.0", "1.0.0")],
        linux_311: [VersionRange("1.0.0", None)],
    }


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {"1.0.0": ("pkg-1.0.0-py3-none-any.whl",)},
)
@patch(f"{MODULE}.fetch_pypi_requires_python", lambda *_args: {"1.0.0": ">=3.9"})
def test_discover_compat_targets_pure_python_wheel_incompatible_python_version() -> None:
    py38 = Target(python_version="3.8", os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(py38,))
    assert compat == {py38: []}


@patch(f"{MODULE}.fetch_pypi_wheel_filenames", lambda *_args: {})
def test_discover_compat_targets_empty() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(linux_311,))
    assert compat == {linux_311: []}


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {"1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",)},
)
def test_discover_compat_targets_multiple_targets() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    macos_311 = Target(python_version="3.11", os="macos", arch="arm64")
    compat = discover_compat_targets("pkg", targets=(linux_311, macos_311))
    assert compat == {
        linux_311: [VersionRange("1.0.0", None)],
        macos_311: [],
    }


#########################################
#     Tests for show_compat_targets     #
#########################################


@rich_available
def test_show_compat_targets_without_rich(capsys: pytest.CaptureFixture) -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = {linux_311: [VersionRange("1.0.0", None)]}
    show_compat_targets(compat, pkg_name="my_package")
    out = capsys.readouterr().out
    assert "my_package" in out
    assert "3.11" in out
    assert "linux" in out
    assert "x86_64" in out
    assert "1.0.0" in out
    assert "latest" in out


@rich_available
def test_show_compat_targets_no_pkg_name(capsys: pytest.CaptureFixture) -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = {linux_311: [VersionRange("1.0.0", "2.0.0")]}
    show_compat_targets(compat)
    out = capsys.readouterr().out
    assert "Compatibility" in out
    assert "1.0.0" in out
    assert "2.0.0" in out


@rich_available
def test_show_compat_targets_unsupported(capsys: pytest.CaptureFixture) -> None:
    macos_arm = Target(python_version="3.11", free_threaded=True, os="macos", arch="arm64")
    compat = {macos_arm: []}
    show_compat_targets(compat, pkg_name="my_package")
    out = capsys.readouterr().out
    assert "unsupported" in out
    assert "True" in out
    assert "macos" in out
    assert "arm64" in out


@rich_available
def test_show_compat_targets_multiple_ranges(capsys: pytest.CaptureFixture) -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = {linux_311: [VersionRange("1.0.0", "1.5.0"), VersionRange("2.0.0", None)]}
    show_compat_targets(compat, pkg_name="my_package")
    out = capsys.readouterr().out
    assert "1.0.0" in out
    assert "1.5.0" in out
    assert "2.0.0" in out
    assert "latest" in out


def test_show_compat_targets_without_rich_package() -> None:
    with (
        patch("feu.imports.rich.is_rich_available", lambda: False),
        pytest.raises(RuntimeError, match=r"'rich' package is required but not installed."),
    ):
        show_compat_targets({})
