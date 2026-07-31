# Compat registry: support multiple disjoint version ranges

## Problem

`CompatRegistry` currently stores a single `{"min": ..., "max": ...}` pair per
`(package, Target)`. This can't represent packages with disjoint supported
version lines for the same Python version — e.g. pydantic 1.x and pydantic
2.8+ are both valid on Python 3.13, but 2.0–2.7 is not. There is no way to
express "valid below X, invalid X–Y, valid above Y" today.

## Design

### `VersionRange`

A new `NamedTuple` in `feu/compat/registry.py`:

```python
class VersionRange(NamedTuple):
    min: str | None
    max: str | None
```

Represents one contiguous supported range. `min`/`max` of `None` means
unconstrained on that side (same semantics as today).

### Storage shape

Each `(package, Target)` entry becomes `list[VersionRange]` instead of a
single dict. Ranges are assumed non-overlapping and given in ascending order
by convention (not validated). An **empty list** means "no version is valid
for this target" — this replaces the `UNSUPPORTED` string sentinel, which is
removed entirely (both the constant and its export from `registry.py`).

`CompatRegistry._base` / `_overrides` become
`dict[str, dict[Target, list[VersionRange]]]`.

### API changes

- `CompatRegistry.register(pkg_name, target, *, ranges: list[VersionRange], exist_ok=False, layer="override")`
  replaces the `pkg_version_min`/`pkg_version_max` kwargs.
- `register_many(mapping: dict[str, dict[Target, list[VersionRange]]], ...)`
  — value type updated accordingly.
- `get_config(pkg_name, target) -> list[VersionRange]` — was
  `dict[str, str | None]`; now returns the matching entry's range list
  directly (empty list if nothing matches — no more `{}` sentinel).
- `is_unsupported(pkg_name, target) -> bool` — `not get_config(...)`.
- `get_version_ranges(pkg_name, target) -> list[tuple[Version | None, Version | None]]`
  replaces `get_min_and_max_versions`. Converts each `VersionRange`'s
  string bounds to `packaging.version.Version`. Raises
  `UnsupportedVersionError` if the config is unsupported (empty ranges).
- `is_valid_version(pkg_name, pkg_version, target) -> bool` — `True` if the
  version falls within *any* range (each range checked with the existing
  bound semantics: `None` means unconstrained on that side).
- `find_closest_version(pkg_name, pkg_version, target) -> str`:
  - if the version already falls within any range, return it unchanged.
  - if it's below every range's min, snap to the lowest min.
  - if it's above every range's max, snap to the highest max.
  - if it falls in a gap between two consecutive ranges, snap **up** to the
    next higher range's min (not distance-based — always prefer moving
    forward to the next supported range).

No back-compat shim: `register()` no longer accepts `pkg_version_min`/
`pkg_version_max`, and there is no dict-shaped range accepted anywhere. This
is an internal, pre-1.0 registry, so the callers below are updated in place
rather than preserving the old shape.

### `defaults.py`

`DEFAULT_COMPAT` literals switch from
`{"min": ..., "max": ...}` to `[VersionRange(min, max)]` per Python version:

```text
"pydantic": {
    "3.15": [VersionRange(None, None)],
    "3.14": [VersionRange("2.12.0", None)],
    "3.13": [
        VersionRange("1.0.0", "1.10.13"),
        VersionRange("2.8.0", None),
    ],
    ...
},
```

(Exact historical pydantic 1.x cutoff versions to be filled in as real data,
not placeholder — see implementation plan.)

`register_defaults` updates its comprehension to pass the `list[VersionRange]`
straight through (no dict conversion needed since the literal is already
typed).

### Callers outside the registry

`feu/compat/interface.py`'s public wrappers (`register_compat`,
`find_closest_version`, `is_valid_version`) forward to the registry
unchanged in spirit; `register_compat`'s signature updates to take
`ranges: list[VersionRange]` instead of min/max kwargs.

### Testing

- `tests/unit/compat/test_registry.py`: update existing single-range cases
  to use one-element `ranges=[VersionRange(...)]`; add new cases for:
  multiple disjoint ranges, `is_valid_version` across a gap, versions above,
  in the gap, and outside every range, `find_closest_version` snapping up
  from a gap, snapping to lowest/highest at the extremes, and empty
  `ranges=[]` (unsupported) behavior for `is_unsupported`,
  `get_version_ranges` (raises), `is_valid_version` (`False`), and
  `find_closest_version` (raises).
- `tests/unit/compat/test_defaults.py`: update to the new `DEFAULT_COMPAT`
  shape; verify pydantic's disjoint ranges round-trip through
  `register_defaults`.
- `tests/unit/compat/test_interface.py`: update `register_compat` calls to
  the new `ranges=` kwarg.

## Out of scope

- Overlap validation between ranges in the same list (not enforced, same as
  today's lack of cross-target validation).
- Changes to `Target` or the os/arch/free-threaded matching logic — unrelated
  to this change (see the separate multiaxis-compat-target spec).
