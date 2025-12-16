r"""Contain utility functions to run commands."""

from __future__ import annotations

__all__ = ["run_bash_command"]

import logging
import subprocess

logger: logging.Logger = logging.getLogger(__name__)


def run_bash_command(cmd: str) -> None:
    r"""Execute a bash command.

    Args:
        cmd: The command to run.

    Example usage:

    ```pycon

    >>> from feu.utils.command import run_bash_command
    >>> run_bash_command("ls -l")  # doctest: +SKIP

    ```
    """
    logger.info(f"execute the following command: {cmd}")
    subprocess.run(cmd.split(), check=True)  # noqa: S603
