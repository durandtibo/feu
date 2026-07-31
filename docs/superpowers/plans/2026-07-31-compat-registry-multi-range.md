# Compat Registry Multi-Range Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let `CompatRegistry` express disjoint supported version ranges per `(package, Target)` (e.g. pydantic 1.x and 2.8+ both valid, 2.0–2.7 not), instead of a single min/max pair.

**Architecture:** Replace the `{"min": ..., "max": ...}` dict stored per `(package, Target)` with a `list[VersionRange]`, where `VersionRange` is a new `NamedTuple`. An empty list means "unsupported", replacing the `UNSUPPORTED` string sentinel, which is removed. `is_valid_version` becomes "valid in any range"; `find_closest_version` snaps to the nearest range boundary below/above the whole set, or up to the next range's min when in a gap between two ranges.

**Tech Stack:** Python, `packaging.version.Version`, pytest.

## Global Constraints

- No backward-compatibility shim: `register()` no longer accepts `pkg_version_min`/`pkg_version_max` kwargs; every caller (production code, tests, `defaults.py`) moves to the `ranges=list[VersionRange]` shape in this same change.
- `UNSUPPORTED` string sentinel is removed entirely, including its export from `feu/compat/__init__.py` and `feu/compat/registry.py`.
- Ranges are assumed non-overlapping and ascending; this is not validated at registration time.
- `get_config` returns `list[VersionRange]` directly (no wrapping dict).

---

### Task 1: `VersionRange` type and `CompatRegistry` core rewrite

**Files:**
- Modify: `src/feu/compat/registry.py` (entire file — rewrite storage, `register`, `register_many`, `get_config`, `is_unsupported`, `get_version_ranges` (renames `get_min_and_max_versions`), `is_valid_version`, `find_closest_version`; remove `UNSUPPORTED`)
- Modify: `tests/unit/compat/test_registry.py` (entire file — rewrite to the new API)

**Interfaces:**
- Produces: `feu.compat.registry.VersionRange` — `NamedTuple` with fields `min: str | None`, `max: str | None`.
- Produces: `CompatRegistry.register(pkg_name: str, target: Target, *, ranges: list[VersionRange], exist_ok: bool = False, layer: Literal["base","override"] = "override") -> None`
- Produces: `CompatRegistry.register_many(mapping: dict[str, dict[Target, list[VersionRange]]], exist_ok: bool = False, layer: ... = "override") -> None`
- Produces: `CompatRegistry.get_config(pkg_name: str, target: Target) -> list[VersionRange]`
- Produces: `CompatRegistry.is_unsupported(pkg_name: str, target: Target) -> bool`
- Produces: `CompatRegistry.get_version_ranges(pkg_name: str, target: Target) -> list[tuple[Version | None, Version | None]]` (raises `UnsupportedVersionError` if `get_config` returns `[]`)
- Produces: `CompatRegistry.is_valid_version(pkg_name: str, pkg_version: str, target: Target) -> bool`
- Produces: `CompatRegistry.find_closest_version(pkg_name: str, pkg_version: str, target: Target) -> str`
- Produces: `CompatRegistry.__init__(initial_state: dict[str, dict[Target, list[VersionRange]]] | None = None)`
- Removed: `UNSUPPORTED` constant, `get_min_and_max_versions` method, `pkg_version_min`/`pkg_version_max` kwargs on `register`.

- [ ] **Step 1: Write failing tests for the new `CompatRegistry` API**

Replace the entire contents of `tests/unit/compat/test_registry.py` with:

