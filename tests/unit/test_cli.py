from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

pytest.importorskip("click")

from click.testing import CliRunner

from feu.cli import check_valid_version, find_closest_version, install
from feu.compat import Target, UnsupportedVersionError
from feu.install import InstallerSpec
from feu.testing import click_available
from feu.utils.package import PackageSpec

#############################
#     Tests for install     #
#############################


@click_available
def test_install() -> None:
    runner = CliRunner()
    mock = Mock()
    with patch("feu.cli.install_package_closest_version", mock):
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
    with patch("feu.cli.install_package_closest_version", mock):
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
    with patch("feu.cli.install_package_closest_version", mock):
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
    with patch("feu.cli.install_package_closest_version", mock):
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
    # Pin --os/--arch explicitly rather than relying on the host's
    # implicit values: numpy has no wheels at all for some target
    # combinations (e.g. python 3.10 on windows/arm64), which would make
    # this test's outcome depend on the host running it.
    runner = CliRunner()
    result = runner.invoke(
        find_closest_version,
        [
            "--pkg-name",
            "numpy",
            "--pkg-version",
            "2.0.2",
            "--python-version",
            "3.10",
            "--os",
            "linux",
            "--arch",
            "x86_64",
        ],
    )
    assert result.exit_code == 0
    assert result.output.strip() == "2.0.2"


@click_available
def test_find_closest_version_all_options() -> None:
    runner = CliRunner()
    mock = Mock(return_value="2.0.2")
    with patch("feu.cli.find_closest_version_", mock):
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
        patch("feu.cli.find_closest_version_", mock),
        patch("feu.compat.target.get_python_version", Mock(return_value="3.12")),
        patch("feu.compat.target.is_free_threaded", Mock(return_value=False)),
        patch("feu.compat.target.get_current_os", Mock(return_value="macos")),
        patch("feu.compat.target.get_current_arch", Mock(return_value="arm64")),
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
    with patch("feu.cli.find_closest_version_", mock):
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
    # Pin --os/--arch explicitly rather than relying on the host's
    # implicit values: numpy has no wheels at all for some target
    # combinations (e.g. python 3.10 on windows/arm64), which would make
    # this test's outcome depend on the host running it.
    runner = CliRunner()
    result = runner.invoke(
        check_valid_version,
        [
            "--pkg-name",
            "numpy",
            "--pkg-version",
            "2.0.2",
            "--python-version",
            "3.10",
            "--os",
            "linux",
            "--arch",
            "x86_64",
        ],
    )
    assert result.exit_code == 0
    assert result.output.strip() == "True"


@click_available
def test_check_valid_version_all_options() -> None:
    runner = CliRunner()
    mock = Mock(return_value=True)
    with patch("feu.cli.is_valid_version", mock):
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
        patch("feu.cli.is_valid_version", mock),
        patch("feu.compat.target.get_python_version", Mock(return_value="3.12")),
        patch("feu.compat.target.is_free_threaded", Mock(return_value=False)),
        patch("feu.compat.target.get_current_os", Mock(return_value="macos")),
        patch("feu.compat.target.get_current_arch", Mock(return_value="arm64")),
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


######################################################
#     Tests for the version request of the CLI      #
######################################################


@click_available
def test_install_without_pkg_version() -> None:
    runner = CliRunner()
    mock = Mock()
    with patch("feu.cli.install_package_closest_version", mock):
        result = runner.invoke(install, ["--pkg-name", "numpy"])
        assert result.exit_code == 0
        assert mock.call_args.kwargs["package"] == PackageSpec(name="numpy", version="", extras=[])


@click_available
def test_install_with_empty_pkg_version() -> None:
    runner = CliRunner()
    mock = Mock()
    with patch("feu.cli.install_package_closest_version", mock):
        result = runner.invoke(install, ["--pkg-name", "numpy", "--pkg-version="])
        assert result.exit_code == 0
        assert mock.call_args.kwargs["package"] == PackageSpec(name="numpy", version="", extras=[])


@click_available
def test_install_with_wildcard_pkg_version() -> None:
    runner = CliRunner()
    mock = Mock()
    with patch("feu.cli.install_package_closest_version", mock):
        result = runner.invoke(install, ["--pkg-name", "numpy", "--pkg-version", "1.*"])
        assert result.exit_code == 0
        assert mock.call_args.kwargs["package"] == PackageSpec(
            name="numpy", version="1.*", extras=[]
        )


NUMPY_PY39 = ["--pkg-name", "numpy", "--python-version", "3.9", "--os", "linux", "--arch", "x86_64"]


@click_available
def test_find_closest_version_without_pkg_version() -> None:
    result = CliRunner().invoke(find_closest_version, NUMPY_PY39)
    assert result.output.strip() == "2.0.2"


@click_available
def test_find_closest_version_with_empty_pkg_version() -> None:
    result = CliRunner().invoke(find_closest_version, [*NUMPY_PY39, "--pkg-version="])
    assert result.output.strip() == "2.0.2"


@click_available
def test_find_closest_version_with_wildcard_pkg_version() -> None:
    result = CliRunner().invoke(find_closest_version, [*NUMPY_PY39, "--pkg-version", "1.*"])
    assert result.output.strip() == "1.26.4"


@click_available
def test_find_closest_version_with_unmatched_wildcard_pkg_version() -> None:
    result = CliRunner().invoke(find_closest_version, [*NUMPY_PY39, "--pkg-version", "3.*"])
    assert result.output.strip() == "None"


@click_available
def test_check_valid_version_without_pkg_version() -> None:
    result = CliRunner().invoke(check_valid_version, NUMPY_PY39)
    assert result.output.strip() == "True"


@click_available
def test_check_valid_version_with_wildcard_pkg_version() -> None:
    result = CliRunner().invoke(check_valid_version, [*NUMPY_PY39, "--pkg-version", "2.*"])
    assert result.output.strip() == "True"


@click_available
def test_check_valid_version_with_unmatched_wildcard_pkg_version() -> None:
    result = CliRunner().invoke(check_valid_version, [*NUMPY_PY39, "--pkg-version", "3.*"])
    assert result.output.strip() == "False"
