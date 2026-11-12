# noqa: INP001
r"""A maintenance script to (re)generate the shipped compatibility data.

For each package name given, this fetches the current PyPI metadata via
``discover_compat_targets`` and writes the result as a JSON file under
``src/feu/compat/data/``, to be committed to the repository. Without
argument, it refreshes the packages that already have a file. A new
package is added by giving its name::

    python dev/generate_compat_data.py numpy pandas
    python dev/generate_compat_data.py --new my-package

Re-run this script periodically to refresh the data (the
``bot-update-discovered-compat`` workflow does it every week).
"""

from __future__ import annotations

import argparse
import logging
from datetime import UTC, datetime
from pathlib import Path

from packaging.utils import canonicalize_name

from feu.compat import discover_compat_targets
from feu.compat.shipped import ShippedData, format_package_data

logger: logging.Logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "src" / "feu" / "compat" / "data"


def generate(pkg_name: str, generated: str, output_dir: Path = OUTPUT_DIR) -> Path:
    r"""Discover and write the compatibility file for one package.

    Args:
        pkg_name: The package name.
        generated: The generation date, in ISO 8601 format.
        output_dir: The directory of the files.

    Returns:
        The path of the written file.
    """
    name = canonicalize_name(pkg_name)
    logger.info("Discovering compatibility targets for %s...", name)
    discovery = discover_compat_targets(name)
    path = output_dir / f"{name}.json"
    path.write_text(format_package_data(name, generated, discovery.targets))
    logger.info("Wrote %s", path)
    return path


def parse_args() -> argparse.Namespace:
    r"""Parse the command line arguments.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "packages", nargs="*", help="The packages to generate. Default: the existing files."
    )
    parser.add_argument(
        "--new", action="store_true", help="Allow packages that do not have a file yet."
    )
    return parser.parse_args()


def main() -> None:
    r"""Define the main function."""
    args = parse_args()
    existing = list(ShippedData().packages())
    packages = [canonicalize_name(p) for p in args.packages] or existing
    unknown = [p for p in packages if p not in existing]
    if unknown and not args.new:
        msg = f"No file exists for {unknown}. Use --new to add a package."
        raise SystemExit(msg)
    generated = datetime.now(tz=UTC).date().isoformat()
    logger.info("Generating compatibility files for packages: %s", packages)
    for pkg_name in packages:
        generate(pkg_name, generated)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