```python
from __future__ import annotations

import pytest
from packaging.version import Version

from feu.compat.registry import CompatRegistry, UnsupportedVersionError, VersionRange
from feu.compat.target import Target

T311 = Target(python_version="3.11")
T310 = Target(python_version="3.10")
T315 = Target(python_version="3.15")

##################################
#     Tests for CompatRegistry    #
##################################


def test_compat_registry_init_empty() -> None:
    registry = CompatRegistry()
    assert registry.base == {}
    assert registry.overrides == {}


def test_compat_registry_init_with_state() -> None:
    registry = CompatRegistry({"numpy": {T311: [VersionRange("1.0.0", None)]}})
    assert registry.base == {"numpy": {T311: [VersionRange("1.0.0", None)]}}
    assert registry.overrides == {}


def test_compat_registry_init_copies_state() -> None:
    state = {"numpy": {T311: [VersionRange("1.0.0", None)]}}
    registry = CompatRegistry(state)
    registry.register("torch", T311, ranges=[VersionRange("2.0.0", None)], layer="base")
    assert "torch" not in state


def test_compat_registry_repr() -> None:
    registry = CompatRegistry()
    assert repr(registry).startswith("CompatRegistry(")


def test_compat_registry_str() -> None:
    registry = CompatRegistry()
    assert str(registry).startswith("CompatRegistry(")


def test_compat_registry_register_default_layer_is_override() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.0.2")])
    assert registry.overrides == {"my_package": {T311: [VersionRange("1.2.0", "2.0.2")]}}
    assert registry.base == {}


def test_compat_registry_register_base_layer() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.0.2")], layer="base")
    assert registry.base == {"my_package": {T311: [VersionRange("1.2.0", "2.0.2")]}}
    assert registry.overrides == {}


def test_compat_registry_register_multiple_ranges() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange(None, "1.10.13"), VersionRange("2.0.0", None)],
        layer="base",
    )
    assert registry.base == {
        "pydantic": {T311: [VersionRange(None, "1.10.13"), VersionRange("2.0.0", None)]}
    }


def test_compat_registry_register_multiple_targets() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.0.2")], layer="base")
    registry.register("my_package", T310, ranges=[VersionRange("1.1.0", "1.5.2")], layer="base")
    assert registry.base == {
        "my_package": {
            T311: [VersionRange("1.2.0", "2.0.2")],
            T310: [VersionRange("1.1.0", "1.5.2")],
        }
    }


def test_compat_registry_register_exist_ok_false_same_layer() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.1.0", "1.5.2")], layer="base")
    with pytest.raises(
        RuntimeError, match=r"A package configuration .* is already registered for package"
    ):
        registry.register(
            "my_package", T311, ranges=[VersionRange("1.2.0", "2.0.2")], layer="base"
        )


def test_compat_registry_register_override_never_conflicts_with_base() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.1.0", "1.5.2")], layer="base")
    # No exist_ok needed: override layer is independent of base layer.
    registry.register("my_package", T311, ranges=[VersionRange("9.0.0", None)])
    assert registry.overrides == {"my_package": {T311: [VersionRange("9.0.0", None)]}}
    assert registry.base == {"my_package": {T311: [VersionRange("1.1.0", "1.5.2")]}}


def test_compat_registry_register_exist_ok_true() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.1.0", "1.5.2")], layer="base")
    registry.register(
        "my_package",
        T311,
        ranges=[VersionRange("1.2.0", "2.0.2")],
        layer="base",
        exist_ok=True,
    )
    assert registry.base == {"my_package": {T311: [VersionRange("1.2.0", "2.0.2")]}}


def test_compat_registry_register_many() -> None:
    registry = CompatRegistry()
    registry.register_many(
        {
            "numpy": {T311: [VersionRange("1.23.2", "2.4.6")]},
            "torch": {T311: [VersionRange("2.0.0", None)]},
        },
        layer="base",
    )
    assert registry.base == {
        "numpy": {T311: [VersionRange("1.23.2", "2.4.6")]},
        "torch": {T311: [VersionRange("2.0.0", None)]},
    }


def test_compat_registry_register_many_exist_ok_false() -> None:
    registry = CompatRegistry()
    registry.register_many({"numpy": {T311: [VersionRange("1.0.0", None)]}}, layer="base")
    with pytest.raises(
        RuntimeError, match=r"A package configuration .* is already registered for package"
    ):
        registry.register_many({"numpy": {T311: [VersionRange("2.0.0", None)]}}, layer="base")


def test_compat_registry_register_many_exist_ok_true() -> None:
    registry = CompatRegistry()
    registry.register_many({"numpy": {T311: [VersionRange("1.0.0", None)]}}, layer="base")
    registry.register_many(
        {"numpy": {T311: [VersionRange("2.0.0", None)]}}, layer="base", exist_ok=True
    )
    assert registry.base == {"numpy": {T311: [VersionRange("2.0.0", None)]}}


def test_compat_registry_get_config_override_wins_over_base() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.0.0", None)], layer="base")
    registry.register("my_package", T311, ranges=[VersionRange("2.0.0", None)], layer="override")
    assert registry.get_config(pkg_name="my_package", target=T311) == [VersionRange("2.0.0", None)]


def test_compat_registry_get_config_falls_back_to_base() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.0.0", None)], layer="base")
    assert registry.get_config(pkg_name="my_package", target=T311) == [VersionRange("1.0.0", None)]


def test_compat_registry_get_config_empty_registry() -> None:
    registry = CompatRegistry()
    assert registry.get_config(pkg_name="my_package", target=T311) == []


def test_compat_registry_get_config_no_matching_target() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T310, ranges=[VersionRange("1.0.0", None)], layer="base")
    assert registry.get_config(pkg_name="my_package", target=T311) == []


#############################################
#     Tests for wildcard/specificity match   #
#############################################


def test_compat_registry_os_wildcard_matches_any_os() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.0.0", None)], layer="base")
    linux_target = Target(python_version="3.11", os="linux")
    assert registry.get_config(pkg_name="my_package", target=linux_target) == [
        VersionRange("1.0.0", None)
    ]


def test_compat_registry_more_specific_entry_wins() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.0.0", None)], layer="base")
    registry.register(
        "my_package",
        Target(python_version="3.11", os="macos", arch="arm64"),
        ranges=[VersionRange("5.0.0", None)],
        layer="base",
    )
    macos_arm = Target(python_version="3.11", os="macos", arch="arm64")
    linux = Target(python_version="3.11", os="linux")
    assert registry.get_config(pkg_name="my_package", target=macos_arm) == [
        VersionRange("5.0.0", None)
    ]
    assert registry.get_config(pkg_name="my_package", target=linux) == [VersionRange("1.0.0", None)]


def test_compat_registry_free_threaded_must_match_exactly() -> None:
    registry = CompatRegistry()
    registry.register(
        "my_package",
        Target(python_version="3.14", free_threaded=True),
        ranges=[VersionRange("1.0.0", None)],
        layer="base",
    )
    non_free_threaded = Target(python_version="3.14", free_threaded=False)
    assert registry.get_config(pkg_name="my_package", target=non_free_threaded) == []


def test_compat_registry_most_recent_wins_among_ties() -> None:
    registry = CompatRegistry()
    registry.register(
        "my_package",
        Target(python_version="3.11", os="linux"),
        ranges=[VersionRange("1.0.0", None)],
        layer="base",
    )
    registry.register(
        "my_package",
        Target(python_version="3.11", arch="x86_64"),
        ranges=[VersionRange("2.0.0", None)],
        layer="base",
    )
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    # Both entries match with equal specificity (one non-None field each);
    # the most recently registered one wins.
    assert registry.get_config(pkg_name="my_package", target=target) == [VersionRange("2.0.0", None)]


########################################
#     Tests for ranges/closest/valid   #
########################################


def test_compat_registry_get_version_ranges() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")], layer="base")
    assert registry.get_version_ranges(pkg_name="my_package", target=T311) == [
        (Version("1.2.0"), Version("2.2.0"))
    ]


def test_compat_registry_get_version_ranges_multiple() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange(None, "1.10.13"), VersionRange("2.0.0", None)],
        layer="base",
    )
    assert registry.get_version_ranges(pkg_name="pydantic", target=T311) == [
        (None, Version("1.10.13")),
        (Version("2.0.0"), None),
    ]


def test_compat_registry_get_version_ranges_empty() -> None:
    registry = CompatRegistry()
    assert registry.get_version_ranges(pkg_name="my_package", target=T311) == []


def test_compat_registry_find_closest_version_valid() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")], layer="base")
    assert (
        registry.find_closest_version(pkg_name="my_package", pkg_version="2.0.0", target=T311)
        == "2.0.0"
    )


def test_compat_registry_find_closest_version_missing() -> None:
    registry = CompatRegistry()
    assert (
        registry.find_closest_version(pkg_name="my_package", pkg_version="2.0.0", target=T311)
        == "2.0.0"
    )


def test_compat_registry_find_closest_version_lower() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")], layer="base")
    assert (
        registry.find_closest_version(pkg_name="my_package", pkg_version="1.0.0", target=T311)
        == "1.2.0"
    )


def test_compat_registry_find_closest_version_higher() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")], layer="base")
    assert (
        registry.find_closest_version(pkg_name="my_package", pkg_version="3.0.0", target=T311)
        == "2.2.0"
    )


def test_compat_registry_find_closest_version_in_first_range() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange("1.0.0", "1.10.13"), VersionRange("2.0.0", None)],
        layer="base",
    )
    assert (
        registry.find_closest_version(pkg_name="pydantic", pkg_version="1.5.0", target=T311)
        == "1.5.0"
    )


def test_compat_registry_find_closest_version_gap_snaps_up() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange("1.0.0", "1.10.13"), VersionRange("2.8.0", None)],
        layer="base",
    )
    # 2.0.0 falls between the two ranges: snap up to the next range's min.
    assert (
        registry.find_closest_version(pkg_name="pydantic", pkg_version="2.0.0", target=T311)
        == "2.8.0"
    )


def test_compat_registry_find_closest_version_below_all_ranges() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange("1.0.0", "1.10.13"), VersionRange("2.8.0", None)],
        layer="base",
    )
    assert (
        registry.find_closest_version(pkg_name="pydantic", pkg_version="0.5.0", target=T311)
        == "1.0.0"
    )


def test_compat_registry_find_closest_version_above_all_ranges() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange("1.0.0", "1.10.13"), VersionRange("2.0.0", "2.5.0")],
        layer="base",
    )
    assert (
        registry.find_closest_version(pkg_name="pydantic", pkg_version="9.0.0", target=T311)
        == "2.5.0"
    )


def test_compat_registry_is_valid_version_true() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")], layer="base")
    assert registry.is_valid_version(pkg_name="my_package", pkg_version="2.0.0", target=T311)


def test_compat_registry_is_valid_version_false_min() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")], layer="base")
    assert not registry.is_valid_version(pkg_name="my_package", pkg_version="1.0.0", target=T311)


def test_compat_registry_is_valid_version_false_max() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")], layer="base")
    assert not registry.is_valid_version(pkg_name="my_package", pkg_version="3.0.0", target=T311)


def test_compat_registry_is_valid_version_empty() -> None:
    registry = CompatRegistry()
    assert registry.is_valid_version(pkg_name="my_package", pkg_version="2.0.0", target=T311)


def test_compat_registry_is_valid_version_second_range() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange("1.0.0", "1.10.13"), VersionRange("2.8.0", None)],
        layer="base",
    )
    assert registry.is_valid_version(pkg_name="pydantic", pkg_version="3.0.0", target=T311)


def test_compat_registry_is_valid_version_in_gap_false() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange("1.0.0", "1.10.13"), VersionRange("2.8.0", None)],
        layer="base",
    )
    assert not registry.is_valid_version(pkg_name="pydantic", pkg_version="2.0.0", target=T311)


###################################
#     Tests for unsupported       #
###################################


def test_compat_registry_is_unsupported_true() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, ranges=[], layer="base")
    assert registry.is_unsupported(pkg_name="my_package", target=T315)


def test_compat_registry_is_unsupported_false() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")], layer="base")
    assert not registry.is_unsupported(pkg_name="my_package", target=T311)


def test_compat_registry_is_unsupported_unconfigured() -> None:
    registry = CompatRegistry()
    assert not registry.is_unsupported(pkg_name="my_package", target=T311)


def test_compat_registry_get_version_ranges_unsupported_raises() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, ranges=[], layer="base")
    with pytest.raises(UnsupportedVersionError, match=r"No version of package my_package"):
        registry.get_version_ranges(pkg_name="my_package", target=T315)


def test_compat_registry_find_closest_version_unsupported_raises() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, ranges=[], layer="base")
    with pytest.raises(UnsupportedVersionError, match=r"No version of package my_package"):
        registry.find_closest_version(pkg_name="my_package", pkg_version="2.0.0", target=T315)


def test_compat_registry_is_valid_version_unsupported_false() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, ranges=[], layer="base")
    assert not registry.is_valid_version(pkg_name="my_package", pkg_version="2.0.0", target=T315)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/unit/compat/test_registry.py -v`
