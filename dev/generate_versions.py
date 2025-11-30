# noqa: INP001
r"""Script to create or update the package versions."""

from __future__ import annotations

import logging
from pathlib import Path

from feu.utils.io import save_json
from feu.version import (
    get_latest_major_versions,
    get_latest_minor_versions,
)

logger = logging.getLogger(__name__)


def get_package_versions() -> dict[str, list[str]]:
    r"""Get the versions for each package.

    Returns:
        A dictionary with the versions for each package.
    """
    return {
        "packaging": list(get_latest_major_versions("packaging", lower="21.0")),
        "typing_extensions": list(get_latest_minor_versions("typing_extensions", lower="4.10")),
        "click": list(get_latest_minor_versions("click", lower="8.1")),
        "gitpython": list(get_latest_minor_versions("gitpython", lower="3.1.41")),
        "requests": list(get_latest_minor_versions("requests", lower="2.30")),
        "urllib3": list(get_latest_minor_versions("urllib3", lower="2.0")),
    }


def main() -> None:
    r"""Generate the package versions and save them in a JSON file."""
    versions = get_package_versions()
    logger.info(f"{versions=}")
    path = Path(__file__).parent.parent.joinpath("dev/config").joinpath("package_versions.json")
    logger.info(f"Saving package versions to {path}")
    save_json(versions, path, exist_ok=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
