r"""Contain the command line interface.

The command line interface requires the ``click`` package, which can be
installed with ``pip install 'feu[cli]'``. It provides the commands
``install``, ``find-closest-version``, ``check-valid-version`` and
``package-versions``, which are run with ``feu <command>`` or
``python -m feu <command>``.

The standard output holds only the answer of a command (it is used in
``$(...)``), the logs and the error messages go to the standard error,
and the exit status carries the result: ``0`` for success, ``1`` for a
negative answer and ``2`` for a usage error.
"""

from __future__ import annotations

__all__ = ["cli"]

import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

import click

from feu import __version__
from feu.compat import (
    UnsupportedVersionError,
    find_closest_version as find_closest_version_,
    is_valid_version as is_valid_version_,
    resolve_target,
)
from feu.install import InstallerSpec, install_package_closest_version
from feu.utils.package import PackageSpec
from feu.version import fetch_package_versions

if TYPE_CHECKING:
    from collections.abc import Callable

F = TypeVar("F", bound="Callable[..., Any]")

_PKG_NAME = click.option("-n", "--pkg-name", "pkg_name", help="Package name", required=True)
_PKG_VERSION = click.option(
    "-v",
    "--pkg-version",
    "pkg_version",
    default="",
    show_default=True,
    help="Package version request: an exact version e.g. '2.0.2', a wildcard e.g. '2.*' or "
    "an empty string for the latest version.",
)


def target_options(function: F) -> F:
    r"""Add the options that define the target of a command.

    The target is the current environment, except the Python version
    and the free-threaded flag that can be chosen. The platform is
    always the current one.

    Args:
        function: The command function. It receives ``python_version``
            and ``free_threaded``.

    Returns:
        The decorated function.
    """
    function = click.option(
        "-f",
        "--free-threaded/--no-free-threaded",
        "free_threaded",
        default=None,
        help="Whether the target is a free-threaded build. Default: the current interpreter.",
    )(function)
    return click.option(
        "-p",
        "--python-version",
        "python_version",
        default=None,
        help="Python version e.g. '3.12' or '3.14t'. Default: the current Python version.",
    )(function)


@click.group()
@click.version_option(__version__, "--version", prog_name="feu")
@click.option("--verbose", is_flag=True, help="Log the executed commands on the standard error.")
def cli(*, verbose: bool) -> None:
    r"""Implement the main entrypoint, which groups the commands."""
    if verbose:
        logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(message)s")


@cli.command()
@_PKG_NAME
@_PKG_VERSION
@click.option(
    "-e",
    "--pkg-extras",
    "pkg_extras",
    default="",
    show_default=True,
    help="Package extra dependencies, separated by commas e.g. 'dev,doc'.",
)
@click.option(
    "-i",
    "--installer-name",
    "installer_name",
    default="pip",
    show_default=True,
    help="The package installer.",
)
@click.option(
    "-a",
    "--installer-args",
    "installer_args",
    default="",
    show_default=True,
    help="Arguments to pass to the package installer, split once like a shell would.",
)
def install(
    pkg_name: str,
    pkg_version: str,
    pkg_extras: str,
    installer_name: str,
    installer_args: str,
) -> None:
    r"""Install a package and associated packages.

    The package is installed in the interpreter that runs ``feu``, for
    the current target. The closest compatible version is installed if
    ``pkg_version`` is not compatible. The exit status is ``1`` if no
    version is compatible and ``2`` if an argument is invalid (e.g. a
    malformed wildcard).

    Args:
        pkg_name: The package name e.g. ``'pandas'``.
        pkg_version: The version request of the package to install:
            an exact version, a wildcard (e.g. ``'2.*'``) or an empty
            string for the latest version.
        pkg_extras: Optional package extra dependencies, separated by
            commas e.g. ``'dev,doc'``. An empty string means no extra.
        installer_name: The package installer name to use to install
            the packages.
        installer_args: Optional arguments to pass to the package
            installer, as a single string e.g. ``'--upgrade'``. It is
            split once with ``shlex.split``. The valid arguments
            depend on the package installer.

    Example:
        ```console
        $ feu install --installer-name=pip --pkg-name=numpy --pkg-version=2.0.2

        ```
    """
    extras = [extra for extra in pkg_extras.split(",") if extra.strip()]
    try:
        install_package_closest_version(
            installer=InstallerSpec(name=installer_name, arguments=installer_args),
            package=PackageSpec(name=pkg_name, version=pkg_version, extras=extras),
        )
    except UnsupportedVersionError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc


