from __future__ import annotations

import sys
from unittest.mock import Mock, patch

import pytest

from feu.compat import Target, UnsupportedVersionError
from feu.imports import package_available
from feu.install import (
    Installer,
    InstallerSpec,
    PipInstaller,
    UvInstaller,
    install_package,
    install_package_closest_version,
)
from feu.utils.package import PackageSpec
from feu.utils.registry import Registry

#####################################
#     Tests for install_package     #
#####################################


def test_install_package_pip_numpy() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        install_package(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "numpy==2.0.0"])


def test_install_package_pip_pandas() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        install_package(
            installer=InstallerSpec("pip"), package=PackageSpec(name="pandas", version="2.1.1")
        )
        run_mock.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "pandas==2.1.1", "numpy<2.0.0"]
        )


def test_install_package_uv_numpy() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        install_package(
            installer=InstallerSpec("uv"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with(
            ["uv", "pip", "install", "--python", sys.executable, "numpy==2.0.0"]
        )


def test_install_package_pip_numpy_with_args() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        install_package(
            installer=InstallerSpec("pip", arguments="-U"),
            package=PackageSpec(name="numpy", version="2.0.0"),
        )
        run_mock.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "-U", "numpy==2.0.0"]
        )


#####################################################
#     Tests for install_package_closest_version     #
#####################################################


def test_install_package_closest_version_pip_numpy() -> None:
    with (
        patch("feu.install.api.resolve_target", Mock(return_value=Target(python_version="3.12"))),
        patch("feu.install.installer.run_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "numpy==2.0.0"])


def test_install_package_closest_version_pip_pandas() -> None:
    with (
        patch("feu.install.api.resolve_target", Mock(return_value=Target(python_version="3.12"))),
        patch("feu.install.installer.run_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"), package=PackageSpec(name="pandas", version="2.1.1")
        )
        run_mock.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "pandas==2.1.1", "numpy<2.0.0"]
        )


def test_install_package_closest_version_uv_numpy() -> None:
    with (
        patch("feu.install.api.resolve_target", Mock(return_value=Target(python_version="3.12"))),
        patch("feu.install.installer.run_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("uv"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with(
            ["uv", "pip", "install", "--python", sys.executable, "numpy==2.0.0"]
        )


def test_install_package_closest_version_pip_numpy_with_args() -> None:
    with (
        patch("feu.install.api.resolve_target", Mock(return_value=Target(python_version="3.12"))),
        patch("feu.install.installer.run_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip", arguments="-U"),
            package=PackageSpec(name="numpy", version="2.0.0"),
        )
        run_mock.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "-U", "numpy==2.0.0"]
        )


def test_install_package_closest_version_pip_wildcard() -> None:
    with (
        patch("feu.install.api.resolve_target", Mock(return_value=Target(python_version="3.12"))),
        patch("feu.install.installer.run_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"), package=PackageSpec(name="torch", version="2.12.*")
        )
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "torch==2.12.*"])


def test_install_package_closest_version_default_target_is_the_full_current_target() -> None:
    current = Target(python_version="3.9", free_threaded=False, os="linux", arch="x86_64")
    with (
        patch("feu.install.api.resolve_target", Mock(return_value=current)),
        patch("feu.install.api.find_closest_version", Mock(return_value="2.0.2")) as find_mock,
        patch("feu.install.installer.run_command"),
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="2.3.0")
        )
        find_mock.assert_called_once_with(pkg_name="numpy", pkg_version="2.3.0", target=current)


def test_install_package_closest_version_explicit_target_is_used() -> None:
    target = Target(python_version="3.9", os="linux", arch="x86_64")
    with (
        patch("feu.install.api.find_closest_version", Mock(return_value="2.0.2")) as find_mock,
        patch("feu.install.installer.run_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"),
            package=PackageSpec(name="numpy", version="2.3.0"),
            target=target,
        )
        find_mock.assert_called_once_with(pkg_name="numpy", pkg_version="2.3.0", target=target)
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "numpy==2.0.2"])


@pytest.mark.parametrize("version", ["", None])
def test_install_package_closest_version_latest_is_not_pinned(version: str | None) -> None:
    with (
        patch("feu.install.api.resolve_target", Mock(return_value=Target(python_version="3.14"))),
        patch("feu.install.installer.run_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version=version)
        )
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "numpy"])


def test_install_package_closest_version_open_wildcard_is_installed_as_requested() -> None:
    with (
        patch("feu.install.api.resolve_target", Mock(return_value=Target(python_version="3.14"))),
        patch("feu.install.installer.run_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="2.*")
        )
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "numpy==2.*"])


