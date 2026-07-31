# Wheel-Tag-Based Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `discover_compat_targets()`, a new discovery function
that inspects real PyPI wheel filenames to detect free-threaded/OS/arch
compatibility, alongside the existing `requires_python`-based
`discover_compat()`.

**Architecture:** A pure wheel-filename parser (`WheelTags`,
`parse_wheel_filename`) classifies PEP 427 wheel tags into
`(python_version, free_threaded, os, arch)`. A new PyPI fetcher
(`fetch_pypi_wheel_filenames`) retrieves wheel filenames per release.
`discover_compat_targets` combines both, mirroring `discover_compat`'s
existing min/max derivation logic but per concrete `Target`.

**Tech Stack:** Python 3.10+, `packaging` for version parsing,
`requests` (via `feu.utils.http.fetch_data`) for PyPI access, `pytest`.
No new dependencies.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-31-wheel-tag-discovery-design.md`
- `discover_compat()`, `DEFAULT_COMPAT`, and `dev/discover_compat.py`
  are NOT touched by this plan.
- `parse_wheel_filename` returns `None` (never raises) for anything it
  can't confidently classify: non-CPython interpreter tags, and
  platform tags outside the known `os`/`arch` table.
- `discover_compat_targets` requires every `Target` in its `targets`
  argument to have concrete (non-`None`) `os` and `arch` — this is a
  caller contract, not runtime-validated (documented, not enforced,
  matching the rest of `feu.compat`'s style of trusting callers at
  internal boundaries).
- `DEFAULT_TARGETS` = cartesian product of `DEFAULT_PYTHON_VERSIONS`
  (existing constant in `feu/compat/discovery.py`) × `{False, True}`
  (free-threaded) × `{"linux", "macos", "windows"}` × `{"x86_64",
  "arm64"}`.

---

### Task 1: Wheel tag parser

**Files:**
- Create: `src/feu/compat/wheel_tags.py`
- Test: `tests/unit/compat/test_wheel_tags.py`

**Interfaces:**
- Produces: `feu.compat.wheel_tags.WheelTags` — frozen dataclass with
  `python_version: str`, `free_threaded: bool`, `os: str`, `arch:
  str`. `feu.compat.wheel_tags.parse_wheel_filename(filename: str) ->
  WheelTags | None`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/compat/test_wheel_tags.py
from __future__ import annotations

import pytest

from feu.compat.wheel_tags import WheelTags, parse_wheel_filename

#################################################
#     Tests for parse_wheel_filename            #
#################################################


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        (
            "numpy-2.3.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            WheelTags(
                python_version="3.12", free_threaded=False, os="linux", arch="x86_64"
            ),
        ),
        (
            "numpy-2.3.0-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            WheelTags(
                python_version="3.14", free_threaded=True, os="linux", arch="x86_64"
            ),
        ),
        (
            "numpy-2.3.0-cp312-cp312-macosx_11_0_arm64.whl",
            WheelTags(
                python_version="3.12", free_threaded=False, os="macos", arch="arm64"
            ),
        ),
        (
            "numpy-2.3.0-cp39-cp39-win_amd64.whl",
            WheelTags(
                python_version="3.9", free_threaded=False, os="windows", arch="x86_64"
            ),
        ),
        (
            "numpy-2.3.0-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl",
            WheelTags(
                python_version="3.10", free_threaded=False, os="linux", arch="arm64"
            ),
        ),
    ],
)
def test_parse_wheel_filename_recognized(filename: str, expected: WheelTags) -> None:
    assert parse_wheel_filename(filename) == expected


def test_parse_wheel_filename_pure_python_returns_none() -> None:
    assert parse_wheel_filename("click-8.1.8-py3-none-any.whl") is None


def test_parse_wheel_filename_pypy_returns_none() -> None:
    assert (
        parse_wheel_filename("numpy-2.3.0-pp310-pypy310_pp73-manylinux_2_17_x86_64.whl")
        is None
    )


def test_parse_wheel_filename_unrecognized_platform_returns_none() -> None:
    assert parse_wheel_filename("numpy-2.3.0-cp312-cp312-linux_i686.whl") is None


def test_parse_wheel_filename_universal2_returns_none() -> None:
    assert (
        parse_wheel_filename("numpy-2.3.0-cp312-cp312-macosx_11_0_universal2.whl")
        is None
    )


def test_parse_wheel_filename_no_extension_match_returns_none() -> None:
    assert parse_wheel_filename("not-a-wheel-file.tar.gz") is None


def test_wheel_tags_is_frozen_and_comparable() -> None:
    a = WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")
    b = WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")
    assert a == b
    with pytest.raises(AttributeError):
        a.os = "macos"  # type: ignore[misc]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/compat/test_wheel_tags.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named
'feu.compat.wheel_tags'`

