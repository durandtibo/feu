from __future__ import annotations

import sys
from unittest.mock import Mock, call, patch

import pytest
from packaging.requirements import InvalidRequirement

from feu.compat import Target
from feu.install import InstallerSpec, InstallResult, get_installable_versions, install_all_versions

#############################################
#     Tests for get_installable_versions     #
#############################################


def test_get_installable_versions() -> None:
    with patch(
        "feu.install.all_versions.fetch_pypi_versions",
        Mock(return_value=("1.0.0", "1.0.0a1", "1.1.0", "2.0.0")),
    ):
        assert get_installable_versions("my_package", target=Target(python_version="3.11")) == [
            "1.0.0",
            "1.1.0",
            "2.0.0",
        ]


def test_get_installable_versions_start_date() -> None:
    fetch_mock = Mock(return_value=("1.0.0", "1.1.0", "2.0.0"))
    with patch("feu.install.all_versions.fetch_pypi_versions", fetch_mock):
        assert get_installable_versions(
            "my_package", target=Target(python_version="3.11"), start_date="2024-01-01"
        ) == ["1.0.0", "1.1.0", "2.0.0"]
        fetch_mock.assert_called_once_with("my_package", start_date="2024-01-01")


def test_get_installable_versions_returns_pep440_order() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.return_value = True
    with (
        patch(
            "feu.install.all_versions.fetch_pypi_versions",
            Mock(return_value=("1.10.0", "1.9.0", "2.0.0")),
        ),
        patch(
            "feu.install.all_versions.get_default_compat_registry",
            Mock(return_value=registry_mock),
        ),
    ):
        assert get_installable_versions("numpy", target=Target(python_version="3.11")) == [
            "1.9.0",
            "1.10.0",
            "2.0.0",
        ]


def test_get_installable_versions_start_date_is_keyword_only() -> None:
    with pytest.raises(TypeError, match="positional argument"):
        get_installable_versions("numpy", Target(python_version="3.11"), "2024-01-01")  # ty: ignore[too-many-positional-arguments]


def test_get_installable_versions_filters_incompatible() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.side_effect = lambda **kwargs: kwargs["pkg_version"] != "1.1.0"
    with (
        patch(
            "feu.install.all_versions.fetch_pypi_versions",
            Mock(return_value=("1.0.0", "1.1.0", "2.0.0")),
        ),
        patch(
            "feu.install.all_versions.get_default_compat_registry", Mock(return_value=registry_mock)
        ),
    ):
        assert get_installable_versions("my_package", target=Target(python_version="3.11")) == [
            "1.0.0",
            "2.0.0",
        ]


######################################
#     Tests for install_all_versions #
######################################


def test_install_all_versions_pip() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.return_value = True
    with (
        patch(
            "feu.install.all_versions.fetch_pypi_versions",
            Mock(return_value=("1.0.0", "1.1.0")),
        ),
        patch(
            "feu.install.all_versions.get_default_compat_registry", Mock(return_value=registry_mock)
        ),
        patch("feu.install.installer.run_command") as run_mock,
    ):
        result = install_all_versions(
            installer=InstallerSpec("pip"),
            package="numpy",
            target=Target(python_version="3.11"),
        )
        run_mock.assert_has_calls(
            [
                call([sys.executable, "-m", "pip", "install", "numpy==1.0.0"]),
                call([sys.executable, "-m", "pip", "install", "numpy==1.1.0"]),
            ]
        )
        assert result == InstallResult(installed=["1.0.0", "1.1.0"], failed=[])


def test_install_all_versions_start_date() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.return_value = True
    fetch_mock = Mock(return_value=("1.0.0", "1.1.0"))
    with (
        patch("feu.install.all_versions.fetch_pypi_versions", fetch_mock),
        patch(
            "feu.install.all_versions.get_default_compat_registry", Mock(return_value=registry_mock)
        ),
        patch("feu.install.installer.run_command"),
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
            "feu.install.all_versions.fetch_pypi_versions",
            Mock(return_value=("1.0.0",)),
        ),
        patch(
            "feu.install.all_versions.get_default_compat_registry", Mock(return_value=registry_mock)
        ),
        patch("feu.install.installer.run_command") as run_mock,
    ):
        result = install_all_versions(
            installer=InstallerSpec("pip"),
            package="my_package[performance]",
            target=Target(python_version="3.11"),
        )
        run_mock.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "my_package[performance]==1.0.0"]
        )
        assert result == InstallResult(installed=["1.0.0"], failed=[])


def test_install_all_versions_partial_failure() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.return_value = True
    with (
        patch(
            "feu.install.all_versions.fetch_pypi_versions",
            Mock(return_value=("1.0.0", "1.1.0", "2.0.0")),
        ),
        patch(
            "feu.install.all_versions.get_default_compat_registry", Mock(return_value=registry_mock)
        ),
        patch(
            "feu.install.installer.run_command",
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
            "feu.install.all_versions.fetch_pypi_versions",
            Mock(return_value=("1.0.0", "1.1.0")),
        ),
        patch(
            "feu.install.all_versions.get_default_compat_registry", Mock(return_value=registry_mock)
        ),
        patch(
            "feu.install.installer.run_command",
            Mock(side_effect=RuntimeError("boom")),
        ),
    ):
        result = install_all_versions(
            installer=InstallerSpec("pip"),
            package="numpy",
            target=Target(python_version="3.11"),
        )
        assert result == InstallResult(installed=[], failed=["1.0.0", "1.1.0"])


def test_install_all_versions_extras_are_sorted() -> None:
    registry_mock = Mock()
    registry_mock.is_valid_version.return_value = True
    with (
        patch("feu.install.all_versions.fetch_pypi_versions", Mock(return_value=("1.0.0",))),
        patch(
            "feu.install.all_versions.get_default_compat_registry",
            Mock(return_value=registry_mock),
        ),
        patch("feu.install.installer.run_command") as run_mock,
    ):
        install_all_versions(
            installer=InstallerSpec("pip"),
            package="my_package[b,a]",
            target=Target(python_version="3.11"),
        )
        run_mock.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "my_package[a,b]==1.0.0"]
        )


def test_install_all_versions_invalid_requirement() -> None:
    with pytest.raises(InvalidRequirement, match="not a requirement"):
        install_all_versions(
            installer=InstallerSpec("pip"),
            package="not a requirement!",
            target=Target(python_version="3.11"),
        )


def test_install_all_versions_start_date_is_keyword_only() -> None:
    with pytest.raises(TypeError, match="positional argument"):
        install_all_versions(
            InstallerSpec("pip"),
            "numpy",
            Target(python_version="3.11"),
            "2024-01-01",  # ty: ignore[too-many-positional-arguments]
        )