def test_install_package_closest_version_closed_wildcard_is_resolved() -> None:
    with (
        patch("feu.install.api.resolve_target", Mock(return_value=Target(python_version="3.9"))),
        patch("feu.install.installer.run_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="1.*")
        )
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "numpy==1.26.4"])


def test_install_package_closest_version_wildcard_without_match_raises_before_install() -> None:
    with (
        patch("feu.install.api.resolve_target", Mock(return_value=Target(python_version="3.14"))),
        patch("feu.install.installer.run_command") as run_mock,
        pytest.raises(UnsupportedVersionError, match=r"matches '1\.24\.\*'"),
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="1.24.*")
        )
    run_mock.assert_not_called()


def test_install_package_closest_version_invalid_wildcard() -> None:
    with pytest.raises(ValueError, match="invalid version wildcard"):
        install_package_closest_version(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="2.*.1")
        )


#########################################
#     Tests for the installer registry  #
#########################################


def test_install_package_unknown_installer() -> None:
    with pytest.raises(RuntimeError, match=r"No installer is registered for the name 'nope'"):
        install_package(
            installer=InstallerSpec("nope"), package=PackageSpec(name="numpy", version="2.0.0")
        )


def test_install_package_unknown_installer_lists_available_installers() -> None:
    with pytest.raises(RuntimeError, match=r"Available installers: \['pip', 'uv'\]"):
        install_package(
            installer=InstallerSpec("nope"), package=PackageSpec(name="numpy", version="2.0.0")
        )


def test_install_package_installer_name_is_case_insensitive() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        install_package(
            installer=InstallerSpec("PIP"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "numpy==2.0.0"])


def test_install_package_custom_registry() -> None:
    registry = Registry[type[Installer]]("installer", normalize=str.lower)
    registry.register("custom", UvInstaller)
    with patch("feu.install.installer.run_command") as run_mock:
        install_package(
            installer=InstallerSpec("custom"),
            package=PackageSpec(name="numpy", version="2.0.0"),
            registry=registry,
        )
        run_mock.assert_called_once_with(
            ["uv", "pip", "install", "--python", sys.executable, "numpy==2.0.0"]
        )


def test_install_package_custom_registry_does_not_know_default_installers() -> None:
    with pytest.raises(RuntimeError, match=r"No installer is registered for the name 'pip'"):
        install_package(
            installer=InstallerSpec("pip"),
            package=PackageSpec(name="numpy", version="2.0.0"),
            registry=Registry[type[Installer]]("installer"),
        )


def test_install_package_installer_arguments_are_passed() -> None:
    with patch("feu.install.installer.run_command") as run_mock:
        install_package(
            installer=InstallerSpec("pip", arguments=["--index-url", "a b"]),
            package=PackageSpec(name="numpy", version="2.0.0"),
        )
        run_mock.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "--index-url", "a b", "numpy==2.0.0"]
        )


def test_install_package_closest_version_custom_registry() -> None:
    registry = Registry[type[Installer]]("installer")
    registry.register("pip", PipInstaller)
    with patch("feu.install.installer.run_command") as run_mock:
        install_package_closest_version(
            installer=InstallerSpec("pip"),
            package=PackageSpec(name="numpy", version="2.0.0"),
            target=Target(python_version="3.12"),
            registry=registry,
        )
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "numpy==2.0.0"])


#############################################
#     Tests for the availability caches     #
#############################################


def test_install_package_clears_the_availability_caches_after_a_success() -> None:
    with (
        patch("feu.install.installer.run_command"),
        patch("feu.install.api.clear_availability_caches") as clear_mock,
    ):
        install_package(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        clear_mock.assert_called_once_with()


def test_install_package_does_not_clear_the_availability_caches_after_a_failure() -> None:
    with (
        patch("feu.install.installer.run_command", Mock(side_effect=RuntimeError("boom"))),
        patch("feu.install.api.clear_availability_caches") as clear_mock,
        pytest.raises(RuntimeError, match="boom"),
    ):
        install_package(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="2.0.0")
        )
    clear_mock.assert_not_called()


def test_install_package_refreshes_package_available() -> None:
    with patch("feu.imports.package.find_spec", Mock(return_value=None)):
        assert not package_available("feu_probe_package")
    with patch("feu.install.installer.run_command"):
        install_package(
            installer=InstallerSpec("pip"), package=PackageSpec(name="feu_probe_package")
        )
    with patch("feu.imports.package.find_spec", Mock(return_value=object())):
        assert package_available("feu_probe_package")
