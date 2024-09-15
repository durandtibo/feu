from __future__ import annotations

import subprocess
from subprocess import CalledProcessError
from unittest.mock import patch

import pytest

from feu.__main__ import main
from feu.install import run_bash_command
from feu.testing import fire_available

################################
#     Tests for entrypoint     #
################################


@fire_available
def test_main() -> None:
    args = ["__main__.py", "install", "--package=numpy", "--version=2.0.2"]
    with patch("sys.argv", args):
        main(args)


@fire_available
def test_main_install() -> None:
    run_bash_command("python -m feu install --package=numpy --version=2.0.2")


@fire_available
def test_main_check_valid_version() -> None:
    cmd = (
        "python -m feu check_valid_version --pkg-name=numpy --pkg-version=2.0.2 "
        "--python-version=3.11"
    )
    out = subprocess.run(cmd.split(), check=True, capture_output=True, text=True)  # noqa: S603
    assert out.stdout == "True\n"


@fire_available
def test_main_find_closest_version() -> None:
    cmd = (
        "python -m feu find_closest_version --pkg-name=numpy --pkg-version=2.0.2 "
        "--python-version=3.11"
    )
    out = subprocess.run(cmd.split(), check=True, capture_output=True, text=True)  # noqa: S603
    assert out.stdout == "2.0.2\n"


def test_invalid() -> None:
    with pytest.raises(CalledProcessError):
        run_bash_command("python -m feu invalid")
