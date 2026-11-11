from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from feu.__main__ import main
from feu.imports import MissingPackageError
from feu.testing import click_available

###########################
#     Tests for main      #
###########################


@click_available
def test_main_runs_the_cli() -> None:
    cli_mock = Mock()
    with patch("feu.cli.cli", cli_mock), patch("feu.__main__.check_click"):
        main()
    cli_mock.assert_called_once_with()


@click_available
def test_main_checks_click_first() -> None:
    cli_mock = Mock()
    with (
        patch("feu.cli.cli", cli_mock),
        patch(
            "feu.__main__.check_click",
            Mock(side_effect=MissingPackageError("no click", name="click")),
        ),
        pytest.raises(MissingPackageError, match="no click"),
    ):
        main()
    cli_mock.assert_not_called()