Expected: FAIL — `ImportError: cannot import name 'VersionRange'` (or similar), since `registry.py` hasn't changed yet.

- [ ] **Step 3: Rewrite `src/feu/compat/registry.py`**

Replace the entire file with:

```python
r"""Define the compatibility registry for package version resolution.

This module provides a registry system that manages and resolves valid
package version ranges per compatibility target, enabling lookup of the
closest valid version and validation of a given version.
"""

from __future__ import annotations

__all__ = ["CompatRegistry", "UnsupportedVersionError", "VersionRange"]

import copy
from typing import TYPE_CHECKING, Literal, NamedTuple

from packaging.version import Version

if TYPE_CHECKING:
    from feu.compat.target import Target

_Layer = Literal["base", "override"]


class VersionRange(NamedTuple):
    r"""Represent one contiguous range of valid package versions.

    Args:
        min: The minimum valid package version, or ``None`` for no
            minimum.
        max: The maximum valid package version, or ``None`` for no
            maximum.
    """

    min: str | None
    max: str | None


class UnsupportedVersionError(Exception):
    r"""Raised when no package version is compatible with a given
    target."""


class CompatRegistry:
    r"""Manage package version compatibility across different
    compatibility targets.

    The registry holds two independent layers per package:

    - ``base``: populated by ``register_defaults`` and discovered
      data. Entries here can be freely refreshed (e.g. by re-running
      discovery) without ever conflicting with user overrides.
    - ``overrides``: populated by user calls (``register_compat`` /
      ``register(layer="override")``, the default). Overrides always
      take precedence over ``base`` and are only conflict-checked
      against other overrides.

    Each layer maps package name to ``Target`` to a list of
    ``VersionRange``. A package version is valid for a target if it
    falls within any of the registered ranges; an empty list means no
    version is valid for that target. A lookup target matches a
    stored entry when ``python_version`` and ``free_threaded`` are
    equal, and the stored entry's ``os``/``arch`` are either ``None``
    (wildcard) or equal to the lookup target's ``os``/``arch``. Among
    all matching entries in a layer, the most specific one (most
    non-``None`` ``os``/``arch`` fields) wins; ties are broken by
    most-recently registered.

    Args:
        initial_state: Optional initial mapping of package
            constraints, seeding the ``base`` layer. If provided, the
            state is copied to prevent external mutations.

    Example:
        ```pycon
        >>> from feu.compat import CompatRegistry, Target
        >>> from feu.compat.registry import VersionRange
        >>> registry = CompatRegistry()
        >>> registry.register(
        ...     pkg_name="numpy",
        ...     target=Target(python_version="3.11"),
        ...     ranges=[VersionRange("1.23.2", "2.4.6")],
        ...     layer="base",
        ... )
        >>> registry.is_valid_version("numpy", "2.0.2", Target(python_version="3.11"))
        True

        ```
    """

    def __init__(
        self, initial_state: dict[str, dict[Target, list[VersionRange]]] | None = None
    ) -> None:
        self._base: dict[str, dict[Target, list[VersionRange]]] = copy.deepcopy(
            initial_state or {}
        )
        self._overrides: dict[str, dict[Target, list[VersionRange]]] = {}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(\n"
            f"  (base): {self._base}\n"
            f"  (overrides): {self._overrides}\n)"
        )

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def base(self) -> dict[str, dict[Target, list[VersionRange]]]:
        r"""The base layer (defaults/discovered data)."""
        return self._base

    @property
    def overrides(self) -> dict[str, dict[Target, list[VersionRange]]]:
        r"""The override layer (user-supplied corrections)."""
        return self._overrides

    def _layer_table(self, layer: _Layer) -> dict[str, dict[Target, list[VersionRange]]]:
        return self._base if layer == "base" else self._overrides

    def register(
        self,
        pkg_name: str,
        target: Target,
        *,
        ranges: list[VersionRange],
        exist_ok: bool = False,
        layer: _Layer = "override",
    ) -> None:
        r"""Register a package configuration for a compatibility target.

        Args:
            pkg_name: The package name to register (e.g., ``"numpy"``).
            target: The compatibility target.
            ranges: The list of valid version ranges for this target.
                An empty list means no version is valid.
            exist_ok: If ``False``, a ``RuntimeError`` is raised when a
                configuration already exists for this package and
                target **within the same layer**. Set to ``True`` to
                overwrite.
            layer: Which layer to write to, ``"base"`` or
                ``"override"``. Defaults to ``"override"``, matching
                the public ``register_compat`` behavior.

        Raises:
            RuntimeError: If a configuration already exists for the
                given package name and target in the same layer, and
                ``exist_ok`` is ``False``.
        """
        table = self._layer_table(layer)
        table[pkg_name] = table.get(pkg_name, {})

        if target in table[pkg_name] and not exist_ok:
            msg = (
                f"A package configuration ({table[pkg_name][target]}) is already "
                f"registered for package {pkg_name} and target {target} in the "
                f"'{layer}' layer. Please use `exist_ok=True` if you want to "
                f"overwrite the package config"
            )
            raise RuntimeError(msg)

        table[pkg_name][target] = list(ranges)

    def register_many(
        self,
        mapping: dict[str, dict[Target, list[VersionRange]]],
        exist_ok: bool = False,
        layer: _Layer = "override",
    ) -> None:
        r"""Register multiple package configurations at once.

        Args:
            mapping: Mapping of package name to ``Target`` to list of
                ``VersionRange``.
            exist_ok: Forwarded to ``register``.
            layer: Forwarded to ``register``.
        """
        for pkg_name, targets in mapping.items():
            for target, ranges in targets.items():
                self.register(
                    pkg_name=pkg_name,
                    target=target,
                    ranges=ranges,
                    exist_ok=exist_ok,
                    layer=layer,
                )

    @staticmethod
    def _matches(entry_target: Target, lookup: Target) -> bool:
        if entry_target.python_version != lookup.python_version:
            return False
        if entry_target.free_threaded != lookup.free_threaded:
            return False
        if entry_target.os is not None and entry_target.os != lookup.os:
            return False
        return not (entry_target.arch is not None and entry_target.arch != lookup.arch)

    @staticmethod
    def _specificity(entry_target: Target) -> int:
        return (entry_target.os is not None) + (entry_target.arch is not None)

    def _resolve_in_layer(
        self, table: dict[str, dict[Target, list[VersionRange]]], pkg_name: str, target: Target
    ) -> list[VersionRange] | None:
        if pkg_name not in table:
            return None
        best: list[VersionRange] | None = None
        best_specificity = -1
        for entry_target, ranges in table[pkg_name].items():
            if not self._matches(entry_target, target):
                continue
            specificity = self._specificity(entry_target)
            if specificity >= best_specificity:
                best_specificity = specificity
                best = ranges
        return best

    def get_config(self, pkg_name: str, target: Target) -> list[VersionRange]:
        r"""Get the list of valid version ranges for a package and
        compatibility target.

        Checks the override layer first, then falls back to the base
        layer.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            target: The compatibility target.

        Returns:
            The list of ``VersionRange`` for this target, or an empty
            list if no configuration matches.
        """
        ranges = self._resolve_in_layer(self._overrides, pkg_name, target)
        if ranges is not None:
            return ranges
        return self._resolve_in_layer(self._base, pkg_name, target) or []

    def is_unsupported(self, pkg_name: str, target: Target) -> bool:
        r"""Indicate if no package version is valid for a target.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            target: The compatibility target.

        Returns:
            ``True`` if the package has no valid version for the
            given target, ``False`` otherwise.
        """
        return not self.get_config(pkg_name=pkg_name, target=target)

    def get_version_ranges(
        self, pkg_name: str, target: Target
    ) -> list[tuple[Version | None, Version | None]]:
        r"""Get the valid version ranges as ``Version`` objects.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            target: The compatibility target.

        Returns:
            A list of ``(min_version, max_version)`` tuples, either
            value being ``None`` if unconstrained on that side.

        Raises:
            UnsupportedVersionError: If no package version is valid
                for the given target.
        """
        ranges = self.get_config(pkg_name=pkg_name, target=target)
        if not ranges:
            msg = f"No version of package {pkg_name} is compatible with target {target}"
            raise UnsupportedVersionError(msg)
        return [
            (
                Version(version_range.min) if version_range.min is not None else None,
                Version(version_range.max) if version_range.max is not None else None,
            )
            for version_range in ranges
        ]

    def find_closest_version(self, pkg_name: str, pkg_version: str, target: Target) -> str:
        r"""Find the closest valid version for a package.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The requested package version.
            target: The compatibility target.

        Returns:
            The closest valid version as a string.

        Raises:
            UnsupportedVersionError: If no package version is valid
                for the given target.
        """
        version = Version(pkg_version)
        ranges = self.get_version_ranges(pkg_name=pkg_name, target=target)

        for min_version, max_version in ranges:
            if (min_version is None or min_version <= version) and (
                max_version is None or version <= max_version
            ):
                return pkg_version

        if ranges[0][0] is not None and version < ranges[0][0]:
            return ranges[0][0].base_version
        if ranges[-1][1] is not None and version > ranges[-1][1]:
            return ranges[-1][1].base_version

        # In a gap between two ranges: snap up to the next range's min.
        for min_version, _ in ranges:
            if min_version is not None and version < min_version:
                return min_version.base_version
        return pkg_version

    def is_valid_version(self, pkg_name: str, pkg_version: str, target: Target) -> bool:
        r"""Check if a package version is valid for a target.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The package version to validate.
            target: The compatibility target.

        Returns:
            ``True`` if valid for any registered range or
            unconfigured, ``False`` otherwise, including when no
            package version is valid for the given target.
        """
        if self.is_unsupported(pkg_name=pkg_name, target=target):
            return False
        version = Version(pkg_version)
        ranges = self.get_version_ranges(pkg_name=pkg_name, target=target)
        return any(
            (min_version is None or min_version <= version)
            and (max_version is None or version <= max_version)
            for min_version, max_version in ranges
        )
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/unit/compat/test_registry.py -v`
Expected: PASS (all tests green).

