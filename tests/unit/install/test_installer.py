from __future__ import annotations

import dataclasses
import sys
from unittest.mock import patch

import pytest
from packaging.requirements import Requirement

from feu.install import (
    Installer,
    InstallerSpec,
    PipInstaller,
    UvInstaller,
    get_default_installer_registry,
    is_pip_available,
    is_uv_available,
    register_installer,
)
from feu.install.installer import normalize_arguments
from feu.utils.package import PackageSpec
from feu.utils.registry import Registry

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


def test_installer_spec_repr() -> None:
    assert repr(InstallerSpec("pip", "-U")) == "InstallerSpec(name='pip', arguments=('-U',))"


def test_installer_spec_is_frozen() -> None:
    spec = InstallerSpec("pip")
    with pytest.raises(dataclasses.FrozenInstanceError, match="cannot assign to field 'name'"):
        spec.name = "uv"  # ty: ignore[invalid-assignment]


###############################
#     Tests for Installer     #
###############################


class EchoInstaller(Installer):
    prefix = ("echo", "install")


def test_installer_command_without_arguments() -> None:
    assert EchoInstaller().command([Requirement("numpy==2.0.0")]) == [
        "echo",
        "install",
        "numpy==2.0.0",
    ]


def test_installer_command_with_arguments() -> None:
    assert EchoInstaller("-U --pre").command(
        [Requirement("numpy==2.0.0"), Requirement("scipy<2")]
    ) == ["echo", "install", "-U", "--pre", "numpy==2.0.0", "scipy<2"]


def test_installer_command_without_requirements() -> None:
    assert EchoInstaller("-U").command([]) == ["echo", "install", "-U"]


def test_installer_command_does_not_split_arguments_given_as_a_list() -> None:
    assert EchoInstaller(["--index-url", "a b"]).command([]) == [
        "echo",
        "install",
        "--index-url",
        "a b",
    ]


def test_installer_arguments_string_is_split_once() -> None:
    assert EchoInstaller("-U --pre").arguments == ("-U", "--pre")


def test_installer_invalid_arguments() -> None:
    with pytest.raises(TypeError, match="installer arguments must be a string"):
        EchoInstaller(1)  # ty: ignore[invalid-argument-type]


def test_installer_repr() -> None:
    assert repr(EchoInstaller("-U")) == "EchoInstaller(arguments=('-U',))"


def test_installer_equal() -> None:
    assert EchoInstaller("-U") == EchoInstaller(["-U"])


def test_installer_not_equal_different_arguments() -> None:
    assert EchoInstaller("-U") != EchoInstaller("-F")


def test_installer_not_equal_different_class() -> None:
    assert EchoInstaller() != PipInstaller()


def test_installer_check_available_default_does_nothing() -> None:
    assert EchoInstaller().check_available() is None


def test_installer_install_runs_the_command() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        EchoInstaller("-U").install(PackageSpec("numpy", "2.0.0"))
        run_mock.assert_called_once_with(["echo", "install", "-U", "numpy==2.0.0"])


def test_installer_install_resolves_the_dependencies() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        EchoInstaller().install(PackageSpec("pandas", "2.1.1"))
        run_mock.assert_called_once_with(["echo", "install", "pandas==2.1.1", "numpy<2.0.0"])


def test_installer_install_custom_resolvers() -> None:
    resolvers = Registry("dependency resolver")
    resolvers.register("numpy", lambda package: [Requirement(f"{package.name}>=1")])
    with patch("feu.install.installer.run_command") as run_mock:
        EchoInstaller().install(PackageSpec("numpy", "2.0.0"), resolvers=resolvers)
        run_mock.assert_called_once_with(["echo", "install", "numpy>=1"])


def test_installer_install_checks_the_tool_before_running_the_command() -> None:
    class MissingToolInstaller(EchoInstaller):
        def check_available(self) -> None:
            msg = "tool is missing"
            raise RuntimeError(msg)

    with (
        patch("feu.install.installer.run_command") as run_mock,
        pytest.raises(RuntimeError, match="tool is missing"),
    ):
        MissingToolInstaller().install(PackageSpec("numpy", "2.0.0"))
    run_mock.assert_not_called()


##################################
#     Tests for PipInstaller     #
##################################


def test_pip_installer_install_numpy() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        PipInstaller().install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "numpy==2.0.0"])


def test_pip_installer_install_with_args() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        PipInstaller(arguments="-U").install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "-U", "numpy==2.0.0"]
        )


