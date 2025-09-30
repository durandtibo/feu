from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from feu.install.pip.resolver2 import (
    BaseDependencyResolver,
    DependencyResolver,
    DependencyResolverRegistry,
    JaxDependencyResolver,
    MatplotlibDependencyResolver,
    Numpy2DependencyResolver,
    PandasDependencyResolver,
    PyarrowDependencyResolver,
    ScipyDependencyResolver,
    SklearnDependencyResolver,
    TorchDependencyResolver,
    XarrayDependencyResolver,
)
from feu.utils.package import PackageDependency, PackageSpec

########################################
#     Tests for DependencyResolver     #
########################################


def test_dependency_resolver_repr() -> None:
    assert repr(DependencyResolver()).startswith("DependencyResolver(")


def test_dependency_resolver_str() -> None:
    assert str(DependencyResolver()).startswith("DependencyResolver(")


def test_dependency_resolver_equal_true() -> None:
    assert DependencyResolver().equal(DependencyResolver())


def test_dependency_resolver_equal_false_different() -> None:
    assert not DependencyResolver().equal(TorchDependencyResolver())


def test_dependency_resolver_equal_false_different_type() -> None:
    assert not DependencyResolver().equal(42)


def test_dependency_resolver_resolve() -> None:
    assert DependencyResolver().resolve(PackageSpec(name="my_package", version="1.2.3")) == [
        PackageDependency(name="my_package", version_specifiers=["==1.2.3"])
    ]


def test_dependency_resolver_resolve_no_version() -> None:
    assert DependencyResolver().resolve(PackageSpec(name="my_package")) == [
        PackageDependency(name="my_package")
    ]


def test_dependency_resolver_resolve_with_extras() -> None:
    assert DependencyResolver().resolve(
        PackageSpec(name="my_package", version="1.2.3", extras=["dev"])
    ) == [PackageDependency(name="my_package", version_specifiers=["==1.2.3"], extras=["dev"])]


def test_dependency_resolver_resolve_with_extras_empty() -> None:
    assert DependencyResolver().resolve(
        PackageSpec(name="my_package", version="1.2.3", extras=[])
    ) == [PackageDependency(name="my_package", version_specifiers=["==1.2.3"], extras=[])]


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
    assert JaxDependencyResolver().resolve(PackageSpec(name="jax", version="0.4.26")) == [
        PackageDependency(name="jax", version_specifiers=["==0.4.26"]),
        PackageDependency(name="jaxlib", version_specifiers=["==0.4.26"]),
    ]


def test_jax_dependency_resolver_resolve_high() -> None:
    assert JaxDependencyResolver().resolve(PackageSpec(name="jax", version="0.4.27")) == [
        PackageDependency(name="jax", version_specifiers=["==0.4.27"]),
        PackageDependency(name="jaxlib", version_specifiers=["==0.4.27"]),
    ]


def test_jax_dependency_resolver_resolve_low() -> None:
    assert JaxDependencyResolver().resolve(PackageSpec(name="jax", version="0.4.25")) == [
        PackageDependency(name="jax", version_specifiers=["==0.4.25"]),
        PackageDependency(name="jaxlib", version_specifiers=["==0.4.25"]),
        PackageDependency(name="numpy", version_specifiers=["<2.0.0"]),
    ]


@pytest.mark.parametrize("version", ["0.4.9", "0.4.10", "0.4.11"])
def test_jax_dependency_resolver_resolve_ml_dtypes(version: str) -> None:
    assert JaxDependencyResolver().resolve(PackageSpec(name="jax", version=version)) == [
        PackageDependency(name="jax", version_specifiers=[f"=={version}"]),
        PackageDependency(name="jaxlib", version_specifiers=[f"=={version}"]),
        PackageDependency(name="numpy", version_specifiers=["<2.0.0"]),
        PackageDependency(name="ml_dtypes", version_specifiers=["<=0.2.0"]),
    ]


def test_jax_dependency_resolver_resolve_with_extras() -> None:
    assert JaxDependencyResolver().resolve(
        PackageSpec(name="jax", version="0.4.26", extras=["dev"])
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
        PackageSpec(name="my_package", version="1.2.3")
    ) == [PackageDependency(name="my_package", version_specifiers=["==1.2.3"])]