- [ ] **Step 5: Commit**

```bash
git add src/feu/compat/registry.py tests/unit/compat/test_registry.py
git commit -m "feat(compat): support multiple disjoint version ranges in CompatRegistry"
```

---

### Task 2: Update `defaults.py` to the `VersionRange` shape, with a real disjoint pydantic entry

**Files:**
- Modify: `src/feu/compat/defaults.py` (entire file)
- Modify: `tests/unit/compat/test_defaults.py`

**Interfaces:**
- Consumes: `feu.compat.registry.VersionRange`, `CompatRegistry.register_many` from Task 1.
- Produces: `DEFAULT_COMPAT: dict[str, dict[str, list[VersionRange]]]`, `register_defaults(registry: CompatRegistry) -> None` (signature unchanged).

- [ ] **Step 1: Write the failing test for the updated defaults shape**

In `tests/unit/compat/test_defaults.py`, replace the whole file with:

```python
from __future__ import annotations

from feu.compat.defaults import DEFAULT_COMPAT, register_defaults
from feu.compat.registry import CompatRegistry, VersionRange
from feu.compat.target import Target

#############################################
#     Tests for register_defaults           #
#############################################


def test_register_defaults_populates_base_layer() -> None:
    registry = CompatRegistry()
    register_defaults(registry)
    assert registry.overrides == {}
    assert registry.base["numpy"][Target(python_version="3.11")] == [
        VersionRange("1.23.2", "2.4.6")
    ]


def test_register_defaults_numpy_entry() -> None:
    registry = CompatRegistry()
    register_defaults(registry)
    assert registry.get_config(pkg_name="numpy", target=Target(python_version="3.11")) == [
        VersionRange("1.23.2", "2.4.6")
    ]


def test_register_defaults_pydantic_has_disjoint_ranges_on_python_3_11() -> None:
    registry = CompatRegistry()
    register_defaults(registry)
    ranges = registry.get_config(pkg_name="pydantic", target=Target(python_version="3.11"))
    assert len(ranges) == 2
    assert ranges[0] == VersionRange(None, "1.10.13")
    assert ranges[1].min == "2.0.0"


def test_default_compat_contains_expected_packages() -> None:
    assert set(DEFAULT_COMPAT.keys()) == {
        "click",
        "duckdb",
        "jax",
        "matplotlib",
        "numpy",
        "pandas",
        "pyarrow",
        "pydantic",
        "requests",
        "scikit-learn",
        "scipy",
        "torch",
        "xarray",
    }


def test_default_compat_values_are_version_ranges() -> None:
    for pkg_versions in DEFAULT_COMPAT.values():
        for ranges in pkg_versions.values():
            assert isinstance(ranges, list)
            assert all(isinstance(r, VersionRange) for r in ranges)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/unit/compat/test_defaults.py -v`
