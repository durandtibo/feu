from __future__ import annotations

from unittest.mock import patch

import pytest

from feu.compat.interface import (
    find_closest_version,
    get_default_registry,
    is_valid_version,
    register_compat,
)
from feu.compat.registry import CompatRegistry, VersionRange
from feu.compat.target import Target

T311 = Target(python_version="3.11")


######################################
#     Tests for get_default_registry #
######################################


@pytest.fixture(autouse=True)
def _reset_default_registry() -> None:
    if hasattr(get_default_registry, "_registry"):
        del get_default_registry._registry
    yield
    if hasattr(get_default_registry, "_registry"):
        del get_default_registry._registry


def test_get_default_registry_returns_compat_registry() -> None:
    registry = get_default_registry()
    assert isinstance(registry, CompatRegistry)


def test_get_default_registry_is_singleton() -> None:
    registry1 = get_default_registry()
    registry2 = get_default_registry()
    assert registry1 is registry2


def test_get_default_registry_populated_with_defaults() -> None:
    registry = get_default_registry()
    assert registry.get_config(pkg_name="numpy", target=T311) == [VersionRange("1.23.2", "2.4.6")]


#################################
#     Tests for register_compat #
#################################


def test_register_compat_adds_to_override_layer() -> None:
    register_compat({"my_package": {T311: [VersionRange("1.0.0", None)]}})
    registry = get_default_registry()
    assert registry.get_config(pkg_name="my_package", target=T311) == [VersionRange("1.0.0", None)]
    assert registry.overrides == {"my_package": {T311: [VersionRange("1.0.0", None)]}}


def test_register_compat_exist_ok_false_raises() -> None:
    register_compat({"my_package": {T311: [VersionRange("1.0.0", None)]}})
    with pytest.raises(RuntimeError, match=r"A package configuration .* is already registered"):
        register_compat({"my_package": {T311: [VersionRange("2.0.0", None)]}})


def test_register_compat_overrides_a_default_without_exist_ok() -> None:
    # numpy has a base entry for 3.11; overriding it must not require exist_ok=True.
    register_compat({"numpy": {T311: [VersionRange("9.9.9", None)]}})
    assert get_default_registry().get_config(pkg_name="numpy", target=T311) == [
        VersionRange("9.9.9", None)
    ]


########################################
#     Tests for find_closest_version   #
########################################


def test_find_closest_version_delegates_to_default_registry() -> None:
    with patch.object(CompatRegistry, "find_closest_version", return_value="1.2.3") as mock_find:
        result = find_closest_version(pkg_name="numpy", pkg_version="2.0.2", target=T311)
    assert result == "1.2.3"
    mock_find.assert_called_once_with(pkg_name="numpy", pkg_version="2.0.2", target=T311)


def test_find_closest_version_uses_defaults() -> None:
    assert find_closest_version(pkg_name="numpy", pkg_version="0.1.0", target=T311) == "1.23.2"


##################################
#     Tests for is_valid_version #
##################################


def test_is_valid_version_delegates_to_default_registry() -> None:
    with patch.object(CompatRegistry, "is_valid_version", return_value=False) as mock_valid:
        result = is_valid_version(pkg_name="numpy", pkg_version="2.0.2", target=T311)
    assert result is False
    mock_valid.assert_called_once_with(pkg_name="numpy", pkg_version="2.0.2", target=T311)


def test_is_valid_version_uses_defaults() -> None:
    assert not is_valid_version(pkg_name="numpy", pkg_version="0.1.0", target=T311)
