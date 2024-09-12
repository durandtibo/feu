from __future__ import annotations

from unittest.mock import patch

import pytest

from feu.package import PackageConfig, is_valid_version

###################################
#     Tests for PackageConfig     #
###################################


@patch.dict(PackageConfig.registry, {}, clear=True)
def test_package_config_add_config() -> None:
    PackageConfig.add_config(
        pkg_name="my_package",
        python_version="3.11",
        pkg_version_min="1.2.0",
        pkg_version_max="2.0.2",
    )
    assert PackageConfig.registry == {"my_package": {"3.11": {"min": "1.2.0", "max": "2.0.2"}}}


@patch.dict(PackageConfig.registry, {}, clear=True)
def test_package_config_add_config_multiple() -> None:
    PackageConfig.add_config(
        pkg_name="my_package",
        python_version="3.11",
        pkg_version_min="1.2.0",
        pkg_version_max="2.0.2",
    )
    PackageConfig.add_config(
        pkg_name="my_package",
        python_version="3.10",
        pkg_version_min="1.1.0",
        pkg_version_max="1.5.2",
    )
    assert PackageConfig.registry == {
        "my_package": {
            "3.10": {"min": "1.1.0", "max": "1.5.2"},
            "3.11": {"min": "1.2.0", "max": "2.0.2"},
        }
    }


@patch.dict(
    PackageConfig.registry,
    {"my_package": {"3.11": {"min": "1.1.0", "max": "1.5.2"}}},
    clear=True,
)
def test_package_config_add_config_exist_ok_false() -> None:
    with pytest.raises(
        RuntimeError, match="A package configuration .* is already registered for package"
    ):
        PackageConfig.add_config(
            pkg_name="my_package",
            python_version="3.11",
            pkg_version_min="1.2.0",
            pkg_version_max="2.0.2",
        )


@patch.dict(
    PackageConfig.registry,
    {"my_package": {"3.11": {"min": "1.1.0", "max": "1.5.2"}}},
    clear=True,
)
def test_package_config_add_config_exist_ok_true() -> None:
    PackageConfig.add_config(
        pkg_name="my_package",
        python_version="3.11",
        pkg_version_min="1.2.0",
        pkg_version_max="2.0.2",
        exist_ok=True,
    )
    assert PackageConfig.registry == {"my_package": {"3.11": {"min": "1.2.0", "max": "2.0.2"}}}


@patch.dict(
    PackageConfig.registry,
    {"my_package": {"3.11": {"min": "1.2.0", "max": "2.0.2"}}},
    clear=True,
)
def test_package_config_get_config() -> None:
    assert PackageConfig.get_config(pkg_name="my_package", python_version="3.11") == {
        "min": "1.2.0",
        "max": "2.0.2",
    }


@patch.dict(PackageConfig.registry, {}, clear=True)
def test_package_config_get_config_empty() -> None:
    assert PackageConfig.get_config(pkg_name="my_package", python_version="3.11") == {}


@patch.dict(PackageConfig.registry, {"my_package": {}}, clear=True)
def test_package_config_get_config_empty_pkg_name() -> None:
    assert PackageConfig.get_config(pkg_name="my_package", python_version="3.11") == {}


@patch.dict(PackageConfig.registry, {"my_package": {"3.11": {}}}, clear=True)
def test_package_config_get_config_empty_python_version() -> None:
    assert PackageConfig.get_config(pkg_name="my_package", python_version="3.11") == {}


@patch.dict(
    PackageConfig.registry,
    {"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}},
    clear=True,
)
def test_package_config_is_valid_version_true() -> None:
    assert PackageConfig.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )


@patch.dict(
    PackageConfig.registry,
    {"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}},
    clear=True,
)
def test_package_config_is_valid_version_false_min() -> None:
    assert not PackageConfig.is_valid_version(
        pkg_name="my_package", pkg_version="1.0.0", python_version="3.11"
    )


@patch.dict(
    PackageConfig.registry,
    {"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}},
    clear=True,
)
def test_package_config_is_valid_version_false_max() -> None:
    assert not PackageConfig.is_valid_version(
        pkg_name="my_package", pkg_version="3.0.0", python_version="3.11"
    )


@patch.dict(
    PackageConfig.registry, {"my_package": {"3.11": {"min": "1.2.0", "max": None}}}, clear=True
)
def test_package_config_is_valid_version_min_true() -> None:
    assert PackageConfig.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )


@patch.dict(
    PackageConfig.registry, {"my_package": {"3.11": {"min": "2.2.0", "max": None}}}, clear=True
)
def test_package_config_is_valid_version_min_false() -> None:
    assert not PackageConfig.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )


@patch.dict(
    PackageConfig.registry, {"my_package": {"3.11": {"min": None, "max": "2.2.0"}}}, clear=True
)
def test_package_config_is_valid_version_max_true() -> None:
    assert PackageConfig.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )


@patch.dict(
    PackageConfig.registry, {"my_package": {"3.11": {"min": None, "max": "1.2.0"}}}, clear=True
)
def test_package_config_is_valid_version_max_false() -> None:
    assert not PackageConfig.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )


@patch.dict(PackageConfig.registry, {}, clear=True)
def test_package_config_is_valid_version_empty() -> None:
    assert PackageConfig.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )


######################################
#     Tests for is_valid_version     #
######################################


@patch.dict(
    PackageConfig.registry,
    {"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}},
    clear=True,
)
def test_is_valid_version_true() -> None:
    assert is_valid_version(pkg_name="my_package", pkg_version="2.0.0", python_version="3.11")


@patch.dict(
    PackageConfig.registry,
    {"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}},
    clear=True,
)
def test_is_valid_version_false_min() -> None:
    assert not is_valid_version(pkg_name="my_package", pkg_version="1.0.0", python_version="3.11")


@patch.dict(
    PackageConfig.registry,
    {"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}},
    clear=True,
)
def test_is_valid_version_false_max() -> None:
    assert not is_valid_version(pkg_name="my_package", pkg_version="3.0.0", python_version="3.11")


@patch.dict(
    PackageConfig.registry, {"my_package": {"3.11": {"min": "1.2.0", "max": None}}}, clear=True
)
def test_is_valid_version_min_true() -> None:
    assert is_valid_version(pkg_name="my_package", pkg_version="2.0.0", python_version="3.11")


@patch.dict(
    PackageConfig.registry, {"my_package": {"3.11": {"min": "2.2.0", "max": None}}}, clear=True
)
def test_is_valid_version_min_false() -> None:
    assert not is_valid_version(pkg_name="my_package", pkg_version="2.0.0", python_version="3.11")


@patch.dict(
    PackageConfig.registry, {"my_package": {"3.11": {"min": None, "max": "2.2.0"}}}, clear=True
)
def test_is_valid_version_max_true() -> None:
    assert is_valid_version(pkg_name="my_package", pkg_version="2.0.0", python_version="3.11")


@patch.dict(
    PackageConfig.registry, {"my_package": {"3.11": {"min": None, "max": "1.2.0"}}}, clear=True
)
def test_is_valid_version_max_false() -> None:
    assert not is_valid_version(pkg_name="my_package", pkg_version="2.0.0", python_version="3.11")


@patch.dict(PackageConfig.registry, {}, clear=True)
def test_is_valid_version_empty() -> None:
    assert is_valid_version(pkg_name="my_package", pkg_version="2.0.0", python_version="3.11")
