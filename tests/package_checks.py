r"""Check that the installed ``feu`` package works.

The script is run by the CI against a package that is *installed* (built
from the source distribution or the wheel, or downloaded from PyPI), not
against the source tree. It is a standalone script, not a pytest module.

Usage::

    python tests/package_checks.py                  # no extra
    python tests/package_checks.py --extra rich     # rich is required
    python tests/package_checks.py --extra all      # every extra is required
"""

from __future__ import annotations

import argparse
import importlib.util
import logging
import operator
import sys
from typing import TYPE_CHECKING

from packaging.version import Version

from feu import (
    compare_version,
    get_package_version,
    is_module_available,
    is_package_available,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

logger: logging.Logger = logging.getLogger(__name__)

# Extra name -> modules that the extra installs.
EXTRA_MODULES: dict[str, tuple[str, ...]] = {
    "cli": ("click",),
    "git": ("git",),
    "requests": ("requests", "urllib3"),
    "rich": ("rich",),
}


def check_imports() -> None:
    logger.info("Checking import functionalities...")
    assert is_package_available("os.path")
    assert is_module_available("os")


def check_version() -> None:
    logger.info("Checking version functionalities...")
    assert compare_version("feu", operator.ge, "0.0.1")
    assert isinstance(get_package_version("feu"), Version)


def check_compat() -> None:
    logger.info("Checking the shipped compatibility data...")
    from feu.compat import (
        Target,
        find_closest_version,
        get_default_compat_registry,
    )

    target = Target(python_version="3.9", os="linux", arch="x86_64")
    # numpy 2.0.2 is the last release for Python 3.9, so a wheel without the
    # data files (an unknown package accepts any version) fails here.
    assert find_closest_version("numpy", "99.0.0", target) == "2.0.2"
    assert "numpy" in get_default_compat_registry().packages()


def check_extras(extras: Sequence[str]) -> None:
    r"""Check that the libraries installed by the extras can be found.

    Args:
        extras: The names of the extras that were installed.

    Raises:
        ModuleNotFoundError: If a library of an extra is not installed.
    """
    logger.info("Checking the extras: %s", sorted(extras) or "none")
    for extra in extras:
        for module in EXTRA_MODULES[extra]:
            if importlib.util.find_spec(module) is None:
                msg = f"the extra {extra!r} was requested but {module!r} is not installed"
                raise ModuleNotFoundError(msg)


def get_required_extras(values: Sequence[str]) -> list[str]:
    r"""Get the extras whose libraries are required.

    Args:
        values: The values of ``--extra``. A value can contain several
            comma-separated extras. ``all`` means every extra and an
            empty value means no extra.

    Returns:
        The sorted names of the extras.

    Raises:
        ValueError: If an extra is unknown.
    """
    extras = {e.strip() for value in values for e in value.split(",") if e.strip()}
    if "all" in extras:
        extras = (extras - {"all"}) | set(EXTRA_MODULES)
    unknown = sorted(extras - set(EXTRA_MODULES))
    if unknown:
        msg = f"Unknown extras: {unknown}. The valid extras are {sorted(EXTRA_MODULES)}"
        raise ValueError(msg)
    return sorted(extras)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    r"""Parse the command line arguments.

    Args:
        argv: The arguments. ``None`` means ``sys.argv[1:]``.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Check that the installed feu package works.")
    parser.add_argument(
        "--extra",
        action="append",
        default=[],
        help="extra installed with the package: its libraries must be importable. "
        "Can be repeated or comma-separated; 'all' means every extra; '' means none.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    check_imports()
    check_version()
    check_compat()
    check_extras(get_required_extras(parse_args(argv).extra))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])
