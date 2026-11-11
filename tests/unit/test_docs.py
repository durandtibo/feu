from __future__ import annotations

import doctest
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from feu.install import get_default_installer_registry, get_default_resolver_registry

if TYPE_CHECKING:
    from collections.abc import Generator

ROOT = Path(__file__).parents[2]
# The documents whose examples are doctests: they cannot drift from the code (a documented
# example that does not run, e.g. `compare_version("2.0.0", "1.5.0")`, fails here).
DOCUMENTS = [
    ROOT / "README.md",
    ROOT / "docs" / "docs" / "index.md",
    ROOT / "docs" / "docs" / "usage.md",
    ROOT / "docs" / "docs" / "migration.md",
    ROOT / "docs" / "docs" / "dev" / "architecture.md",
    ROOT / "docs" / "docs" / "properties.md",
]


@pytest.fixture(autouse=True)
def _fresh_default_registries() -> Generator[None]:
    r"""The examples register an installer and a resolver in the default
    registries: do not leak them into the other tests."""
    get_default_installer_registry.cache_clear()
    get_default_resolver_registry.cache_clear()
    yield
    get_default_installer_registry.cache_clear()
    get_default_resolver_registry.cache_clear()


@pytest.mark.parametrize("path", DOCUMENTS, ids=lambda p: p.name)
def test_the_examples_of_the_document_run(path: Path) -> None:
    results = doctest.testfile(
        str(path),
        module_relative=False,
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
        verbose=False,
    )
    assert results.failed == 0


@pytest.mark.parametrize("path", DOCUMENTS, ids=lambda p: p.name)
def test_the_document_exists(path: Path) -> None:
    assert path.is_file()
