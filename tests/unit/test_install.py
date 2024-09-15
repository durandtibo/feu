from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from feu.install import (
    BaseInstaller,
    DefaultInstaller,
    JaxInstaller,
    MatplotlibInstaller,
    PackageInstaller,
    PandasInstaller,
    PyarrowInstaller,
    ScipyInstaller,
    SklearnInstaller,
    TorchInstaller,
    XarrayInstaller,
    install_package,
    run_bash_command,
)

######################################
#     Tests for run_bash_command     #
######################################


def test_run_bash_command() -> None:
    # check it does not raise an error
    run_bash_command("ls -l")


def test_run_bash_command_mock() -> None:
    with patch("feu.install.subprocess.run") as run_mock:
        run_bash_command("ls -l")
        run_mock.assert_called_once_with(["ls", "-l"], check=True)


######################################
#     Tests for DefaultInstaller     #
######################################


def test_default_installer_repr() -> None:
    assert repr(DefaultInstaller("numpy")).startswith("DefaultInstaller(")


def test_default_installer_str() -> None:
    assert str(DefaultInstaller("numpy")).startswith("DefaultInstaller(")


def test_default_installer_install() -> None:
    installer = DefaultInstaller("numpy")
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2.0.0")
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")


##################################
#     Tests for JaxInstaller     #
##################################


def test_jax_installer_repr() -> None:
    assert repr(JaxInstaller()).startswith("JaxInstaller(")


def test_jax_installer_str() -> None:
    assert str(JaxInstaller()).startswith("JaxInstaller(")


def test_jax_installer_install_high() -> None:
    installer = JaxInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("0.4.30")
        run_mock.assert_called_once_with("pip install -U jax==0.4.30 jaxlib==0.4.30")


def test_jax_installer_install_low() -> None:
    installer = JaxInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("0.4.25")
        run_mock.assert_called_once_with("pip install -U jax==0.4.25 jaxlib==0.4.25 numpy<2.0.0")


def test_jax_installer_install_ml_dtypes() -> None:
    installer = JaxInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("0.4.9")
        run_mock.assert_called_once_with(
            "pip install -U jax==0.4.9 jaxlib==0.4.9 numpy<2.0.0 ml_dtypes<=0.2.0"
        )


#########################################
#     Tests for MatplotlibInstaller     #
#########################################


def test_matplotlib_installer_repr() -> None:
    assert repr(MatplotlibInstaller()).startswith("MatplotlibInstaller(")


def test_matplotlib_installer_str() -> None:
    assert str(MatplotlibInstaller()).startswith("MatplotlibInstaller(")


def test_matplotlib_installer_install_high() -> None:
    installer = MatplotlibInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("3.8.4")
        run_mock.assert_called_once_with("pip install -U matplotlib==3.8.4")


def test_matplotlib_installer_install_low() -> None:
    installer = MatplotlibInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("3.7.1")
        run_mock.assert_called_once_with("pip install -U matplotlib==3.7.1 numpy<2.0.0")


#####################################
#     Tests for PandasInstaller     #
#####################################


def test_pandas_installer_repr() -> None:
    assert repr(PandasInstaller()).startswith("PandasInstaller(")


def test_pandas_installer_str() -> None:
    assert str(PandasInstaller()).startswith("PandasInstaller(")


def test_pandas_installer_install_high() -> None:
    installer = PandasInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2.2.2")
        run_mock.assert_called_once_with("pip install -U pandas==2.2.2")


def test_pandas_installer_install_low() -> None:
    installer = PandasInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2.1.1")
        run_mock.assert_called_once_with("pip install -U pandas==2.1.1 numpy<2.0.0")


######################################
#     Tests for PyarrowInstaller     #
######################################


def test_pyarrow_installer_repr() -> None:
    assert repr(PyarrowInstaller()).startswith("PyarrowInstaller(")


def test_pyarrow_installer_str() -> None:
    assert str(PyarrowInstaller()).startswith("PyarrowInstaller(")


def test_pyarrow_installer_install_high() -> None:
    installer = PyarrowInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("16.0")
        run_mock.assert_called_once_with("pip install -U pyarrow==16.0")


def test_pyarrow_installer_install_low() -> None:
    installer = PyarrowInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("15.0")
        run_mock.assert_called_once_with("pip install -U pyarrow==15.0 numpy<2.0.0")


####################################
#     Tests for ScipyInstaller     #
####################################


def test_scipy_installer_repr() -> None:
    assert repr(ScipyInstaller()).startswith("ScipyInstaller(")


def test_scipy_installer_str() -> None:
    assert str(ScipyInstaller()).startswith("ScipyInstaller(")


def test_scipy_installer_install_high() -> None:
    installer = ScipyInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("1.13.0")
        run_mock.assert_called_once_with("pip install -U scipy==1.13.0")


