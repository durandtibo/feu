from __future__ import annotations

from feu.installer.pip import DependencyResolver, Numpy2DependencyResolver

########################################
#     Tests for DependencyResolver     #
########################################


def test_dependency_resolver_repr() -> None:
    assert repr(DependencyResolver("numpy")).startswith("DependencyResolver(")


def test_dependency_resolver_str() -> None:
    assert str(DependencyResolver("numpy")).startswith("DependencyResolver(")


def test_dependency_resolver_resolve() -> None:
    assert DependencyResolver("numpy").resolve("2.3.1") == ("numpy==2.3.1",)


##############################################
#     Tests for Numpy2DependencyResolver     #
##############################################


def test_numpy2_dependency_resolver_repr() -> None:
    assert repr(Numpy2DependencyResolver(package="my_package", min_version="1.2.3")).startswith(
        "Numpy2DependencyResolver("
    )


def test_numpy2_dependency_resolver_str() -> None:
    assert str(Numpy2DependencyResolver(package="my_package", min_version="1.2.3")).startswith(
        "Numpy2DependencyResolver("
    )


def test_numpy2_dependency_resolver_resolve() -> None:
    assert Numpy2DependencyResolver(package="my_package", min_version="1.2.3").resolve("1.2.3") == (
        "my_package==1.2.3",
    )


def test_numpy2_dependency_resolver_resolve_high() -> None:
    assert Numpy2DependencyResolver(package="my_package", min_version="1.2.3").resolve("1.3.0") == (
        "my_package==1.3.0",
    )


def test_numpy2_dependency_resolver_resolve_low() -> None:
    assert Numpy2DependencyResolver(package="my_package", min_version="1.2.3").resolve("1.2.0") == (
        "my_package==1.2.0",
        "numpy<2.0.0",
    )