def test_numpy2_dependency_resolver_resolve_high() -> None:
    assert Numpy2DependencyResolver(min_version="1.2.3").resolve(
        PackageSpec(name="my_package", version="1.3.0")
    ) == [PackageDependency(name="my_package", version_specifiers=["==1.3.0"])]


def test_numpy2_dependency_resolver_resolve_low() -> None:
    assert Numpy2DependencyResolver(min_version="1.2.3").resolve(
        PackageSpec(name="my_package", version="1.2.0")
    ) == [
        PackageDependency(name="my_package", version_specifiers=["==1.2.0"]),
        PackageDependency(name="numpy", version_specifiers=["<2.0.0"]),
    ]


def test_numpy2_dependency_resolver_resolve_with_extras() -> None:
    assert Numpy2DependencyResolver(min_version="1.2.3").resolve(
        PackageSpec(name="my_package", version="1.2.3", extras=["dev"])
    ) == [PackageDependency(name="my_package", version_specifiers=["==1.2.3"], extras=["dev"])]


##################################################
#     Tests for MatplotlibDependencyResolver     #
##################################################


def test_matplotlib_dependency_resolver_repr() -> None:
    assert repr(MatplotlibDependencyResolver()).startswith("MatplotlibDependencyResolver(")


def test_matplotlib_dependency_resolver_str() -> None:
    assert str(MatplotlibDependencyResolver()).startswith("MatplotlibDependencyResolver(")


def test_matplotlib_dependency_resolver_equal_true() -> None:
    assert MatplotlibDependencyResolver().equal(MatplotlibDependencyResolver())


def test_matplotlib_dependency_resolver_equal_false() -> None:
    assert not MatplotlibDependencyResolver().equal(42)


def test_matplotlib_dependency_resolver_resolve() -> None:
    assert MatplotlibDependencyResolver().resolve(
        PackageSpec(name="matplotlib", version="3.8.4")
    ) == [PackageDependency(name="matplotlib", version_specifiers=["==3.8.4"])]


def test_matplotlib_dependency_resolver_resolve_high() -> None:
    assert MatplotlibDependencyResolver().resolve(
        PackageSpec(name="matplotlib", version="3.9.0")
    ) == [PackageDependency(name="matplotlib", version_specifiers=["==3.9.0"])]


def test_matplotlib_dependency_resolver_resolve_low() -> None:
    assert MatplotlibDependencyResolver().resolve(
        PackageSpec(name="matplotlib", version="3.8.3")
    ) == [
        PackageDependency(name="matplotlib", version_specifiers=["==3.8.3"]),
        PackageDependency(name="numpy", version_specifiers=["<2.0.0"]),
    ]


def test_matplotlib_dependency_resolver_resolve_with_extras() -> None:
    assert MatplotlibDependencyResolver().resolve(
        PackageSpec(name="matplotlib", version="3.8.4", extras=["tk"])
    ) == [PackageDependency(name="matplotlib", version_specifiers=["==3.8.4"], extras=["tk"])]


##############################################
#     Tests for PandasDependencyResolver     #
##############################################


def test_pandas_dependency_resolver_repr() -> None:
    assert repr(PandasDependencyResolver()).startswith("PandasDependencyResolver(")


def test_pandas_dependency_resolver_str() -> None:
    assert str(PandasDependencyResolver()).startswith("PandasDependencyResolver(")


def test_pandas_dependency_resolver_equal_true() -> None:
    assert PandasDependencyResolver().equal(PandasDependencyResolver())


def test_pandas_dependency_resolver_equal_false() -> None:
    assert not PandasDependencyResolver().equal(42)


def test_pandas_dependency_resolver_resolve() -> None:
    assert PandasDependencyResolver().resolve(PackageSpec(name="pandas", version="2.2.2")) == [
        PackageDependency(name="pandas", version_specifiers=["==2.2.2"])
    ]


def test_pandas_dependency_resolver_resolve_high() -> None:
    assert PandasDependencyResolver().resolve(PackageSpec(name="pandas", version="2.2.3")) == [
        PackageDependency(name="pandas", version_specifiers=["==2.2.3"])
    ]


