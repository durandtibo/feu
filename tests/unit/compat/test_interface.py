from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from feu.compat.interface import (
    find_closest_version,
    get_compatible_versions,
    get_default_compat_registry,
    is_valid_version,
    register_compat,
)
from feu.compat.registry import CompatRegistry, VersionRange
from feu.compat.shipped import ShippedData
from feu.compat.target import Target

if TYPE_CHECKING:
    from collections.abc import Generator

T311 = Target(python_version="3.11")


######################################
#     Tests for get_default_compat_registry #
######################################


@pytest.fixture(autouse=True)
def _reset_default_registry() -> Generator[None]:
    get_default_compat_registry.cache_clear()
    yield
    get_default_compat_registry.cache_clear()


def test_get_default_compat_registry_returns_compat_registry() -> None:
    registry = get_default_compat_registry()
    assert isinstance(registry, CompatRegistry)


def test_get_default_compat_registry_is_singleton() -> None:
    registry1 = get_default_compat_registry()
    registry2 = get_default_compat_registry()
    assert registry1 is registry2


def test_get_default_compat_registry_uses_the_shipped_data() -> None:
    assert "numpy" in get_default_compat_registry().packages()


def test_get_default_compat_registry_does_not_load_a_package_at_creation() -> None:
    with patch.object(ShippedData, "load") as load_mock:
        get_default_compat_registry()
        load_mock.assert_not_called()


def test_get_default_compat_registry_loads_a_package_on_first_lookup() -> None:
    registry = get_default_compat_registry()
    with patch.object(ShippedData, "load", wraps=ShippedData().load) as load_mock:
        registry.has_package("numpy")
        registry.has_package("numpy")
        load_mock.assert_called_once_with("numpy")


#################################
#     Tests for register_compat #
#################################


def test_register_compat_adds_to_registry() -> None:
    register_compat({"my_package": {T311: [VersionRange("1.0.0", None)]}})
    registry = get_default_compat_registry()
    assert registry.get_config(pkg_name="my_package", target=T311) == [VersionRange("1.0.0", None)]
    assert registry.state["my-package"] == {T311: [VersionRange("1.0.0", None)]}


def test_register_compat_exist_ok_false_raises() -> None:
    register_compat({"my_package": {T311: [VersionRange("1.0.0", None)]}})
    with pytest.raises(RuntimeError, match=r"A package configuration .* is already registered"):
        register_compat({"my_package": {T311: [VersionRange("2.0.0", None)]}})


def test_register_compat_numpy_without_exist_ok() -> None:
    register_compat({"numpy": {T311: [VersionRange("9.9.9", None)]}})
    assert get_default_compat_registry().state["numpy"][T311] == [VersionRange("9.9.9", None)]


########################################
#     Tests for find_closest_version   #
########################################


def test_find_closest_version_delegates_to_default_registry() -> None:
    with patch.object(CompatRegistry, "find_closest_version", return_value="1.2.3") as mock_find:
        result = find_closest_version(pkg_name="numpy", pkg_version="2.0.2", target=T311)
    assert result == "1.2.3"
    mock_find.assert_called_once_with(pkg_name="numpy", pkg_version="2.0.2", target=T311)


def test_find_closest_version_unknown_package_is_permissive() -> None:
    assert (
        find_closest_version(pkg_name="not-a-real-package", pkg_version="0.1.0", target=T311)
        == "0.1.0"
    )


##################################
#     Tests for is_valid_version #
##################################


def test_is_valid_version_delegates_to_default_registry() -> None:
    with patch.object(CompatRegistry, "is_valid_version", return_value=False) as mock_valid:
        result = is_valid_version(pkg_name="numpy", pkg_version="2.0.2", target=T311)
    assert result is False
    mock_valid.assert_called_once_with(pkg_name="numpy", pkg_version="2.0.2", target=T311)


def test_is_valid_version_unknown_package_is_permissive() -> None:
    assert is_valid_version(pkg_name="not-a-real-package", pkg_version="0.1.0", target=T311)


########################################
#     Tests for get_compatible_versions #
########################################


def test_get_compatible_versions_delegates_to_default_registry() -> None:
    with patch.object(
        CompatRegistry, "get_compatible_versions", return_value=["1.2.3"]
    ) as mock_versions:
        result = get_compatible_versions("numpy", T311, "1.*")
    assert result == ["1.2.3"]
    mock_versions.assert_called_once_with("numpy", T311, "1.*")


def test_get_compatible_versions_custom_registry() -> None:
    registry = CompatRegistry()
    registry.register_versions("numpy", ["1.0.0", "2.0.0"])
    assert get_compatible_versions("numpy", T311, "2.*", registry=registry) == ["2.0.0"]


def test_find_closest_version_custom_registry() -> None:
    registry = CompatRegistry({"numpy": {T311: [VersionRange("1.0.0", "1.5.0")]}})
    assert find_closest_version("numpy", "2.0.0", T311, registry=registry) == "1.5.0"


def test_is_valid_version_custom_registry() -> None:
    registry = CompatRegistry({"numpy": {T311: [VersionRange("1.0.0", "1.5.0")]}})
    assert not is_valid_version("numpy", "2.0.0", T311, registry=registry)
