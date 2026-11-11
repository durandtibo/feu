from __future__ import annotations

import logging
import sys
import zipfile
from typing import TYPE_CHECKING

import pytest

from feu.install import install_package
from feu.testing import pip_available, uv_available
from feu.utils.installer import InstallerSpec
from feu.utils.package import PackageSpec

if TYPE_CHECKING:
    from pathlib import Path

NAME = "feu_offline_probe"
VERSION = "1.0.0"


@pytest.fixture
def wheel_dir(tmp_path: Path) -> Path:
    r"""Build a pure-Python wheel in a temporary directory."""
    dist_info = f"{NAME}-{VERSION}.dist-info"
    files = {
        f"{NAME}/__init__.py": "",
        f"{dist_info}/METADATA": f"Metadata-Version: 2.1\nName: {NAME}\nVersion: {VERSION}\n",
        f"{dist_info}/WHEEL": (
            "Wheel-Version: 1.0\nGenerator: feu-test\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
        ),
        f"{dist_info}/RECORD": "",
    }
    with zipfile.ZipFile(tmp_path / f"{NAME}-{VERSION}-py3-none-any.whl", "w") as wheel:
        for filename, content in files.items():
            wheel.writestr(filename, content)
    return tmp_path


def _offline_installer(name: str, wheel_dir: Path) -> InstallerSpec:
    return InstallerSpec(
        name, arguments=["--dry-run", "--no-index", "--find-links", str(wheel_dir)]
    )


@pip_available
def test_install_package_pip_offline_targets_the_current_interpreter(
    wheel_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that pip installs with the interpreter that runs the
    tests."""
    with caplog.at_level(logging.INFO, logger="feu.utils.command"):
        install_package(
            installer=_offline_installer("pip", wheel_dir),
            package=PackageSpec(name=NAME, version=VERSION),
        )
    assert caplog.messages[0].startswith(
        f"execute the following command: {sys.executable} -m pip install --dry-run"
    )


@uv_available
def test_install_package_uv_offline_targets_the_current_interpreter(
    wheel_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that uv installs with the interpreter that runs the tests."""
    with caplog.at_level(logging.INFO, logger="feu.utils.command"):
        install_package(
            installer=_offline_installer("uv", wheel_dir),
            package=PackageSpec(name=NAME, version=VERSION),
        )
    assert f"--python {sys.executable} --dry-run" in caplog.messages[0]
