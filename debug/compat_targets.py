r"""A debugging script for discover_compat_targets."""

from __future__ import annotations

import logging

from feu.compat import discover_compat_targets, show_compat_targets

logger: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    r"""Define the main function."""
    pkg_name = "torch"
    compat = discover_compat_targets(pkg_name)
    logger.info(compat)
    show_compat_targets(compat=compat, pkg_name=pkg_name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
