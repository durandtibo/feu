from __future__ import annotations

import sys
from unittest.mock import patch

from feu.utils.command import run_bash_command

######################################
#     Tests for run_bash_command     #
######################################


def test_run_bash_command() -> None:
    # check it does not raise an error; use a command available on all
    # platforms, including Windows, unlike POSIX-only tools such as `ls`
    run_bash_command(f"{sys.executable} -c pass")


def test_run_bash_command_mock() -> None:
    with patch("feu.utils.command.subprocess.run") as run_mock:
        run_bash_command("ls -l")
        run_mock.assert_called_once_with(["ls", "-l"], check=True)


def test_run_bash_command_windows_path_not_mangled() -> None:
    # On Windows, command tokenization must not treat backslashes as
    # POSIX escape characters, otherwise paths like C:\Users\foo get mangled.
    with (
        patch("feu.utils.command.os.name", "nt"),
        patch("feu.utils.command.subprocess.run") as run_mock,
    ):
        run_bash_command(r"echo C:\Users\foo")
        run_mock.assert_called_once_with(["echo", r"C:\Users\foo"], check=True)