@cli.command(name="find-closest-version")
@_PKG_NAME
@_PKG_VERSION
@target_options
def find_closest_version(
    pkg_name: str, pkg_version: str, *, python_version: str | None, free_threaded: bool | None
) -> None:
    r"""Print the closest valid version of a package for a target.

    The standard output holds only the version to install. For a
    wildcard or an empty version request that lies in an open-ended
    range, the request itself is printed. If no version is compatible
    with the target, the message is printed on the standard error, the
    standard output is empty and the exit status is ``1``.

    Args:
        pkg_name: The package name.
        pkg_version: The package version request to check.
        python_version: The python version. If not provided, the
            current python version is used.
        free_threaded: Whether the target is a free-threaded build.
            If not provided, the current interpreter's free-threaded
            status is used.

    Example:
        ```console
        $ feu find-closest-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10

        ```
    """
    try:
        version = find_closest_version_(
            pkg_name=pkg_name,
            pkg_version=pkg_version,
            target=resolve_target(python_version, free_threaded=free_threaded),
        )
    except UnsupportedVersionError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    click.echo(version)


@cli.command(name="check-valid-version")
@_PKG_NAME
@_PKG_VERSION
@target_options
def check_valid_version(
    pkg_name: str, pkg_version: str, *, python_version: str | None, free_threaded: bool | None
) -> None:
    r"""Print if a package version is valid for a target.

    ``True`` is printed and the exit status is ``0`` if the version is
    valid or if the package is not configured for the target. Otherwise
    ``False`` is printed and the exit status is ``1``.

    Args:
        pkg_name: The package name.
        pkg_version: The package version request to check.
        python_version: The python version. If not provided, the
            current python version is used.
        free_threaded: Whether the target is a free-threaded build.
            If not provided, the current interpreter's free-threaded
            status is used.

    Example:
        ```console
        $ feu check-valid-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10

        ```
    """
    try:
        valid = is_valid_version_(
            pkg_name=pkg_name,
            pkg_version=pkg_version,
            target=resolve_target(python_version, free_threaded=free_threaded),
        )
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    click.echo(valid)
    sys.exit(0 if valid else 1)


@cli.command(name="package-versions")
@click.option(
    "--pyproject",
    "pyproject",
    type=click.Path(exists=True, dir_okay=False),
    default="pyproject.toml",
    show_default=True,
    help="The pyproject.toml file to read the dependencies from.",
)
@click.option(
    "--output",
    "output",
    type=click.Path(dir_okay=False),
    default=None,
    help="The JSON file to write. Default: the standard output.",
)
@click.option(
    "--major-only",
    "major_only",
    multiple=True,
    default=("packaging",),
    show_default=True,
    help="A package for which only the latest version of each major version is kept. "
    "Repeat the option for several packages.",
)
def package_versions(pyproject: str, output: str | None, major_only: tuple[str, ...]) -> None:
    r"""Write the versions to test of the dependencies of a project.

    The dependencies are read from ``[project.dependencies]`` and
    ``[project.optional-dependencies]``. The output is a JSON object
    that maps each package to the latest version of each minor (or
    major) version at or above its lower bound.

    Args:
        pyproject: The ``pyproject.toml`` file.
        output: The JSON file to write, or ``None`` for the standard
            output.
        major_only: The packages for which only the major versions
            are kept.

    Example:
        ```console
        $ feu package-versions --pyproject pyproject.toml --output dev/config/package_versions.json

        ```
    """
    text = json.dumps(fetch_package_versions(pyproject, major_only=major_only))
    if output is None:
        click.echo(text)
    else:
        Path(output).write_text(text + "\n", encoding="utf-8")