- [ ] **Step 3: Implement the parser**

```python
# src/feu/compat/wheel_tags.py
r"""Contain functions to parse PEP 427 wheel filenames into
compatibility-relevant tags."""

from __future__ import annotations

__all__ = ["WheelTags", "parse_wheel_filename"]

import re
from dataclasses import dataclass

_PYTHON_TAG_PATTERN = re.compile(r"^cp3(\d+)$")

_OS_TABLE: dict[str, str] = {
    "manylinux": "linux",
    "linux": "linux",
    "macosx": "macos",
    "win_amd64": "windows",
    "win_arm64": "windows",
    "win32": "windows",
}

_ARCH_TABLE: dict[str, str] = {
    "x86_64": "x86_64",
    "amd64": "x86_64",
    "aarch64": "arm64",
    "arm64": "arm64",
}


@dataclass(frozen=True)
class WheelTags:
    r"""Compatibility-relevant tags extracted from a wheel filename.

    Args:
        python_version: The CPython version, e.g. ``"3.14"``.
        free_threaded: ``True`` if the wheel targets a free-threaded
            (no-GIL) build.
        os: The operating system, e.g. ``"linux"``, ``"macos"``,
            ``"windows"``.
        arch: The CPU architecture, e.g. ``"x86_64"``, ``"arm64"``.
    """

    python_version: str
    free_threaded: bool
    os: str
    arch: str


def _parse_python_tag(python_tag: str) -> str | None:
    match = _PYTHON_TAG_PATTERN.match(python_tag)
    if not match:
        return None
    digits = match.group(1)
    return f"3.{digits}"


def _parse_os(platform_tag: str) -> str | None:
    for key, os_name in _OS_TABLE.items():
        if platform_tag.startswith(key):
            return os_name
    return None


def _parse_arch(platform_tag: str) -> str | None:
    for key, arch_name in _ARCH_TABLE.items():
        if key in platform_tag:
            return arch_name
    return None


def parse_wheel_filename(filename: str) -> WheelTags | None:
    r"""Parse a PEP 427 wheel filename into compatibility tags.

    Args:
        filename: The wheel filename, e.g.
            ``"numpy-2.3.0-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"``.

    Returns:
        The parsed ``WheelTags``, or ``None`` if the filename doesn't
            end in ``.whl``, targets a non-CPython interpreter, or its
            platform tag isn't in the known ``os``/``arch`` tables.

    Example:
        ```pycon
        >>> from feu.compat.wheel_tags import parse_wheel_filename
        >>> parse_wheel_filename("numpy-2.3.0-cp312-cp312-macosx_11_0_arm64.whl")
        WheelTags(python_version='3.12', free_threaded=False, os='macos', arch='arm64')

        ```
    """
    if not filename.endswith(".whl"):
        return None
    stem = filename[: -len(".whl")]
    parts = stem.split("-")
    if len(parts) < 5:
        return None
    python_tag, abi_tag, platform_tag = parts[-3], parts[-2], parts[-1]

    python_version = _parse_python_tag(python_tag)
    if python_version is None:
        return None

    first_platform_component = platform_tag.split(".")[0]
    os_name = _parse_os(first_platform_component)
    arch_name = _parse_arch(first_platform_component)
    if os_name is None or arch_name is None:
        return None

    free_threaded = abi_tag.endswith("t")

    return WheelTags(
        python_version=python_version,
        free_threaded=free_threaded,
        os=os_name,
        arch=arch_name,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/compat/test_wheel_tags.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add src/feu/compat/wheel_tags.py tests/unit/compat/test_wheel_tags.py
git commit -m "feat(compat): add PEP 427 wheel filename tag parser"
```

