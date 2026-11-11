from __future__ import annotations

import logging
import subprocess
import sys
from unittest.mock import patch

import pytest

from feu.utils.command import run_command

################################
#     Tests for run_command    #
################################


def test_run_command() -> None:
    # check it does not raise an error; use a command available on all
    # platforms, including Windows, unlike POSIX-only tools such as `ls`
    run_command([sys.executable, "-c", "pass"])


def test_run_command_mock() -> None:
    with patch("feu.utils.command.subprocess.run") as run_mock:
        run_command(["ls", "-l"])
        run_mock.assert_called_once_with(["ls", "-l"], check=True)


def test_run_command_does_not_split_arguments() -> None:
    with patch("feu.utils.command.subprocess.run") as run_mock:
        run_command(["echo", "a b", r"C:\Users\foo"])
        run_mock.assert_called_once_with(["echo", "a b", r"C:\Users\foo"], check=True)


def test_run_command_accepts_a_tuple() -> None:
    with patch("feu.utils.command.subprocess.run") as run_mock:
        run_command(("ls", "-l"))
        run_mock.assert_called_once_with(["ls", "-l"], check=True)


def test_run_command_does_not_use_a_shell() -> None:
    with patch("feu.utils.command.subprocess.run") as run_mock:
        run_command(["ls", "-l"])
        assert "shell" not in run_mock.call_args.kwargs


def test_run_command_logs_the_quoted_command(caplog: pytest.LogCaptureFixture) -> None:
    with (
        patch("feu.utils.command.subprocess.run"),
        caplog.at_level(logging.INFO, logger="feu.utils.command"),
    ):
        run_command(["echo", "a b"])
    assert caplog.messages == ["execute the following command: echo 'a b'"]


def test_run_command_failure_raises() -> None:
    with pytest.raises(subprocess.CalledProcessError, match="non-zero exit status 3"):
        run_command([sys.executable, "-c", "raise SystemExit(3)"])
