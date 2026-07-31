# Multi-axis Compat Target Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the `python_version: str` key in `feu.compat` with a
`Target(python_version, free_threaded, os, arch)` key, and split
`CompatRegistry` into a base layer (defaults/discovered data) and an
overrides layer (user corrections) that always wins and never
conflicts with the base layer.

**Architecture:** A new frozen `Target` dataclass becomes the registry
key. `CompatRegistry` stores two `dict[str, dict[Target, dict[str, str
| None]]]` tables (`_base`, `_overrides`). Lookups resolve against
`_overrides` first using wildcard/specificity matching (unset
`os`/`arch` on a stored entry matches any value; the most specific
matching entry wins), falling back to `_base`. `register()` /
`register_many()` take a `layer` parameter (`"base"` or `"override"`,
default `"override"`) so `register_defaults()` can seed `_base` while
the public `register_compat()` always writes to `_overrides`.

**Tech Stack:** Python 3.10+ (repo baseline), `packaging` for version
parsing, `pytest` for tests. No new dependencies.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-31-multiaxis-compat-target-design.md`
- `discover_compat` keeps returning `dict[str, dict[str, str | None]]`
  keyed by python-version string — it is NOT touched in this plan.
- `Target.free_threaded` defaults to `False`; `Target.os`/`Target.arch`
  default to `None` (wildcard).
- `os`/`arch` on a *lookup* target are matched against a stored
  entry's `os`/`arch` only when the stored entry specifies them
  (non-`None`); `python_version` and `free_threaded` must always match
  exactly.
- A user override (`register_compat` / `register()` with default
  `layer="override"`) must never conflict-check against `_base` —
  `exist_ok=False` only raises for a collision within the same layer.
- Every existing public symbol keeps working, just with `target:
  Target` replacing `python_version: str` in signatures.

---

### Task 1: `Target` dataclass

**Files:**
- Create: `src/feu/compat/target.py`
- Test: `tests/unit/compat/test_target.py`

**Interfaces:**
- Produces: `feu.compat.target.Target` — frozen dataclass with fields
  `python_version: str`, `free_threaded: bool = False`, `os: str |
  None = None`, `arch: str | None = None`. Hashable (usable as a dict
  key) because it's frozen and all fields are hashable.

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/compat/test_target.py
from __future__ import annotations

from feu.compat.target import Target


def test_target_defaults() -> None:
    target = Target(python_version="3.11")
    assert target.python_version == "3.11"
    assert target.free_threaded is False
    assert target.os is None
    assert target.arch is None


def test_target_all_fields() -> None:
    target = Target(python_version="3.14", free_threaded=True, os="macos", arch="arm64")
    assert target.python_version == "3.14"
    assert target.free_threaded is True
    assert target.os == "macos"
    assert target.arch == "arm64"


def test_target_equality() -> None:
    assert Target(python_version="3.11") == Target(python_version="3.11")
    assert Target(python_version="3.11") != Target(python_version="3.12")
    assert Target(python_version="3.11", os="linux") != Target(python_version="3.11")


def test_target_is_hashable() -> None:
    targets = {Target(python_version="3.11"), Target(python_version="3.11")}
    assert len(targets) == 1
    targets.add(Target(python_version="3.11", free_threaded=True))
    assert len(targets) == 2


def test_target_used_as_dict_key() -> None:
    mapping = {Target(python_version="3.11"): "value"}
    assert mapping[Target(python_version="3.11")] == "value"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/compat/test_target.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'feu.compat.target'`

- [ ] **Step 3: Implement `Target`**

```python
# src/feu/compat/target.py
r"""Define the compatibility target key used to look up package
version constraints."""

from __future__ import annotations

__all__ = ["Target"]

from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    r"""Identify the environment a package compatibility constraint
    applies to.

    Args:
        python_version: The Python version, e.g. ``"3.11"``.
        free_threaded: ``True`` for a free-threaded (no-GIL) Python
            build, e.g. ``3.14t``. Defaults to ``False``.
        os: The operating system, e.g. ``"linux"``, ``"macos"``,
            ``"windows"``. ``None`` means "any OS" when used as a
            registry entry, and "unspecified" when used as a lookup
            target.
        arch: The CPU architecture, e.g. ``"x86_64"``, ``"arm64"``.
            ``None`` means "any architecture" when used as a registry
            entry, and "unspecified" when used as a lookup target.

    Example:
        ```pycon
        >>> from feu.compat.target import Target
        >>> Target(python_version="3.14", free_threaded=True, os="linux", arch="x86_64")
        Target(python_version='3.14', free_threaded=True, os='linux', arch='x86_64')

        ```
    """

    python_version: str
    free_threaded: bool = False
    os: str | None = None
    arch: str | None = None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/compat/test_target.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add src/feu/compat/target.py tests/unit/compat/test_target.py
git commit -m "feat(compat): add Target dataclass for multi-axis compat keys"
```

---

### Task 2: Rewrite `CompatRegistry` with base/override layers and wildcard matching

**Files:**
- Modify: `src/feu/compat/registry.py` (full rewrite of `CompatRegistry`)
- Test: `tests/unit/compat/test_registry.py` (full rewrite)

