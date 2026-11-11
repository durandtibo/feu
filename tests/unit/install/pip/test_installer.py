from __future__ import annotations

import sys
from unittest.mock import patch

import pytest

from feu.install.pip import PipInstaller, UvInstaller
from feu.install.pip.installer import BasePipInstaller
from feu.utils.package import PackageDependency, PackageSpec

##################################
#     Tests for PipInstaller     #
##################################


def test_pip_installer_repr() -> None:
    assert repr(PipInstaller()).startswith("PipInstaller(")


def test_pip_installer_str() -> None:
    assert str(PipInstaller()).startswith("PipInstaller(")


def test_pip_installer_equal_true() -> None:
    assert PipInstaller().equal(PipInstaller())


def test_pip_installer_equal_true_with_args() -> None:
    assert PipInstaller("-U").equal(PipInstaller("-U"))


def test_pip_installer_equal_false_different_args() -> None:
    assert not PipInstaller("-U").equal(PipInstaller("-F"))


def test_pip_installer_equal_false_different_type() -> None:
    assert not PipInstaller("-U").equal(42)


def test_pip_installer_install_numpy() -> None:
    with patch("feu.install.pip.installer.run_command") as run_mock:
        PipInstaller().install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "numpy==2.0.0"])


def test_pip_installer_install_pandas() -> None:
    with patch("feu.install.pip.installer.run_command") as run_mock:
        PipInstaller().install(PackageSpec(name="pandas", version="2.1.1"))
        run_mock.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "pandas==2.1.1", "numpy<2.0.0"]
        )


def test_pip_installer_install_numpy_with_args() -> None:
    with patch("feu.install.pip.installer.run_command") as run_mock:
        PipInstaller(arguments="-U").install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "-U", "numpy==2.0.0"]
        )


def test_pip_installer_install_wildcard_version() -> None:
    with patch("feu.install.pip.installer.run_command") as run_mock:
        PipInstaller().install(PackageSpec(name="torch", version="2.12.*"))
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "torch==2.12.*"])


def test_pip_installer_instantiate_with_arguments() -> None:
    assert PipInstaller.instantiate_with_arguments(arguments="-U").equal(
        PipInstaller(arguments="-U")
    )


#################################
#     Tests for UvInstaller     #
#################################


def test_uv_installer_repr() -> None:
    assert repr(UvInstaller()).startswith("UvInstaller(")


def test_uv_installer_str() -> None:
    assert str(UvInstaller()).startswith("UvInstaller(")


def test_uv_installer_equal_true() -> None:
    assert UvInstaller().equal(UvInstaller())


def test_uv_installer_equal_true_with_args() -> None:
    assert UvInstaller("-U").equal(UvInstaller("-U"))


def test_uv_installer_equal_false_different_args() -> None:
    assert not UvInstaller("-U").equal(UvInstaller("-F"))


def test_uv_installer_equal_false_different_type() -> None:
    assert not UvInstaller("-U").equal(42)


def test_uv_installer_install_numpy() -> None:
    with (
        patch("feu.install.pip.installer.which", return_value="/usr/bin/uv"),
        patch("feu.install.pip.installer.run_command") as run_mock,
    ):
        UvInstaller().install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with(
            ["uv", "pip", "install", "--python", sys.executable, "numpy==2.0.0"]
        )


def test_uv_installer_install_pandas() -> None:
    with (
        patch("feu.install.pip.installer.which", return_value="/usr/bin/uv"),
        patch("feu.install.pip.installer.run_command") as run_mock,
    ):
        UvInstaller().install(PackageSpec(name="pandas", version="2.1.1"))
        run_mock.assert_called_once_with(
            ["uv", "pip", "install", "--python", sys.executable, "pandas==2.1.1", "numpy<2.0.0"]
        )


def test_uv_installer_install_numpy_with_args() -> None:
    with (
        patch("feu.install.pip.installer.which", return_value="/usr/bin/uv"),
        patch("feu.install.pip.installer.run_command") as run_mock,
    ):
        UvInstaller(arguments="-U").install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with(
            ["uv", "pip", "install", "--python", sys.executable, "-U", "numpy==2.0.0"]
        )


def test_uv_installer_instantiate_with_arguments() -> None:
    assert UvInstaller.instantiate_with_arguments(arguments="-U").equal(UvInstaller(arguments="-U"))


def test_uv_installer_install_targets_the_current_interpreter() -> None:
    with (
        patch("feu.install.pip.installer.which", return_value="/usr/bin/uv"),
        patch("feu.install.pip.installer.run_command") as run_mock,
    ):
        UvInstaller().install(PackageSpec(name="numpy", version="2.0.0"))
        assert run_mock.call_args.args[0][3:5] == ["--python", sys.executable]


def test_uv_installer_install_uv_not_found() -> None:
    with (
        patch("feu.install.pip.installer.which", return_value=None),
        patch("feu.install.pip.installer.run_command") as run_mock,
        pytest.raises(RuntimeError, match="uv is not found on the PATH"),
    ):
        UvInstaller().install(PackageSpec(name="numpy", version="2.0.0"))
    run_mock.assert_not_called()


########################################################
#     Tests for the command of the pip installers      #
########################################################


def test_pip_installer_generate_command() -> None:
    deps = [PackageDependency("numpy", ["==2.0.0"]), PackageDependency("scipy", ["<2"])]
    assert PipInstaller()._generate_command(deps, ("-U",)) == [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-U",
        "numpy==2.0.0",
        "scipy<2",
    ]


def test_uv_installer_generate_command() -> None:
    deps = [PackageDependency("numpy", ["==2.0.0"])]
    assert UvInstaller()._generate_command(deps, ("-U",)) == [
        "uv",
        "pip",
        "install",
        "--python",
        sys.executable,
        "-U",
        "numpy==2.0.0",
    ]


def test_pip_installer_arguments_with_spaces_are_not_split_again() -> None:
    with patch("feu.install.pip.installer.run_command") as run_mock:
        PipInstaller(arguments=["--index-url", "https://example.com/my index"]).install(
            PackageSpec(name="numpy", version="2.0.0")
        )
        assert run_mock.call_args.args[0][4:6] == ["--index-url", "https://example.com/my index"]


def test_pip_installer_arguments_string_is_split_once() -> None:
    assert PipInstaller(arguments="-U --pre")._arguments == ("-U", "--pre")


def test_pip_installer_repr_with_arguments() -> None:
    assert repr(PipInstaller("-U --pre")) == "PipInstaller(arguments=('-U', '--pre'))"


def test_pip_installer_invalid_arguments() -> None:
    with pytest.raises(TypeError, match="installer arguments must be a string"):
        PipInstaller(arguments=1)  # ty: ignore[invalid-argument-type]


def test_pip_installer_install_pip_not_available() -> None:
    with (
        patch("feu.install.pip.installer.find_spec", return_value=None),
        patch("feu.install.pip.installer.run_command") as run_mock,
        pytest.raises(RuntimeError, match="pip is not available in the interpreter"),
    ):
        PipInstaller().install(PackageSpec(name="numpy", version="2.0.0"))
    run_mock.assert_not_called()


def test_base_pip_installer_check_available_default_does_nothing() -> None:
    class MyInstaller(BasePipInstaller):
        def _generate_command(self, deps: object, args: tuple[str, ...]) -> list[str]:  # noqa: ARG002
            return ["echo", *args]

    assert MyInstaller()._check_available() is None