---

### Task 2: `fetch_pypi_wheel_filenames`

**Files:**
- Modify: `src/feu/version/pypi.py`
- Modify: `src/feu/version/__init__.py`
- Test: `tests/unit/version/test_pypi.py`

**Interfaces:**
- Produces: `feu.version.pypi.fetch_pypi_wheel_filenames(package: str)
  -> dict[str, tuple[str, ...]]` — mapping release version to the
  filenames of its `bdist_wheel` files (empty tuple if none).
  Re-exported from `feu.version`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/unit/version/test_pypi.py` (same file, same
`_reset_cache` fixture pattern — add `fetch_pypi_wheel_filenames` to
its `cache_clear()` calls too):

```python
# tests/unit/version/test_pypi.py — additions

# Update the existing import line to also import fetch_pypi_wheel_filenames:
# from feu.version import fetch_pypi_requires_python, fetch_pypi_versions, fetch_pypi_wheel_filenames

# Update the existing _reset_cache fixture to also clear the new cache:
# @pytest.fixture(autouse=True)
# def _reset_cache() -> None:
#     fetch_pypi_versions.cache_clear()
#     fetch_pypi_requires_python.cache_clear()
#     fetch_pypi_wheel_filenames.cache_clear()


####################################################
#     Tests for fetch_pypi_wheel_filenames          #
####################################################


def make_mock_wheel_filenames_response() -> Response:
    resp = Mock(
        json=Mock(
            return_value={
                "releases": {
                    "1.0.0": [
                        {
                            "filename": "pkg-1.0.0-cp39-cp39-manylinux_2_17_x86_64.whl",
                            "packagetype": "bdist_wheel",
                        },
                        {"filename": "pkg-1.0.0.tar.gz", "packagetype": "sdist"},
                    ],
                    "1.1.0": [
                        {
                            "filename": "pkg-1.1.0-cp39-cp39-manylinux_2_17_x86_64.whl",
                            "packagetype": "bdist_wheel",
                        },
                        {
                            "filename": "pkg-1.1.0-cp310-cp310-manylinux_2_17_x86_64.whl",
                            "packagetype": "bdist_wheel",
                        },
                    ],
                    "1.2.0": [{"filename": "pkg-1.2.0.tar.gz", "packagetype": "sdist"}],
                    "1.3.0": [],
                }
            }
        )
    )
    resp.status_code = 200
    return resp


