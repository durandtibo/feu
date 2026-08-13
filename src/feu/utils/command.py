r"""Contain utility functions to run commands."""

from __future__ import annotations

__all__ = ["run_bash_command"]

import logging
import os
import shlex
import subprocess

logger: logging.Logger = logging.getLogger(__name__)


def run_bash_command(cmd: str) -> None:
    r"""Execute a command.

    On Windows, the command is tokenized using non-POSIX rules so
    that backslashes (e.g. in paths like ``C:\Users\foo``) are kept
    literal instead of being interpreted as POSIX escape characters.

    Args:
        cmd: The command to run.

    Example:
        ```pycon
        >>> from feu.utils.command import run_bash_command
        >>> run_bash_command("ls -l")  # doctest: +SKIP

        ```
    """
    logger.info(f"execute the following command: {cmd}")
    subprocess.run(shlex.split(cmd, posix=(os.name != "nt")), check=True)  # noqa: S603
