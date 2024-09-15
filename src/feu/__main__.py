r"""Contain the main entry point."""

from __future__ import annotations

import sys

from feu.imports import check_fire, is_fire_available
from feu.install import install_package

if is_fire_available():  # pragma: no cover
    import fire


def main(args: list) -> None:
    r"""Define the main entry point.

    Args:
        args: The list of input arguments.

    Example usage:

    python feu install --package=torch --version=2.2.2
    """
    options = {"install": install_package}
    opt = args.pop(1)
    fn = options.get(opt)
    if fn is None:
        msg = f"Incorrect argument: {opt}. Valid values are: {sorted(options.keys())}"
        raise RuntimeError(msg)

    check_fire()
    fire.Fire(fn)


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv)
