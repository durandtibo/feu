from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

from feu.utils.platform import (
    get_current_arch,
    get_current_os,
    get_python_version,
    is_free_threaded,
)

##################################
#     Tests for get_current_os     #
##################################


@pytest.mark.parametrize(
    ("system", "os"),
    [
        ("Linux", "linux"),
        ("linux", "linux"),
        ("Darwin", "macos"),
        ("darwin", "macos"),
        ("Windows", "windows"),
        ("windows", "windows"),
    ],
)
def test_get_current_os(monkeypatch: pytest.MonkeyPatch, system: str, os: str) -> None:
    monkeypatch.setattr("platform.system", lambda: system)
    assert get_current_os() == os


def test_get_current_os_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "FreeBSD")
    assert get_current_os() is None


####################################
#     Tests for get_current_arch     #
####################################


@pytest.mark.parametrize(
    ("machine", "arch"),
    [
        ("x86_64", "x86_64"),
        ("X86_64", "x86_64"),
        ("amd64", "x86_64"),
        ("AMD64", "x86_64"),
        ("aarch64", "arm64"),
        ("AARCH64", "arm64"),
        ("arm64", "arm64"),
        ("ARM64", "arm64"),
    ],
)
def test_get_current_arch(monkeypatch: pytest.MonkeyPatch, machine: str, arch: str) -> None:
    monkeypatch.setattr("platform.machine", lambda: machine)
    assert get_current_arch() == arch


def test_get_current_arch_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("platform.machine", lambda: "i386")
    assert get_current_arch() is None


###################################
#     Tests for is_free_threaded     #
###################################


def test_is_free_threaded_true(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "_is_gil_enabled", lambda: False, raising=False)
    assert is_free_threaded() is True


def test_is_free_threaded_gil_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "_is_gil_enabled", lambda: True, raising=False)
    assert is_free_threaded() is False


def test_is_free_threaded_not_available(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delattr(sys, "_is_gil_enabled", raising=False)
    assert is_free_threaded() is False


####################################
#     Tests for get_python_version     #
####################################


@pytest.mark.parametrize(
    ("major", "minor", "version"),
    [
        (3, 11, "3.11"),
        (3, 12, "3.12"),
        (3, 9, "3.9"),
    ],
)
def test_get_python_version(
    monkeypatch: pytest.MonkeyPatch, major: int, minor: int, version: str
) -> None:
    monkeypatch.setattr(sys, "version_info", SimpleNamespace(major=major, minor=minor))
    assert get_python_version() == version


def test_get_python_version_matches_running_interpreter() -> None:
    assert get_python_version() == f"{sys.version_info.major}.{sys.version_info.minor}"