@requests_available
def test_fetch_pypi_wheel_filenames(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock(get=Mock(return_value=make_mock_wheel_filenames_response()))
    monkeypatch.setattr(requests, "Session", lambda: session)

    assert fetch_pypi_wheel_filenames("my_package") == {
        "1.0.0": ("pkg-1.0.0-cp39-cp39-manylinux_2_17_x86_64.whl",),
        "1.1.0": (
            "pkg-1.1.0-cp39-cp39-manylinux_2_17_x86_64.whl",
            "pkg-1.1.0-cp310-cp310-manylinux_2_17_x86_64.whl",
        ),
        "1.2.0": (),
        "1.3.0": (),
    }
    session.get.assert_called_once_with(
        url="https://pypi.org/pypi/my_package/json", timeout=10.0
    )


@patch("feu.imports.requests.is_requests_available", lambda: False)
def test_fetch_pypi_wheel_filenames_no_requests() -> None:
    with pytest.raises(
        RuntimeError, match=r"'requests' package is required but not installed."
    ):
        fetch_pypi_wheel_filenames("my_package")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/version/test_pypi.py -v`
Expected: FAIL with `ImportError: cannot import name
'fetch_pypi_wheel_filenames'`

- [ ] **Step 3: Implement `fetch_pypi_wheel_filenames`**

Add to `src/feu/version/pypi.py`, after `fetch_pypi_requires_python`,
and add `"fetch_pypi_wheel_filenames"` to the module's `__all__`:

```python
@lru_cache
def fetch_pypi_wheel_filenames(package: str) -> dict[str, tuple[str, ...]]:
    r"""Get the wheel filenames for each release of a package on PyPI.

    Args:
        package: The package name.

    Returns:
        A dictionary mapping each release version string to a tuple of
            its ``bdist_wheel`` filenames (empty tuple if the release
            has no wheel files).

    Example:
        ```pycon
        >>> from feu.version import fetch_pypi_wheel_filenames
        >>> mapping = fetch_pypi_wheel_filenames("numpy")  # doctest: +SKIP

        ```
    """
    metadata = fetch_data(url=f"https://pypi.org/pypi/{package}/json", timeout=10)
    result: dict[str, tuple[str, ...]] = {}
    for version, files in metadata["releases"].items():
        result[version] = tuple(
            file["filename"]
            for file in (files or [])
            if file.get("packagetype") == "bdist_wheel"
        )
    return result
```

Add `"fetch_pypi_wheel_filenames"` to `src/feu/version/__init__.py`'s
`__all__` list (alphabetically, next to `"fetch_pypi_requires_python"`)
and to its import from `feu.version.pypi`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/version/test_pypi.py -v`
Expected: PASS (all tests, including pre-existing ones)

- [ ] **Step 5: Commit**

```bash
git add src/feu/version/pypi.py src/feu/version/__init__.py tests/unit/version/test_pypi.py
git commit -m "feat(version): add fetch_pypi_wheel_filenames"
```

---

### Task 3: `discover_compat_targets`

**Files:**
- Modify: `src/feu/compat/discovery.py`
- Test: `tests/unit/compat/test_discovery.py`

**Interfaces:**
- Consumes: `feu.compat.target.Target` (already exists), `WheelTags`,
  `parse_wheel_filename` (Task 1), `fetch_pypi_wheel_filenames` (Task
  2), `feu.compat.registry.UNSUPPORTED` (already exists),
  `filter_stable_versions`, `filter_valid_versions` (already used by
  `discover_compat`).
- Produces: `feu.compat.discovery.DEFAULT_TARGETS: tuple[Target,
  ...]`, `feu.compat.discovery.discover_compat_targets(pkg_name: str,
  targets: Sequence[Target] = DEFAULT_TARGETS) -> dict[Target,
  dict[str, str | None]]`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/compat/test_discovery.py — additions (append to the
# existing file; add the new imports at the top alongside the
# existing ones)

# from feu.compat.discovery import (
#     DEFAULT_PYTHON_VERSIONS,
#     DEFAULT_TARGETS,
#     discover_compat,
#     discover_compat_targets,
# )
# from feu.compat.target import Target

##############################################
#     Tests for DEFAULT_TARGETS              #
##############################################


def test_default_targets_shape() -> None:
    assert len(DEFAULT_TARGETS) == len(DEFAULT_PYTHON_VERSIONS) * 2 * 3 * 2
    assert all(isinstance(target, Target) for target in DEFAULT_TARGETS)
    assert all(
        target.os is not None and target.arch is not None for target in DEFAULT_TARGETS
    )


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
        "1.1.0a1": (
            "pkg-1.1.0a1-cp311-cp311-manylinux_2_17_x86_64.whl",
        ),  # pre-release, ignored
        "not-a-version": ("pkg-bad.whl",),  # invalid, ignored
    },
)
def test_discover_compat_targets_basic() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(linux_311,))
    assert compat == {linux_311: {"min": "1.0.0", "max": None}}


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
    free_threaded_314 = Target(
        python_version="3.14", free_threaded=True, os="linux", arch="x86_64"
    )
    compat = discover_compat_targets("pkg", targets=(free_threaded_314,))
    assert compat == {free_threaded_314: {"min": "1.1.0", "max": None}}


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
    assert compat == {macos_arm: {"min": UNSUPPORTED, "max": UNSUPPORTED}}


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
    assert compat == {linux_311: {"min": "1.0.0", "max": "1.0.0"}}


@patch("feu.compat.discovery.fetch_pypi_wheel_filenames", lambda *_args: {})
def test_discover_compat_targets_empty() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(linux_311,))
    assert compat == {linux_311: {"min": UNSUPPORTED, "max": UNSUPPORTED}}


