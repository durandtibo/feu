from __future__ import annotations

from feu.utils.installer import InstallerSpec

###################################
#     Tests for InstallerSpec     #
###################################


def test_installer_spec_name() -> None:
    assert InstallerSpec("my_installer").name == "my_installer"


def test_installer_spec_arguments() -> None:
    assert InstallerSpec("my_installer", arguments="-U").arguments == "-U"


def test_installer_spec_arguments_default() -> None:
    assert InstallerSpec("my_installer").arguments == ""
