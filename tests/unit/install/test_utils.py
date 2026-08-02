from unittest.mock import Mock, call, patch

import pytest

from feu.compat import Target
from feu.install import (
    InstallResult,
    get_available_installers,
    get_installable_versions,
    install_all_versions,
    install_package,
    install_package_closest_version,
    install_packages_all_versions,
    is_pip_available,
    is_pipx_available,
    is_uv_available,
)
from feu.testing import pip_available, pipx_available, uv_available
from feu.utils.installer import InstallerSpec
from feu.utils.package import PackageSpec


@pytest.fixture(autouse=True)
def _reset() -> None:
    is_pip_available.cache_clear()
    is_pipx_available.cache_clear()
    is_uv_available.cache_clear()
    get_available_installers.cache_clear()


#####################################
#     Tests for install_package     #
#####################################


def test_install_package_pip_numpy() -> None:
    with patch("feu.install.pip.installer.run_bash_command") as run_mock:
        install_package(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with("pip install numpy==2.0.0")


def test_install_package_pip_pandas() -> None:
    with patch("feu.install.pip.installer.run_bash_command") as run_mock:
        install_package(
            installer=InstallerSpec("pip"), package=PackageSpec(name="pandas", version="2.1.1")
        )
        run_mock.assert_called_once_with("pip install pandas==2.1.1 numpy<2.0.0")


def test_install_package_uv_numpy() -> None:
    with patch("feu.install.pip.installer.run_bash_command") as run_mock:
        install_package(
            installer=InstallerSpec("uv"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with("uv pip install numpy==2.0.0")


def test_install_package_pip_numpy_with_args() -> None:
    with patch("feu.install.pip.installer.run_bash_command") as run_mock:
        install_package(
            installer=InstallerSpec("pip", arguments="-U"),
            package=PackageSpec(name="numpy", version="2.0.0"),
        )
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")


#####################################################
#     Tests for install_package_closest_version     #
#####################################################


def test_install_package_closest_version_pip_numpy() -> None:
    with (
        patch("feu.install.utils.get_python_major_minor", Mock(return_value="3.12")),
        patch("feu.install.pip.installer.run_bash_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with("pip install numpy==2.0.0")


def test_install_package_closest_version_pip_pandas() -> None:
    with (
        patch("feu.install.utils.get_python_major_minor", Mock(return_value="3.12")),
        patch("feu.install.pip.installer.run_bash_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"), package=PackageSpec(name="pandas", version="2.1.1")
        )
        run_mock.assert_called_once_with("pip install pandas==2.1.1 numpy<2.0.0")


def test_install_package_closest_version_uv_numpy() -> None:
    with (
        patch("feu.install.utils.get_python_major_minor", Mock(return_value="3.12")),
        patch("feu.install.pip.installer.run_bash_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("uv"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with("uv pip install numpy==2.0.0")


def test_install_package_closest_version_pip_numpy_with_args() -> None:
    with (
        patch("feu.install.utils.get_python_major_minor", Mock(return_value="3.12")),
        patch("feu.install.pip.installer.run_bash_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip", arguments="-U"),
            package=PackageSpec(name="numpy", version="2.0.0"),
        )
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")


def test_install_package_closest_version_missing_package_version() -> None:
    with (
        patch("feu.install.utils.get_python_major_minor", Mock(return_value="3.12")),
        pytest.raises(RuntimeError, match="A package version must be specified for numpy"),
    ):
        install_package_closest_version(
            installer=InstallerSpec("uv"), package=PackageSpec(name="numpy")
        )


#############################################
#     Tests for get_installable_versions     #
#############################################


def test_get_installable_versions() -> None:
    with patch(
        "feu.install.utils.fetch_pypi_versions",
        Mock(return_value=("1.0.0", "1.0.0a1", "1.1.0", "2.0.0")),
    ):
        assert get_installable_versions("my_package", target=Target(python_version="3.11")) == [
            "1.0.0",
            "1.1.0",
            "2.0.0",
        ]


def test_get_installable_versions_start_date() -> None:
    fetch_mock = Mock(return_value=("1.0.0", "1.1.0", "2.0.0"))
    with patch("feu.install.utils.fetch_pypi_versions", fetch_mock):
        assert get_installable_versions(
            "my_package", target=Target(python_version="3.11"), start_date="2024-01-01"
        ) == ["1.0.0", "1.1.0", "2.0.0"]
        fetch_mock.assert_called_once_with("my_package", start_date="2024-01-01")


def test_get_installable_versions_filters_incompatible() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.side_effect = lambda **kwargs: kwargs["pkg_version"] != "1.1.0"
    with (
        patch(
            "feu.install.utils.fetch_pypi_versions",
            Mock(return_value=("1.0.0", "1.1.0", "2.0.0")),
        ),
        patch("feu.install.utils.get_default_registry", Mock(return_value=registry_mock)),
    ):
        assert get_installable_versions("my_package", target=Target(python_version="3.11")) == [
            "1.0.0",
            "2.0.0",
        ]


######################################
#     Tests for install_all_versions     #
######################################


def test_install_all_versions_pip() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.return_value = True
    with (
        patch(
            "feu.install.utils.fetch_pypi_versions",
            Mock(return_value=("1.0.0", "1.1.0")),
        ),
        patch("feu.install.utils.get_default_registry", Mock(return_value=registry_mock)),
        patch("feu.install.pip.installer.run_bash_command") as run_mock,
    ):
        result = install_all_versions(
            installer=InstallerSpec("pip"),
            package="numpy",
            target=Target(python_version="3.11"),
        )
        run_mock.assert_has_calls(
            [call("pip install numpy==1.0.0"), call("pip install numpy==1.1.0")]
        )
        assert result == InstallResult(installed=["1.0.0", "1.1.0"], failed=[])


def test_install_all_versions_start_date() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.return_value = True
    fetch_mock = Mock(return_value=("1.0.0", "1.1.0"))
    with (
        patch("feu.install.utils.fetch_pypi_versions", fetch_mock),
        patch("feu.install.utils.get_default_registry", Mock(return_value=registry_mock)),
        patch("feu.install.pip.installer.run_bash_command"),
    ):
        install_all_versions(
            installer=InstallerSpec("pip"),
            package="numpy",
            target=Target(python_version="3.11"),
            start_date="2024-01-01",
        )
        fetch_mock.assert_called_once_with("numpy", start_date="2024-01-01")


def test_install_all_versions_with_extras() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.return_value = True
    with (
        patch(
            "feu.install.utils.fetch_pypi_versions",
            Mock(return_value=("1.0.0",)),
        ),
        patch("feu.install.utils.get_default_registry", Mock(return_value=registry_mock)),
        patch("feu.install.pip.installer.run_bash_command") as run_mock,
    ):
        result = install_all_versions(
            installer=InstallerSpec("pip"),
            package="my_package[performance]",
            target=Target(python_version="3.11"),
        )
        run_mock.assert_called_once_with("pip install my_package[performance]==1.0.0")
        assert result == InstallResult(installed=["1.0.0"], failed=[])


def test_install_all_versions_partial_failure() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.return_value = True
    with (
        patch(
            "feu.install.utils.fetch_pypi_versions",
            Mock(return_value=("1.0.0", "1.1.0", "2.0.0")),
        ),
        patch("feu.install.utils.get_default_registry", Mock(return_value=registry_mock)),
        patch(
            "feu.install.pip.installer.run_bash_command",
            Mock(side_effect=[None, RuntimeError("boom"), None]),
        ),
    ):
        result = install_all_versions(
            installer=InstallerSpec("pip"),
            package="numpy",
            target=Target(python_version="3.11"),
        )
        assert result == InstallResult(installed=["1.0.0", "2.0.0"], failed=["1.1.0"])


def test_install_all_versions_all_fail() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.return_value = True
    with (
        patch(
            "feu.install.utils.fetch_pypi_versions",
            Mock(return_value=("1.0.0", "1.1.0")),
        ),
        patch("feu.install.utils.get_default_registry", Mock(return_value=registry_mock)),
        patch(
            "feu.install.pip.installer.run_bash_command",
            Mock(side_effect=RuntimeError("boom")),
        ),
    ):
        result = install_all_versions(
            installer=InstallerSpec("pip"),
            package="numpy",
            target=Target(python_version="3.11"),
        )
        assert result == InstallResult(installed=[], failed=["1.0.0", "1.1.0"])


##############################################
#     Tests for install_packages_all_versions     #
##############################################


def test_install_packages_all_versions() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.return_value = True
    with (
        patch(
            "feu.install.utils.fetch_pypi_versions",
            Mock(return_value=("1.0.0",)),
        ),
        patch("feu.install.utils.get_default_registry", Mock(return_value=registry_mock)),
        patch("feu.install.pip.installer.run_bash_command") as run_mock,
    ):
        result = install_packages_all_versions(
            installer=InstallerSpec("pip"),
            packages=["numpy", "my_package"],
            target=Target(python_version="3.11"),
        )
        run_mock.assert_has_calls(
            [call("pip install numpy==1.0.0"), call("pip install my_package==1.0.0")]
        )
        assert result == {
            "numpy": InstallResult(installed=["1.0.0"], failed=[]),
            "my_package": InstallResult(installed=["1.0.0"], failed=[]),
        }


def test_install_packages_all_versions_start_date() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.return_value = True
    fetch_mock = Mock(return_value=("1.0.0",))
    with (
        patch("feu.install.utils.fetch_pypi_versions", fetch_mock),
        patch("feu.install.utils.get_default_registry", Mock(return_value=registry_mock)),
        patch("feu.install.pip.installer.run_bash_command"),
    ):
        install_packages_all_versions(
            installer=InstallerSpec("pip"),
            packages=["numpy", "my_package"],
            target=Target(python_version="3.11"),
            start_date="2024-01-01",
        )
        fetch_mock.assert_has_calls(
            [call("numpy", start_date="2024-01-01"), call("my_package", start_date="2024-01-01")],
            any_order=True,
        )


def test_install_packages_all_versions_with_failure() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.return_value = True
    with (
        patch(
            "feu.install.utils.fetch_pypi_versions",
            Mock(return_value=("1.0.0", "1.1.0")),
        ),
        patch("feu.install.utils.get_default_registry", Mock(return_value=registry_mock)),
        patch(
            "feu.install.pip.installer.run_bash_command",
            Mock(side_effect=[None, RuntimeError("boom"), None, None]),
        ),
    ):
        result = install_packages_all_versions(
            installer=InstallerSpec("pip"),
            packages=["numpy", "my_package"],
            target=Target(python_version="3.11"),
        )
        assert result == {
            "numpy": InstallResult(installed=["1.0.0"], failed=["1.1.0"]),
            "my_package": InstallResult(installed=["1.0.0", "1.1.0"], failed=[]),
        }


######################################
#     Tests for is_pip_available     #
######################################


def test_is_pip_available() -> None:
    assert isinstance(is_pip_available(), bool)


@pip_available
def test_is_pip_available_true() -> None:
    assert is_pip_available()


#######################################
#     Tests for is_pipx_available     #
#######################################


def test_is_pipx_available() -> None:
    assert isinstance(is_pipx_available(), bool)


@pipx_available
def test_is_pipx_available_true() -> None:
    assert is_pipx_available()


#####################################
#     Tests for is_uv_available     #
#####################################


def test_is_uv_available() -> None:
    assert isinstance(is_uv_available(), bool)


@uv_available
def test_is_uv_available_true() -> None:
    assert is_uv_available()


##############################################
#     Tests for get_available_installers     #
##############################################


@patch("feu.install.utils.is_pip_available", lambda: True)
def test_get_available_installers_pip_available() -> None:
    assert "pip" in get_available_installers()


@patch("feu.install.utils.is_pip_available", lambda: False)
def test_get_available_installers_pip_not_available() -> None:
    assert "pip" not in get_available_installers()


@pip_available
def test_get_available_installers_pip() -> None:
    assert "pip" in get_available_installers()


@patch("feu.install.utils.is_pipx_available", lambda: True)
def test_get_available_installers_pipx_available() -> None:
    assert "pipx" in get_available_installers()


@patch("feu.install.utils.is_pipx_available", lambda: False)
def test_get_available_installers_pipx_not_available() -> None:
    assert "pipx" not in get_available_installers()


@pipx_available
def test_get_available_installers_pipx() -> None:
    assert "pipx" in get_available_installers()


@patch("feu.install.utils.is_uv_available", lambda: True)
def test_get_available_installers_uv_available() -> None:
    assert "uv" in get_available_installers()


@patch("feu.install.utils.is_uv_available", lambda: False)
def test_get_available_installers_uv_not_available() -> None:
    assert "uv" not in get_available_installers()


@uv_available
def test_get_available_installers_uv() -> None:
    assert "uv" in get_available_installers()
