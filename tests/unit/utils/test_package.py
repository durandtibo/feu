from __future__ import annotations

import dataclasses

import pytest
from packaging.requirements import Requirement

from feu.utils.package import PackageSpec

#################################
#     Tests for PackageSpec     #
#################################


def test_package_spec_name() -> None:
    assert PackageSpec("my_package").name == "my_package"


def test_package_spec_version_default_is_latest() -> None:
    assert PackageSpec("my_package").version == ""


def test_package_spec_version() -> None:
    assert PackageSpec("my_package", version="1.2.3").version == "1.2.3"


def test_package_spec_version_none_is_latest() -> None:
    assert PackageSpec("my_package", version=None).version == ""


def test_package_spec_extras_default() -> None:
    assert PackageSpec("my_package").extras == ()


def test_package_spec_extras_list_becomes_tuple() -> None:
    assert PackageSpec("my_package", extras=["security", "socks"]).extras == ("security", "socks")


def test_package_spec_extras_none() -> None:
    assert PackageSpec("my_package", extras=None).extras == ()


def test_package_spec_repr() -> None:
    assert (
        repr(PackageSpec("my_package", version="1.2.3", extras=["dev"]))
        == "PackageSpec(name='my_package', version='1.2.3', extras=('dev',))"
    )


def test_package_spec_is_frozen() -> None:
    spec = PackageSpec("my_package")
    with pytest.raises(dataclasses.FrozenInstanceError, match="cannot assign to field 'name'"):
        spec.name = "other"  # ty: ignore[invalid-assignment]


def test_package_spec_is_hashable() -> None:
    assert hash(PackageSpec("my_package", extras=["dev"])) == hash(
        PackageSpec("my_package", extras=("dev",))
    )


def test_package_spec_str_name() -> None:
    assert str(PackageSpec("my_package")) == "my_package"


def test_package_spec_str_version() -> None:
    assert str(PackageSpec("my_package", version="1.2.3")) == "my_package==1.2.3"


def test_package_spec_str_empty_version() -> None:
    assert str(PackageSpec("my_package", version="")) == "my_package"


def test_package_spec_str_extras() -> None:
    assert (
        str(PackageSpec("my_package", version="1.2.3", extras=["security", "socks"]))
        == "my_package[security,socks]==1.2.3"
    )


def test_package_spec_str_extras_empty() -> None:
    assert str(PackageSpec("my_package", extras=[])) == "my_package"


def test_package_spec_str_wildcard_version() -> None:
    assert str(PackageSpec("my_package", version="1.2.*")) == "my_package==1.2.*"


def test_package_spec_to_requirement() -> None:
    assert PackageSpec("my_package", version="1.2.3").to_requirement() == Requirement(
        "my_package==1.2.3"
    )


def test_package_spec_to_requirement_no_version() -> None:
    assert str(PackageSpec("my_package").to_requirement()) == "my_package"


def test_package_spec_to_requirement_extras() -> None:
    assert str(PackageSpec("my_package", extras=["b", "a"]).to_requirement()) == "my_package[a,b]"


def test_package_spec_to_requirement_wildcard_version() -> None:
    assert str(PackageSpec("my_package", version="1.2.*").to_requirement()) == "my_package==1.2.*"


def test_package_spec_eq_true() -> None:
    assert PackageSpec("my_package", "1.2.3", ["dev"]) == PackageSpec(
        "my_package", "1.2.3", ("dev",)
    )


def test_package_spec_eq_true_none_and_empty_version() -> None:
    assert PackageSpec("my_package", None) == PackageSpec("my_package", "")


def test_package_spec_eq_false_different_name() -> None:
    assert PackageSpec("my_package") != PackageSpec("other")


def test_package_spec_eq_false_different_version() -> None:
    assert PackageSpec("my_package", "1.2.3") != PackageSpec("my_package", "1.2.4")


def test_package_spec_eq_false_different_extras() -> None:
    assert PackageSpec("my_package", extras=["a"]) != PackageSpec("my_package", extras=["b"])


def test_package_spec_with_version() -> None:
    assert PackageSpec("my_package", "1.2.0").with_version("1.2.3") == PackageSpec(
        "my_package", "1.2.3"
    )


def test_package_spec_with_version_none() -> None:
    assert PackageSpec("my_package", "1.2.0").with_version(None).version == ""


def test_package_spec_with_version_keeps_extras() -> None:
    assert PackageSpec("my_package", "1.2.0", ["dev"]).with_version("1.2.3").extras == ("dev",)


def test_package_spec_with_version_does_not_change_the_original() -> None:
    spec = PackageSpec("my_package", "1.2.0")
    spec.with_version("1.2.3")
    assert spec.version == "1.2.0"