**Interfaces:**
- Consumes: `feu.compat.target.Target` (Task 1).
- Produces:
  - `CompatRegistry(initial_state: dict[str, dict[Target, dict[str,
    str | None]]] | None = None)` — `initial_state` seeds the **base**
    layer.
  - `CompatRegistry.register(pkg_name: str, target: Target,
    pkg_version_min: str | None, pkg_version_max: str | None,
    exist_ok: bool = False, layer: str = "override") -> None`
  - `CompatRegistry.register_many(mapping: dict[str, dict[Target,
    dict[str, str | None]]], exist_ok: bool = False, layer: str =
    "override") -> None`
  - `CompatRegistry.get_config(pkg_name: str, target: Target) ->
    dict[str, str | None]`
  - `CompatRegistry.is_unsupported(pkg_name: str, target: Target) ->
    bool`
  - `CompatRegistry.get_min_and_max_versions(pkg_name: str, target:
    Target) -> tuple[Version | None, Version | None]`
  - `CompatRegistry.find_closest_version(pkg_name: str, pkg_version:
    str, target: Target) -> str`
  - `CompatRegistry.is_valid_version(pkg_name: str, pkg_version: str,
    target: Target) -> bool`
  - `CompatRegistry.base: dict[str, dict[Target, dict[str, str |
    None]]]` and `CompatRegistry.overrides: dict[str, dict[Target,
    dict[str, str | None]]]` — read-only-by-convention properties
    exposing the two layers (used by tests and by `test_defaults.py`
    in Task 3).
  - `UNSUPPORTED`, `UnsupportedVersionError` — unchanged, re-exported
    as before.

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/compat/test_registry.py
from __future__ import annotations

import pytest
from packaging.version import Version

from feu.compat.registry import UNSUPPORTED, CompatRegistry, UnsupportedVersionError
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
    registry = CompatRegistry({"numpy": {T311: {"min": "1.0.0", "max": None}}})
    assert registry.base == {"numpy": {T311: {"min": "1.0.0", "max": None}}}
    assert registry.overrides == {}


def test_compat_registry_init_copies_state() -> None:
    state = {"numpy": {T311: {"min": "1.0.0", "max": None}}}
    registry = CompatRegistry(state)
    registry.register("torch", T311, "2.0.0", None, layer="base")
    assert "torch" not in state


def test_compat_registry_repr() -> None:
    registry = CompatRegistry()
    assert repr(registry).startswith("CompatRegistry(")


def test_compat_registry_str() -> None:
    registry = CompatRegistry()
    assert str(registry).startswith("CompatRegistry(")


def test_compat_registry_register_default_layer_is_override() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.2.0", "2.0.2")
    assert registry.overrides == {
        "my_package": {T311: {"min": "1.2.0", "max": "2.0.2"}}
    }
    assert registry.base == {}


def test_compat_registry_register_base_layer() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.2.0", "2.0.2", layer="base")
    assert registry.base == {"my_package": {T311: {"min": "1.2.0", "max": "2.0.2"}}}
    assert registry.overrides == {}


def test_compat_registry_register_multiple() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.2.0", "2.0.2", layer="base")
    registry.register("my_package", T310, "1.1.0", "1.5.2", layer="base")
    assert registry.base == {
        "my_package": {
            T311: {"min": "1.2.0", "max": "2.0.2"},
            T310: {"min": "1.1.0", "max": "1.5.2"},
        }
    }


def test_compat_registry_register_exist_ok_false_same_layer() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.1.0", "1.5.2", layer="base")
    with pytest.raises(
        RuntimeError,
        match=r"A package configuration .* is already registered for package",
    ):
        registry.register("my_package", T311, "1.2.0", "2.0.2", layer="base")


def test_compat_registry_register_override_never_conflicts_with_base() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.1.0", "1.5.2", layer="base")
    # No exist_ok needed: override layer is independent of base layer.
    registry.register("my_package", T311, "9.0.0", None)
    assert registry.overrides == {"my_package": {T311: {"min": "9.0.0", "max": None}}}
    assert registry.base == {"my_package": {T311: {"min": "1.1.0", "max": "1.5.2"}}}


def test_compat_registry_register_exist_ok_true() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.1.0", "1.5.2", layer="base")
    registry.register("my_package", T311, "1.2.0", "2.0.2", layer="base", exist_ok=True)
    assert registry.base == {"my_package": {T311: {"min": "1.2.0", "max": "2.0.2"}}}


def test_compat_registry_register_many() -> None:
    registry = CompatRegistry()
    registry.register_many(
        {
            "numpy": {T311: {"min": "1.23.2", "max": "2.4.6"}},
            "torch": {T311: {"min": "2.0.0", "max": None}},
        },
        layer="base",
    )
    assert registry.base == {
        "numpy": {T311: {"min": "1.23.2", "max": "2.4.6"}},
        "torch": {T311: {"min": "2.0.0", "max": None}},
    }


def test_compat_registry_register_many_exist_ok_false() -> None:
    registry = CompatRegistry()
    registry.register_many(
        {"numpy": {T311: {"min": "1.0.0", "max": None}}}, layer="base"
    )
    with pytest.raises(
        RuntimeError,
        match=r"A package configuration .* is already registered for package",
    ):
        registry.register_many(
            {"numpy": {T311: {"min": "2.0.0", "max": None}}}, layer="base"
        )


