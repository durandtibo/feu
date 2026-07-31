# Wheel-Tag-Based Multi-Axis Compatibility Discovery

Date: 2026-07-31

## Problem

`feu.compat.discovery.discover_compat` derives Python-version
compatibility from PyPI's `requires_python` release metadata only. It
has no way to tell whether a package actually ships a free-threaded
build, or whether it publishes wheels for a given OS/architecture —
some packages only compile for specific platforms, and
`requires_python` says nothing about that.

Since [2026-07-31 multi-axis compat targets](2026-07-31-multiaxis-compat-target-design.md),
`feu.compat`'s registry can express these axes via `Target(python_version,
free_threaded, os, arch)`. This change adds a discovery function that
inspects actual wheel filenames per PyPI release to populate those
axes automatically, instead of requiring users to hand-author every
free-threaded/OS/arch override.

## Goals

- Given a package name and a set of concrete `Target`s, determine
  which stable releases actually shipped a wheel matching each target,
  and derive `{"min": ..., "max": ...}` the same way `discover_compat`
  does today.
- Detect free-threaded support, OS, and architecture from real wheel
  filenames (PEP 427 tags), not from metadata a maintainer may have
  forgotten to declare.

## Non-goals

- Changing `discover_compat()`'s existing return shape or behavior. It
  keeps deriving Python-version-only constraints from
  `requires_python`, and `dev/discover_compat.py` /
  `DEFAULT_COMPAT`'s file format are untouched.
- Regenerating `DEFAULT_COMPAT` with real multi-axis data. This change
  only builds and tests the discovery capability; wiring it into the
  `dev/discover_compat.py` regeneration script and shipping real
  free-threaded/OS/arch defaults is a separate follow-up.
- Full PEP 425 tag support (compressed multi-platform tags on a single
  wheel like `manylinux_2_17_x86_64.manylinux2014_x86_64`, PyPy
  builds, `universal2` macOS wheels, 32-bit platforms). The parser
  recognizes a small, explicit set of common CPython/OS/arch
  combinations and returns `None` (skip) for anything else rather than
  guessing.

## Design

### Wheel tag parsing — `feu/compat/wheel_tags.py`

```text
@dataclass(frozen=True)
class WheelTags:
    python_version: str
    free_threaded: bool
    os: str
    arch: str


def parse_wheel_filename(filename: str) -> WheelTags | None:
```

A wheel filename is `{name}-{version}(-{build})?-{python
tag}-{abi tag}-{platform tag}.whl` (PEP 427). `parse_wheel_filename`:

1. Splits on `-` and takes the python tag, ABI tag, and platform tag
   (the last three `-`-separated components before `.whl`).
2. Parses the python tag: only `cp3\d+` (CPython 3.x) is recognized;
   anything else (`py3`, `pp3`, ...) returns `None` — pure-Python and
   non-CPython wheels don't carry OS/arch/free-threading signal.
   `cp310` → `"3.10"`, `cp39` → `"3.9"`, `cp314` → `"3.14"` (digits
   after `cp3` form the minor version).
3. Free-threaded: `True` if the ABI tag ends in `t` (e.g. `cp314t`),
   `False` otherwise (`cp314`, `abi3`, `none`).
4. Parses the platform tag against a small normalization table:

   | platform tag prefix/substring | `os`      |
   |--------------------------------|-----------|
   | `manylinux`, `linux`           | `"linux"` |
   | `macosx`                        | `"macos"` |
   | `win32`, `win_amd64`, `win_arm64` | `"windows"` |

   | platform tag substring | `arch`      |
   |-------------------------|-------------|
   | `x86_64`, `amd64`       | `"x86_64"`  |
   | `aarch64`, `arm64`      | `"arm64"`   |

   If the platform tag doesn't match a known `os` or a known `arch`
   (e.g. `i686`, `universal2`, `armv7l`, `win32`), `parse_wheel_filename`
   returns `None` for that file — better to skip a wheel than
   misclassify it.
5. If a wheel's compressed platform tag contains multiple dotted
   platform components (e.g. two manylinux variants), only the first
   is inspected — they always resolve to the same `os`/`arch` in
   practice for the combinations this parser supports.

### Fetching wheel filenames per release — `feu/version/pypi.py`

```text
def fetch_pypi_wheel_filenames(package: str) -> dict[str, tuple[str, ...]]:
```

Mirrors `fetch_pypi_requires_python`: same `https://pypi.org/pypi/{package}/json`
endpoint, same `@lru_cache`, but collects the `filename` of every file
with `packagetype == "bdist_wheel"` for each release into a tuple
(empty tuple for releases with no wheels).