def test_pandas_dependency_resolver_resolve_low() -> None:
    assert PandasDependencyResolver().resolve(PackageSpec(name="pandas", version="2.2.1")) == [
        PackageDependency(name="pandas", version_specifiers=["==2.2.1"]),
        PackageDependency(name="numpy", version_specifiers=["<2.0.0"]),
    ]


def test_pandas_dependency_resolver_resolve_with_extras() -> None:
    assert PandasDependencyResolver().resolve(
        PackageSpec(name="pandas", version="2.2.2", extras=["performance"])
    ) == [PackageDependency(name="pandas", version_specifiers=["==2.2.2"], extras=["performance"])]


###############################################
#     Tests for PyarrowDependencyResolver     #
###############################################


def test_pyarrow_dependency_resolver_repr() -> None:
    assert repr(PyarrowDependencyResolver()).startswith("PyarrowDependencyResolver(")


def test_pyarrow_dependency_resolver_str() -> None:
    assert str(PyarrowDependencyResolver()).startswith("PyarrowDependencyResolver(")


def test_pyarrow_dependency_resolver_equal_true() -> None:
    assert PyarrowDependencyResolver().equal(PyarrowDependencyResolver())


def test_pyarrow_dependency_resolver_equal_false() -> None:
    assert not PyarrowDependencyResolver().equal(42)


def test_pyarrow_dependency_resolver_resolve() -> None:
    assert PyarrowDependencyResolver().resolve(PackageSpec(name="pyarrow", version="16.0")) == [
        PackageDependency(name="pyarrow", version_specifiers=["==16.0"])
    ]


def test_pyarrow_dependency_resolver_resolve_high() -> None:
    assert PyarrowDependencyResolver().resolve(PackageSpec(name="pyarrow", version="16.1")) == [
        PackageDependency(name="pyarrow", version_specifiers=["==16.1"])
    ]


def test_pyarrow_dependency_resolver_resolve_low() -> None:
    assert PyarrowDependencyResolver().resolve(PackageSpec(name="pyarrow", version="15.0")) == [
        PackageDependency(name="pyarrow", version_specifiers=["==15.0"]),
        PackageDependency(name="numpy", version_specifiers=["<2.0.0"]),
    ]


def test_pyarrow_dependency_resolver_resolve_with_extras() -> None:
    assert PyarrowDependencyResolver().resolve(
        PackageSpec(name="pyarrow", version="16.0", extras=["pandas"])
    ) == [PackageDependency(name="pyarrow", version_specifiers=["==16.0"], extras=["pandas"])]


#############################################
#     Tests for ScipyDependencyResolver     #
#############################################


def test_scipy_dependency_resolver_repr() -> None:
    assert repr(ScipyDependencyResolver()).startswith("ScipyDependencyResolver(")


def test_scipy_dependency_resolver_str() -> None:
    assert str(ScipyDependencyResolver()).startswith("ScipyDependencyResolver(")


def test_scipy_dependency_resolver_equal_true() -> None:
    assert ScipyDependencyResolver().equal(ScipyDependencyResolver())


def test_scipy_dependency_resolver_equal_false() -> None:
    assert not ScipyDependencyResolver().equal(42)


def test_scipy_dependency_resolver_resolve() -> None:
    assert ScipyDependencyResolver().resolve(PackageSpec(name="scipy", version="1.13.0")) == [
        PackageDependency(name="scipy", version_specifiers=["==1.13.0"])
    ]


def test_scipy_dependency_resolver_resolve_high() -> None:
    assert ScipyDependencyResolver().resolve(PackageSpec(name="scipy", version="1.13.1")) == [
        PackageDependency(name="scipy", version_specifiers=["==1.13.1"])
    ]


def test_scipy_dependency_resolver_resolve_low() -> None:
    assert ScipyDependencyResolver().resolve(PackageSpec(name="scipy", version="1.12.0")) == [
        PackageDependency(name="scipy", version_specifiers=["==1.12.0"]),
        PackageDependency(name="numpy", version_specifiers=["<2.0.0"]),
    ]


