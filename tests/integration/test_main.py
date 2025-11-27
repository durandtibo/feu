from __future__ import annotations

import subprocess
from subprocess import CalledProcessError

import pytest

from feu.testing import (
    click_available,
    click_not_available,
    pip_available,
    uv_available,
)
from feu.utils.command import run_bash_command

################################
#     Tests for entrypoint     #
################################


@click_available
@pip_available
def test_install_default_installer() -> None:
    run_bash_command("python -m feu install --pkg-name=coola --pkg-version=0.9.1")


@click_available
@pip_available
def test_install_installer_pip() -> None:
    run_bash_command(
        "python -m feu install --pkg-name=coola --pkg-version=0.9.1 --installer-name=pip"
    )


@click_available
@uv_available
def test_install_uv() -> None:
    run_bash_command(
        "python -m feu install --pkg-name=coola --pkg-version=0.9.1 --installer-name=uv"
    )


@click_available
def test_check_valid_version() -> None:
    cmd = (
        "python -m feu check-valid-version --pkg-name=coola --pkg-version=0.9.1 "
        "--python-version=3.11"
    )
    out = subprocess.run(cmd.split(), check=True, capture_output=True, text=True)  # noqa: S603
    assert out.stdout == "True\n"


@click_available
def test_find_closest_version() -> None:
    cmd = (
        "python -m feu find-closest-version --pkg-name=coola --pkg-version=0.9.1 "
        "--python-version=3.11"
    )
    out = subprocess.run(cmd.split(), check=True, capture_output=True, text=True)  # noqa: S603
    assert out.stdout == "0.9.1\n"


def test_invalid() -> None:
    with pytest.raises(CalledProcessError):
        run_bash_command("python -m feu invalid")


@click_not_available
def test_install_not_click() -> None:
    with pytest.raises(CalledProcessError):
        run_bash_command(
            "python -m feu install --pkg-name=coola --pkg-version=0.9.1 --installer-name=pip"
        )
