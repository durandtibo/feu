from __future__ import annotations

import json
import subprocess
import sys

import pytest

OPTIONAL_MODULES = ("requests", "urllib3", "click", "git", "rich", "pytest")


def _loaded_optional_modules(module: str) -> list[str]:
    code = (
        "import json, sys\n"
        f"import {module}\n"
        f"print(json.dumps(sorted(m for m in {OPTIONAL_MODULES!r} if m in sys.modules)))\n"
    )
    out = subprocess.run(  # noqa: S603
        [sys.executable, "-I", "-c", code], check=True, capture_output=True, text=True
    )
    return json.loads(out.stdout)


@pytest.mark.parametrize(
    "module",
    [
        "feu",
        "feu.compat",
        "feu.install",
        "feu.version",
        "feu.imports",
        "feu.utils.http",
        "feu.local_git",
        "feu.github",
    ],
)
def test_import_does_not_import_an_optional_library(module: str) -> None:
    """Test that importing ``feu`` and its subpackages does not import
    an optional library."""
    assert _loaded_optional_modules(module) == []
