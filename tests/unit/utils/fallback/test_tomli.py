from __future__ import annotations

from types import ModuleType

import pytest

from feu.utils.fallback.tomli import tomli


def test_tomli_is_module_type() -> None:
    assert isinstance(tomli, ModuleType)


def test_tomli_module_name() -> None:
    assert tomli.__name__ == "tomli"


def test_tomli_load_class_exists() -> None:
    assert hasattr(tomli, "load")


def test_tomli_load_call() -> None:
    with pytest.raises(RuntimeError, match=r"'tomli' package is required but not installed."):
        tomli.load()