def test_compat_registry_register_many_exist_ok_true() -> None:
    registry = CompatRegistry()
    registry.register_many(
        {"numpy": {T311: {"min": "1.0.0", "max": None}}}, layer="base"
    )
    registry.register_many(
        {"numpy": {T311: {"min": "2.0.0", "max": None}}}, layer="base", exist_ok=True
    )
    assert registry.base == {"numpy": {T311: {"min": "2.0.0", "max": None}}}


def test_compat_registry_get_config_override_wins_over_base() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.0.0", None, layer="base")
    registry.register("my_package", T311, "2.0.0", None, layer="override")
    assert registry.get_config(pkg_name="my_package", target=T311) == {
        "min": "2.0.0",
        "max": None,
    }


def test_compat_registry_get_config_falls_back_to_base() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.0.0", None, layer="base")
    assert registry.get_config(pkg_name="my_package", target=T311) == {
        "min": "1.0.0",
        "max": None,
    }


def test_compat_registry_get_config_empty_registry() -> None:
    registry = CompatRegistry()
    assert registry.get_config(pkg_name="my_package", target=T311) == {}


def test_compat_registry_get_config_no_matching_target() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T310, "1.0.0", None, layer="base")
    assert registry.get_config(pkg_name="my_package", target=T311) == {}


#############################################
#     Tests for wildcard/specificity match   #
#############################################


def test_compat_registry_os_wildcard_matches_any_os() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.0.0", None, layer="base")
    linux_target = Target(python_version="3.11", os="linux")
    assert registry.get_config(pkg_name="my_package", target=linux_target) == {
        "min": "1.0.0",
        "max": None,
    }


def test_compat_registry_more_specific_entry_wins() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.0.0", None, layer="base")
    registry.register(
        "my_package",
        Target(python_version="3.11", os="macos", arch="arm64"),
        "5.0.0",
        None,
        layer="base",
    )
    macos_arm = Target(python_version="3.11", os="macos", arch="arm64")
    linux = Target(python_version="3.11", os="linux")
    assert registry.get_config(pkg_name="my_package", target=macos_arm) == {
        "min": "5.0.0",
        "max": None,
    }
    assert registry.get_config(pkg_name="my_package", target=linux) == {
        "min": "1.0.0",
        "max": None,
    }


def test_compat_registry_free_threaded_must_match_exactly() -> None:
    registry = CompatRegistry()
    registry.register(
        "my_package",
        Target(python_version="3.14", free_threaded=True),
        "1.0.0",
        None,
        layer="base",
    )
    non_free_threaded = Target(python_version="3.14", free_threaded=False)
    assert registry.get_config(pkg_name="my_package", target=non_free_threaded) == {}


def test_compat_registry_most_recent_wins_among_ties() -> None:
    registry = CompatRegistry()
    registry.register(
        "my_package",
        Target(python_version="3.11", os="linux"),
        "1.0.0",
        None,
        layer="base",
    )
    registry.register(
        "my_package",
        Target(python_version="3.11", arch="x86_64"),
        "2.0.0",
        None,
        layer="base",
    )
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    # Both entries match with equal specificity (one non-None field each);
    # the most recently registered one wins.
    assert registry.get_config(pkg_name="my_package", target=target) == {
        "min": "2.0.0",
        "max": None,
    }


########################################
#     Tests for min/max/closest/valid  #
########################################


def test_compat_registry_get_min_and_max_versions() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.2.0", "2.2.0", layer="base")
    assert registry.get_min_and_max_versions(pkg_name="my_package", target=T311) == (
        Version("1.2.0"),
        Version("2.2.0"),
    )


def test_compat_registry_get_min_and_max_versions_empty() -> None:
    registry = CompatRegistry()
    assert registry.get_min_and_max_versions(pkg_name="my_package", target=T311) == (
        None,
        None,
    )


def test_compat_registry_find_closest_version_valid() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.2.0", "2.2.0", layer="base")
    assert (
        registry.find_closest_version(
            pkg_name="my_package", pkg_version="2.0.0", target=T311
        )
        == "2.0.0"
    )


def test_compat_registry_find_closest_version_missing() -> None:
    registry = CompatRegistry()
    assert (
        registry.find_closest_version(
            pkg_name="my_package", pkg_version="2.0.0", target=T311
        )
        == "2.0.0"
    )


def test_compat_registry_find_closest_version_lower() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.2.0", "2.2.0", layer="base")
    assert (
        registry.find_closest_version(
            pkg_name="my_package", pkg_version="1.0.0", target=T311
        )
        == "1.2.0"
    )


def test_compat_registry_find_closest_version_higher() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.2.0", "2.2.0", layer="base")
    assert (
        registry.find_closest_version(
            pkg_name="my_package", pkg_version="3.0.0", target=T311
        )
        == "2.2.0"
    )


def test_compat_registry_is_valid_version_true() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.2.0", "2.2.0", layer="base")
    assert registry.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", target=T311
    )


