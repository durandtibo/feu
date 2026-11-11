from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(autouse=True)
def _tools_available() -> Generator[None]:
    r"""Make the unit tests independent of the tools of the host: ``pip``
    and ``uv`` are reported as available, and the commands are patched
    by the tests."""
    with (
        patch("feu.install.pip.installer.find_spec", return_value=object()),
        patch("feu.install.pip.installer.which", return_value="/usr/bin/uv"),
    ):
        yield
