from __future__ import annotations

import pytest

from feu.install.pip.resolver2 import (
    DependencyResolver,
    JaxDependencyResolver,
    Numpy2DependencyResolver,
)
from feu.utils.package import Package, PackageDependency

########################################
#     Tests for DependencyResolver     #
########################################


def test_dependency_resolver_repr() -> None:
    assert repr(DependencyResolver()).startswith("DependencyResolver(")


def test_dependency_resolver_str() -> None:
    assert str(DependencyResolver()).startswith("DependencyResolver(")


def test_dependency_resolver_equal_true() -> None:
    assert DependencyResolver().equal(DependencyResolver())


def test_dependency_resolver_equal_false_different_type() -> None:
    assert not DependencyResolver().equal(42)


def test_dependency_resolver_resolve() -> None:
    assert DependencyResolver().resolve(Package(name="my_package", version="1.2.3")) == [
        PackageDependency(name="my_package", version_specifiers=["==1.2.3"])
    ]


def test_dependency_resolver_resolve_no_version() -> None:
    assert DependencyResolver().resolve(Package(name="my_package")) == [
        PackageDependency(name="my_package")
    ]


def test_dependency_resolver_resolve_with_extras() -> None:
    assert DependencyResolver().resolve(
        Package(name="my_package", version="1.2.3", extras=["dev"])
    ) == [PackageDependency(name="my_package", version_specifiers=["==1.2.3"], extras=["dev"])]


def test_dependency_resolver_resolve_with_extras_empty() -> None:
    assert DependencyResolver().resolve(Package(name="my_package", version="1.2.3", extras=[])) == [
        PackageDependency(name="my_package", version_specifiers=["==1.2.3"], extras=[])
    ]


###########################################
#     Tests for JaxDependencyResolver     #
###########################################


def test_jax_dependency_resolver_repr() -> None:
    assert repr(JaxDependencyResolver()).startswith("JaxDependencyResolver(")


def test_jax_dependency_resolver_str() -> None:
    assert str(JaxDependencyResolver()).startswith("JaxDependencyResolver(")


def test_jax_dependency_resolver_equal_true() -> None:
    assert JaxDependencyResolver().equal(JaxDependencyResolver())


def test_jax_dependency_resolver_equal_false() -> None:
    assert not JaxDependencyResolver().equal(42)


def test_jax_dependency_resolver_resolve() -> None:
    assert JaxDependencyResolver().resolve(Package(name="jax", version="0.4.26")) == [
        PackageDependency(name="jax", version_specifiers=["==0.4.26"]),
        PackageDependency(name="jaxlib", version_specifiers=["==0.4.26"]),
    ]


def test_jax_dependency_resolver_resolve_high() -> None:
    assert JaxDependencyResolver().resolve(Package(name="jax", version="0.4.27")) == [
        PackageDependency(name="jax", version_specifiers=["==0.4.27"]),
        PackageDependency(name="jaxlib", version_specifiers=["==0.4.27"]),
    ]


def test_jax_dependency_resolver_resolve_low() -> None:
    assert JaxDependencyResolver().resolve(Package(name="jax", version="0.4.25")) == [
        PackageDependency(name="jax", version_specifiers=["==0.4.25"]),
        PackageDependency(name="jaxlib", version_specifiers=["==0.4.25"]),
        PackageDependency(name="numpy", version_specifiers=["<2.0.0"]),
    ]


@pytest.mark.parametrize("version", ["0.4.9", "0.4.10", "0.4.11"])
def test_jax_dependency_resolver_resolve_ml_dtypes(version: str) -> None:
    assert JaxDependencyResolver().resolve(Package(name="jax", version=version)) == [
        PackageDependency(name="jax", version_specifiers=[f"=={version}"]),
        PackageDependency(name="jaxlib", version_specifiers=[f"=={version}"]),
        PackageDependency(name="numpy", version_specifiers=["<2.0.0"]),
        PackageDependency(name="ml_dtypes", version_specifiers=["<=0.2.0"]),
    ]


def test_jax_dependency_resolver_resolve_with_extras() -> None:
    assert JaxDependencyResolver().resolve(
        Package(name="jax", version="0.4.26", extras=["dev"])
    ) == [
        PackageDependency(name="jax", version_specifiers=["==0.4.26"], extras=["dev"]),
        PackageDependency(name="jaxlib", version_specifiers=["==0.4.26"]),
    ]


##############################################
#     Tests for Numpy2DependencyResolver     #
##############################################


def test_numpy2_dependency_resolver_repr() -> None:
    assert repr(Numpy2DependencyResolver(min_version="1.2.3")).startswith(
        "Numpy2DependencyResolver("
    )


def test_numpy2_dependency_resolver_str() -> None:
    assert str(Numpy2DependencyResolver(min_version="1.2.3")).startswith(
        "Numpy2DependencyResolver("
    )


def test_numpy2_dependency_resolver_equal_true() -> None:
    assert Numpy2DependencyResolver(min_version="1.2.3").equal(
        Numpy2DependencyResolver(min_version="1.2.3")
    )


def test_numpy2_dependency_resolver_equal_false_different_min_version() -> None:
    assert not Numpy2DependencyResolver(min_version="1.2.3").equal(
        Numpy2DependencyResolver(min_version="2.0.0")
    )


def test_numpy2_dependency_resolver_equal_false_different_type() -> None:
    assert not Numpy2DependencyResolver(min_version="1.2.3").equal(42)


def test_numpy2_dependency_resolver_resolve() -> None:
    assert Numpy2DependencyResolver(min_version="1.2.3").resolve(
        Package(name="my_package", version="1.2.3")
    ) == [PackageDependency(name="my_package", version_specifiers=["==1.2.3"])]


def test_numpy2_dependency_resolver_resolve_high() -> None:
    assert Numpy2DependencyResolver(min_version="1.2.3").resolve(
        Package(name="my_package", version="1.3.0")
    ) == [PackageDependency(name="my_package", version_specifiers=["==1.3.0"])]


def test_numpy2_dependency_resolver_resolve_low() -> None:
    assert Numpy2DependencyResolver(min_version="1.2.3").resolve(
        Package(name="my_package", version="1.2.0")
    ) == [
        PackageDependency(name="my_package", version_specifiers=["==1.2.0"]),
        PackageDependency(name="numpy", version_specifiers=["<2.0.0"]),
    ]


def test_numpy2_dependency_resolver_resolve_with_extras() -> None:
    assert Numpy2DependencyResolver(min_version="1.2.3").resolve(
        Package(name="my_package", version="1.2.3", extras=["dev"])
    ) == [PackageDependency(name="my_package", version_specifiers=["==1.2.3"], extras=["dev"])]
