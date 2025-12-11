r"""Contain the main entry point."""

from __future__ import annotations

from feu.imports import check_click, is_click_available
from feu.install import install_package_closest_version
from feu.package import find_closest_version as find_closest_version_
from feu.package import is_valid_version
from feu.utils.installer import InstallerSpec
from feu.utils.package import PackageSpec

if is_click_available():
    import click
else:  # pragma: no cover
    from feu.utils.fallback.click import click


@click.group()
def cli() -> None:
    r"""Implement the main entrypoint."""


@click.command()
@click.option("-n", "--pkg-name", "pkg_name", help="Package name", required=True, type=str)
@click.option("-v", "--pkg-version", "pkg_version", help="Package version", required=True, type=str)
@click.option(
    "-e", "--pkg-extras", "pkg_extras", help="Package version", required=True, type=str, default=""
)
@click.option(
    "-i",
    "--installer-name",
    "installer_name",
    help="Optional installer name",
    required=True,
    type=str,
    default="pip",
)
@click.option(
    "-a",
    "--installer-args",
    "installer_args",
    help="Optional installer arguments",
    required=True,
    type=str,
    default="",
)
def install(
    pkg_name: str,
    pkg_version: str,
    pkg_extras: str,
    installer_name: str,
    installer_args: str,
) -> None:
    r"""Install a package and associated packages.

    Args:
        pkg_name: The package name e.g. ``'pandas'``.
        pkg_version: The target version of the package to install.
        pkg_extras: Optional package extra dependencies.
        installer_name: The package installer name to use to install
            the packages.
        installer_args: Optional arguments to pass to the package
            installer. The valid arguments depend on the package
            installer.

    Example usage:

    ```
    python -m feu install --installer-name=pip --pkg-name=numpy --pkg-version=2.0.2
    ```
    """
    pkg_extras = pkg_extras.strip()
    install_package_closest_version(
        installer=InstallerSpec(name=installer_name, arguments=installer_args),
        package=PackageSpec(
            name=pkg_name,
            version=pkg_version,
            extras=pkg_extras.split(",") if pkg_extras else [],
        ),
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

    python -m feu find-closest-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10
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
    check_click()
    cli()
