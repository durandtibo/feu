r"""Contain the main entry point."""

from __future__ import annotations

from feu.imports import is_click_available
from feu.install import install_package_closest_version
from feu.package import find_closest_version as find_closest_version_
from feu.package import is_valid_version

if is_click_available():  # pragma: no cover
    import click


@click.group()
def cli() -> None:
    r"""Implement the main entrypoint."""


@click.command()
@click.option(
    "-i", "--installer", "installer", help="Installer name", required=True, type=str, default="pip"
)
@click.option("-n", "--pkg-name", "pkg_name", help="Package name", required=True, type=str)
@click.option("-v", "--pkg-version", "pkg_version", help="Package version", required=True, type=str)
@click.option(
    "-a", "--args", "args", help="Optional installer arguments", required=True, type=str, default=""
)
def install(installer: str, pkg_name: str, pkg_version: str, args: str = "") -> None:
    r"""Install a package and associated packages.

    Args:
        installer: The package installer name to use to install
            the packages.
        pkg_name: The package name e.g. ``'pandas'``.
        pkg_version: The target version to install.
        args: Optional arguments to pass to the package installer.
            The list of valid arguments depend on the package
            installer.

    Example usage:

    ```
    python -m feu install --installer=pip --pkg-name=numpy --pkg-version=2.0.2
    ```
    """
    install_package_closest_version(
        installer=installer, package=pkg_name, version=pkg_version, args=args
    )


@click.command()
@click.option("-n", "--pkg-name", "pkg_name", help="Package name", required=True, type=str)
@click.option("-v", "--pkg-version", "pkg_version", help="Package version", required=True, type=str)
@click.option(
    "-p", "--python-version", "python_version", help="Python version", required=True, type=str
)
def find_closest_version(pkg_name: str, pkg_version: str, python_version: str) -> None:
    r"""Print the closest valid version given the package name and
    version, and python version.

    Args:
        pkg_name: The package name.
        pkg_version: The package version to check.
        python_version: The python version.

    Example usage:

    python -m feu find-closest-version --pkg_name=numpy --pkg_version=2.0.2 --python_version=3.10
    """
    print(  # noqa: T201
        find_closest_version_(
            pkg_name=pkg_name, pkg_version=pkg_version, python_version=python_version
        )
    )


@click.command()
@click.option("-n", "--pkg-name", "pkg_name", help="Package name", required=True, type=str)
@click.option("-v", "--pkg-version", "pkg_version", help="Package version", required=True, type=str)
@click.option(
    "-p", "--python-version", "python_version", help="Python version", required=True, type=str
)
def check_valid_version(pkg_name: str, pkg_version: str, python_version: str) -> None:
    r"""Print if the specified package version is valid for the given
    Python version.

    Args:
        pkg_name: The package name.
        pkg_version: The package version to check.
        python_version: The python version.

    Example usage:

    python -m feu check-valid-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10
    """
    print(  # noqa: T201
        is_valid_version(pkg_name=pkg_name, pkg_version=pkg_version, python_version=python_version)
    )


cli.add_command(install)
cli.add_command(find_closest_version)
cli.add_command(check_valid_version)


if __name__ == "__main__":  # pragma: no cover
    cli()