def test_pip_installer_install_wildcard_version() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        PipInstaller().install(PackageSpec(name="torch", version="2.12.*"))
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "torch==2.12.*"])


def test_pip_installer_install_latest_version() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        PipInstaller().install(PackageSpec(name="torch"))
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "torch"])


def test_pip_installer_install_pip_not_available() -> None:
    with (
        patch("feu.install.installer.is_pip_available", return_value=False),
        patch("feu.install.installer.run_command") as run_mock,
        pytest.raises(RuntimeError, match="pip is not available in the interpreter"),
    ):
        PipInstaller().install(PackageSpec(name="numpy", version="2.0.0"))
    run_mock.assert_not_called()


def test_pip_installer_prefix_targets_the_current_interpreter() -> None:
    assert PipInstaller.prefix == (sys.executable, "-m", "pip", "install")


#################################
#     Tests for UvInstaller     #
#################################


def test_uv_installer_install_numpy() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        UvInstaller().install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with(
            ["uv", "pip", "install", "--python", sys.executable, "numpy==2.0.0"]
        )


def test_uv_installer_install_with_args() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        UvInstaller(arguments="-U").install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with(
            ["uv", "pip", "install", "--python", sys.executable, "-U", "numpy==2.0.0"]
        )


def test_uv_installer_install_uv_not_found() -> None:
    with (
        patch("feu.install.installer.is_uv_available", return_value=False),
        patch("feu.install.installer.run_command") as run_mock,
        pytest.raises(RuntimeError, match="uv is not found on the PATH"),
    ):
        UvInstaller().install(PackageSpec(name="numpy", version="2.0.0"))
    run_mock.assert_not_called()


##############################################
#     Tests for the installer registry       #
##############################################


def test_get_default_installer_registry_keys() -> None:
    assert get_default_installer_registry().keys() == ["pip", "uv"]


def test_get_default_installer_registry_is_a_registry() -> None:
    assert isinstance(get_default_installer_registry(), Registry)


def test_get_default_installer_registry_is_a_singleton() -> None:
    assert get_default_installer_registry() is get_default_installer_registry()


def test_get_default_installer_registry_pip() -> None:
    assert get_default_installer_registry().find("pip") is PipInstaller


def test_get_default_installer_registry_uv() -> None:
    assert get_default_installer_registry().find("uv") is UvInstaller


def test_get_default_installer_registry_is_case_insensitive() -> None:
    assert get_default_installer_registry().find("UV") is UvInstaller


def test_register_installer() -> None:
    register_installer("echo", EchoInstaller)
    assert get_default_installer_registry().find("echo") is EchoInstaller


def test_register_installer_exist_ok_false() -> None:
    with pytest.raises(RuntimeError, match="already registered for the key 'pip'"):
        register_installer("pip", EchoInstaller)


def test_register_installer_exist_ok_true() -> None:
    register_installer("pip", EchoInstaller, exist_ok=True)
    assert get_default_installer_registry().find("pip") is EchoInstaller


#####################################
#     Tests for is_pip_available    #
#####################################


@pytest.fixture
def _real_availability() -> None:
    is_pip_available.cache_clear()
    is_uv_available.cache_clear()


@pytest.mark.usefixtures("_real_availability")
def test_is_pip_available_true() -> None:
    with patch("feu.install.installer.find_spec", return_value=object()):
        assert is_pip_available()


@pytest.mark.usefixtures("_real_availability")
def test_is_pip_available_false() -> None:
    with patch("feu.install.installer.find_spec", return_value=None):
        assert not is_pip_available()


@pytest.mark.usefixtures("_real_availability")
def test_is_pip_available_is_cached() -> None:
    with patch("feu.install.installer.find_spec", return_value=object()) as find_mock:
        is_pip_available()
        is_pip_available()
        find_mock.assert_called_once_with("pip")


@pytest.mark.usefixtures("_real_availability")
def test_is_uv_available_true() -> None:
    with patch("feu.install.installer.which", return_value="/usr/bin/uv"):
        assert is_uv_available()


@pytest.mark.usefixtures("_real_availability")
def test_is_uv_available_false() -> None:
    with patch("feu.install.installer.which", return_value=None):
        assert not is_uv_available()


@pytest.mark.usefixtures("_real_availability")
def test_is_uv_available_is_cached() -> None:
    with patch("feu.install.installer.which", return_value="/usr/bin/uv") as which_mock:
        is_uv_available()
        is_uv_available()
        which_mock.assert_called_once_with("uv")