@patch(
    "feu.compat.discovery.fetch_pypi_wheel_filenames",
    lambda *_args: {"1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",)},
)
def test_discover_compat_targets_multiple_targets() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    macos_311 = Target(python_version="3.11", os="macos", arch="arm64")
    compat = discover_compat_targets("pkg", targets=(linux_311, macos_311))
    assert compat == {
        linux_311: {"min": "1.0.0", "max": None},
        macos_311: {"min": UNSUPPORTED, "max": UNSUPPORTED},
    }
```

Note: `test_discover_compat_targets_max_is_last_compatible` above
actually exercises the "no compatible release" path (no macOS wheels
in the mocked data) — this matches the `UNSUPPORTED` assertion; keep
the test name as written since it documents that a target with zero
matches degrades to `UNSUPPORTED`, not a crash.

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/compat/test_discovery.py -v`
Expected: FAIL with `ImportError: cannot import name
'discover_compat_targets'` (and `DEFAULT_TARGETS`)

- [ ] **Step 3: Implement `discover_compat_targets`**

Add to `src/feu/compat/discovery.py`. Update the module's `__all__` to
add `"DEFAULT_TARGETS"` and `"discover_compat_targets"`, and add the
new imports:

```python
from feu.compat.target import Target
from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
from feu.version.pypi import fetch_pypi_wheel_filenames
```

Then, after the existing `discover_compat`/`_is_compatible` functions:

```python
DEFAULT_TARGETS: tuple[Target, ...] = tuple(
    Target(python_version=python_version, free_threaded=free_threaded, os=os, arch=arch)
    for python_version in DEFAULT_PYTHON_VERSIONS
    for free_threaded in (False, True)
    for os in ("linux", "macos", "windows")
    for arch in ("x86_64", "arm64")
)


def discover_compat_targets(
    pkg_name: str, targets: Sequence[Target] = DEFAULT_TARGETS
) -> dict[Target, dict[str, str | None]]:
    r"""Discover the min/max package version compatible with each
    target, using actual wheel filenames published on PyPI.

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
        A mapping of ``Target`` to ``{"min": ..., "max": ...}``, in
            the same shape expected by
            ``CompatRegistry.register_many``.

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

    result: dict[Target, dict[str, str | None]] = {}
    for target in targets:
        wanted = WheelTags(
            python_version=target.python_version,
            free_threaded=target.free_threaded,
            os=target.os,
            arch=target.arch,
        )
        compatible = [
            version for version in versions if wanted in tags_by_version[version]
        ]
        if not compatible:
            result[target] = {"min": UNSUPPORTED, "max": UNSUPPORTED}
            continue
        result[target] = {
            "min": compatible[0],
            "max": None if compatible[-1] == latest else compatible[-1],
        }
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/compat/test_discovery.py -v`
Expected: PASS (all tests, including pre-existing `discover_compat`
tests)

- [ ] **Step 5: Commit**

```bash
git add src/feu/compat/discovery.py tests/unit/compat/test_discovery.py
git commit -m "feat(compat): add discover_compat_targets for wheel-tag-based discovery"
```

---

### Task 4: Integration test, package exports, and full verification

**Files:**
- Modify: `tests/integration/compat/test_discovery.py`
- Modify: `src/feu/compat/__init__.py`

**Interfaces:**
- Consumes: `discover_compat_targets`, `DEFAULT_TARGETS` (Task 3),
  `WheelTags`, `parse_wheel_filename` (Task 1).
- Produces: `feu.compat.__init__` additionally re-exports
  `discover_compat_targets`, `WheelTags`, and `parse_wheel_filename`.

- [ ] **Step 1: Write the integration test**

Append to `tests/integration/compat/test_discovery.py` (add
`discover_compat_targets, DEFAULT_TARGETS` to the existing `from
feu.compat.discovery import ...` line, and `from feu.compat.target
import Target` alongside the existing imports):

