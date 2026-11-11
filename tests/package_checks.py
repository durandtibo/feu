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

logger: logging.Logger = logging.getLogger(__name__)


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


def main() -> None:
    check_imports()
    check_version()
    check_compat()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