Expected: FAIL — `defaults.py` still uses the old dict shape.

- [ ] **Step 3: Rewrite `src/feu/compat/defaults.py`**

Replace the entire file with:

```python
r"""Contain the default package version compatibility constraints."""

from __future__ import annotations

__all__ = ["DEFAULT_COMPAT", "register_defaults"]

from typing import TYPE_CHECKING

from feu.compat.registry import VersionRange
from feu.compat.target import Target

if TYPE_CHECKING:
    from feu.compat.registry import CompatRegistry

DEFAULT_COMPAT: dict[str, dict[str, list[VersionRange]]] = {
    # https://click.palletsprojects.com/en/stable/changes/
    "click": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange(None, None)],
        "3.13": [VersionRange(None, None)],
        "3.12": [VersionRange(None, None)],
        "3.11": [VersionRange(None, None)],
        "3.10": [VersionRange(None, None)],
        "3.9": [VersionRange(None, "8.1.8")],
    },
    # https://github.com/duckdb/duckdb-python/releases
    "duckdb": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("1.4.2", None)],
        "3.13": [VersionRange(None, None)],
        "3.12": [VersionRange(None, None)],
        "3.11": [VersionRange(None, None)],
        "3.10": [VersionRange(None, None)],
    },
    # https://pypi.org/project/jaxlib/#history
    "jax": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("0.7.1", None)],
        "3.13": [VersionRange("0.4.34", None)],
        "3.12": [VersionRange("0.4.17", None)],
        "3.11": [VersionRange("0.4.6", None)],
        "3.10": [VersionRange("0.4.6", "0.6.2")],
        "3.9": [VersionRange("0.4.6", "0.4.30")],
    },
    # https://matplotlib.org/stable/users/release_notes.html
    "matplotlib": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("3.10.5", None)],
        "3.13": [VersionRange(None, None)],
        "3.12": [VersionRange(None, None)],
        "3.11": [VersionRange(None, None)],
        "3.10": [VersionRange(None, None)],
        "3.9": [VersionRange(None, "3.9.4")],
    },
    # https://numpy.org/devdocs/release.html
    "numpy": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("2.3.0", None)],
        "3.13": [VersionRange("2.1.0", None)],
        "3.12": [VersionRange("1.26.0", None)],
        "3.11": [VersionRange("1.23.2", "2.4.6")],
        "3.10": [VersionRange("1.21.3", "2.2.6")],
        "3.9": [VersionRange("1.19.3", "2.0.2")],
    },
    # https://github.com/pandas-dev/pandas/releases
    # https://pandas.pydata.org/docs/whatsnew/index.html
    "pandas": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("2.3.3", None)],
        "3.13": [VersionRange("2.2.3", None)],
        "3.12": [VersionRange("2.1.1", None)],
        "3.11": [VersionRange("1.3.4", None)],
        "3.10": [VersionRange("1.3.3", "2.3.3")],
        "3.9": [VersionRange(None, "2.3.3")],
    },
    # https://arrow.apache.org/release/
    "pyarrow": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("22.0.0", None)],
        "3.13": [VersionRange("18.0.0", None)],
        "3.12": [VersionRange("14.0.0", None)],
        "3.11": [VersionRange("10.0.1", None)],
        "3.10": [VersionRange("6.0.0", None)],
        "3.9": [VersionRange("3.0.0", "16.1.0")],
    },
    # pydantic 1.x (last release 1.10.13) and pydantic 2.x are both valid
    # on Python versions where 1.x still ships wheels (3.9-3.11); pydantic
    # 2.8.0 is the first release with Python 3.13 support
    # (https://github.com/pydantic/pydantic/issues/11524), and 1.x never
    # shipped wheels for 3.12/3.13, so those Python versions only have a
    # single valid range.
    "pydantic": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("2.12.0", None)],
        "3.13": [VersionRange("2.8.0", None)],
        "3.12": [VersionRange("2.0.0", None)],
        "3.11": [VersionRange(None, "1.10.13"), VersionRange("2.0.0", None)],
        "3.10": [VersionRange(None, "1.10.13"), VersionRange("2.0.0", None)],
        "3.9": [VersionRange(None, "1.10.13"), VersionRange("2.0.0", None)],
    },
    "requests": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange(None, None)],
        "3.13": [VersionRange(None, None)],
        "3.12": [VersionRange(None, None)],
        "3.11": [VersionRange(None, None)],
        "3.10": [VersionRange(None, None)],
        "3.9": [VersionRange(None, None)],
    },
    # https://github.com/scikit-learn/scikit-learn/releases
    "scikit-learn": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("1.7.2", None)],
        "3.13": [VersionRange("1.6.0", None)],
        "3.12": [VersionRange("1.3.1", None)],
        "3.11": [VersionRange("1.2.0", None)],
        "3.10": [VersionRange("1.1.0", "1.7.2")],
        "3.9": [VersionRange(None, "1.6.1")],
    },
    # https://github.com/scipy/scipy/releases/
    "scipy": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("1.16.1", None)],
        "3.13": [VersionRange("1.14.1", None)],
        "3.12": [VersionRange("1.12.0", None)],
        "3.11": [VersionRange("1.10.0", "1.17.1")],
        "3.10": [VersionRange("1.8.0", "1.15.3")],
        "3.9": [VersionRange(None, "1.13.1")],
    },
    # https://github.com/pytorch/pytorch/releases
    "torch": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange("2.9.0", None)],
        "3.13": [VersionRange("2.6.0", None)],
        "3.12": [VersionRange("2.4.0", None)],
        "3.11": [VersionRange("2.0.0", None)],
        "3.10": [VersionRange("1.11.0", None)],
        "3.9": [VersionRange(None, "2.8.0")],
    },
    # https://docs.xarray.dev/en/stable/whats-new.html
    "xarray": {
        "3.15": [VersionRange(None, None)],
        "3.14": [VersionRange(None, None)],
        "3.13": [VersionRange(None, None)],
        "3.12": [VersionRange(None, None)],
        "3.11": [VersionRange(None, None)],
        "3.10": [VersionRange(None, "2025.6.1")],
        "3.9": [VersionRange(None, "2024.7.0")],
    },
}


def register_defaults(registry: CompatRegistry) -> None:
    r"""Populate a registry's base layer with the default package
    compatibility constraints.

    Args:
        registry: The registry to populate.
    """
    mapping: dict[str, dict[Target, list[VersionRange]]] = {
        pkg_name: {
            Target(python_version=python_version): ranges
            for python_version, ranges in versions.items()
        }
        for pkg_name, versions in DEFAULT_COMPAT.items()
    }
    registry.register_many(mapping, layer="base")
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/unit/compat/test_defaults.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/feu/compat/defaults.py tests/unit/compat/test_defaults.py
git commit -m "feat(compat): switch DEFAULT_COMPAT to VersionRange lists, add disjoint pydantic ranges"
```

---

### Task 3: Update `discovery.py` to produce `VersionRange` lists

**Files:**
- Modify: `src/feu/compat/discovery.py`
- Modify: `tests/unit/compat/test_discovery.py`
- Modify: `tests/integration/compat/test_discovery.py`

