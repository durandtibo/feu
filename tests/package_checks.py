from __future__ import annotations

import logging
import operator

from packaging.version import Version

from feu import (
    compare_version,
    get_package_version,
    is_module_available,
    is_package_available,
)

logger = logging.getLogger(__name__)


def check_imports() -> None:
    logger.info("Checking import functionalities...")
    assert is_package_available("os.path")
    assert is_module_available("os")


def check_version() -> None:
    logger.info("Checking version functionalities...")
    assert compare_version("feu", operator.ge, "0.0.1")
    assert isinstance(get_package_version("feu"), Version)


def main() -> None:
    check_imports()
    check_version()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
