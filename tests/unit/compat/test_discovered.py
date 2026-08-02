from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

import feu.compat.discovered as discovered
from feu.compat.registry import CompatRegistry, VersionRange
from feu.compat.target import Target

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

T311 = Target(python_version="3.11")

#######################################
#     Tests for register_discovered  #
#######################################


@pytest.fixture
def fake_discovered_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    package_dir = tmp_path / "fake_discovered"
    package_dir.mkdir()
    (package_dir / "numpy.py").write_text(
        "from feu.compat.registry import VersionRange\n"
        "from feu.compat.target import Target\n"
        "PKG_NAME = 'numpy'\n"
        "def compat():\n"
        "    return {Target(python_version='3.11'): [VersionRange('1.0.0', None)]}\n"
    )
    (package_dir / "scikit_learn.py").write_text(
        "from feu.compat.registry import VersionRange\n"
        "from feu.compat.target import Target\n"
        "PKG_NAME = 'scikit-learn'\n"
        "def compat():\n"
        "    return {Target(python_version='3.11'): [VersionRange('2.0.0', None)]}\n"
    )
    monkeypatch.setattr(discovered, "__path__", [str(package_dir)])
    monkeypatch.setattr(discovered, "__name__", "feu.compat.discovered")
    monkeypatch.syspath_prepend(str(tmp_path.parent))
    yield package_dir
    for name in ("feu.compat.discovered.numpy", "feu.compat.discovered.scikit_learn"):
        sys.modules.pop(name, None)


def test_register_discovered_populates_base_layer(fake_discovered_path: Path) -> None:
    del fake_discovered_path  # only needed to install the fixture's patches
    registry = CompatRegistry()
    discovered.register_discovered(registry)

    assert registry.overrides == {}
    assert registry.base["numpy"][T311] == [VersionRange("1.0.0", None)]
    assert registry.base["scikit-learn"][T311] == [VersionRange("2.0.0", None)]
