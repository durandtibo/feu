from __future__ import annotations

from unittest.mock import patch

import pytest

from feu.compat import Discovery, show_compat_targets
from feu.compat.display import _format_ranges
from feu.compat.registry import VersionRange
from feu.compat.target import Target
from feu.imports import MissingPackageError
from feu.testing import rich_available

LINUX_311 = Target(python_version="3.11", os="linux", arch="x86_64")

#########################################
#     Tests for show_compat_targets     #
#########################################


@rich_available
def test_show_compat_targets(capsys: pytest.CaptureFixture) -> None:
    show_compat_targets({LINUX_311: [VersionRange("1.0.0", None)]}, pkg_name="my_package")
    out = capsys.readouterr().out
    assert "my_package" in out
    assert "3.11" in out
    assert "linux" in out
    assert "x86_64" in out
    assert "1.0.0" in out
    assert "latest" in out


@rich_available
def test_show_compat_targets_discovery(capsys: pytest.CaptureFixture) -> None:
    discovery = Discovery(("1.0.0",), {LINUX_311: [VersionRange("1.0.0", None)]})
    show_compat_targets(discovery, pkg_name="my_package")
    out = capsys.readouterr().out
    assert "1.0.0" in out
    assert "latest" in out


@rich_available
def test_show_compat_targets_no_pkg_name(capsys: pytest.CaptureFixture) -> None:
    show_compat_targets({LINUX_311: [VersionRange("1.0.0", "2.0.0")]})
    out = capsys.readouterr().out
    assert "Compatibility" in out
    assert "1.0.0" in out
    assert "2.0.0" in out


@rich_available
def test_show_compat_targets_unsupported(capsys: pytest.CaptureFixture) -> None:
    macos_arm = Target(python_version="3.11", free_threaded=True, os="macos", arch="arm64")
    show_compat_targets({macos_arm: []}, pkg_name="my_package")
    out = capsys.readouterr().out
    assert "unsupported" in out
    assert "True" in out
    assert "macos" in out
    assert "arm64" in out


@rich_available
def test_show_compat_targets_multiple_ranges(capsys: pytest.CaptureFixture) -> None:
    compat = {LINUX_311: [VersionRange("1.0.0", "1.5.0"), VersionRange("2.0.0", None)]}
    show_compat_targets(compat, pkg_name="my_package")
    out = capsys.readouterr().out
    assert "1.5.0" in out
    assert "2.0.0" in out
    # both ranges are shown on a single row for the target
    assert out.count("3.11") == 1


@rich_available
def test_show_compat_targets_unspecified_platform(capsys: pytest.CaptureFixture) -> None:
    show_compat_targets({Target(python_version="3.11"): [VersionRange("1.0.0", None)]})
    assert "-" in capsys.readouterr().out


def test_show_compat_targets_without_rich_package() -> None:
    with (
        patch("feu.imports.optional.is_rich_available", lambda: False),
        pytest.raises(MissingPackageError, match="'rich' package is required but not installed"),
    ):
        show_compat_targets({})


###################################
#     Tests for _format_ranges    #
###################################


def test_format_ranges_empty() -> None:
    assert _format_ranges([]) == "[red]unsupported[/red]"


def test_format_ranges_closed_and_open() -> None:
    assert _format_ranges([VersionRange("1.0", "1.5"), VersionRange("2.0", None)]) == (
        "1.0 - 1.5, 2.0 - [green]latest[/green]"
    )


def test_format_ranges_unbounded_min() -> None:
    assert _format_ranges([VersionRange(None, "1.5")]) == "- - 1.5"
