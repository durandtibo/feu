from __future__ import annotations

from unittest.mock import patch

import pytest

from feu.package import PackageValidator

######################################
#     Tests for PackageValidator     #
######################################


@patch.dict(PackageValidator.registry, {}, clear=True)
def test_package_validator_add_package_config() -> None:
    PackageValidator.add_package_config(
        pkg_name="numpy", python_version="3.11", pkg_version_min="1.2.0", pkg_version_max="2.0.2"
    )
    assert PackageValidator.registry == {
        "numpy": {"3.11": {"default": {"min": "1.2.0", "max": "2.0.2"}}}
    }


@patch.dict(PackageValidator.registry, {}, clear=True)
def test_package_validator_add_package_config_multiple() -> None:
    PackageValidator.add_package_config(
        pkg_name="numpy", python_version="3.11", pkg_version_min="1.2.0", pkg_version_max="2.0.2"
    )
    PackageValidator.add_package_config(
        pkg_name="numpy", python_version="3.10", pkg_version_min="1.1.0", pkg_version_max="1.5.2"
    )
    assert PackageValidator.registry == {
        "numpy": {
            "3.10": {"default": {"min": "1.1.0", "max": "1.5.2"}},
            "3.11": {"default": {"min": "1.2.0", "max": "2.0.2"}},
        }
    }


@patch.dict(
    PackageValidator.registry,
    {"numpy": {"3.11": {"default": {"min": "1.1.0", "max": "1.5.2"}}}},
    clear=True,
)
def test_package_validator_add_package_config_exist_ok_false() -> None:
    with pytest.raises(
        RuntimeError, match="A package configuration .* is already registered for package"
    ):
        PackageValidator.add_package_config(
            pkg_name="numpy",
            python_version="3.11",
            pkg_version_min="1.2.0",
            pkg_version_max="2.0.2",
        )


@patch.dict(
    PackageValidator.registry,
    {"numpy": {"3.11": {"default": {"min": "1.1.0", "max": "1.5.2"}}}},
    clear=True,
)
def test_package_validator_add_package_config_exist_ok_true() -> None:
    PackageValidator.add_package_config(
        pkg_name="numpy",
        python_version="3.11",
        pkg_version_min="1.2.0",
        pkg_version_max="2.0.2",
        exist_ok=True,
    )
    assert PackageValidator.registry == {
        "numpy": {"3.11": {"default": {"min": "1.2.0", "max": "2.0.2"}}}
    }


@patch.dict(
    PackageValidator.registry,
    {"numpy": {"3.11": {"default": {"min": "1.2.0", "max": "2.0.2"}}}},
    clear=True,
)
def test_package_validator_get_package_config() -> None:
    assert PackageValidator.get_package_config(pkg_name="numpy", python_version="3.11") == {
        "min": "1.2.0",
        "max": "2.0.2",
    }


@patch.dict(
    PackageValidator.registry,
    {
        "numpy": {
            "3.11": {
                "default": {"min": "1.2.0", "max": "2.0.2"},
                "ubuntu": {"min": "1.2.0", "max": "1.5.2"},
            }
        }
    },
    clear=True,
)
def test_package_validator_get_package_config_os() -> None:
    assert PackageValidator.get_package_config(
        pkg_name="numpy", python_version="3.11", os="ubuntu"
    ) == {"min": "1.2.0", "max": "1.5.2"}


@patch.dict(
    PackageValidator.registry,
    {
        "numpy": {
            "3.11": {
                "default": {"min": "1.2.0", "max": "2.0.2"},
                "ubuntu": {"min": "1.2.0", "max": "1.5.2"},
            }
        }
    },
    clear=True,
)
def test_package_validator_get_package_config_os_missing() -> None:
    assert PackageValidator.get_package_config(
        pkg_name="numpy", python_version="3.11", os="ubuntu-missing"
    ) == {"min": "1.2.0", "max": "2.0.2"}


@patch.dict(PackageValidator.registry, {}, clear=True)
def test_package_validator_get_package_config_empty() -> None:
    assert PackageValidator.get_package_config(pkg_name="numpy", python_version="3.11") == {}


@patch.dict(PackageValidator.registry, {"numpy": {}}, clear=True)
def test_package_validator_get_package_config_empty_pkg_name() -> None:
    assert PackageValidator.get_package_config(pkg_name="numpy", python_version="3.11") == {}


@patch.dict(PackageValidator.registry, {"numpy": {"3.11": {}}}, clear=True)
def test_package_validator_get_package_config_empty_python_version() -> None:
    assert PackageValidator.get_package_config(pkg_name="numpy", python_version="3.11") == {}
