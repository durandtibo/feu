# `feu.compat`: registry-based package/Python-version compatibility

## Purpose

Replace `feu.package.PackageConfig` with a new sub-package, `feu.compat`,
that resolves the valid version of a package for a given Python version,
following the registry pattern used in
[`coola.hashing`](https://github.com/durandtibo/coola/tree/main/src/coola/hashing)
(a `*Registry` class holding state, a singleton default registry, and
module-level convenience functions).

## Why not a direct port of `coola.hashing`'s dispatch model

`coola.hashing`'s `HasherRegistry` dispatches on Python **type** via MRO,
and each registered value is a `BaseHasher` instance. `PackageConfig`'s
registry is keyed by package **name** (a string) with per-Python-version
min/max constraints as plain data — there is no natural "class per type"
here, and no MRO-style resolution is needed. The design borrows the
registry/singleton/interface *shape* of `coola.hashing`, not its type
dispatch mechanics.

## Package layout

```
src/feu/compat/
    __init__.py     # public exports
    registry.py      # CompatRegistry class
    defaults.py       # built-in package version constraints + registration helper
    interface.py       # get_default_registry(), register_compat(), find_closest_version(), is_valid_version()
```

### `registry.py` — `CompatRegistry`

Wraps `dict[str, dict[str, dict[str, str | None]]]` (package name ->
python version -> `{"min": ..., "max": ...}`). Instance (not class-level)
state, constructible with an optional `initial_state` mapping, mirroring
`HasherRegistry.__init__`.

Methods (ported from the current `PackageConfig` classmethods, made
instance methods):

- `register(pkg_name, python_version, pkg_version_min, pkg_version_max, exist_ok=False)`
  — replaces `add_config`; raises `RuntimeError` if an entry already
  exists for `(pkg_name, python_version)` and `exist_ok=False`.
- `register_many(mapping, exist_ok=False)` — bulk registration from a
  `dict[str, dict[str, dict[str, str | None]]]`, for loading `defaults.py`
  and for user extension, mirroring `HasherRegistry.register_many`.
- `get_config(pkg_name, python_version) -> dict[str, str | None]`
- `get_min_and_max_versions(pkg_name, python_version) -> tuple[Version | None, Version | None]`
- `find_closest_version(pkg_name, pkg_version, python_version) -> str`
- `is_valid_version(pkg_name, pkg_version, python_version) -> bool`
- `__repr__`/`__str__` for readable debugging output.

Behavior of `get_config`/`get_min_and_max_versions`/`find_closest_version`/
`is_valid_version` is unchanged from today's `PackageConfig`: missing
package or Python version means "no constraint" (permissive default).

### `defaults.py`

Holds the existing big dict of default constraints (click, duckdb, jax,
matplotlib, numpy, pandas, pyarrow, pydantic, requests, scikit-learn,
scipy, torch, xarray — copied verbatim from `PackageConfig.registry`),
plus a `_register_defaults(registry: CompatRegistry) -> None` helper that
loads that dict into a given registry via `register_many`, mirroring
`_register_default_hashers` in `coola.hashing.interface`.

### `interface.py`

- `get_default_registry() -> CompatRegistry` — singleton, created and
  populated from `defaults.py` on first call, reused afterwards (same
  lazy-singleton pattern as `coola.hashing.get_default_registry`).
- `register_compat(mapping, exist_ok=False) -> None` — convenience
  function that calls `get_default_registry().register_many(...)`,
  mirroring `register_hashers`.
- `find_closest_version(pkg_name, pkg_version, python_version) -> str`
  and `is_valid_version(pkg_name, pkg_version, python_version) -> bool`
  — module-level convenience functions delegating to
  `get_default_registry()`, mirroring `hash_object`. These preserve the
  existing public function signatures from `feu.package`.

### `__init__.py`

```python
__all__ = [
    "CompatRegistry",
    "find_closest_version",
    "get_default_registry",
    "is_valid_version",
    "register_compat",
]

from feu.compat.registry import CompatRegistry
from feu.compat.interface import (
    find_closest_version,
    get_default_registry,
    is_valid_version,
    register_compat,
)
```

## Migration

- Delete `src/feu/package.py` and `tests/unit/test_package.py` (replaced
  by `src/feu/compat/` and `tests/unit/compat/`).
- Update `src/feu/install/utils.py` (`from feu.package import
  find_closest_version` -> `from feu.compat import find_closest_version`).
- Update `src/feu/__main__.py` (same import path change, if applicable).
- Update `docs/docs/usage.md`'s `PackageConfig` example to use
  `CompatRegistry`/`get_default_registry()` instead.
- No shim/deprecation layer — full replacement, per user preference.

## Testing

Mirror `tests/unit/test_package.py`'s coverage under
`tests/unit/compat/`, split by module (`test_registry.py`,
`test_interface.py`), using a fresh `CompatRegistry()` instance per test
instead of `@patch.dict(PackageConfig.registry, ...)` (instance state
removes the need to patch class-level shared state). Include a test that
`get_default_registry()` returns the same singleton instance across
calls, and that `find_closest_version`/`is_valid_version` module
functions delegate to it correctly.

## Out of scope

- No per-package config object/class (rejected during design — plain
  nested dict is kept, consistent with the string-keyed, non-MRO nature
  of this registry).
- No backward-compatibility shim for `feu.package.PackageConfig`.
