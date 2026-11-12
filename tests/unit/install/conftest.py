from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from feu.install import get_default_installer_registry, get_default_resolver_registry

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(autouse=True)
def _tools_available() -> Generator[None]:
    r"""Make the unit tests independent of the tools of the host:
    ``pip`` and ``uv`` are reported as available, and the commands are
    patched by the tests."""
    with (
        patch("feu.install.installer.is_pip_available", return_value=True),
        patch("feu.install.installer.is_uv_available", return_value=True),
    ):
        yield


@pytest.fixture(autouse=True)
def _fresh_default_registries() -> Generator[None]:
    r"""Reset the default registries so a test cannot leak a
    registration into another one."""
    get_default_installer_registry.cache_clear()
    get_default_resolver_registry.cache_clear()
    yield
    get_default_installer_registry.cache_clear()
    get_default_resolver_registry.cache_clear()