###############################################
#     Tests for SklearnDependencyResolver     #
###############################################


def test_sklearn_dependency_resolver_repr() -> None:
    assert repr(SklearnDependencyResolver()).startswith("SklearnDependencyResolver(")


def test_sklearn_dependency_resolver_str() -> None:
    assert str(SklearnDependencyResolver()).startswith("SklearnDependencyResolver(")


def test_sklearn_dependency_resolver_equal_true() -> None:
    assert SklearnDependencyResolver().equal(SklearnDependencyResolver())


def test_sklearn_dependency_resolver_equal_false() -> None:
    assert not SklearnDependencyResolver().equal(42)


def test_sklearn_dependency_resolver_resolve() -> None:
    assert SklearnDependencyResolver().resolve(
        PackageSpec(name="scikit-learn", version="1.4.2")
    ) == [PackageDependency(name="scikit-learn", version_specifiers=["==1.4.2"])]


def test_sklearn_dependency_resolver_resolve_high() -> None:
    assert SklearnDependencyResolver().resolve(
        PackageSpec(name="scikit-learn", version="1.4.3")
    ) == [PackageDependency(name="scikit-learn", version_specifiers=["==1.4.3"])]


def test_sklearn_dependency_resolver_resolve_low() -> None:
    assert SklearnDependencyResolver().resolve(
        PackageSpec(name="scikit-learn", version="1.4.1")
    ) == [
        PackageDependency(name="scikit-learn", version_specifiers=["==1.4.1"]),
        PackageDependency(name="numpy", version_specifiers=["<2.0.0"]),
    ]


def test_sklearn_dependency_resolver_resolve_with_extras() -> None:
    assert SklearnDependencyResolver().resolve(
        PackageSpec(name="scikit-learn", version="1.4.2", extras=["benchmark"])
    ) == [
        PackageDependency(name="scikit-learn", version_specifiers=["==1.4.2"], extras=["benchmark"])
    ]


#############################################
#     Tests for TorchDependencyResolver     #
#############################################


def test_torch_dependency_resolver_repr() -> None:
    assert repr(TorchDependencyResolver()).startswith("TorchDependencyResolver(")


def test_torch_dependency_resolver_str() -> None:
    assert str(TorchDependencyResolver()).startswith("TorchDependencyResolver(")


def test_torch_dependency_resolver_equal_true() -> None:
    assert TorchDependencyResolver().equal(TorchDependencyResolver())


def test_torch_dependency_resolver_equal_false() -> None:
    assert not TorchDependencyResolver().equal(42)


def test_torch_dependency_resolver_resolve() -> None:
    assert TorchDependencyResolver().resolve(PackageSpec(name="torch", version="2.3.0")) == [
        PackageDependency(name="torch", version_specifiers=["==2.3.0"])
    ]


def test_torch_dependency_resolver_resolve_high() -> None:
    assert TorchDependencyResolver().resolve(PackageSpec(name="torch", version="2.3.1")) == [
        PackageDependency(name="torch", version_specifiers=["==2.3.1"])
    ]


def test_torch_dependency_resolver_resolve_low() -> None:
    assert TorchDependencyResolver().resolve(PackageSpec(name="torch", version="2.2.0")) == [
        PackageDependency(name="torch", version_specifiers=["==2.2.0"]),
        PackageDependency(name="numpy", version_specifiers=["<2.0.0"]),
    ]


##############################################
#     Tests for XarrayDependencyResolver     #
##############################################


def test_xarray_dependency_resolver_repr() -> None:
    assert repr(XarrayDependencyResolver()).startswith("XarrayDependencyResolver(")


def test_xarray_dependency_resolver_str() -> None:
    assert str(XarrayDependencyResolver()).startswith("XarrayDependencyResolver(")


def test_xarray_dependency_resolver_equal_true() -> None:
    assert XarrayDependencyResolver().equal(XarrayDependencyResolver())


def test_xarray_dependency_resolver_equal_false() -> None:
    assert not XarrayDependencyResolver().equal(42)


