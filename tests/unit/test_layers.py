from __future__ import annotations

import ast
from pathlib import Path

import pytest

import feu

SRC = Path(feu.__file__).parent

# The imports go one way: a layer imports only the layers on its left.
LAYERS = ["imports", "utils", "version", "compat", "install", "cli"]
# Packages that are not part of the chain; they only use the lower layers.
OTHER_LAYERS = {"github": 2, "local_git": 2, "testing": 5, "__main__": 6, "__init__": 6}


def _layer(name: str) -> int | None:
    if name in LAYERS:
        return LAYERS.index(name)
    return OTHER_LAYERS.get(name)


def _top_level(path: Path) -> str:
    relative = path.relative_to(SRC)
    return relative.parts[0].removesuffix(".py")


def _imported_features(path: Path) -> set[str]:
    imported = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    return {name.split(".")[1] for name in imported if name.startswith("feu.")}


def _violations(path: Path) -> list[str]:
    layer = _layer(_top_level(path))
    return [
        f"{path.relative_to(SRC)} imports feu.{name}"
        for name in sorted(_imported_features(path))
        if (other := _layer(name)) is not None and layer is not None and other > layer
    ]


@pytest.mark.parametrize("path", sorted(SRC.rglob("*.py")), ids=lambda p: str(p.relative_to(SRC)))
def test_a_module_does_not_import_a_higher_layer(path: Path) -> None:
    assert _violations(path) == []


def test_imports_imports_nothing_from_feu() -> None:
    assert not [
        path for path in (SRC / "imports").rglob("*.py") if _imported_features(path) - {"imports"}
    ]
