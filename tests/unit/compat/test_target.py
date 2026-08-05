from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from feu.compat.target import Target, resolve_target


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


######################################
#     Tests for resolve_target       #
######################################


def test_resolve_target_all_options() -> None:
    assert resolve_target(
        python_version="3.10", free_threaded=True, os="linux", arch="x86_64"
    ) == Target(python_version="3.10", free_threaded=True, os="linux", arch="x86_64")


def test_resolve_target_default_options() -> None:
    with (
        patch("feu.compat.target.get_python_version", Mock(return_value="3.12")),
        patch("feu.compat.target.is_free_threaded", Mock(return_value=False)),
        patch("feu.compat.target.get_current_os", Mock(return_value="macos")),
        patch("feu.compat.target.get_current_arch", Mock(return_value="arm64")),
    ):
        assert resolve_target() == Target(
            python_version="3.12", free_threaded=False, os="macos", arch="arm64"
        )


def test_resolve_target_free_threaded_default_from_python_version() -> None:
    with patch("feu.compat.target.is_free_threaded", Mock(return_value=False)):
        assert resolve_target(python_version="3.14t", os="linux", arch="x86_64") == Target(
            python_version="3.14", free_threaded=True, os="linux", arch="x86_64"
        )


def test_resolve_target_free_threaded_true_with_suffix() -> None:
    assert resolve_target(
        python_version="3.14t", free_threaded=True, os="linux", arch="x86_64"
    ) == Target(python_version="3.14", free_threaded=True, os="linux", arch="x86_64")


def test_resolve_target_free_threaded_false_with_suffix_raises_error() -> None:
    with pytest.raises(ValueError, match="indicates a free-threaded build"):
        resolve_target(python_version="3.14t", free_threaded=False, os="linux", arch="x86_64")


def test_resolve_target_free_threaded_none_uses_interpreter_status() -> None:
    with patch("feu.compat.target.is_free_threaded", Mock(return_value=True)):
        assert resolve_target(python_version="3.14", os="linux", arch="x86_64") == Target(
            python_version="3.14", free_threaded=True, os="linux", arch="x86_64"
        )


def test_resolve_target_python_version_default_from_interpreter() -> None:
    with (
        patch("feu.compat.target.get_python_version", Mock(return_value="3.13t")),
        patch("feu.compat.target.is_free_threaded", Mock(return_value=True)),
    ):
        assert resolve_target(os="linux", arch="x86_64") == Target(
            python_version="3.13", free_threaded=True, os="linux", arch="x86_64"
        )
