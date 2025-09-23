from __future__ import annotations

import subprocess
from subprocess import CalledProcessError

import pytest

from feu.install import run_bash_command
from feu.testing import click_available, pip_available, uv_available

################################
#     Tests for entrypoint     #
################################


@click_available
@pip_available
def test_install_pip() -> None:
    run_bash_command("python -m feu install --installer=pip --pkg-name=numpy --pkg-version=2.2.5")


@click_available
@uv_available
def test_install_uv() -> None:
    run_bash_command("python -m feu install --installer=uv --pkg-name=numpy --pkg-version=2.2.5")


@click_available
def test_check_valid_version() -> None:
    cmd = (
        "python -m feu check-valid-version --pkg-name=numpy --pkg-version=2.2.5 "
        "--python-version=3.11"
    )
    out = subprocess.run(cmd.split(), check=True, capture_output=True, text=True)  # noqa: S603
    assert out.stdout == "True\n"


@click_available
def test_find_closest_version() -> None:
    cmd = (
        "python -m feu find-closest-version --pkg-name=numpy --pkg-version=2.2.5 "
        "--python-version=3.11"
    )
    out = subprocess.run(cmd.split(), check=True, capture_output=True, text=True)  # noqa: S603
    assert out.stdout == "2.2.5\n"


def test_invalid() -> None:
    with pytest.raises(CalledProcessError):
        run_bash_command("python -m feu invalid")