def test_compat_registry_is_valid_version_false_min() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.2.0", "2.2.0", layer="base")
    assert not registry.is_valid_version(
        pkg_name="my_package", pkg_version="1.0.0", target=T311
    )


def test_compat_registry_is_valid_version_false_max() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.2.0", "2.2.0", layer="base")
    assert not registry.is_valid_version(
        pkg_name="my_package", pkg_version="3.0.0", target=T311
    )


def test_compat_registry_is_valid_version_empty() -> None:
    registry = CompatRegistry()
    assert registry.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", target=T311
    )


###################################
#     Tests for UNSUPPORTED       #
###################################


def test_compat_registry_is_unsupported_true() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, UNSUPPORTED, UNSUPPORTED, layer="base")
    assert registry.is_unsupported(pkg_name="my_package", target=T315)


def test_compat_registry_is_unsupported_false() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, "1.2.0", "2.2.0", layer="base")
    assert not registry.is_unsupported(pkg_name="my_package", target=T311)


def test_compat_registry_is_unsupported_unconfigured() -> None:
    registry = CompatRegistry()
    assert not registry.is_unsupported(pkg_name="my_package", target=T311)


def test_compat_registry_get_min_and_max_versions_unsupported_raises() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, UNSUPPORTED, UNSUPPORTED, layer="base")
    with pytest.raises(
        UnsupportedVersionError, match=r"No version of package my_package"
    ):
        registry.get_min_and_max_versions(pkg_name="my_package", target=T315)


def test_compat_registry_find_closest_version_unsupported_raises() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, UNSUPPORTED, UNSUPPORTED, layer="base")
    with pytest.raises(
        UnsupportedVersionError, match=r"No version of package my_package"
    ):
        registry.find_closest_version(
            pkg_name="my_package", pkg_version="2.0.0", target=T315
        )


def test_compat_registry_is_valid_version_unsupported_false() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, UNSUPPORTED, UNSUPPORTED, layer="base")
    assert not registry.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", target=T315
    )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/compat/test_registry.py -v`
Expected: FAIL — `CompatRegistry` still uses the old `python_version:
str` / single-table API (`AttributeError`/`TypeError` on `.base`,
`register(layer=...)`, `get_config(target=...)`, etc).

- [ ] **Step 3: Rewrite `CompatRegistry`**

```python
# src/feu/compat/registry.py
r"""Define the compatibility registry for package version resolution.

This module provides a registry system that manages and resolves valid
package version ranges per compatibility target, enabling lookup of
the closest valid version and validation of a given version.
"""

from __future__ import annotations

__all__ = ["UNSUPPORTED", "CompatRegistry", "UnsupportedVersionError"]

import copy
from typing import Literal

from packaging.version import Version

from feu.compat.target import Target

UNSUPPORTED = "unsupported"
r"""Sentinel used as the ``min``/``max`` value to mark a target for
which no package version is valid.

This is distinct from ``None``, which means "unconstrained" (i.e. any
version is valid).
"""

