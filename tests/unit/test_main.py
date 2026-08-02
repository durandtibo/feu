from __future__ import annotations

from unittest.mock import Mock, patch

from click.testing import CliRunner

from feu.__main__ import check_valid_version, find_closest_version, install
from feu.compat import Target, UnsupportedVersionError
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


@click_available
def test_find_closest_version_all_options() -> None:
    runner = CliRunner()
    mock = Mock(return_value="2.0.2")
    with patch("feu.__main__.find_closest_version_", mock):
        result = runner.invoke(
            find_closest_version,
            [
                "--pkg-name",
                "numpy",
                "--pkg-version",
                "2.0.2",
                "--python-version",
                "3.10",
                "--free-threaded",
                "true",
                "--os",
                "linux",
                "--arch",
                "x86_64",
            ],
        )
        assert result.exit_code == 0
        assert result.output.strip() == "2.0.2"
        assert mock.call_args.kwargs == {
            "pkg_name": "numpy",
            "pkg_version": "2.0.2",
            "target": Target(python_version="3.10", free_threaded=True, os="linux", arch="x86_64"),
        }


@click_available
def test_find_closest_version_default_options() -> None:
    runner = CliRunner()
    mock = Mock(return_value="2.0.2")
    with (
        patch("feu.__main__.find_closest_version_", mock),
        patch("feu.__main__.get_python_version", Mock(return_value="3.12")),
        patch("feu.__main__.is_free_threaded", Mock(return_value=False)),
        patch("feu.__main__.get_current_os", Mock(return_value="macos")),
        patch("feu.__main__.get_current_arch", Mock(return_value="arm64")),
    ):
        result = runner.invoke(
            find_closest_version, ["--pkg-name", "numpy", "--pkg-version", "2.0.2"]
        )
        assert result.exit_code == 0
        assert result.output.strip() == "2.0.2"
        assert mock.call_args.kwargs == {
            "pkg_name": "numpy",
            "pkg_version": "2.0.2",
            "target": Target(python_version="3.12", free_threaded=False, os="macos", arch="arm64"),
        }


@click_available
def test_find_closest_version_unsupported() -> None:
    runner = CliRunner()
    mock = Mock(side_effect=UnsupportedVersionError("no valid version"))
    with patch("feu.__main__.find_closest_version_", mock):
        result = runner.invoke(
            find_closest_version,
            ["--pkg-name", "numpy", "--pkg-version", "2.0.2", "--python-version", "3.10"],
        )
        assert result.exit_code == 0
        assert result.output.strip() == "None"


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


@click_available
def test_check_valid_version_all_options() -> None:
    runner = CliRunner()
    mock = Mock(return_value=True)
    with patch("feu.__main__.is_valid_version", mock):
        result = runner.invoke(
            check_valid_version,
            [
                "--pkg-name",
                "numpy",
                "--pkg-version",
                "2.0.2",
                "--python-version",
                "3.10",
                "--free-threaded",
                "false",
                "--os",
                "windows",
                "--arch",
                "arm64",
            ],
        )
        assert result.exit_code == 0
        assert result.output.strip() == "True"
        assert mock.call_args.kwargs == {
            "pkg_name": "numpy",
            "pkg_version": "2.0.2",
            "target": Target(
                python_version="3.10", free_threaded=False, os="windows", arch="arm64"
            ),
        }


@click_available
def test_check_valid_version_default_options() -> None:
    runner = CliRunner()
    mock = Mock(return_value=True)
    with (
        patch("feu.__main__.is_valid_version", mock),
        patch("feu.__main__.get_python_version", Mock(return_value="3.12")),
        patch("feu.__main__.is_free_threaded", Mock(return_value=False)),
        patch("feu.__main__.get_current_os", Mock(return_value="macos")),
        patch("feu.__main__.get_current_arch", Mock(return_value="arm64")),
    ):
        result = runner.invoke(
            check_valid_version, ["--pkg-name", "numpy", "--pkg-version", "2.0.2"]
        )
        assert result.exit_code == 0
        assert result.output.strip() == "True"
        assert mock.call_args.kwargs == {
            "pkg_name": "numpy",
            "pkg_version": "2.0.2",
            "target": Target(python_version="3.12", free_threaded=False, os="macos", arch="arm64"),
        }
