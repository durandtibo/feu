from __future__ import annotations

from feu.installer.pip import (
    DependencyResolver,
    MatplotlibDependencyResolver,
    Numpy2DependencyResolver,
    PandasDependencyResolver,
    PyarrowDependencyResolver,
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
