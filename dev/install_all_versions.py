# noqa: INP001
r"""Script to install all the compatible versions of a list of packages
for a given target."""

from __future__ import annotations

import argparse
import logging
import sys
import sysconfig
from datetime import datetime, timedelta, timezone

from feu.compat import Target
from feu.compat.packages import get_package_names
from feu.install import install_packages_all_versions
from feu.utils.installer import InstallerSpec
from feu.version import sort_versions

logger: logging.Logger = logging.getLogger(__name__)

MAX_VERSION_AGE_YEARS = 6


def parse_args() -> argparse.Namespace:
    r"""Parse the command line arguments.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installer", default="pip", help="Installer name e.g. 'pip'.")
    parser.add_argument(
        "--installer-arguments", default="", help="Optional installer arguments e.g. '-U'."
    )
    return parser.parse_args()


def main() -> None:
    r"""Install all the compatible versions of a list of packages."""
    args = parse_args()
    target = Target(
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
        free_threaded=bool(sysconfig.get_config_var("Py_GIL_DISABLED")),
    )
    installer = InstallerSpec(name=args.installer, arguments=args.installer_arguments)

    packages = get_package_names()
    start_date = datetime.now(tz=timezone.utc).date() - timedelta(days=365 * MAX_VERSION_AGE_YEARS)

    logger.info(
        "Installing all versions of %s released since %s for %s...", packages, start_date, target
    )
    results = install_packages_all_versions(
        installer=installer, packages=packages, target=target, start_date=start_date
    )
    for package, result in results.items():
        logger.info(
            "%s: (%s) installed=%s", package, len(result.installed), sort_versions(result.installed)
        )

    logger.info("")
    logger.info("===== Packages with failed installations =====")
    for package, result in results.items():
        if result.failed:
            logger.info(
                "%s: (%s) failed=%s", package, len(result.failed), sort_versions(result.failed)
            )

    if any(result.failed for result in results.values()):
        msg = "Some package versions failed to install"
        raise RuntimeError(msg)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