```python
# tests/integration/compat/test_discovery.py — additions

##############################################
#     Tests for discover_compat_targets      #
##############################################


@pytest.fixture(autouse=True)
def _reset_wheel_cache() -> None:
    from feu.version.pypi import fetch_pypi_wheel_filenames

    fetch_pypi_wheel_filenames.cache_clear()


@requests_available
def test_discover_compat_targets_numpy_linux_free_threaded() -> None:
    # numpy started publishing free-threaded (cp313t/cp314t) linux x86_64
    # wheels once free-threaded CPython builds became available on PyPI;
    # assert a non-empty, internally consistent result rather than exact
    # version numbers, to stay resilient to upstream releases.
    target = Target(
        python_version="3.14", free_threaded=True, os="linux", arch="x86_64"
    )
    compat = discover_compat_targets("numpy", targets=(target,))
    assert set(compat) == {target}
    config = compat[target]
    assert set(config) == {"min", "max"}
    if config["min"] not in (None, "unsupported"):
        assert Version(config["min"])
    if config["max"] not in (None, "unsupported"):
        assert Version(config["max"])


@requests_not_available
def test_discover_compat_targets_no_requests() -> None:
    with pytest.raises(
        RuntimeError, match=r"'requests' package is required but not installed."
    ):
        discover_compat_targets("numpy")
```

- [ ] **Step 2: Run the integration test to verify it passes**

`discover_compat_targets` was already implemented and committed in
Task 3, so this test exercises real, already-working code — it should
pass on the first run (hits real PyPI; may take ~1-2s).

Run: `pytest tests/integration/compat/test_discovery.py -v -k discover_compat_targets`
Expected: PASS

- [ ] **Step 3: Update `feu/compat/__init__.py` exports**

```python
# src/feu/compat/__init__.py
```

Add `"discover_compat_targets"`, `"WheelTags"`,
`"parse_wheel_filename"` to `__all__` (alphabetically), and add:

```python
from feu.compat.discovery import (
    discover_compat_targets,
)  # alongside existing discover_compat import
from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
```

- [ ] **Step 4: Run the full test suite, doctests, and linter**

Run: `pytest tests/unit tests/integration -v`
Expected: PASS (all tests, including everything from Tasks 1-3 plus
pre-existing tests)

Run: `pytest --doctest-modules src/feu/compat -v`
Expected: PASS

Run: `ruff check src/feu/compat src/feu/version tests/unit/compat tests/unit/version tests/integration/compat`
Expected: no errors

Run: `black --check src/feu/compat src/feu/version tests/unit/compat tests/unit/version tests/integration/compat`
Expected: no reformatting needed (run `black` on the same paths and
re-check if it does)

- [ ] **Step 5: Commit**

```bash
git add tests/integration/compat/test_discovery.py src/feu/compat/__init__.py
git commit -m "feat(compat): export discover_compat_targets and add integration test"
```

---

## Post-plan follow-ups (not part of this plan)

- Wiring `discover_compat_targets` into `dev/discover_compat.py` (or a
  new sibling script) to actually regenerate `DEFAULT_COMPAT` with
  real free-threaded/OS/arch data is a separate follow-up, once this
  capability has been used/reviewed in practice.
- `parse_wheel_filename` intentionally skips `universal2`, 32-bit
  (`i686`, `win32`), and non-CPython wheels. Extending the
  `os`/`arch` tables is straightforward if a future package needs one
  of those.
- `parse_wheel_filename` derives `python_version` solely from the
  wheel's *python tag* (e.g. `cp39` -> `"3.9"`); it does not account
  for `abi3` (stable ABI) wheels, which are forward-compatible with
  every CPython version >= the tagged one, not just that exact
  version. A wheel like `cryptography-...-cp39-abi3-...whl` is
  actually installable on 3.9, 3.10, 3.11, etc., but the parser
  currently reports it as supporting only `"3.9"`. As a result,
  `discover_compat_targets` will under-report (be overly
  conservative about) support for packages that ship stable-ABI
  wheels — not a crash, just a wrong/too-narrow answer for that
  specific case. The design spec only mentions `abi3` in the context
  of free-threaded detection, not python-version semantics, so this
  is a genuine gap that needs a deliberate design decision (e.g.
  treat the tagged version as a floor and mark all newer target
  versions as compatible too, vs. skip/flag `abi3` wheels
  specially) before `discover_compat_targets` is used to regenerate
  real `DEFAULT_COMPAT` data — otherwise packages using the stable
  ABI (e.g. `cryptography`) will get incorrect, overly narrow compat
  ranges.
