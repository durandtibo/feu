r"""Contain utility functions to run commands."""

from __future__ import annotations

__all__ = ["run_command"]

import logging
import shlex
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

logger: logging.Logger = logging.getLogger(__name__)


def run_command(argv: Sequence[str]) -> None:
    r"""Execute a command given as an argument vector.

    The command is not run in a shell and is not tokenised, so it
    behaves the same way on Linux, macOS and Windows. The command is
    logged before it runs.

    Args:
        argv: The command and its arguments, e.g.
            ``["python", "-m", "pip", "--version"]``.

    Raises:
        subprocess.CalledProcessError: If the command exits with a
            non-zero status.

    Example:
        ```pycon
        >>> from feu.utils.command import run_command
        >>> run_command(["ls", "-l"])  # doctest: +SKIP

        ```
    """
    logger.info("execute the following command: %s", shlex.join(argv))
    subprocess.run(list(argv), check=True)  # noqa: S603
