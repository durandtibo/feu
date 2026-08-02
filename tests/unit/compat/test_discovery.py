from __future__ import annotations

from unittest.mock import patch

import pytest

from feu.compat.discovery import DEFAULT_TARGETS, is_compatible, show_compat_targets
from feu.compat.registry import VersionRange
from feu.compat.target import Target
from feu.testing import rich_available

MODULE = "feu.compat.discovery"


##############################################
#     Tests for DEFAULT_TARGETS              #
##############################################


def test_default_targets_shape() -> None:
    assert len(DEFAULT_TARGETS) == 60
    assert all(isinstance(target, Target) for target in DEFAULT_TARGETS)
    assert all(target.os is not None and target.arch is not None for target in DEFAULT_TARGETS)


####################################
#     Tests for is_compatible     #
####################################


def test_is_compatible_none() -> None:
    assert is_compatible(None, "3.11") is True


def test_is_compatible_empty_string() -> None:
    assert is_compatible("", "3.11") is True


def test_is_compatible_true() -> None:
    assert is_compatible(">=3.9", "3.11") is True


def test_is_compatible_false() -> None:
    assert is_compatible(">=3.12", "3.11") is False


def test_is_compatible_invalid_specifier() -> None:
    assert is_compatible("invalid-specifier", "3.11") is True


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
