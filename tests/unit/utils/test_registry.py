from __future__ import annotations

import pytest
from packaging.utils import canonicalize_name

from feu.utils.registry import Registry

##############################
#     Tests for Registry     #
##############################


def test_registry_empty() -> None:
    assert len(Registry[int]("number")) == 0


def test_registry_repr() -> None:
    registry = Registry[int]("number")
    registry.register("one", 1)
    assert repr(registry) == "Registry(kind='number', keys=['one'])"


def test_registry_register() -> None:
    registry = Registry[int]("number")
    registry.register("one", 1)
    assert registry.find("one") == 1


def test_registry_register_exist_ok_false() -> None:
    registry = Registry[int]("number")
    registry.register("one", 1)
    with pytest.raises(
        RuntimeError, match=r"A number \(1\) is already registered for the key 'one'"
    ):
        registry.register("one", 11)


def test_registry_register_exist_ok_false_keeps_value() -> None:
    registry = Registry[int]("number")
    registry.register("one", 1)
    with pytest.raises(RuntimeError, match="already registered"):
        registry.register("one", 11)
    assert registry.find("one") == 1


def test_registry_register_exist_ok_true() -> None:
    registry = Registry[int]("number")
    registry.register("one", 1)
    registry.register("one", 11, exist_ok=True)
    assert registry.find("one") == 11


def test_registry_register_many() -> None:
    registry = Registry[int]("number")
    registry.register_many({"one": 1, "two": 2})
    assert registry.keys() == ["one", "two"]


def test_registry_register_many_conflict() -> None:
    registry = Registry[int]("number")
    registry.register("one", 1)
    with pytest.raises(RuntimeError, match="already registered for the key 'one'"):
        registry.register_many({"one": 11, "two": 2})


def test_registry_register_many_exist_ok_true() -> None:
    registry = Registry[int]("number")
    registry.register("one", 1)
    registry.register_many({"one": 11, "two": 2}, exist_ok=True)
    assert registry.find("one") == 11


def test_registry_find_unknown_lists_known_keys() -> None:
    registry = Registry[int]("number")
    registry.register_many({"two": 2, "one": 1})
    with pytest.raises(
        KeyError, match=r"No number is registered for the key 'three'. Known keys: \['one', 'two'\]"
    ):
        registry.find("three")


def test_registry_get() -> None:
    registry = Registry[int]("number")
    registry.register("one", 1)
    assert registry.get("one") == 1


def test_registry_get_missing_is_none() -> None:
    assert Registry[int]("number").get("one") is None


def test_registry_get_missing_default() -> None:
    assert Registry[int]("number").get("one", 0) == 0


def test_registry_contains_true() -> None:
    registry = Registry[int]("number")
    registry.register("one", 1)
    assert "one" in registry


def test_registry_contains_false() -> None:
    assert "one" not in Registry[int]("number")


def test_registry_contains_not_a_string() -> None:
    assert 1 not in Registry[int]("number")


def test_registry_len() -> None:
    registry = Registry[int]("number")
    registry.register_many({"one": 1, "two": 2})
    assert len(registry) == 2


def test_registry_iter_is_sorted() -> None:
    registry = Registry[int]("number")
    registry.register_many({"two": 2, "one": 1})
    assert list(registry) == ["one", "two"]


def test_registry_keys_are_sorted() -> None:
    registry = Registry[int]("number")
    registry.register_many({"b": 2, "a": 1})
    assert registry.keys() == ["a", "b"]


def test_registry_without_normalize_is_case_sensitive() -> None:
    registry = Registry[int]("number")
    registry.register("One", 1)
    assert "one" not in registry


def test_registry_normalize_register_and_find() -> None:
    registry = Registry[int]("number", normalize=str.lower)
    registry.register("One", 1)
    assert registry.find("ONE") == 1


def test_registry_normalize_keys() -> None:
    registry = Registry[int]("number", normalize=str.lower)
    registry.register("One", 1)
    assert registry.keys() == ["one"]


def test_registry_normalize_conflict() -> None:
    registry = Registry[int]("number", normalize=str.lower)
    registry.register("One", 1)
    with pytest.raises(RuntimeError, match="already registered for the key 'one'"):
        registry.register("ONE", 11)


def test_registry_normalize_contains() -> None:
    registry = Registry[int]("number", normalize=str.lower)
    registry.register("one", 1)
    assert "ONE" in registry


def test_registry_normalize_get() -> None:
    registry = Registry[int]("number", normalize=str.lower)
    registry.register("one", 1)
    assert registry.get("ONE") == 1


@pytest.mark.parametrize("name", ["Scikit-Learn", "scikit_learn", "SCIKIT.LEARN"])
def test_registry_canonical_package_names(name: str) -> None:
    registry = Registry[int]("resolver", normalize=canonicalize_name)
    registry.register("scikit-learn", 1)
    assert registry.find(name) == 1
