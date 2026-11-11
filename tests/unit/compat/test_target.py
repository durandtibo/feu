from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from feu.compat.target import (
    DEFAULT_TARGETS,
    PLATFORMS,
    PYTHON_VERSIONS,
    Target,
    resolve_target,
)

if TYPE_CHECKING:
    from collections.abc import Generator


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


def test_target_invalid_python_version_free_threaded_suffix() -> None:
    with pytest.raises(ValueError, match="invalid python_version"):
        Target(python_version="3.14t")


def test_target_invalid_python_version_missing_minor() -> None:
    with pytest.raises(ValueError, match="invalid python_version"):
        Target(python_version="3")


def test_target_invalid_python_version_empty() -> None:
    with pytest.raises(ValueError, match="invalid python_version"):
        Target(python_version="")


def test_target_invalid_os() -> None:
    with pytest.raises(ValueError, match="invalid os"):
        Target(python_version="3.11", os="freebsd")


def test_target_invalid_arch() -> None:
    with pytest.raises(ValueError, match="invalid arch"):
        Target(python_version="3.11", arch="ppc64")


def test_target_os_none_is_valid() -> None:
    assert Target(python_version="3.11", os=None).os is None


def test_target_arch_none_is_valid() -> None:
    assert Target(python_version="3.11", arch=None).arch is None


######################################
#     Tests for resolve_target       #
######################################


@pytest.fixture
def current_platform() -> Generator[None]:
    with (
        patch("feu.compat.target.get_current_os", Mock(return_value="macos")),
        patch("feu.compat.target.get_current_arch", Mock(return_value="arm64")),
    ):
        yield


@pytest.mark.usefixtures("current_platform")
def test_resolve_target_all_options() -> None:
    assert resolve_target(python_version="3.10", free_threaded=True) == Target(
        python_version="3.10", free_threaded=True, os="macos", arch="arm64"
    )


@pytest.mark.usefixtures("current_platform")
def test_resolve_target_default_options() -> None:
    with (
        patch("feu.compat.target.get_python_version", Mock(return_value="3.12")),
        patch("feu.compat.target.is_free_threaded", Mock(return_value=False)),
    ):
        assert resolve_target() == Target(
            python_version="3.12", free_threaded=False, os="macos", arch="arm64"
        )


@pytest.mark.usefixtures("current_platform")
def test_resolve_target_platform_is_always_the_current_one() -> None:
    target = resolve_target(python_version="3.10")
    assert (target.os, target.arch) == ("macos", "arm64")


def test_resolve_target_has_no_os_or_arch_parameter() -> None:
    with pytest.raises(TypeError, match="unexpected keyword argument 'os'"):
        resolve_target(python_version="3.10", os="linux")  # ty: ignore[unknown-argument]


def test_resolve_target_free_threaded_is_keyword_only() -> None:
    with pytest.raises(TypeError, match="positional argument"):
        resolve_target("3.10", True)  # ty: ignore[too-many-positional-arguments]


@pytest.mark.usefixtures("current_platform")
def test_resolve_target_free_threaded_default_from_python_version() -> None:
    with patch("feu.compat.target.is_free_threaded", Mock(return_value=False)):
        assert resolve_target(python_version="3.14t") == Target(
            python_version="3.14", free_threaded=True, os="macos", arch="arm64"
        )


@pytest.mark.usefixtures("current_platform")
def test_resolve_target_free_threaded_true_with_suffix() -> None:
    assert resolve_target(python_version="3.14t", free_threaded=True) == Target(
        python_version="3.14", free_threaded=True, os="macos", arch="arm64"
    )


def test_resolve_target_free_threaded_false_with_suffix_raises_error() -> None:
    with pytest.raises(ValueError, match="indicates a free-threaded build"):
        resolve_target(python_version="3.14t", free_threaded=False)


@pytest.mark.usefixtures("current_platform")
def test_resolve_target_free_threaded_none_uses_interpreter_status() -> None:
    with patch("feu.compat.target.is_free_threaded", Mock(return_value=True)):
        assert resolve_target(python_version="3.14") == Target(
            python_version="3.14", free_threaded=True, os="macos", arch="arm64"
        )


@pytest.mark.usefixtures("current_platform")
def test_resolve_target_python_version_default_from_interpreter() -> None:
    with (
        patch("feu.compat.target.get_python_version", Mock(return_value="3.13t")),
        patch("feu.compat.target.is_free_threaded", Mock(return_value=True)),
    ):
        assert resolve_target() == Target(
            python_version="3.13", free_threaded=True, os="macos", arch="arm64"
        )


@pytest.mark.parametrize("python_version", ["3.11\n", "3.11 ", " 3.11", "3.11\n3.12"])
def test_target_rejects_trailing_or_leading_characters(python_version: str) -> None:
    with pytest.raises(ValueError, match="invalid python_version"):
        Target(python_version=python_version)


########################################
#     Tests for the shipped targets    #
########################################


def test_python_versions() -> None:
    assert PYTHON_VERSIONS == ("3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15")


def test_platforms() -> None:
    assert PLATFORMS == (
        ("linux", "x86_64"),
        ("linux", "arm64"),
        ("macos", "x86_64"),
        ("macos", "arm64"),
        ("windows", "x86_64"),
        ("windows", "arm64"),
    )


def test_default_targets_count() -> None:
    # 3.9 to 3.12: 6 platforms; 3.13 to 3.15: 6 platforms, with and without free threading.
    assert len(DEFAULT_TARGETS) == 4 * 6 + 3 * 12


def test_default_targets_are_unique() -> None:
    assert len(set(DEFAULT_TARGETS)) == len(DEFAULT_TARGETS)


def test_default_targets_have_a_concrete_platform() -> None:
    assert all(target.os is not None and target.arch is not None for target in DEFAULT_TARGETS)


def test_default_targets_free_threaded_from_python_313() -> None:
    assert {t.python_version for t in DEFAULT_TARGETS if t.free_threaded} == {
        "3.13",
        "3.14",
        "3.15",
    }


def test_default_targets_first() -> None:
    assert DEFAULT_TARGETS[0] == Target("3.9", False, "linux", "x86_64")


def test_default_targets_last() -> None:
    assert DEFAULT_TARGETS[-1] == Target("3.15", True, "windows", "arm64")
