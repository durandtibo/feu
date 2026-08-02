from __future__ import annotations

import pytest

from feu.utils.platform import get_current_arch, get_current_os

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
