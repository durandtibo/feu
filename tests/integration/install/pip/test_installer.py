from __future__ import annotations

import subprocess
import sys

import pytest

from feu import is_package_available
from feu.install.pip import PipInstaller, PipxInstaller, UvInstaller
from feu.package import find_closest_version
from feu.testing import pip_available, pipx_available, uv_available
from feu.utils.package import PackageSpec
from feu.version import get_python_major_minor


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    is_package_available.cache_clear()


@pytest.fixture(scope="module")
def package() -> PackageSpec:
    return PackageSpec(
        name="mkdocs",
        version=find_closest_version(
            pkg_name="mkdocs", pkg_version="1.6.1", python_version=get_python_major_minor()
        ),
    )


def is_pip_installed(package_name: str) -> bool:
    """Check whether a package is installed via pip in the current
    environment.

    This function runs ``python -m pip list`` using the current interpreter
    to determine whether the specified package is installed. This avoids
    calling the ``pip`` executable directly, satisfying security linters
    such as flake8-bandit (S607).

    Args:
        package_name: The name of the package to check.

    Returns:
        True if the package is installed in the current environment,
        otherwise False.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return False

    output = result.stdout.lower().splitlines()
    package_name = package_name.lower()

    return any(line.startswith(package_name + " ") for line in output)


def is_pipx_installed(package_name: str) -> bool:
    """Check whether a given package is installed via pipx.

    This function runs ``pipx list`` and parses its output to determine
    whether the specified package appears in the list of pipx-managed
    environments.

    Args:
        package_name: The name of the package to check.

    Returns:
        True if the package is installed with pipx, otherwise False.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pipx", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return False

    output = result.stdout.lower()
    token = f"package {package_name.lower()} "
    return token in output


@pip_available
def test_pip_installer(package: PackageSpec) -> None:
    PipInstaller().install(package)
    assert is_pip_installed(package.name)


@pipx_available
def test_pipx_installer(package: PackageSpec) -> None:
    PipxInstaller(arguments="--force").install(package)
    assert is_pipx_installed(package.name)


@uv_available
def test_uv_installer(package: PackageSpec) -> None:
    UvInstaller().install(package)
    assert is_package_available(package.name)
