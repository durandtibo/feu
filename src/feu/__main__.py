r"""Contain the main entry point."""

from __future__ import annotations

from feu.compat import Target
from feu.compat import find_closest_version as find_closest_version_
from feu.compat import is_valid_version
from feu.imports import check_click, is_click_available
from feu.install import install_package_closest_version
from feu.utils.installer import InstallerSpec
from feu.utils.package import PackageSpec
from feu.utils.platform import (
    get_current_arch,
    get_current_os,
    get_python_version,
    is_free_threaded,
)

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
    "-e",
    "--pkg-extras",
    "pkg_extras",
    help="Package extra dependencies",
    required=True,
    type=str,
    default="",
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

    Example:
        ```console
        $ python -m feu install --installer-name=pip --pkg-name=numpy --pkg-version=2.0.2

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
    "-p",
    "--python-version",
    "python_version",
    help="Python version. If not provided, the current python version is used.",
    required=False,
    type=str,
    default=None,
)
@click.option(
    "-f",
    "--free-threaded",
    "free_threaded",
    help="Whether the target is a free-threaded build. If not provided, the "
    "current interpreter's free-threaded status is used.",
    required=False,
    type=bool,
    default=None,
)
@click.option(
    "-o",
    "--os",
    "os_",
    help="Target OS. If not provided, the current OS is used.",
    required=False,
    type=str,
    default=None,
)
@click.option(
    "-r",
    "--arch",
    "arch",
    help="Target CPU architecture. If not provided, the current architecture is used.",
    required=False,
    type=str,
    default=None,
)
def find_closest_version(
    pkg_name: str,
    pkg_version: str,
    *,
    python_version: str | None,
    free_threaded: bool | None,
    os_: str | None,
    arch: str | None,
) -> None:
    r"""Print the closest valid version given the package name and
    version, and python version.

    Args:
        pkg_name: The package name.
        pkg_version: The package version to check.
        python_version: The python version. If not provided, the
            current python version is used.
        free_threaded: Whether the target is a free-threaded build.
            If not provided, the current interpreter's free-threaded
            status is used.
        os_: The target OS. If not provided, the current OS is used.
        arch: The target CPU architecture. If not provided, the
            current architecture is used.

    Example:
        ```console
        $ python -m feu find-closest-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10

        ```
    """
    print(  # noqa: T201
        find_closest_version_(
            pkg_name=pkg_name,
            pkg_version=pkg_version,
            target=Target(
                python_version=python_version or get_python_version(),
                free_threaded=is_free_threaded() if free_threaded is None else free_threaded,
                os=os_ or get_current_os(),
                arch=arch or get_current_arch(),
            ),
        )
    )


@click.command()
@click.option("-n", "--pkg-name", "pkg_name", help="Package name", required=True, type=str)
@click.option("-v", "--pkg-version", "pkg_version", help="Package version", required=True, type=str)
@click.option(
    "-p",
    "--python-version",
    "python_version",
    help="Python version. If not provided, the current python version is used.",
    required=False,
    type=str,
    default=None,
)
@click.option(
    "-f",
    "--free-threaded",
    "free_threaded",
    help="Whether the target is a free-threaded build. If not provided, the "
    "current interpreter's free-threaded status is used.",
    required=False,
    type=bool,
    default=None,
)
@click.option(
    "-o",
    "--os",
    "os_",
    help="Target OS. If not provided, the current OS is used.",
    required=False,
    type=str,
    default=None,
)
@click.option(
    "-r",
    "--arch",
    "arch",
    help="Target CPU architecture. If not provided, the current architecture is used.",
    required=False,
    type=str,
    default=None,
)
def check_valid_version(
    pkg_name: str,
    pkg_version: str,
    *,
    python_version: str | None,
    free_threaded: bool | None,
    os_: str | None,
    arch: str | None,
) -> None:
    r"""Print if the specified package version is valid for the given
    Python version.

    Args:
        pkg_name: The package name.
        pkg_version: The package version to check.
        python_version: The python version. If not provided, the
            current python version is used.
        free_threaded: Whether the target is a free-threaded build.
            If not provided, the current interpreter's free-threaded
            status is used.
        os_: The target OS. If not provided, the current OS is used.
        arch: The target CPU architecture. If not provided, the
            current architecture is used.

    Example:
        ```console
        $ python -m feu check-valid-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10

        ```
    """
    print(  # noqa: T201
        is_valid_version(
            pkg_name=pkg_name,
            pkg_version=pkg_version,
            target=Target(
                python_version=python_version or get_python_version(),
                free_threaded=is_free_threaded() if free_threaded is None else free_threaded,
                os=os_ or get_current_os(),
                arch=arch or get_current_arch(),
            ),
        )
    )


cli.add_command(install)
cli.add_command(find_closest_version)
cli.add_command(check_valid_version)


if __name__ == "__main__":  # pragma: no cover
    check_click()
    cli()
