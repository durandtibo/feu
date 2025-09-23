from __future__ import annotations

from unittest.mock import patch

from click.testing import CliRunner

from feu.__main__ import check_valid_version, find_closest_version, install
from feu.testing import click_available


@click_available
def test_install() -> None:
    runner = CliRunner()
    with patch("feu.__main__.install_package_closest_version"):
        result = runner.invoke(
            install,
            ["--installer", "pip", "--pkg-name", "numpy", "--pkg-version", "2.0.2"],
        )
        assert result.exit_code == 0
        assert result.output.strip() == ""


@click_available
def test_install_with_args() -> None:
    runner = CliRunner()
    with patch("feu.__main__.install_package_closest_version"):
        result = runner.invoke(
            install,
            ["--installer", "pip", "--pkg-name", "numpy", "--pkg-version", "2.0.2", "--args", "-U"],
        )
        assert result.exit_code == 0
        assert result.output.strip() == ""


@click_available
def test_find_closest_version() -> None:
    runner = CliRunner()
    result = runner.invoke(
        find_closest_version,
        ["--pkg-name", "numpy", "--pkg-version", "2.0.2", "--python-version", "3.10"],
    )
    assert result.exit_code == 0
    assert result.output.strip() == "2.0.2"


@click_available
def test_check_valid_version() -> None:
    runner = CliRunner()
    result = runner.invoke(
        check_valid_version,
        ["--pkg-name", "numpy", "--pkg-version", "2.0.2", "--python-version", "3.10"],
    )
    assert result.exit_code == 0
    assert result.output.strip() == "True"