def test_scipy_installer_install_low() -> None:
    installer = ScipyInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("1.12.0")
        run_mock.assert_called_once_with("pip install -U scipy==1.12.0 numpy<2.0.0")


######################################
#     Tests for SklearnInstaller     #
######################################


def test_sklearn_installer_repr() -> None:
    assert repr(SklearnInstaller()).startswith("SklearnInstaller(")


def test_sklearn_installer_str() -> None:
    assert str(SklearnInstaller()).startswith("SklearnInstaller(")


def test_sklearn_installer_install_high() -> None:
    installer = SklearnInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("1.4.2")
        run_mock.assert_called_once_with("pip install -U scikit-learn==1.4.2")


def test_sklearn_installer_install_low() -> None:
    installer = SklearnInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("1.4.1")
        run_mock.assert_called_once_with("pip install -U scikit-learn==1.4.1 numpy<2.0.0")


####################################
#     Tests for TorchInstaller     #
####################################


def test_torch_installer_repr() -> None:
    assert repr(TorchInstaller()).startswith("TorchInstaller(")


def test_torch_installer_str() -> None:
    assert str(TorchInstaller()).startswith("TorchInstaller(")


def test_torch_installer_install_high() -> None:
    installer = TorchInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2.3.1")
        run_mock.assert_called_once_with("pip install -U torch==2.3.1")


def test_torch_installer_install_low() -> None:
    installer = TorchInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2.1.1")
        run_mock.assert_called_once_with("pip install -U torch==2.1.1 numpy<2.0.0")


#####################################
#     Tests for XarrayInstaller     #
#####################################


def test_xarray_installer_repr() -> None:
    assert repr(XarrayInstaller()).startswith("XarrayInstaller(")


def test_xarray_installer_str() -> None:
    assert str(XarrayInstaller()).startswith("XarrayInstaller(")


def test_xarray_installer_install_high() -> None:
    installer = XarrayInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2024.6")
        run_mock.assert_called_once_with("pip install -U xarray==2024.6")


def test_xarray_installer_install_low() -> None:
    installer = XarrayInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2023.5")
        run_mock.assert_called_once_with("pip install -U xarray==2023.5 numpy<2.0.0")


######################################
#     Tests for PackageInstaller     #
######################################


@patch.dict(PackageInstaller.registry, {}, clear=True)
def test_package_installer_add_installer() -> None:
    installer = Mock(spec=BaseInstaller)
    PackageInstaller.add_installer("pandas", installer)
    assert PackageInstaller.registry["pandas"] == installer


@patch.dict(PackageInstaller.registry, {}, clear=True)
def test_package_installer_add_installer_duplicate_exist_ok_true() -> None:
    installer = Mock(spec=BaseInstaller)
    PackageInstaller.add_installer("pandas", Mock(spec=BaseInstaller))
    PackageInstaller.add_installer("pandas", installer, exist_ok=True)
    assert PackageInstaller.registry["pandas"] == installer


@patch.dict(PackageInstaller.registry, {}, clear=True)
def test_package_installer_add_installer_duplicate_exist_ok_false() -> None:
    installer = Mock(spec=BaseInstaller)
    PackageInstaller.add_installer("pandas", Mock(spec=BaseInstaller))
    with pytest.raises(RuntimeError, match="An installer (.*) is already registered"):
        PackageInstaller.add_installer("pandas", installer)


@patch.dict(PackageInstaller.registry, {}, clear=True)
def test_package_installer_has_installer_false() -> None:
    assert not PackageInstaller.has_installer("pandas")


@patch.dict(PackageInstaller.registry, {}, clear=True)
def test_package_installer_has_installer_true() -> None:
    PackageInstaller.add_installer("pandas", Mock(spec=BaseInstaller))
    assert PackageInstaller.has_installer("pandas")


def test_package_installer_install_numpy() -> None:
    with patch("feu.install.run_bash_command") as run_mock:
        PackageInstaller.install(package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")


def test_package_installer_install_pandas() -> None:
    with patch("feu.install.run_bash_command") as run_mock:
        PackageInstaller.install(package="pandas", version="2.1.1")
        run_mock.assert_called_once_with("pip install -U pandas==2.1.1 numpy<2.0.0")


def test_package_installer_registry() -> None:
    assert set(PackageInstaller.registry) == {
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


#####################################
#     Tests for install_package     #
#####################################


def test_install_package_numpy() -> None:
    with patch("feu.install.run_bash_command") as run_mock:
        install_package(package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")


def test_install_package_pandas() -> None:
    with patch("feu.install.run_bash_command") as run_mock:
        install_package(package="pandas", version="2.1.1")
        run_mock.assert_called_once_with("pip install -U pandas==2.1.1 numpy<2.0.0")
