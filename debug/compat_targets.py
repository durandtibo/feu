r"""A debugging script for discover_compat_targets."""

from __future__ import annotations

from feu.compat import discover_compat_targets, show_compat_targets


def main() -> None:
    r"""Define the main function."""
    pkg_name = "scipy"
    compat = discover_compat_targets(pkg_name)
    show_compat_targets(compat=compat, pkg_name=pkg_name)


if __name__ == "__main__":
    main()
