from __future__ import annotations

import dataclasses

import pytest

from feu.utils.installer import InstallerSpec, normalize_arguments

#####################################
#     Tests for normalize_arguments #
#####################################


def test_normalize_arguments_empty_string() -> None:
    assert normalize_arguments("") == ()


def test_normalize_arguments_blank_string() -> None:
    assert normalize_arguments("   ") == ()


def test_normalize_arguments_string() -> None:
    assert normalize_arguments("-U --pre") == ("-U", "--pre")


def test_normalize_arguments_string_with_quotes() -> None:
    assert normalize_arguments("--index-url 'https://example.com/my index'") == (
        "--index-url",
        "https://example.com/my index",
    )


def test_normalize_arguments_string_keeps_backslashes_of_quoted_values() -> None:
    assert normalize_arguments(r"--find-links 'C:\Users\foo'") == ("--find-links", r"C:\Users\foo")


def test_normalize_arguments_list() -> None:
    assert normalize_arguments(["-U", "--pre"]) == ("-U", "--pre")


def test_normalize_arguments_list_is_not_split_again() -> None:
    assert normalize_arguments(["--index-url", "a b"]) == ("--index-url", "a b")


def test_normalize_arguments_tuple() -> None:
    assert normalize_arguments(("-U",)) == ("-U",)


def test_normalize_arguments_empty_list() -> None:
    assert normalize_arguments([]) == ()


@pytest.mark.parametrize("arguments", [1, None, ["-U", 1], {"-U"}])
def test_normalize_arguments_invalid_type(arguments: object) -> None:
    with pytest.raises(TypeError, match="installer arguments must be a string or a list/tuple"):
        normalize_arguments(arguments)  # ty: ignore[invalid-argument-type]


###################################
#     Tests for InstallerSpec     #
###################################


def test_installer_spec_name() -> None:
    assert InstallerSpec("my_installer").name == "my_installer"


def test_installer_spec_arguments_default() -> None:
    assert InstallerSpec("my_installer").arguments == ()


def test_installer_spec_arguments_string_is_split() -> None:
    assert InstallerSpec("my_installer", arguments="-U --pre").arguments == ("-U", "--pre")


def test_installer_spec_arguments_list_becomes_tuple() -> None:
    assert InstallerSpec("my_installer", arguments=["-U"]).arguments == ("-U",)


def test_installer_spec_arguments_invalid_type() -> None:
    with pytest.raises(TypeError, match="installer arguments must be a string or a list/tuple"):
        InstallerSpec("my_installer", arguments=1)  # ty: ignore[invalid-argument-type]


def test_installer_spec_equal_string_and_list() -> None:
    assert InstallerSpec("pip", arguments="-U --pre") == InstallerSpec(
        "pip", arguments=["-U", "--pre"]
    )


def test_installer_spec_is_frozen() -> None:
    spec = InstallerSpec("pip")
    with pytest.raises(dataclasses.FrozenInstanceError, match="cannot assign to field 'name'"):
        spec.name = "uv"  # ty: ignore[invalid-assignment]
