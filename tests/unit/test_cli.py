from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

pytest.importorskip("click")

from click.testing import CliRunner

from feu import __version__
from feu.cli import cli
from feu.compat import Target, UnsupportedVersionError
from feu.install import InstallerSpec
from feu.testing import click_available, requests_available
from feu.utils.package import PackageSpec

if TYPE_CHECKING:
    from pathlib import Path

# numpy 2.0.2 is the last release for Python 3.9 on every platform, so the answers do not depend
# on the host. The target is a regular build: the default is the current interpreter, which is
# free-threaded on the 3.14t CI jobs.
NUMPY_PY39 = ["--pkg-name", "numpy", "--python-version", "3.9", "--no-free-threaded"]


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


#################################
#     Tests for the group       #
#################################


@click_available
def test_cli_version(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"feu, version {__version__}\n"


@click_available
def test_cli_help(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "package-versions" in result.output


@click_available
def test_cli_no_command_shows_the_usage(runner: CliRunner) -> None:
    result = runner.invoke(cli, [])
    assert "Usage" in result.output


@click_available
def test_cli_unknown_command_is_a_usage_error(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["unknown"])
    assert result.exit_code == 2


@click_available
def test_cli_verbose_configures_the_logging_to_stderr(runner: CliRunner) -> None:
    with (
        patch("feu.cli.logging.basicConfig") as config_mock,
        patch("feu.cli.find_closest_version_", Mock(return_value="2.0.2")),
    ):
        runner.invoke(cli, ["--verbose", "find-closest-version", "--pkg-name", "numpy"])
        config_mock.assert_called_once()
        assert config_mock.call_args.kwargs["level"] == logging.INFO


@click_available
def test_cli_without_verbose_does_not_configure_the_logging(runner: CliRunner) -> None:
    with (
        patch("feu.cli.logging.basicConfig") as config_mock,
        patch("feu.cli.find_closest_version_", Mock(return_value="2.0.2")),
    ):
        runner.invoke(cli, ["find-closest-version", "--pkg-name", "numpy"])
        config_mock.assert_not_called()


@click_available
def test_cli_verbose_has_no_short_option(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["-v", "find-closest-version"])
    assert result.exit_code == 2


#############################
#     Tests for install     #
#############################


@click_available
def test_install(runner: CliRunner) -> None:
    mock = Mock()
    with patch("feu.cli.install_package_closest_version", mock):
        result = runner.invoke(cli, ["install", "--pkg-name", "numpy", "--pkg-version", "2.0.2"])
    assert result.exit_code == 0
    assert result.output == ""
    assert mock.call_args.kwargs == {
        "installer": InstallerSpec(name="pip"),
        "package": PackageSpec(name="numpy", version="2.0.2"),
    }


@click_available
def test_install_with_pkg_extras(runner: CliRunner) -> None:
    mock = Mock()
    with patch("feu.cli.install_package_closest_version", mock):
        runner.invoke(cli, ["install", "-n", "numpy", "-v", "2.0.2", "-e", "dev,doc"])
    assert mock.call_args.kwargs["package"] == PackageSpec("numpy", "2.0.2", ["dev", "doc"])


@click_available
def test_install_with_empty_pkg_extras(runner: CliRunner) -> None:
    mock = Mock()
    with patch("feu.cli.install_package_closest_version", mock):
        runner.invoke(cli, ["install", "-n", "numpy", "-v", "2.0.2", "-e", " "])
    assert mock.call_args.kwargs["package"] == PackageSpec("numpy", "2.0.2")


@click_available
@pytest.mark.parametrize("name", ["pip", "uv"])
def test_install_installer_name(runner: CliRunner, name: str) -> None:
    mock = Mock()
    with patch("feu.cli.install_package_closest_version", mock):
        runner.invoke(cli, ["install", "-n", "numpy", "-v", "2.0.2", "--installer-name", name])
    assert mock.call_args.kwargs["installer"] == InstallerSpec(name=name)


@click_available
def test_install_installer_args_are_split_once(runner: CliRunner) -> None:
    mock = Mock()
    with patch("feu.cli.install_package_closest_version", mock):
        runner.invoke(
            cli,
            ["install", "-n", "numpy", "-v", "2.0.2", "-a", "-U --index-url 'https://a b'"],
        )
    assert mock.call_args.kwargs["installer"].arguments == ("-U", "--index-url", "https://a b")


@click_available
def test_install_without_pkg_version(runner: CliRunner) -> None:
    mock = Mock()
    with patch("feu.cli.install_package_closest_version", mock):
        result = runner.invoke(cli, ["install", "--pkg-name", "numpy"])
    assert result.exit_code == 0
    assert mock.call_args.kwargs["package"] == PackageSpec("numpy", "")


@click_available
def test_install_with_empty_pkg_version(runner: CliRunner) -> None:
    mock = Mock()
    with patch("feu.cli.install_package_closest_version", mock):
        runner.invoke(cli, ["install", "--pkg-name", "numpy", "--pkg-version="])
    assert mock.call_args.kwargs["package"] == PackageSpec("numpy", "")


@click_available
def test_install_with_wildcard_pkg_version(runner: CliRunner) -> None:
    mock = Mock()
    with patch("feu.cli.install_package_closest_version", mock):
        runner.invoke(cli, ["install", "--pkg-name", "numpy", "--pkg-version", "1.*"])
    assert mock.call_args.kwargs["package"] == PackageSpec("numpy", "1.*")


@click_available
def test_install_unsupported_version_exits_with_1(runner: CliRunner) -> None:
    mock = Mock(side_effect=UnsupportedVersionError("no compatible version"))
    with patch("feu.cli.install_package_closest_version", mock):
        result = runner.invoke(cli, ["install", "-n", "numpy", "-v", "1.24.*"])
    assert result.exit_code == 1
    assert "no compatible version" in result.output


@click_available
def test_install_missing_pkg_name_is_a_usage_error(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["install"])
    assert result.exit_code == 2


@click_available
def test_install_does_not_accept_target_options(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["install", "-n", "numpy", "--python-version", "3.9"])
    assert result.exit_code == 2


@click_available
def test_install_invalid_wildcard_is_a_usage_error(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["install", "-n", "numpy", "-v", "2.*.1"])
    assert result.exit_code == 2
    assert "invalid version wildcard" in result.output


@click_available
def test_find_closest_version_invalid_wildcard_is_a_usage_error(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["find-closest-version", *NUMPY_PY39, "-v", "2.*.1"])
    assert result.exit_code == 2


@click_available
def test_find_closest_version_invalid_python_version_is_a_usage_error(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["find-closest-version", "-n", "numpy", "-p", "3.9.1"])
    assert result.exit_code == 2


@click_available
def test_check_valid_version_invalid_wildcard_is_a_usage_error(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["check-valid-version", *NUMPY_PY39, "-v", "*"])
    assert result.exit_code == 2


##########################################
#     Tests for find-closest-version     #
##########################################


@click_available
def test_find_closest_version(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["find-closest-version", *NUMPY_PY39, "--pkg-version", "99.0.0"])
    assert result.exit_code == 0
    assert result.output == "2.0.2\n"


@click_available
def test_find_closest_version_exact_valid_version(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["find-closest-version", *NUMPY_PY39, "-v", "2.0.0"])
    assert result.output == "2.0.0\n"


@click_available
def test_find_closest_version_without_pkg_version(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["find-closest-version", *NUMPY_PY39])
    assert result.output == "2.0.2\n"


@click_available
def test_find_closest_version_with_empty_pkg_version(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["find-closest-version", *NUMPY_PY39, "--pkg-version="])
    assert result.output == "2.0.2\n"


@click_available
@requests_available
def test_find_closest_version_with_wildcard_pkg_version(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["find-closest-version", *NUMPY_PY39, "--pkg-version", "1.*"])
    assert result.output == "1.26.4\n"


@click_available
def test_find_closest_version_unsupported_exits_with_1(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["find-closest-version", *NUMPY_PY39, "-v", "3.*"])
    assert result.exit_code == 1


@click_available
@requests_available
def test_find_closest_version_unsupported_prints_the_message_not_none(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["find-closest-version", *NUMPY_PY39, "-v", "3.*"])
    assert "None" not in result.output
    assert "matches '3.*'" in result.output


@click_available
def test_find_closest_version_target_options(runner: CliRunner) -> None:
    mock = Mock(return_value="2.0.2")
    with (
        patch("feu.cli.find_closest_version_", mock),
        patch("feu.compat.target.get_current_os", Mock(return_value="macos")),
        patch("feu.compat.target.get_current_arch", Mock(return_value="arm64")),
    ):
        result = runner.invoke(
            cli,
            ["find-closest-version", "-n", "numpy", "-v", "2.0.2", "-p", "3.10", "--free-threaded"],
        )
    assert result.exit_code == 0
    assert mock.call_args.kwargs == {
        "pkg_name": "numpy",
        "pkg_version": "2.0.2",
        "target": Target(python_version="3.10", free_threaded=True, os="macos", arch="arm64"),
    }


@click_available
def test_find_closest_version_no_free_threaded(runner: CliRunner) -> None:
    mock = Mock(return_value="2.0.2")
    with (
        patch("feu.cli.find_closest_version_", mock),
        patch("feu.compat.target.is_free_threaded", Mock(return_value=True)),
    ):
        runner.invoke(
            cli, ["find-closest-version", "-n", "numpy", "-p", "3.10", "--no-free-threaded"]
        )
    assert mock.call_args.kwargs["target"].free_threaded is False


@click_available
def test_find_closest_version_short_free_threaded_is_a_flag(runner: CliRunner) -> None:
    mock = Mock(return_value="2.0.2")
    with patch("feu.cli.find_closest_version_", mock):
        runner.invoke(cli, ["find-closest-version", "-n", "numpy", "-p", "3.14", "-f"])
    assert mock.call_args.kwargs["target"].free_threaded is True


@click_available
def test_find_closest_version_default_target(runner: CliRunner) -> None:
    mock = Mock(return_value="2.0.2")
    with (
        patch("feu.cli.find_closest_version_", mock),
        patch("feu.compat.target.get_python_version", Mock(return_value="3.12")),
        patch("feu.compat.target.is_free_threaded", Mock(return_value=False)),
        patch("feu.compat.target.get_current_os", Mock(return_value="macos")),
        patch("feu.compat.target.get_current_arch", Mock(return_value="arm64")),
    ):
        runner.invoke(cli, ["find-closest-version", "-n", "numpy"])
    assert mock.call_args.kwargs["target"] == Target("3.12", False, "macos", "arm64")


@click_available
def test_find_closest_version_free_threaded_with_a_value_is_a_usage_error(
    runner: CliRunner,
) -> None:
    result = runner.invoke(cli, ["find-closest-version", "-n", "numpy", "--free-threaded", "true"])
    assert result.exit_code == 2


@pytest.mark.parametrize("option", ["--os", "--arch"])
@click_available
def test_find_closest_version_has_no_os_or_arch_option(runner: CliRunner, option: str) -> None:
    result = runner.invoke(cli, ["find-closest-version", "-n", "numpy", option, "linux"])
    assert result.exit_code == 2


@click_available
def test_find_closest_version_missing_pkg_name_is_a_usage_error(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["find-closest-version"])
    assert result.exit_code == 2


#########################################
#     Tests for check-valid-version     #
#########################################


@click_available
def test_check_valid_version_valid(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["check-valid-version", *NUMPY_PY39, "-v", "2.0.2"])
    assert result.exit_code == 0
    assert result.output == "True\n"


@click_available
def test_check_valid_version_not_valid_exits_with_1(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["check-valid-version", *NUMPY_PY39, "-v", "2.3.0"])
    assert result.exit_code == 1
    assert result.output == "False\n"


@click_available
def test_check_valid_version_without_pkg_version(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["check-valid-version", *NUMPY_PY39])
    assert result.output == "True\n"


@click_available
@requests_available
def test_check_valid_version_wildcard(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["check-valid-version", *NUMPY_PY39, "-v", "2.*"])
    assert result.exit_code == 0


@click_available
@requests_available
def test_check_valid_version_unmatched_wildcard_exits_with_1(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["check-valid-version", *NUMPY_PY39, "-v", "3.*"])
    assert result.exit_code == 1
    assert result.output == "False\n"


@click_available
def test_check_valid_version_target_options(runner: CliRunner) -> None:
    mock = Mock(return_value=True)
    with (
        patch("feu.cli.is_valid_version_", mock),
        patch("feu.compat.target.get_current_os", Mock(return_value="linux")),
        patch("feu.compat.target.get_current_arch", Mock(return_value="x86_64")),
    ):
        runner.invoke(cli, ["check-valid-version", "-n", "numpy", "-v", "2.0.2", "-p", "3.14t"])
    assert mock.call_args.kwargs["target"] == Target("3.14", True, "linux", "x86_64")


@click_available
def test_check_valid_version_missing_pkg_name_is_a_usage_error(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["check-valid-version"])
    assert result.exit_code == 2


@pytest.mark.parametrize("option", ["--os", "--arch"])
@click_available
def test_check_valid_version_has_no_os_or_arch_option(runner: CliRunner, option: str) -> None:
    result = runner.invoke(cli, ["check-valid-version", "-n", "numpy", option, "linux"])
    assert result.exit_code == 2


########################################
#     Tests for package-versions       #
########################################

PYPROJECT = """\
[project]
name = "demo"
dependencies = ["packaging>=22.0", "numpy>=1.21"]
"""


@pytest.fixture
def pyproject(tmp_path: Path) -> Path:
    path = tmp_path / "pyproject.toml"
    path.write_text(PYPROJECT)
    return path


@click_available
def test_package_versions_prints_the_json(runner: CliRunner, pyproject: Path) -> None:
    with patch("feu.cli.fetch_package_versions", Mock(return_value={"numpy": ["1.21.0"]})) as mock:
        result = runner.invoke(cli, ["package-versions", "--pyproject", str(pyproject)])
    assert result.exit_code == 0
    assert json.loads(result.output) == {"numpy": ["1.21.0"]}
    mock.assert_called_once_with(str(pyproject), major_only=("packaging",))


@click_available
def test_package_versions_writes_the_output_file(
    runner: CliRunner, pyproject: Path, tmp_path: Path
) -> None:
    output = tmp_path / "versions.json"
    with patch("feu.cli.fetch_package_versions", Mock(return_value={"numpy": ["1.21.0"]})):
        result = runner.invoke(
            cli, ["package-versions", "--pyproject", str(pyproject), "--output", str(output)]
        )
    assert result.exit_code == 0
    assert result.output == ""
    assert json.loads(output.read_text()) == {"numpy": ["1.21.0"]}


@click_available
def test_package_versions_major_only_is_repeatable(runner: CliRunner, pyproject: Path) -> None:
    with patch("feu.cli.fetch_package_versions", Mock(return_value={})) as mock:
        runner.invoke(
            cli,
            [
                "package-versions",
                "--pyproject",
                str(pyproject),
                "--major-only",
                "packaging",
                "--major-only",
                "click",
            ],
        )
    mock.assert_called_once_with(str(pyproject), major_only=("packaging", "click"))


@click_available
def test_package_versions_default_pyproject(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text(PYPROJECT)
    with patch("feu.cli.fetch_package_versions", Mock(return_value={})) as mock:
        runner.invoke(cli, ["package-versions"])
    mock.assert_called_once_with("pyproject.toml", major_only=("packaging",))


@click_available
def test_package_versions_default_pyproject_missing_is_a_usage_error(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(cli, ["package-versions"]).exit_code == 2


@click_available
def test_package_versions_missing_pyproject_is_a_usage_error(
    runner: CliRunner, tmp_path: Path
) -> None:
    result = runner.invoke(cli, ["package-versions", "--pyproject", str(tmp_path / "missing.toml")])
    assert result.exit_code == 2
