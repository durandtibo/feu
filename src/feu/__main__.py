r"""Contain the entry point of the command line interface.

The command line interface requires the ``click`` package, which can be
installed with ``pip install 'feu[cli]'``. It is run with
``python -m feu <command>``.
"""

from __future__ import annotations

__all__ = ["main"]

from feu.imports import check_click


def main() -> None:
    r"""Run the command line interface.

    Raises:
        MissingPackageError: If the ``click`` package is not
            installed.

    Example:
        ```console
        $ python -m feu --help

        ```
    """
    check_click()
    from feu.cli import cli  # noqa: PLC0415

    cli()


if __name__ == "__main__":  # pragma: no cover
    main()
