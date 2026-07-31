# Multi-axis Compatibility Targets with Layered Overrides

Date: 2026-07-31

## Problem

`feu.compat` currently keys compatibility constraints on a single Python
version string (e.g. `"3.11"`). This can't express:

- Free-threaded builds (e.g. `3.14t`), which some packages don't ship
  wheels for yet.
- OS (Linux / macOS / Windows) and architecture (x86_64 / arm64)
  differences, since some packages only publish wheels for specific
  platforms.

Additionally, `discover_compat` derives constraints from PyPI
`requires_python` metadata, which isn't always accurate. There is
currently no clean way to let user-supplied corrections coexist with
(and take precedence over) auto-discovered/default data without
overwriting it in the same flat dict.

## Goals

- Support Python version, free-threaded, OS, and architecture as
  independent axes of a compatibility "target".
- Allow entries to be registered at any level of specificity (e.g. a
  blanket rule for `python_version="3.14"`, plus a narrower override
  for `python_version="3.14", free_threaded=True, os="macos"`).
- Let user-registered corrections always take precedence over
  defaults/discovered data, and never conflict with them, so a
  discovery refresh never silently clobbers a user correction.

## Non-goals

- Changing `discover_compat` to inspect actual wheel filenames to
  auto-detect free-threaded/OS/arch support. It continues to derive
  constraints from `requires_python` only, producing
  python-version-only entries. Wheel-tag-based discovery is a
  candidate follow-up, not part of this change.
- Plumbing OS/arch/free-threaded detection through `feu.install`
  (`PackageSpec`, `InstallerSpec`, the pip resolver) to automatically
  build a fully-populated `Target` at install time. The install
  callsite is updated only to pass an equivalent `Target` for its
  current python-version-only lookup.

## Design

### `Target`

A new frozen dataclass in `feu/compat/target.py`:

```python
@dataclass(frozen=True)
class Target:
    python_version: str
    free_threaded: bool = False
    os: str | None = None      # e.g. "linux", "macos", "windows"; None = wildcard
    arch: str | None = None    # e.g. "x86_64", "arm64"; None = wildcard
```

`os`/`arch` default to `None`, meaning "unspecified / matches
anything". `free_threaded` defaults to `False`. `Target` replaces the
`python_version: str` parameter across the registry and public API.

### Wildcard matching and specificity

`CompatRegistry` stores entries per package as `dict[Target, {"min":
..., "max": ...}]`. When resolving a lookup target, an entry matches
if every one of its non-`None`/non-default fields equals the
corresponding lookup field:

- `python_version` must match exactly (always required).
- `free_threaded` must match exactly (always required — `False` is a
  real value, not a wildcard, since it's the default for the vast
  majority of environments).
- `os` matches if the entry's `os` is `None` or equal to the lookup's
  `os`.
- `arch` matches if the entry's `arch` is `None` or equal to the
  lookup's `arch`.

Among all matching entries, the most specific one wins: the entry
with the greater count of non-`None` `os`/`arch` fields. If multiple
entries tie in specificity, the override layer takes precedence, and
within the same layer the most recently registered entry wins.

### Two-layer registry

`CompatRegistry` holds two independent tables:

```python
self._base: dict[str, dict[Target, dict[str, str | None]]]
self._overrides: dict[str, dict[Target, dict[str, str | None]]]
```

- `register_defaults()` and any bulk-loading of `discover_compat`
  output write to `_base` via a new `register_base`/`register_many`
  variant (internal use).
- The public `register_compat()` / `CompatRegistry.register()`
  (called by end users) always writes to `_overrides`.
- Lookup methods (`get_config`, `is_unsupported`,
  `get_min_and_max_versions`, `find_closest_version`,
  `is_valid_version`) resolve against `_overrides` first (using the
  specificity rule above); if no entry in `_overrides` matches, they
  fall back to `_base`.
- `exist_ok` conflict detection in `register()`/`register_many()`
  only ever compares a new override against existing entries in
  `_overrides` — never against `_base`. A user can therefore always
  register a correction over a shipped/discovered default without
  passing `exist_ok=True`, and re-running discovery to refresh
  `_base` can never conflict with a stored user override.

### Public API changes

- `CompatRegistry.register(pkg_name, target: Target, pkg_version_min,
  pkg_version_max, exist_ok=False)` — `python_version: str` param
  replaced by `target: Target`.
- `CompatRegistry.register_many(mapping: dict[str, dict[Target,
  dict[str, str | None]]], exist_ok=False)`.
- `CompatRegistry.get_config`, `is_unsupported`,
  `get_min_and_max_versions`, `find_closest_version`,
  `is_valid_version` — all take `target: Target` instead of
  `python_version: str`.
- Module-level `feu.compat.register_compat(mapping, exist_ok=False)`,
  `find_closest_version(pkg_name, pkg_version, target)`,
  `is_valid_version(pkg_name, pkg_version, target)` — same param
  rename.
- `DEFAULT_COMPAT` / `register_defaults` internally build `Target`
  keys from the existing python-version-only data (each entry becomes
  `Target(python_version=X)`).
- `discover_compat` continues to return `dict[str, dict[str, str |
  None]]` keyed by python-version string (unchanged, since it only
  knows about the python-version axis); the caller (`register_defaults`
  / `dev/discover_compat.py`) wraps each key in `Target(python_version=X)`
  when loading it into the registry.

### Callsite update

`feu/install/utils.py::install_package_closest_version` changes:

```python
find_closest_version(
    pkg_name=package.name,
    pkg_version=pkg_version,
    target=Target(python_version=get_python_major_minor()),
)
```

No behavioral change — `os`/`arch`/`free_threaded` stay unspecified
(wildcard / `False`), matching current behavior exactly.

## Testing

- Unit tests for `Target` (equality/hashability, defaults).
- Unit tests for `CompatRegistry` specificity/wildcard matching:
  exact match, os-only wildcard, arch-only wildcard, free-threaded
  mismatch, most-specific-wins with multiple candidate matches.
- Unit tests for override-vs-base precedence: override present →
  wins; override absent → falls back to base; `exist_ok=False`
  conflict only triggers between two overrides, not override vs base.
- Update existing `test_registry.py`, `test_defaults.py`,
  `test_interface.py`, `test_discovery.py` call sites to use `Target`.
- Update `tests/integration/compat/test_discovery.py` if it touches
  the registry-loading path.