### Discovery — `feu/compat/discovery.py`

```text
DEFAULT_TARGETS: tuple[Target, ...] = (
    # cartesian product of DEFAULT_PYTHON_VERSIONS x free_threaded x os x arch
)

def discover_compat_targets(
    pkg_name: str,
    targets: Sequence[Target] = DEFAULT_TARGETS,
) -> dict[Target, dict[str, str | None]]:
```

For each `target` in `targets`:

1. Fetch `fetch_pypi_wheel_filenames(pkg_name)` (cached, so calling
   this once per package regardless of `len(targets)` is cheap).
2. Compute the same stable/valid version filtering `discover_compat`
   uses (`filter_stable_versions(filter_valid_versions(...))`),
   sorted ascending by `Version`.
3. A release is "compatible with `target`" if at least one of its
   wheel filenames parses (via `parse_wheel_filename`) to a
   `WheelTags` equal to `(target.python_version, target.free_threaded,
   target.os, target.arch)`.
4. Same min/max derivation as `discover_compat`: `min` = first
   compatible stable release, `max` = last compatible release (or
   `None` if it's the newest stable release overall). No compatible
   release → `{"min": UNSUPPORTED, "max": UNSUPPORTED}`.

`target.os`/`target.arch` must be concrete (non-`None`) for this
function — `DEFAULT_TARGETS` only contains fully-specified targets,
and matching against a wildcard target isn't meaningful here (there's
nothing to compare a wheel's concrete OS/arch against).

`DEFAULT_TARGETS` is the cartesian product of
`discovery.DEFAULT_PYTHON_VERSIONS` (already defined) × `{False,
True}` (free-threaded) × `{"linux", "macos", "windows"}` × `{"x86_64",
"arm64"}` — 7 × 2 × 3 × 2 = 84 targets. Callers that only care about a
subset (e.g. one OS) pass a narrower `targets` sequence.

The output's shape, `dict[Target, dict[str, str | None]]`, is exactly
what `CompatRegistry.register_many(mapping, layer="base")` expects, so
integrating this into a future defaults-regeneration script is a
direct plug-in — not part of this change.

## Testing

- Unit tests for `parse_wheel_filename`: standard CPython wheel,
  free-threaded wheel, macOS arm64, Windows, pure-Python wheel
  (returns `None`), unrecognized platform tag (returns `None`),
  unrecognized interpreter tag (returns `None`).
- Unit tests for `fetch_pypi_wheel_filenames`: mocked `fetch_data`,
  mirroring `fetch_pypi_requires_python`'s existing test style.
- Unit tests for `discover_compat_targets`: mocked
  `fetch_pypi_wheel_filenames`, covering compatible/incompatible
  targets, min/max derivation, and the `UNSUPPORTED` case — mirroring
  `discover_compat`'s existing unit tests.
- One integration test (`tests/integration/compat/test_discovery.py`)
  against a real package on PyPI (e.g. `numpy`, which ships
  free-threaded wheels) verifying `discover_compat_targets` returns
  plausible, non-empty results for at least one concrete target
  without asserting exact version numbers (to stay resilient to
  upstream releases, matching this repo's existing integration-test
  convention).