**Interfaces:**
- Consumes: `feu.compat.registry.VersionRange` from Task 1.
- Produces: `discover_compat(pkg_name: str, python_versions: Sequence[str] = DEFAULT_PYTHON_VERSIONS) -> dict[str, list[VersionRange]]`
- Produces: `discover_compat_targets(pkg_name: str, targets: Sequence[Target] = DEFAULT_TARGETS) -> dict[Target, list[VersionRange]]`
- Removed: import of `UNSUPPORTED` (no longer exists); unsupported is now represented by `[]`.

- [ ] **Step 1: Write the failing tests**

Replace `tests/unit/compat/test_discovery.py` with:

```python
from __future__ import annotations

from unittest.mock import patch

from feu.compat.discovery import (
    DEFAULT_PYTHON_VERSIONS,
    DEFAULT_TARGETS,
    discover_compat,
    discover_compat_targets,
)
from feu.compat.registry import VersionRange
from feu.compat.target import Target


@patch(
    "feu.compat.discovery.fetch_pypi_requires_python",
    lambda *_args: {
        "1.0.0": ">=3.6",
        "1.5.0": ">=3.8",
        "2.0.0": ">=3.9",
        "2.1.0": ">=3.9",
        "2.1.0a1": ">=3.9",  # pre-release, should be ignored
        "not-a-version": ">=3.9",  # invalid, should be ignored
    },
)
def test_discover_compat() -> None:
    compat = discover_compat("my_package", python_versions=("3.8", "3.9", "3.10"))
    assert compat == {
        "3.8": [VersionRange("1.0.0", "1.5.0")],
        "3.9": [VersionRange("1.0.0", None)],
        "3.10": [VersionRange("1.0.0", None)],
    }


@patch(
    "feu.compat.discovery.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": ">=3.9", "2.0.0": ">=3.9"},
)
def test_discover_compat_no_compatible_version() -> None:
    compat = discover_compat("my_package", python_versions=("3.7",))
    assert compat == {"3.7": []}


@patch(
    "feu.compat.discovery.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": None, "2.0.0": None},
)
def test_discover_compat_no_requires_python() -> None:
    compat = discover_compat("my_package", python_versions=("3.9",))
    assert compat == {"3.9": [VersionRange("1.0.0", None)]}


@patch(
    "feu.compat.discovery.fetch_pypi_requires_python",
    lambda *_args: {"1.0.0": "invalid specifier!!", "2.0.0": ">=3.9"},
)
def test_discover_compat_invalid_specifier() -> None:
    compat = discover_compat("my_package", python_versions=("3.5",))
    assert compat == {"3.5": [VersionRange("1.0.0", "1.0.0")]}


@patch("feu.compat.discovery.fetch_pypi_requires_python", lambda *_args: {})
def test_discover_compat_empty() -> None:
    compat = discover_compat("my_package", python_versions=("3.9",))
    assert compat == {"3.9": []}


def test_discover_compat_default_python_versions() -> None:
    with patch(
        "feu.compat.discovery.fetch_pypi_requires_python",
        lambda *_args: {"1.0.0": None},
    ):
        compat = discover_compat("my_package")
    assert set(compat.keys()) == {"3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15"}


##############################################
#     Tests for DEFAULT_TARGETS              #
##############################################


def test_default_targets_shape() -> None:
    assert len(DEFAULT_TARGETS) == len(DEFAULT_PYTHON_VERSIONS) * 2 * 3 * 2
    assert all(isinstance(target, Target) for target in DEFAULT_TARGETS)
    assert all(target.os is not None and target.arch is not None for target in DEFAULT_TARGETS)


##############################################
#     Tests for discover_compat_targets      #
##############################################


@patch(
    "feu.compat.discovery.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "1.1.0": (
            "pkg-1.1.0-cp311-cp311-manylinux_2_17_x86_64.whl",
            "pkg-1.1.0-cp314-cp314t-manylinux_2_17_x86_64.whl",
        ),
        "1.1.0a1": ("pkg-1.1.0a1-cp311-cp311-manylinux_2_17_x86_64.whl",),  # pre-release, ignored
        "not-a-version": ("pkg-bad.whl",),  # invalid, ignored
    },
)
def test_discover_compat_targets_basic() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("1.0.0", None)]}


@patch(
    "feu.compat.discovery.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "1.1.0": (
            "pkg-1.1.0-cp311-cp311-manylinux_2_17_x86_64.whl",
            "pkg-1.1.0-cp314-cp314t-manylinux_2_17_x86_64.whl",
        ),
    },
)
def test_discover_compat_targets_free_threaded() -> None:
    free_threaded_314 = Target(python_version="3.14", free_threaded=True, os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(free_threaded_314,))
    assert compat == {free_threaded_314: [VersionRange("1.1.0", None)]}


@patch(
    "feu.compat.discovery.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "2.0.0": ("pkg-2.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
    },
)
def test_discover_compat_targets_max_is_last_compatible() -> None:
    macos_arm = Target(python_version="3.11", os="macos", arch="arm64")
    compat = discover_compat_targets("pkg", targets=(macos_arm,))
    assert compat == {macos_arm: []}


@patch(
    "feu.compat.discovery.fetch_pypi_wheel_filenames",
    lambda *_args: {
        "1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        "1.5.0": ("pkg-1.5.0-cp39-cp39-manylinux_2_17_x86_64.whl",),
        "2.0.0": ("pkg-2.0.0-cp39-cp39-manylinux_2_17_x86_64.whl",),
    },
)
def test_discover_compat_targets_upper_bound() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("1.0.0", "1.0.0")]}


@patch("feu.compat.discovery.fetch_pypi_wheel_filenames", lambda *_args: {})
def test_discover_compat_targets_empty() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(linux_311,))
    assert compat == {linux_311: []}


@patch(
    "feu.compat.discovery.fetch_pypi_wheel_filenames",
    lambda *_args: {"1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",)},
)
def test_discover_compat_targets_multiple_targets() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    macos_311 = Target(python_version="3.11", os="macos", arch="arm64")
    compat = discover_compat_targets("pkg", targets=(linux_311, macos_311))
    assert compat == {
        linux_311: [VersionRange("1.0.0", None)],
        macos_311: [],
    }
```

Also update `tests/integration/compat/test_discovery.py`:
- Replace `from feu.compat.registry import UNSUPPORTED` with `from feu.compat.registry import VersionRange`.
- Replace the `_assert_valid_compat` helper and its usages:

```python
def _assert_valid_compat(compat: dict[str, list[VersionRange]]) -> None:
    for ranges in compat.values():
        for version_range in ranges:
            if version_range.min is not None and version_range.max is not None:
                assert Version(version_range.min) <= Version(version_range.max)
```

