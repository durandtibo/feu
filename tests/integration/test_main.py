from __future__ import annotations

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
def test_entrypoint() -> None:
    run_bash_command("python -m feu install --package=numpy --version=2.0.2")


def test_invalid() -> None:
    with pytest.raises(CalledProcessError):
        run_bash_command("python -m feu invalid")
