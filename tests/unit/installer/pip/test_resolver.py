from __future__ import annotations

from feu.installer.pip import (
    DependencyResolver,
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

########################################
#     Tests for DependencyResolver     #
########################################


def test_dependency_resolver_repr() -> None:
    assert repr(DependencyResolver("numpy")).startswith("DependencyResolver(")


def test_dependency_resolver_str() -> None:
    assert str(DependencyResolver("numpy")).startswith("DependencyResolver(")


def test_dependency_resolver_resolve() -> None:
    assert DependencyResolver("numpy").resolve("2.3.1") == ("numpy==2.3.1",)


###########################################
#     Tests for JaxDependencyResolver     #
###########################################


def test_jax_dependency_resolver_repr() -> None:
    assert repr(JaxDependencyResolver()).startswith("JaxDependencyResolver(")


def test_jax_dependency_resolver_str() -> None:
    assert str(JaxDependencyResolver()).startswith("JaxDependencyResolver(")


def test_jax_dependency_resolver_resolve() -> None:
    assert JaxDependencyResolver().resolve("0.4.26") == ("jax==0.4.26", "jaxlib==0.4.26")


def test_jax_dependency_resolver_resolve_high() -> None:
    assert JaxDependencyResolver().resolve("0.4.27") == ("jax==0.4.27", "jaxlib==0.4.27")


def test_jax_dependency_resolver_resolve_low() -> None:
    assert JaxDependencyResolver().resolve("0.4.25") == (
        "jax==0.4.25",
        "jaxlib==0.4.25",
        "numpy<2.0.0",
    )


def test_jax_dependency_resolver_resolve_ml_dtypes() -> None:
    assert JaxDependencyResolver().resolve("0.4.9") == (
        "jax==0.4.9",
        "jaxlib==0.4.9",
        "numpy<2.0.0",
        "ml_dtypes<=0.2.0",
    )


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


##################################################
#     Tests for MatplotlibDependencyResolver     #
##################################################


def test_matplotlib_dependency_resolver_repr() -> None:
    assert repr(MatplotlibDependencyResolver()).startswith("MatplotlibDependencyResolver(")


def test_matplotlib_dependency_resolver_str() -> None:
    assert str(MatplotlibDependencyResolver()).startswith("MatplotlibDependencyResolver(")


def test_matplotlib_dependency_resolver_resolve() -> None:
    assert MatplotlibDependencyResolver().resolve("3.8.4") == ("matplotlib==3.8.4",)


def test_matplotlib_dependency_resolver_resolve_high() -> None:
    assert MatplotlibDependencyResolver().resolve("3.9.0") == ("matplotlib==3.9.0",)


def test_matplotlib_dependency_resolver_resolve_low() -> None:
    assert MatplotlibDependencyResolver().resolve("3.8.3") == (
        "matplotlib==3.8.3",
        "numpy<2.0.0",
    )


##############################################
#     Tests for PandasDependencyResolver     #
##############################################


def test_pandas_dependency_resolver_repr() -> None:
    assert repr(PandasDependencyResolver()).startswith("PandasDependencyResolver(")


def test_pandas_dependency_resolver_str() -> None:
    assert str(PandasDependencyResolver()).startswith("PandasDependencyResolver(")


def test_pandas_dependency_resolver_resolve() -> None:
    assert PandasDependencyResolver().resolve("2.2.2") == ("pandas==2.2.2",)


def test_pandas_dependency_resolver_resolve_high() -> None:
    assert PandasDependencyResolver().resolve("2.3.0") == ("pandas==2.3.0",)


def test_pandas_dependency_resolver_resolve_low() -> None:
    assert PandasDependencyResolver().resolve("2.2.1") == (
        "pandas==2.2.1",
        "numpy<2.0.0",
    )


###############################################
#     Tests for PyarrowDependencyResolver     #
###############################################


def test_pyarrow_dependency_resolver_repr() -> None:
    assert repr(PyarrowDependencyResolver()).startswith("PyarrowDependencyResolver(")


def test_pyarrow_dependency_resolver_str() -> None:
    assert str(PyarrowDependencyResolver()).startswith("PyarrowDependencyResolver(")


def test_pyarrow_dependency_resolver_resolve() -> None:
    assert PyarrowDependencyResolver().resolve("16.0") == ("pyarrow==16.0",)


def test_pyarrow_dependency_resolver_resolve_high() -> None:
    assert PyarrowDependencyResolver().resolve("16.1") == ("pyarrow==16.1",)


def test_pyarrow_dependency_resolver_resolve_low() -> None:
    assert PyarrowDependencyResolver().resolve("15.0") == (
        "pyarrow==15.0",
        "numpy<2.0.0",
    )


#############################################
#     Tests for ScipyDependencyResolver     #
#############################################


def test_scipy_dependency_resolver_repr() -> None:
    assert repr(ScipyDependencyResolver()).startswith("ScipyDependencyResolver(")


def test_scipy_dependency_resolver_str() -> None:
    assert str(ScipyDependencyResolver()).startswith("ScipyDependencyResolver(")


def test_scipy_dependency_resolver_resolve() -> None:
    assert ScipyDependencyResolver().resolve("1.13.0") == ("scipy==1.13.0",)


def test_scipy_dependency_resolver_resolve_high() -> None:
    assert ScipyDependencyResolver().resolve("1.13.1") == ("scipy==1.13.1",)


def test_scipy_dependency_resolver_resolve_low() -> None:
    assert ScipyDependencyResolver().resolve("1.12.0") == (
        "scipy==1.12.0",
        "numpy<2.0.0",
    )


###############################################
#     Tests for SklearnDependencyResolver     #
###############################################


def test_sklearn_dependency_resolver_repr() -> None:
    assert repr(SklearnDependencyResolver()).startswith("SklearnDependencyResolver(")


def test_sklearn_dependency_resolver_str() -> None:
    assert str(SklearnDependencyResolver()).startswith("SklearnDependencyResolver(")


def test_sklearn_dependency_resolver_resolve() -> None:
    assert SklearnDependencyResolver().resolve("1.4.2") == ("scikit-learn==1.4.2",)


def test_sklearn_dependency_resolver_resolve_high() -> None:
    assert SklearnDependencyResolver().resolve("1.4.3") == ("scikit-learn==1.4.3",)


def test_sklearn_dependency_resolver_resolve_low() -> None:
    assert SklearnDependencyResolver().resolve("1.4.1") == (
        "scikit-learn==1.4.1",
        "numpy<2.0.0",
    )


#############################################
#     Tests for TorchDependencyResolver     #
#############################################


def test_torch_dependency_resolver_repr() -> None:
    assert repr(TorchDependencyResolver()).startswith("TorchDependencyResolver(")


def test_torch_dependency_resolver_str() -> None:
    assert str(TorchDependencyResolver()).startswith("TorchDependencyResolver(")


def test_torch_dependency_resolver_resolve() -> None:
    assert TorchDependencyResolver().resolve("2.3.0") == ("torch==2.3.0",)


def test_torch_dependency_resolver_resolve_high() -> None:
    assert TorchDependencyResolver().resolve("2.3.1") == ("torch==2.3.1",)


def test_torch_dependency_resolver_resolve_low() -> None:
    assert TorchDependencyResolver().resolve("2.2.0") == (
        "torch==2.2.0",
        "numpy<2.0.0",
    )


##############################################
#     Tests for XarrayDependencyResolver     #
##############################################


def test_xarray_dependency_resolver_repr() -> None:
    assert repr(XarrayDependencyResolver()).startswith("XarrayDependencyResolver(")


def test_xarray_dependency_resolver_str() -> None:
    assert str(XarrayDependencyResolver()).startswith("XarrayDependencyResolver(")


def test_xarray_dependency_resolver_resolve() -> None:
    assert XarrayDependencyResolver().resolve("2024.6.0") == ("xarray==2024.6.0",)


def test_xarray_dependency_resolver_resolve_high() -> None:
    assert XarrayDependencyResolver().resolve("2024.7.0") == ("xarray==2024.7.0",)


def test_xarray_dependency_resolver_resolve_low() -> None:
    assert XarrayDependencyResolver().resolve("2024.5.0") == (
        "xarray==2024.5.0",
        "numpy<2.0.0",
    )
