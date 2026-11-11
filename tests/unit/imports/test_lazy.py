from __future__ import annotations

from collections import OrderedDict
from typing import Any

import pytest

from feu.imports import lazy_exports

#############################
#     Tests for lazy_exports #
#############################


def test_lazy_exports_getattr_imports_the_name() -> None:
    getattr_, _ = lazy_exports("example", {"OrderedDict": "collections"}, {})
    assert getattr_("OrderedDict") is OrderedDict


def test_lazy_exports_getattr_caches_the_name_in_the_namespace() -> None:
    namespace: dict[str, Any] = {}
    getattr_, _ = lazy_exports("example", {"OrderedDict": "collections"}, namespace)
    getattr_("OrderedDict")
    assert namespace == {"OrderedDict": OrderedDict}


def test_lazy_exports_getattr_unknown_name() -> None:
    getattr_, _ = lazy_exports("example", {"OrderedDict": "collections"}, {})
    with pytest.raises(AttributeError, match="module 'example' has no attribute 'missing'"):
        getattr_("missing")


def test_lazy_exports_getattr_missing_attribute_in_module() -> None:
    getattr_, _ = lazy_exports("example", {"Missing": "collections"}, {})
    with pytest.raises(AttributeError, match="Missing"):
        getattr_("Missing")


def test_lazy_exports_dir_is_sorted_and_unique() -> None:
    _, dir_ = lazy_exports("example", {"b": "collections", "a": "collections"}, {"a": 1, "c": 2})
    assert dir_() == ["a", "b", "c"]


def test_lazy_exports_dir_before_import() -> None:
    _, dir_ = lazy_exports("example", {"OrderedDict": "collections"}, {})
    assert dir_() == ["OrderedDict"]