- In `test_discover_compat_requests`, `test_discover_compat_torch`, `test_discover_compat_default_python_versions`: replace `config["min"]`/`config["max"]` accesses with `compat[python_version][0].min`/`compat[python_version][0].max` (each of these packages only ever has one range per Python version, since the mocked/live data doesn't create a gap):

```python
@requests_available
def test_discover_compat_requests() -> None:
    compat = discover_compat("requests", python_versions=("3.9", "3.10", "3.11"))
    assert set(compat) == {"3.9", "3.10", "3.11"}
    _assert_valid_compat(compat)
    for ranges in compat.values():
        assert ranges[0].min == "0.0.1"
    assert compat["3.9"][0].max is not None
    assert Version(compat["3.9"][0].max) >= Version("2.32.5")
    assert compat["3.10"][0].max is None
    assert compat["3.11"][0].max is None


@requests_available
def test_discover_compat_torch() -> None:
    compat = discover_compat("torch", python_versions=("3.9", "3.10", "3.11"))
    assert set(compat) == {"3.9", "3.10", "3.11"}
    _assert_valid_compat(compat)
    for ranges in compat.values():
        assert ranges[0].min == "1.0.0"
    assert compat["3.9"][0].max is not None
    assert Version(compat["3.9"][0].max) >= Version("2.8.0")
    assert compat["3.10"][0].max is None
    assert compat["3.11"][0].max is None


@requests_available
def test_discover_compat_default_python_versions() -> None:
    compat = discover_compat("requests")
    assert set(compat) == set(DEFAULT_PYTHON_VERSIONS)
    _assert_valid_compat(compat)
    for ranges in compat.values():
        assert ranges[0].min == "0.0.1"
    assert compat["3.9"][0].max is not None
    assert Version(compat["3.9"][0].max) >= Version("2.32.5")
    for python_version in ("3.10", "3.11", "3.12", "3.13", "3.14", "3.15"):
        assert compat[python_version][0].max is None
```

And `test_discover_compat_targets_numpy_linux_free_threaded`:

```python
@requests_available
def test_discover_compat_targets_numpy_linux_free_threaded() -> None:
    target = Target(python_version="3.14", free_threaded=True, os="linux", arch="x86_64")
    compat = discover_compat_targets("numpy", targets=(target,))
    assert set(compat) == {target}
    ranges = compat[target]
    assert len(ranges) == 1
    assert ranges[0].min is not None
    assert Version(ranges[0].min)
    if ranges[0].max is not None:
        assert Version(ranges[0].max)
```

- [ ] **Step 2: Run the unit tests to verify they fail**

Run: `pytest tests/unit/compat/test_discovery.py -v`
Expected: FAIL — `discovery.py` still imports `UNSUPPORTED` and returns dict-shaped configs.

- [ ] **Step 3: Update `src/feu/compat/discovery.py`**

Apply these changes:

1. Replace the import line:
```python
from feu.compat.registry import UNSUPPORTED
```
with:
```python
from feu.compat.registry import VersionRange
```

2. Replace the body of `discover_compat` (from the `result: dict[str, dict[str, str | None]] = {}` line onward) and its return type annotation:

```python
def discover_compat(
    pkg_name: str, python_versions: Sequence[str] = DEFAULT_PYTHON_VERSIONS
) -> dict[str, list[VersionRange]]:
    r"""Discover the version range compatible with each Python version,
    using the ``requires_python`` metadata published on PyPI.

    For each Python version, the earliest stable package release
    compatible with it becomes the range's ``min``, and the latest
    compatible release becomes its ``max``, or ``None`` if the newest
    stable release overall is still compatible (i.e. no upper bound
    has been hit yet). If no stable release is compatible with a
    given Python version, the range list is empty.

    Args:
        pkg_name: The package name to inspect (e.g., ``"numpy"``).
        python_versions: The Python versions to compute constraints
            for. Defaults to ``DEFAULT_PYTHON_VERSIONS``.

    Returns:
        A mapping of Python version to a list of ``VersionRange``, in
            the same shape expected by ``CompatRegistry.register_many``.

    Example:
        ```pycon
        >>> from feu.compat import discover_compat
        >>> compat = discover_compat("requests")  # doctest: +SKIP

        ```
    """
    requires_python = fetch_pypi_requires_python(pkg_name)
    versions = filter_stable_versions(filter_valid_versions(requires_python.keys()))
    versions = sorted(versions, key=Version)
    latest = versions[-1] if versions else None

    result: dict[str, list[VersionRange]] = {}
    for python_version in python_versions:
        compatible = [
            version
            for version in versions
            if _is_compatible(requires_python[version], python_version)
        ]
        if not compatible:
            result[python_version] = []
            continue
        result[python_version] = [
            VersionRange(compatible[0], None if compatible[-1] == latest else compatible[-1])
        ]
    return result
```

3. Replace the body of `discover_compat_targets` (from the `result: dict[Target, dict[str, str | None]] = {}` line onward) and its return type annotation:

```python
def discover_compat_targets(
    pkg_name: str, targets: Sequence[Target] = DEFAULT_TARGETS
) -> dict[Target, list[VersionRange]]:
    r"""Discover the version range compatible with each target, using
    actual wheel filenames published on PyPI.

    Unlike ``discover_compat``, which only inspects the
    ``requires_python`` metadata, this function parses each release's
    wheel filenames to determine whether it shipped a build matching
    a target's free-threaded/OS/arch axes, not just its Python
    version.

    Args:
        pkg_name: The package name to inspect (e.g., ``"numpy"``).
        targets: The compatibility targets to compute constraints for.
            Each target must have concrete (non-``None``) ``os`` and
            ``arch``. Defaults to ``DEFAULT_TARGETS``.

    Returns:
        A mapping of ``Target`` to a list of ``VersionRange``, in the
            same shape expected by ``CompatRegistry.register_many``.

    Example:
        ```pycon
        >>> from feu.compat.discovery import discover_compat_targets
        >>> compat = discover_compat_targets("numpy")  # doctest: +SKIP

        ```
    """
    wheel_filenames = fetch_pypi_wheel_filenames(pkg_name)
    versions = filter_stable_versions(filter_valid_versions(wheel_filenames.keys()))
    versions = sorted(versions, key=Version)
    latest = versions[-1] if versions else None

    tags_by_version: dict[str, set[WheelTags]] = {
        version: {
            tags
            for filename in wheel_filenames[version]
            if (tags := parse_wheel_filename(filename)) is not None
        }
        for version in versions
    }

    result: dict[Target, list[VersionRange]] = {}
    for target in targets:
        wanted = WheelTags(
            python_version=target.python_version,
            free_threaded=target.free_threaded,
            os=target.os,
            arch=target.arch,
        )
        compatible = [version for version in versions if wanted in tags_by_version[version]]
        if not compatible:
            result[target] = []
            continue
        result[target] = [
            VersionRange(compatible[0], None if compatible[-1] == latest else compatible[-1])
        ]
    return result
```

- [ ] **Step 4: Run all discovery tests to verify they pass**

Run: `pytest tests/unit/compat/test_discovery.py tests/integration/compat/test_discovery.py -v`
Expected: PASS (integration tests hit real PyPI — run them; if the environment has no network access, at minimum confirm the unit tests pass and note that integration tests need to be run separately with network access).

- [ ] **Step 5: Commit**

```bash
git add src/feu/compat/discovery.py tests/unit/compat/test_discovery.py tests/integration/compat/test_discovery.py
git commit -m "feat(compat): return VersionRange lists from discover_compat/discover_compat_targets"
```

---

### Task 4: Update `interface.py` and `__init__.py` exports

**Files:**
- Modify: `src/feu/compat/interface.py`
- Modify: `src/feu/compat/__init__.py`
- Modify: `tests/unit/compat/test_interface.py`

**Interfaces:**
- Consumes: `feu.compat.registry.VersionRange`, updated `CompatRegistry` from Task 1.
- Produces: `register_compat(mapping: dict[str, dict[Target, list[VersionRange]]], exist_ok: bool = False) -> None` (signature updated); `get_default_registry`, `find_closest_version`, `is_valid_version` unchanged in signature (they already pass through pkg_version/target, only the underlying data shape changed).
- `feu/compat/__init__.py` no longer exports `UNSUPPORTED`; exports `VersionRange` instead.

- [ ] **Step 1: Write the failing tests**

Replace `tests/unit/compat/test_interface.py` with:

```python
from __future__ import annotations

from unittest.mock import patch

import pytest

from feu.compat.interface import (
    find_closest_version,
    get_default_registry,
    is_valid_version,
    register_compat,
)
from feu.compat.registry import CompatRegistry, VersionRange
from feu.compat.target import Target

T311 = Target(python_version="3.11")


######################################
#     Tests for get_default_registry #
######################################


@pytest.fixture(autouse=True)
def _reset_default_registry() -> None:
    if hasattr(get_default_registry, "_registry"):
        del get_default_registry._registry
    yield
    if hasattr(get_default_registry, "_registry"):
        del get_default_registry._registry


def test_get_default_registry_returns_compat_registry() -> None:
    registry = get_default_registry()
    assert isinstance(registry, CompatRegistry)


def test_get_default_registry_is_singleton() -> None:
    registry1 = get_default_registry()
    registry2 = get_default_registry()
    assert registry1 is registry2


def test_get_default_registry_populated_with_defaults() -> None:
    registry = get_default_registry()
    assert registry.get_config(pkg_name="numpy", target=T311) == [VersionRange("1.23.2", "2.4.6")]


#################################
#     Tests for register_compat #
#################################


def test_register_compat_adds_to_override_layer() -> None:
    register_compat({"my_package": {T311: [VersionRange("1.0.0", None)]}})
    registry = get_default_registry()
    assert registry.get_config(pkg_name="my_package", target=T311) == [VersionRange("1.0.0", None)]
    assert registry.overrides == {"my_package": {T311: [VersionRange("1.0.0", None)]}}


def test_register_compat_exist_ok_false_raises() -> None:
    register_compat({"my_package": {T311: [VersionRange("1.0.0", None)]}})
    with pytest.raises(RuntimeError, match=r"A package configuration .* is already registered"):
        register_compat({"my_package": {T311: [VersionRange("2.0.0", None)]}})


def test_register_compat_overrides_a_default_without_exist_ok() -> None:
    # numpy has a base entry for 3.11; overriding it must not require exist_ok=True.
    register_compat({"numpy": {T311: [VersionRange("9.9.9", None)]}})
    assert get_default_registry().get_config(pkg_name="numpy", target=T311) == [
        VersionRange("9.9.9", None)
    ]


########################################
#     Tests for find_closest_version   #
########################################


def test_find_closest_version_delegates_to_default_registry() -> None:
    with patch.object(CompatRegistry, "find_closest_version", return_value="1.2.3") as mock_find:
        result = find_closest_version(pkg_name="numpy", pkg_version="2.0.2", target=T311)
    assert result == "1.2.3"
    mock_find.assert_called_once_with(pkg_name="numpy", pkg_version="2.0.2", target=T311)


def test_find_closest_version_uses_defaults() -> None:
    assert find_closest_version(pkg_name="numpy", pkg_version="0.1.0", target=T311) == "1.23.2"


##################################
#     Tests for is_valid_version #
##################################


def test_is_valid_version_delegates_to_default_registry() -> None:
    with patch.object(CompatRegistry, "is_valid_version", return_value=False) as mock_valid:
        result = is_valid_version(pkg_name="numpy", pkg_version="2.0.2", target=T311)
    assert result is False
    mock_valid.assert_called_once_with(pkg_name="numpy", pkg_version="2.0.2", target=T311)


def test_is_valid_version_uses_defaults() -> None:
    assert not is_valid_version(pkg_name="numpy", pkg_version="0.1.0", target=T311)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/unit/compat/test_interface.py -v`
Expected: FAIL — `register_compat`'s docstring example and type hints still reference the old dict shape (functionally `register_many` already accepts whatever is passed through, so failures will mainly show as `AttributeError`/`TypeError` from `VersionRange` not being unpacked correctly if `interface.py` doesn't import it — confirm by running before editing).

