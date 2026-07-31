from __future__ import annotations

from feu.compat.target import Target


def test_target_defaults() -> None:
    target = Target(python_version="3.11")
    assert target.python_version == "3.11"
    assert target.free_threaded is False
    assert target.os is None
    assert target.arch is None


def test_target_all_fields() -> None:
    target = Target(python_version="3.14", free_threaded=True, os="macos", arch="arm64")
    assert target.python_version == "3.14"
    assert target.free_threaded is True
    assert target.os == "macos"
    assert target.arch == "arm64"


def test_target_equality() -> None:
    assert Target(python_version="3.11") == Target(python_version="3.11")
    assert Target(python_version="3.11") != Target(python_version="3.12")
    assert Target(python_version="3.11", os="linux") != Target(python_version="3.11")


def test_target_is_hashable() -> None:
    targets = {Target(python_version="3.11"), Target(python_version="3.11")}
    assert len(targets) == 1
    targets.add(Target(python_version="3.11", free_threaded=True))
    assert len(targets) == 2


def test_target_used_as_dict_key() -> None:
    mapping = {Target(python_version="3.11"): "value"}
    assert mapping[Target(python_version="3.11")] == "value"
