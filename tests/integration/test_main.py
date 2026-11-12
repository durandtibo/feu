from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path
from subprocess import CalledProcessError

import pytest

from feu.testing import (
    click_available,
    click_not_available,
    pip_available,
    requests_available,
    uv_available,
)
from feu.utils.command import run_command

# Use `sys.executable` rather than the literal "python": the bare command
# name is not guaranteed to resolve to the interpreter running these tests
# (the one `feu` is installed into) -- PATH ordering can point it elsewhere,
# e.g. a different interpreter uv downloaded, which does not have `feu`
# installed and fails with "No module named feu".
PYTHON = sys.executable

################################
#     Tests for entrypoint     #
################################


@click_available
@pip_available
def test_install_default_installer() -> None:
    run_command([PYTHON, "-m", "feu", "install", "--pkg-name=coola", "--pkg-version=1.1.10"])


@click_available
@pip_available
def test_install_installer_pip() -> None:
    run_command(
        [
            PYTHON,
            "-m",
            "feu",
            "install",
            "--pkg-name=coola",
            "--pkg-version=1.1.10",
            "--installer-name=pip",
        ]
    )


@click_available
@uv_available
def test_install_uv() -> None:
    run_command(
        [
            PYTHON,
            "-m",
            "feu",
            "install",
            "--pkg-name=coola",
            "--pkg-version=1.1.10",
            "--installer-name=uv",
        ]
    )


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [PYTHON, "-m", "feu", *args], check=False, capture_output=True, text=True
    )


NUMPY_PY39 = ("--pkg-name=numpy", "--python-version=3.9")


@click_available
def test_find_closest_version() -> None:
    """Test that the standard output holds only the version, as the
    actions use it in ``$(...)``."""
    out = _run("find-closest-version", *NUMPY_PY39, "--pkg-version=99.0.0")
    assert (out.returncode, out.stdout, out.stderr) == (0, "2.0.2\n", "")


@click_available
def test_find_closest_version_default_target() -> None:
    out = _run("find-closest-version", "--pkg-name=coola", "--pkg-version=1.1.10")
    assert out.stdout.strip() != ""


@click_available
@requests_available
def test_find_closest_version_unsupported() -> None:
    """Test that an unsupported request gives an empty standard output,
    the message on the standard error and the exit status 1."""
    out = _run("find-closest-version", *NUMPY_PY39, "--pkg-version=3.*")
    assert out.returncode == 1
    assert out.stdout == ""
    assert "matches '3.*'" in out.stderr


@click_available
def test_find_closest_version_unsupported_is_not_the_string_none() -> None:
    assert "None" not in _run("find-closest-version", *NUMPY_PY39, "--pkg-version=3.*").stdout


@click_available
def test_find_closest_version_usage_error() -> None:
    out = _run("find-closest-version", "--pkg-name=numpy", "--os=linux")
    assert out.returncode == 2
    assert out.stdout == ""


@click_available
def test_find_closest_version_free_threaded_flag() -> None:
    out = _run(
        "find-closest-version", "--pkg-name=numpy", "--python-version=3.9", "--free-threaded"
    )
    assert out.returncode == 0


@click_available
def test_check_valid_version() -> None:
    out = _run("check-valid-version", *NUMPY_PY39, "--pkg-version=2.0.2")
    assert (out.returncode, out.stdout, out.stderr) == (0, "True\n", "")


@click_available
def test_check_valid_version_not_valid() -> None:
    out = _run("check-valid-version", *NUMPY_PY39, "--pkg-version=2.3.0")
    assert (out.returncode, out.stdout) == (1, "False\n")


@click_available
def test_check_valid_version_default_python_version() -> None:
    out = _run("check-valid-version", "--pkg-name=coola", "--pkg-version=1.1.10")
    assert out.stdout.strip() in {"True", "False"}


@click_available
def test_version() -> None:
    out = _run("--version")
    assert out.returncode == 0
    assert out.stdout.startswith("feu, version ")


@click_available
def test_verbose_logs_go_to_stderr() -> None:
    out = _run("--verbose", "find-closest-version", *NUMPY_PY39)
    assert out.stdout == "2.0.2\n"


@click_available
@requests_available
def test_package_versions(tmp_path: Path) -> None:
    """Test that the versions of the dependencies of a project are
    written as JSON."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"\ndependencies = ["requests>=2.30,<2.32"]\n')
    output = tmp_path / "versions.json"
    out = _run("package-versions", f"--pyproject={pyproject}", f"--output={output}")
    assert out.returncode == 0
    assert json.loads(output.read_text())["requests"][0] == "2.30.0"


@click_available
@requests_available
def test_package_versions_stdout(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"\ndependencies = ["requests>=2.30,<2.32"]\n')
    out = _run("package-versions", f"--pyproject={pyproject}")
    assert json.loads(out.stdout)["requests"][0] == "2.30.0"


def test_console_script_entry_point_is_declared() -> None:
    """Test that the console script points to ``feu.__main__:main``."""
    pyproject = tomllib.loads((Path(__file__).parents[2] / "pyproject.toml").read_text())
    assert pyproject["project"]["scripts"] == {"feu": "feu.__main__:main"}


def test_invalid() -> None:
    with pytest.raises(CalledProcessError):
        run_command([PYTHON, "-m", "feu", "invalid"])


@click_not_available
def test_install_not_click() -> None:
    with pytest.raises(CalledProcessError):
        run_command(
            [
                PYTHON,
                "-m",
                "feu",
                "install",
                "--pkg-name=coola",
                "--pkg-version=1.1.10",
                "--installer-name=pip",
            ]
        )