- [ ] **Step 3: Update `src/feu/compat/interface.py`**

Change the `register_compat` signature and docstring (function body is unchanged — it already forwards `mapping` to `register_many` untouched):

```python
def register_compat(
    mapping: dict[str, dict[Target, list[VersionRange]]],
    exist_ok: bool = False,
) -> None:
    r"""Register custom package configurations into the default global
    registry's override layer.

    Override entries always take precedence over the default/base
    layer, and are only conflict-checked against other overrides, so
    correcting an inaccurate default never requires ``exist_ok=True``.

    Args:
        mapping: Mapping of package name to ``Target`` to a list of
            ``VersionRange``.
        exist_ok: If ``False`` (default), raises an error if any entry
            is already registered as an override. If ``True``,
            overwrites existing override registrations silently.

    Raises:
        RuntimeError: If any entry is already registered as an
            override and ``exist_ok`` is ``False``.

    Example:
        ```pycon
        >>> from feu.compat import register_compat, Target, VersionRange
        >>> register_compat(
        ...     {"my_package": {Target(python_version="3.11"): [VersionRange("1.0.0", None)]}}
        ... )

        ```
    """
    get_default_registry().register_many(mapping, exist_ok=exist_ok)
```

Add `VersionRange` to the `TYPE_CHECKING` import block:

```python
if TYPE_CHECKING:
    from feu.compat.registry import VersionRange
    from feu.compat.target import Target
```

- [ ] **Step 4: Update `src/feu/compat/__init__.py`**

Replace the `UNSUPPORTED` export with `VersionRange`:

```python
r"""Contain a registry-based system for package/target compatibility
resolution."""

from __future__ import annotations

__all__ = [
    "CompatRegistry",
    "Target",
    "UnsupportedVersionError",
    "VersionRange",
    "WheelTags",
    "discover_compat",
    "discover_compat_targets",
    "find_closest_version",
    "get_default_registry",
    "is_valid_version",
    "parse_wheel_filename",
    "register_compat",
]

from feu.compat.discovery import discover_compat, discover_compat_targets
from feu.compat.interface import (
    find_closest_version,
    get_default_registry,
    is_valid_version,
    register_compat,
)
from feu.compat.registry import CompatRegistry, UnsupportedVersionError, VersionRange
from feu.compat.target import Target
from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `pytest tests/unit/compat/test_interface.py -v`
Expected: PASS.

- [ ] **Step 6: Run the full compat test suite and a project-wide grep for stragglers**

Run: `pytest tests/unit/compat tests/integration/compat -v`
Expected: PASS.

Run: `grep -rn "UNSUPPORTED\|pkg_version_min\|pkg_version_max\|get_min_and_max_versions" src tests`
Expected: no results (confirms no leftover references to the removed API).

- [ ] **Step 7: Commit**

```bash
git add src/feu/compat/interface.py src/feu/compat/__init__.py tests/unit/compat/test_interface.py
git commit -m "feat(compat): update public interface and exports for VersionRange"
```

---

## Final Verification

- [ ] Run the full test suite: `pytest tests/unit tests/integration -v`
- [ ] Run any configured linter/type-checker for the project (check `pyproject.toml` / `Makefile` for the exact commands, e.g. `ruff check src tests`, `mypy src`) and fix any new violations introduced by this change.
