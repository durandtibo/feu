r"""Contain the main entry point."""

from __future__ import annotations

import sys

from feu.imports import check_fire, is_fire_available
from feu.install import install_package
from feu.package import _find_closest_version, _is_valid_version

if is_fire_available():  # pragma: no cover
    import fire


def main(args: list) -> None:
    r"""Define the main entry point.

    Args:
        args: The list of input arguments.

    Example usage:

    python -m feu install --package=numpy --version=2.0.2
    python -m feu check_valid_version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.11
    python -m feu find_closest_version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.11
    """
    options = {
        "install": install_package,
        "check_valid_version": _is_valid_version,
        "find_closest_version": _find_closest_version,
    }
    opt = args.pop(1)
    fn = options.get(opt)
    if fn is None:
        msg = f"Incorrect argument: {opt}. Valid values are: {sorted(options.keys())}"
        raise RuntimeError(msg)

    check_fire()
    fire.Fire(fn)


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv)
