from __future__ import annotations

from feu.installer.pip import DependencyResolver

########################################
#     Tests for DependencyResolver     #
########################################


def test_dependency_resolver_repr() -> None:
    assert repr(DependencyResolver("numpy")).startswith("DependencyResolver(")


def test_dependency_resolver_str() -> None:
    assert str(DependencyResolver("numpy")).startswith("DependencyResolver(")


def test_dependency_resolver_resolve() -> None:
    assert DependencyResolver("numpy").resolve("2.3.1") == ("numpy==2.3.1",)
