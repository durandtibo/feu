from __future__ import annotations

import logging
import subprocess
from subprocess import CalledProcessError

import pytest

from feu.install import PackageInstaller, run_bash_command
from feu.package import find_closest_version
from feu.testing import click_available

logger = logging.getLogger(__name__)

################################
#     Tests for entrypoint     #
################################


@click_available
def test_install() -> None:
    logger.info(PackageInstaller.registry)
    logger.info(
        find_closest_version(
            pkg_name="numpy",
            pkg_version="2.2.5",
            python_version="3.9",
        )
    )
    run_bash_command("python -m feu install --pkg-name=numpy --pkg-version=2.2.5")


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
