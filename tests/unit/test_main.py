from __future__ import annotations

from unittest.mock import Mock, patch

from click.testing import CliRunner

from feu.__main__ import check_valid_version, find_closest_version, install
from feu.testing import click_available
from feu.utils.installer import InstallerSpec
from feu.utils.package import PackageSpec

#############################
#     Tests for install     #
#############################


@click_available
def test_install() -> None:
    runner = CliRunner()
    mock = Mock()
    with patch("feu.__main__.install_package_closest_version", mock):
        result = runner.invoke(
            install,
            ["--pkg-name", "numpy", "--pkg-version", "2.0.2"],
        )
        assert result.exit_code == 0
        assert result.output.strip() == ""
        assert mock.call_args.kwargs == {
            "installer": InstallerSpec(name="pip", arguments=""),
            "package": PackageSpec(name="numpy", version="2.0.2", extras=[]),
        }


@click_available
def test_install_with_pkg_extras() -> None:
    runner = CliRunner()
    mock = Mock()
    with patch("feu.__main__.install_package_closest_version", mock):
        result = runner.invoke(
            install,
            ["--pkg-name", "numpy", "--pkg-version", "2.0.2", "--pkg-extras", "all"],
        )
        assert result.exit_code == 0
        assert result.output.strip() == ""
        assert mock.call_args.kwargs == {
            "installer": InstallerSpec(name="pip", arguments=""),
            "package": PackageSpec(name="numpy", version="2.0.2", extras=["all"]),
        }


@click_available
def test_install_installer_uv() -> None:
    runner = CliRunner()
    mock = Mock()
    with patch("feu.__main__.install_package_closest_version", mock):
        result = runner.invoke(
            install,
            ["--pkg-name", "numpy", "--pkg-version", "2.0.2", "--installer-name", "uv"],
        )
        assert result.exit_code == 0
        assert result.output.strip() == ""
        assert mock.call_args.kwargs == {
            "installer": InstallerSpec(name="uv", arguments=""),
            "package": PackageSpec(name="numpy", version="2.0.2", extras=[]),
        }


@click_available
def test_install_with_installer_args() -> None:
    runner = CliRunner()
    mock = Mock()
    with patch("feu.__main__.install_package_closest_version", mock):
        result = runner.invoke(
            install,
            [
                "--pkg-name",
                "numpy",
                "--pkg-version",
                "2.0.2",
                "--installer-name",
                "pip",
                "--installer-args",
                "-U",
            ],
        )
        assert result.exit_code == 0
        assert result.output.strip() == ""
        assert mock.call_args.kwargs == {
            "installer": InstallerSpec(name="pip", arguments="-U"),
            "package": PackageSpec(name="numpy", version="2.0.2", extras=[]),
        }


##########################################
#     Tests for find_closest_version     #
##########################################


@click_available
def test_find_closest_version() -> None:
    runner = CliRunner()
    result = runner.invoke(
        find_closest_version,
        ["--pkg-name", "numpy", "--pkg-version", "2.0.2", "--python-version", "3.10"],
    )
    assert result.exit_code == 0
    assert result.output.strip() == "2.0.2"


#########################################
#     Tests for check_valid_version     #
#########################################


@click_available
def test_check_valid_version() -> None:
    runner = CliRunner()
    result = runner.invoke(
        check_valid_version,
        ["--pkg-name", "numpy", "--pkg-version", "2.0.2", "--python-version", "3.10"],
    )
    assert result.exit_code == 0
    assert result.output.strip() == "True"
