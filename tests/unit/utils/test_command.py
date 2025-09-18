from __future__ import annotations

from unittest.mock import patch

from feu.utils.command import run_bash_command

######################################
#     Tests for run_bash_command     #
######################################


def test_run_bash_command() -> None:
    # check it does not raise an error
    run_bash_command("ls -l")


def test_run_bash_command_mock() -> None:
    with patch("feu.utils.command.subprocess.run") as run_mock:
        run_bash_command("ls -l")
        run_mock.assert_called_once_with(["ls", "-l"], check=True)