_Layer = Literal["base", "override"]


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

    Each layer maps package name to ``Target`` to ``{"min": ...,
    "max": ...}``. A lookup target matches a stored entry when
    ``python_version`` and ``free_threaded`` are equal, and the
    stored entry's ``os``/``arch`` are either ``None`` (wildcard) or
    equal to the lookup target's ``os``/``arch``. Among all matching
    entries in a layer, the most specific one (most non-``None``
    ``os``/``arch`` fields) wins; ties are broken by most-recently
    registered.

    Args:
        initial_state: Optional initial mapping of package
            constraints, seeding the ``base`` layer. If provided, the
            state is copied to prevent external mutations.

    Example:
        ```pycon
        >>> from feu.compat import CompatRegistry, Target
        >>> registry = CompatRegistry()
        >>> registry.register(
        ...     pkg_name="numpy",
        ...     target=Target(python_version="3.11"),
        ...     pkg_version_min="1.23.2",
        ...     pkg_version_max="2.4.6",
        ...     layer="base",
        ... )
        >>> registry.is_valid_version("numpy", "2.0.2", Target(python_version="3.11"))
        True

        ```
    """

    def __init__(
        self,
        initial_state: dict[str, dict[Target, dict[str, str | None]]] | None = None,
    ) -> None:
        self._base: dict[str, dict[Target, dict[str, str | None]]] = copy.deepcopy(
            initial_state or {}
        )
        self._overrides: dict[str, dict[Target, dict[str, str | None]]] = {}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(\n"
            f"  (base): {self._base}\n"
            f"  (overrides): {self._overrides}\n)"
        )

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def base(self) -> dict[str, dict[Target, dict[str, str | None]]]:
        r"""The base layer (defaults/discovered data)."""
        return self._base

    @property
    def overrides(self) -> dict[str, dict[Target, dict[str, str | None]]]:
        r"""The override layer (user-supplied corrections)."""
        return self._overrides

    def _layer_table(
        self, layer: _Layer
    ) -> dict[str, dict[Target, dict[str, str | None]]]:
        return self._base if layer == "base" else self._overrides

    def register(
        self,
        pkg_name: str,
        target: Target,
        pkg_version_min: str | None,
        pkg_version_max: str | None,
        exist_ok: bool = False,
        layer: _Layer = "override",
    ) -> None:
        r"""Register a package configuration for a compatibility
        target.

        Args:
            pkg_name: The package name to register (e.g., ``"numpy"``).
            target: The compatibility target.
            pkg_version_min: The minimum valid package version for
                this target, or ``None`` for no minimum.
            pkg_version_max: The maximum valid package version for
                this target, or ``None`` for no maximum.
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

        table[pkg_name][target] = {"min": pkg_version_min, "max": pkg_version_max}

    def register_many(
        self,
        mapping: dict[str, dict[Target, dict[str, str | None]]],
        exist_ok: bool = False,
        layer: _Layer = "override",
    ) -> None:
        r"""Register multiple package configurations at once.

        Args:
            mapping: Mapping of package name to ``Target`` to
                ``{"min": ..., "max": ...}`` constraints.
            exist_ok: Forwarded to ``register``.
            layer: Forwarded to ``register``.
        """
        for pkg_name, targets in mapping.items():
            for target, config in targets.items():
                self.register(
                    pkg_name=pkg_name,
                    target=target,
                    pkg_version_min=config.get("min"),
                    pkg_version_max=config.get("max"),
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
        self,
        table: dict[str, dict[Target, dict[str, str | None]]],
        pkg_name: str,
        target: Target,
    ) -> dict[str, str | None] | None:
        if pkg_name not in table:
            return None
        best: dict[str, str | None] | None = None
        best_specificity = -1
        for entry_target, config in table[pkg_name].items():
            if not self._matches(entry_target, target):
                continue
            specificity = self._specificity(entry_target)
            if specificity >= best_specificity:
                best_specificity = specificity
                best = config
        return best

    def get_config(self, pkg_name: str, target: Target) -> dict[str, str | None]:
        r"""Get the package version configuration for a package and
        compatibility target.

        Checks the override layer first, then falls back to the base
        layer.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            target: The compatibility target.

        Returns:
            A dictionary with ``"min"`` and ``"max"`` keys, or an
            empty dictionary if no configuration matches.
        """
        config = self._resolve_in_layer(self._overrides, pkg_name, target)
        if config is not None:
            return config
        return self._resolve_in_layer(self._base, pkg_name, target) or {}

    def is_unsupported(self, pkg_name: str, target: Target) -> bool:
        r"""Indicate if no package version is valid for a target.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            target: The compatibility target.

        Returns:
            ``True`` if the package has no valid version for the
            given target, ``False`` otherwise.
        """
        config = self.get_config(pkg_name=pkg_name, target=target)
        return config.get("min") == UNSUPPORTED or config.get("max") == UNSUPPORTED

    def get_min_and_max_versions(
        self, pkg_name: str, target: Target
    ) -> tuple[Version | None, Version | None]:
        r"""Get the minimum and maximum versions as ``Version``
        objects.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            target: The compatibility target.

        Returns:
            A tuple ``(min_version, max_version)``, either value being
            ``None`` if unconstrained or unconfigured.

        Raises:
            UnsupportedVersionError: If no package version is valid
                for the given target.
        """
        if self.is_unsupported(pkg_name=pkg_name, target=target):
            msg = f"No version of package {pkg_name} is compatible with target {target}"
            raise UnsupportedVersionError(msg)
        config = self.get_config(pkg_name=pkg_name, target=target)
        min_version = config.get("min", None)
        max_version = config.get("max", None)
        if min_version is not None:
            min_version = Version(min_version)
        if max_version is not None:
            max_version = Version(max_version)
        return min_version, max_version

    def find_closest_version(
        self, pkg_name: str, pkg_version: str, target: Target
    ) -> str:
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
        min_version, max_version = self.get_min_and_max_versions(
            pkg_name=pkg_name, target=target
        )
        if min_version is not None and version < min_version:
            return min_version.base_version
        if max_version is not None and version > max_version:
            return max_version.base_version
        return pkg_version

    def is_valid_version(self, pkg_name: str, pkg_version: str, target: Target) -> bool:
        r"""Check if a package version is valid for a target.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The package version to validate.
            target: The compatibility target.

        Returns:
            ``True`` if valid or unconfigured, ``False`` otherwise,
            including when no package version is valid for the given
            target.
        """
        if self.is_unsupported(pkg_name=pkg_name, target=target):
            return False
        version = Version(pkg_version)
        min_version, max_version = self.get_min_and_max_versions(
            pkg_name=pkg_name, target=target
        )
        return (min_version is None or min_version <= version) and (
            max_version is None or version <= max_version
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/compat/test_registry.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add src/feu/compat/registry.py tests/unit/compat/test_registry.py
git commit -m "feat(compat): rewrite CompatRegistry with base/override layers and Target keys"
```

---

### Task 3: Update `defaults.py` to load into the base layer via `Target`

**Files:**
- Modify: `src/feu/compat/defaults.py`
- Modify: `tests/unit/compat/test_defaults.py`

**Interfaces:**
- Consumes: `CompatRegistry.register_many(mapping, layer="base")`
  (Task 2), `Target` (Task 1).
- Produces: `register_defaults(registry: CompatRegistry) -> None` —
  unchanged signature, now writes to the base layer with `Target`
  keys built from `DEFAULT_COMPAT`'s existing
  `dict[pkg][python_version_str]` shape. `DEFAULT_COMPAT` itself is
  **not** changed in shape (stays `dict[str, dict[str, dict[str, str |
  None]]]`) so `dev/discover_compat.py`'s source-rewriting logic keeps
  working untouched.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/compat/test_defaults.py
from __future__ import annotations

from feu.compat.defaults import DEFAULT_COMPAT, register_defaults
from feu.compat.registry import CompatRegistry
from feu.compat.target import Target

#############################################
#     Tests for register_defaults           #
#############################################


def test_register_defaults_populates_base_layer() -> None:
    registry = CompatRegistry()
    register_defaults(registry)
    assert registry.overrides == {}
    assert registry.base["numpy"][Target(python_version="3.11")] == {
        "min": "1.23.2",
        "max": "2.4.6",
    }


def test_register_defaults_numpy_entry() -> None:
    registry = CompatRegistry()
    register_defaults(registry)
    assert registry.get_config(
        pkg_name="numpy", target=Target(python_version="3.11")
    ) == {
        "min": "1.23.2",
        "max": "2.4.6",
    }


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/compat/test_defaults.py -v`
Expected: FAIL — `register_defaults` still calls
`registry.register_many(DEFAULT_COMPAT)` with string keys, which now
raises/mismatches since `register_many` expects `Target` keys and the
old test attributes (`registry.registry`) no longer exist.

- [ ] **Step 3: Update `register_defaults`**

Only the last function in the file changes; `DEFAULT_COMPAT` itself is
untouched.

```python
# src/feu/compat/defaults.py — replace the closing function only
def register_defaults(registry: CompatRegistry) -> None:
    r"""Populate a registry's base layer with the default package
    compatibility constraints.

    Args:
        registry: The registry to populate.
    """
    mapping: dict[str, dict[Target, dict[str, str | None]]] = {
        pkg_name: {
            Target(python_version=python_version): config
            for python_version, config in versions.items()
        }
        for pkg_name, versions in DEFAULT_COMPAT.items()
    }
    registry.register_many(mapping, layer="base")
```

Add the import at the top of the file (next to the existing
`TYPE_CHECKING` import block):

```python
from feu.compat.target import Target
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/compat/test_defaults.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/feu/compat/defaults.py tests/unit/compat/test_defaults.py
git commit -m "feat(compat): load DEFAULT_COMPAT into the registry base layer as Targets"
```

---

### Task 4: Update `interface.py` and package `__init__.py` exports

**Files:**
- Modify: `src/feu/compat/interface.py`
- Modify: `src/feu/compat/__init__.py`
- Modify: `tests/unit/compat/test_interface.py`

**Interfaces:**
- Consumes: `Target` (Task 1), updated `CompatRegistry` (Task 2),
  updated `register_defaults` (Task 3).
- Produces:
  - `get_default_registry() -> CompatRegistry` — unchanged.
  - `register_compat(mapping: dict[str, dict[Target, dict[str, str |
    None]]], exist_ok: bool = False) -> None` — delegates to
    `get_default_registry().register_many(mapping, exist_ok=exist_ok)`
    (default `layer="override"` from `register_many`).
  - `find_closest_version(pkg_name: str, pkg_version: str, target:
    Target) -> str`
  - `is_valid_version(pkg_name: str, pkg_version: str, target: Target)
    -> bool`
  - `feu.compat.__init__` re-exports `Target` in addition to the
    existing symbols.

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/compat/test_interface.py
from __future__ import annotations

from unittest.mock import patch

import pytest

from feu.compat.interface import (
    find_closest_version,
    get_default_registry,
    is_valid_version,
    register_compat,
)
from feu.compat.registry import CompatRegistry
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
    assert registry.get_config(pkg_name="numpy", target=T311) == {
        "min": "1.23.2",
        "max": "2.4.6",
    }


#################################
#     Tests for register_compat #
#################################


def test_register_compat_adds_to_override_layer() -> None:
    register_compat({"my_package": {T311: {"min": "1.0.0", "max": None}}})
    registry = get_default_registry()
    assert registry.get_config(pkg_name="my_package", target=T311) == {
        "min": "1.0.0",
        "max": None,
    }
    assert registry.overrides == {"my_package": {T311: {"min": "1.0.0", "max": None}}}


def test_register_compat_exist_ok_false_raises() -> None:
    register_compat({"my_package": {T311: {"min": "1.0.0", "max": None}}})
    with pytest.raises(
        RuntimeError, match=r"A package configuration .* is already registered"
    ):
        register_compat({"my_package": {T311: {"min": "2.0.0", "max": None}}})


def test_register_compat_overrides_a_default_without_exist_ok() -> None:
    # numpy has a base entry for 3.11; overriding it must not require exist_ok=True.
    register_compat({"numpy": {T311: {"min": "9.9.9", "max": None}}})
    assert get_default_registry().get_config(pkg_name="numpy", target=T311) == {
        "min": "9.9.9",
        "max": None,
    }


########################################
#     Tests for find_closest_version   #
########################################


def test_find_closest_version_delegates_to_default_registry() -> None:
    with patch.object(
        CompatRegistry, "find_closest_version", return_value="1.2.3"
    ) as mock_find:
        result = find_closest_version(
            pkg_name="numpy", pkg_version="2.0.2", target=T311
        )
    assert result == "1.2.3"
    mock_find.assert_called_once_with(
        pkg_name="numpy", pkg_version="2.0.2", target=T311
    )


def test_find_closest_version_uses_defaults() -> None:
    assert (
        find_closest_version(pkg_name="numpy", pkg_version="0.1.0", target=T311)
        == "1.23.2"
    )


##################################
#     Tests for is_valid_version #
##################################


def test_is_valid_version_delegates_to_default_registry() -> None:
    with patch.object(
        CompatRegistry, "is_valid_version", return_value=False
    ) as mock_valid:
        result = is_valid_version(pkg_name="numpy", pkg_version="2.0.2", target=T311)
    assert result is False
    mock_valid.assert_called_once_with(
        pkg_name="numpy", pkg_version="2.0.2", target=T311
    )


def test_is_valid_version_uses_defaults() -> None:
    assert not is_valid_version(pkg_name="numpy", pkg_version="0.1.0", target=T311)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/compat/test_interface.py -v`
Expected: FAIL — current `interface.py` functions take
`python_version: str`, not `target: Target`.

- [ ] **Step 3: Update `interface.py`**

Replace every `python_version: str` parameter with `target: Target`
and update the docstrings/examples accordingly:

```python
# src/feu/compat/interface.py
r"""Define the public interface for package/target compatibility
resolution."""

from __future__ import annotations

__all__ = [
    "find_closest_version",
    "get_default_registry",
    "is_valid_version",
    "register_compat",
]

from feu.compat.defaults import register_defaults
from feu.compat.registry import CompatRegistry
from feu.compat.target import Target


def get_default_registry() -> CompatRegistry:
    r"""Return the default global compatibility registry.

    The registry is created on the first call and reused on all
    subsequent calls (singleton pattern). It is pre-configured with
    the default package version constraints in its base layer.

    Returns:
        A singleton ``CompatRegistry`` configured with the default
        package version constraints.

    Example:
        ```pycon
        >>> from feu.compat import get_default_registry, Target
        >>> registry = get_default_registry()
        >>> registry.is_valid_version("numpy", "2.0.2", Target(python_version="3.11"))
        True

        ```
    """
    if not hasattr(get_default_registry, "_registry"):
        registry = CompatRegistry()
        register_defaults(registry)
        get_default_registry._registry = registry
    return get_default_registry._registry


def register_compat(
    mapping: dict[str, dict[Target, dict[str, str | None]]],
    exist_ok: bool = False,
) -> None:
    r"""Register custom package configurations into the default global
    registry's override layer.

    Override entries always take precedence over the default/base
    layer, and are only conflict-checked against other overrides, so
    correcting an inaccurate default never requires ``exist_ok=True``.

    Args:
        mapping: Mapping of package name to ``Target`` to
            ``{"min": ..., "max": ...}`` constraints.
        exist_ok: If ``False`` (default), raises an error if any entry
            is already registered as an override. If ``True``,
            overwrites existing override registrations silently.

    Raises:
        RuntimeError: If any entry is already registered as an
            override and ``exist_ok`` is ``False``.

    Example:
        ```pycon
        >>> from feu.compat import register_compat, Target
        >>> register_compat(
        ...     {"my_package": {Target(python_version="3.11"): {"min": "1.0.0", "max": None}}}
        ... )

        ```
    """
    get_default_registry().register_many(mapping, exist_ok=exist_ok)


def find_closest_version(pkg_name: str, pkg_version: str, target: Target) -> str:
    r"""Find the closest valid version for a package using the default
    registry.

    Args:
        pkg_name: The package name to check (e.g., ``"numpy"``).
        pkg_version: The requested package version.
        target: The compatibility target.

    Returns:
        The closest valid version as a string.

    Example:
        ```pycon
        >>> from feu.compat import find_closest_version, Target
        >>> find_closest_version(
        ...     pkg_name="numpy", pkg_version="2.0.2", target=Target(python_version="3.11")
        ... )
        '2.0.2'

        ```
    """
    return get_default_registry().find_closest_version(
        pkg_name=pkg_name, pkg_version=pkg_version, target=target
    )


def is_valid_version(pkg_name: str, pkg_version: str, target: Target) -> bool:
    r"""Check if a package version is valid for a target using the
    default registry.

    Args:
        pkg_name: The package name to check (e.g., ``"numpy"``).
        pkg_version: The package version to validate.
        target: The compatibility target.

    Returns:
        ``True`` if valid or unconfigured, ``False`` otherwise.

    Example:
        ```pycon
        >>> from feu.compat import is_valid_version, Target
        >>> is_valid_version(
        ...     pkg_name="numpy", pkg_version="2.0.2", target=Target(python_version="3.11")
        ... )
        True

        ```
    """
    return get_default_registry().is_valid_version(
        pkg_name=pkg_name, pkg_version=pkg_version, target=target
    )
```

Update `src/feu/compat/__init__.py` to also export `Target`:

```python
# src/feu/compat/__init__.py
r"""Contain a registry-based system for package/target compatibility
resolution."""

from __future__ import annotations

__all__ = [
    "UNSUPPORTED",
    "CompatRegistry",
    "Target",
    "UnsupportedVersionError",
    "discover_compat",
    "find_closest_version",
    "get_default_registry",
    "is_valid_version",
    "register_compat",
]

from feu.compat.discovery import discover_compat
from feu.compat.interface import (
    find_closest_version,
    get_default_registry,
    is_valid_version,
    register_compat,
)
from feu.compat.registry import UNSUPPORTED, CompatRegistry, UnsupportedVersionError
from feu.compat.target import Target
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/compat/ -v`
Expected: PASS (all tests in the `compat` unit test directory,
including Tasks 1-3's tests)

- [ ] **Step 5: Commit**

```bash
git add src/feu/compat/interface.py src/feu/compat/__init__.py tests/unit/compat/test_interface.py
git commit -m "feat(compat): migrate public interface to Target-based signatures"
```

---

### Task 5: Update `feu.install` callsite

**Files:**
- Modify: `src/feu/install/utils.py:79-83`
- Modify: `tests/unit/install/test_utils.py` (only the assertions that
  check `find_closest_version` call args, if any patch/mock it
  directly — otherwise no changes needed since it's exercised via
  `install_package_closest_version` end to end)

**Interfaces:**
- Consumes: `feu.compat.Target`, `feu.compat.find_closest_version(pkg_name,
  pkg_version, target)` (Task 4).
- Produces: `install_package_closest_version` behavior unchanged
  externally.

- [ ] **Step 1: Check for existing tests that assert on
  `find_closest_version` call arguments**

Run: `grep -n "find_closest_version" tests/unit/install/test_utils.py`

If this returns no matches, the existing behavioral tests for
`install_package_closest_version` (which exercise the real default
registry end-to-end) will simply keep passing once the callsite is
updated — proceed to Step 2. If it does return matches, update those
assertions to expect a `Target` instead of a bare string, following
the same pattern as Task 4's `mock_find.assert_called_once_with(...)`
update.

- [ ] **Step 2: Update the callsite**

```python
# src/feu/install/utils.py
```

Change the import block:

```python
from feu.compat import Target, find_closest_version
```

Change the call inside `install_package_closest_version`:

```python
install_package(
    installer=installer,
    package=package.with_version(
        find_closest_version(
            pkg_name=package.name,
            pkg_version=pkg_version,
            target=Target(python_version=get_python_major_minor()),
        )
    ),
)
```

- [ ] **Step 3: Run the install unit tests**

Run: `pytest tests/unit/install/ -v`
Expected: PASS (no behavioral change — `Target(python_version=X)` with
default `free_threaded=False, os=None, arch=None` resolves identically
to the old `python_version=X` string lookups)

- [ ] **Step 4: Commit**

```bash
git add src/feu/install/utils.py
git commit -m "refactor(install): pass a Target to find_closest_version"
```

---

### Task 6: Full test suite, lint, and doctest verification

**Files:** none created/modified (verification-only task); fix
whatever the checks below surface.

- [ ] **Step 1: Run the full unit + integration test suite**

Run: `pytest tests/unit tests/integration -v`
Expected: PASS. If `tests/integration/compat/test_discovery.py` or any
other test fails, inspect it — `discover_compat` itself is unchanged
in this plan, so a failure there indicates a missed update in
`register_defaults`/`interface.py`; fix and re-run.

- [ ] **Step 2: Run doctests for the touched modules**

Run: `pytest --doctest-modules src/feu/compat -v`
Expected: PASS. This exercises every `>>>` example updated in Tasks
1-4.

- [ ] **Step 3: Run the project linter**

Run: `ruff check src/feu/compat src/feu/install/utils.py tests/unit/compat tests/unit/install`
Expected: no errors. Fix any import-order or unused-import issues
(e.g. leftover `python_version` references) directly.

- [ ] **Step 4: Grep for any leftover `python_version=` compat call
  sites outside the discovery module**

Run: `grep -rn "python_version=" src/feu tests | grep -v "feu/compat/discovery.py\|feu/version\|test_discovery.py"`
Expected: no output. Anything printed here is a callsite that still
passes the old string-based signature and needs updating using the
same `Target(python_version=...)` pattern as Task 5.

- [ ] **Step 5: Commit (only if Steps 1-4 required fixes)**

```bash
git add -A
git commit -m "test(compat): fix remaining call sites after Target migration"
```

If no fixes were needed, skip this commit — there is nothing to
record.

---

## Post-plan follow-ups (not part of this plan)

- `dev/discover_compat.py` / `discover_compat()` still only produce
  python-version-keyed data. A follow-up could extend discovery to
  inspect actual wheel filenames per release to auto-populate
  `os`/`arch`/`free_threaded` axes in the base layer.
- `docs/docs/refs/compat.md` is a stub (15 bytes) and was not expanded
  as part of this plan; consider documenting `Target` and the
  base/override layering there separately.