def test_xarray_dependency_resolver_resolve() -> None:
    assert XarrayDependencyResolver().resolve(PackageSpec(name="xarray", version="2024.6.0")) == [
        PackageDependency(name="xarray", version_specifiers=["==2024.6.0"]),
    ]


def test_xarray_dependency_resolver_resolve_high() -> None:
    assert XarrayDependencyResolver().resolve(PackageSpec(name="xarray", version="2024.7.0")) == [
        PackageDependency(name="xarray", version_specifiers=["==2024.7.0"]),
    ]


def test_xarray_dependency_resolver_resolve_low() -> None:
    assert XarrayDependencyResolver().resolve(PackageSpec(name="xarray", version="2024.5.0")) == [
        PackageDependency(name="xarray", version_specifiers=["==2024.5.0"]),
        PackageDependency(name="numpy", version_specifiers=["<2.0.0"]),
    ]


def test_xarray_dependency_resolver_resolve_with_extras() -> None:
    assert XarrayDependencyResolver().resolve(
        PackageSpec(name="xarray", version="2024.6.0", extras=["performance"])
    ) == [
        PackageDependency(name="xarray", version_specifiers=["==2024.6.0"], extras=["performance"]),
    ]


################################################
#     Tests for DependencyResolverRegistry     #
################################################


def test_dependency_resolver_registry_registry() -> None:
    assert set(DependencyResolverRegistry.registry) == {
        "jax",
        "matplotlib",
        "pandas",
        "pyarrow",
        "scikit-learn",
        "scipy",
        "sklearn",
        "torch",
        "xarray",
    }


@patch.dict(DependencyResolverRegistry.registry, {}, clear=True)
def test_dependency_resolver_registry_add_resolver() -> None:
    resolver = Mock(spec=BaseDependencyResolver)
    DependencyResolverRegistry.add_resolver(PackageSpec("my_package"), resolver)
    assert DependencyResolverRegistry.registry["my_package"] == resolver


@patch.dict(DependencyResolverRegistry.registry, {}, clear=True)
def test_dependency_resolver_registry_add_resolver_exist_ok_true() -> None:
    resolver = Mock(spec=BaseDependencyResolver)
    DependencyResolverRegistry.add_resolver(
        PackageSpec("my_package"), Mock(spec=BaseDependencyResolver)
    )
    DependencyResolverRegistry.add_resolver(PackageSpec("my_package"), resolver, exist_ok=True)
    assert DependencyResolverRegistry.registry["my_package"] == resolver


@patch.dict(DependencyResolverRegistry.registry, {}, clear=True)
def test_dependency_resolver_registry_add_resolver_exist_ok_false() -> None:
    resolver = Mock(spec=BaseDependencyResolver)
    DependencyResolverRegistry.add_resolver(
        PackageSpec("my_package"), Mock(spec=BaseDependencyResolver)
    )
    with pytest.raises(RuntimeError, match=r"A dependency resolver is already registered"):
        DependencyResolverRegistry.add_resolver(PackageSpec("my_package"), resolver)


@patch.dict(DependencyResolverRegistry.registry, {}, clear=True)
def test_dependency_resolver_registry_has_resolver_true() -> None:
    DependencyResolverRegistry.add_resolver(
        PackageSpec("my_package"), Mock(spec=BaseDependencyResolver)
    )
    assert DependencyResolverRegistry.has_resolver(PackageSpec("my_package"))


@patch.dict(DependencyResolverRegistry.registry, {}, clear=True)
def test_dependency_resolver_registry_has_resolver_false() -> None:
    assert not DependencyResolverRegistry.has_resolver(PackageSpec("my_package"))


def test_dependency_resolver_registry_find_resolver_pandas() -> None:
    assert DependencyResolverRegistry.find_resolver(PackageSpec("pandas")).equal(
        PandasDependencyResolver()
    )


def test_dependency_resolver_registry_find_resolver_torch() -> None:
    assert DependencyResolverRegistry.find_resolver(PackageSpec("torch")).equal(
        TorchDependencyResolver()
    )


def test_dependency_resolver_registry_find_resolver_default() -> None:
    assert DependencyResolverRegistry.find_resolver(PackageSpec("my_package")).equal(
        DependencyResolver()
    )
