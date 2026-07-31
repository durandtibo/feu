# feu.compat Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `feu.package.PackageConfig` with a registry-based `feu.compat` sub-package, mirroring the `coola.hashing` pattern (registry class + default singleton + module-level convenience functions).

**Architecture:** A `CompatRegistry` class wraps `dict[str, dict[str, dict[str, str | None]]]` (package name -> python version -> `{"min", "max"}`) with instance methods for registration and lookup. `defaults.py` holds the built-in constraints table. `interface.py` exposes a lazy singleton (`get_default_registry`), a bulk-registration convenience (`register_compat`), and two convenience functions (`find_closest_version`, `is_valid_version`) that delegate to the singleton. `feu/package.py` is deleted; all call sites move to `feu.compat`.

**Tech Stack:** Python, `packaging.version.Version`, `pytest`.

## Global Constraints

- No per-package config object/class — registry state stays a plain nested dict (per spec decision).
- No backward-compatibility shim for `feu.package.PackageConfig` — full replacement.
- Preserve existing public behavior exactly: missing package/python-version config means "no constraint" (permissive).
- Preserve existing public function signatures for `find_closest_version(pkg_name, pkg_version, python_version)` and `is_valid_version(pkg_name, pkg_version, python_version)`.
- Do not commit any changes — the user will review and commit themselves.

---

### Task 1: `CompatRegistry` class

**Files:**
- Create: `src/feu/compat/__init__.py`
- Create: `src/feu/compat/registry.py`
- Test: `tests/unit/compat/__init__.py`
- Test: `tests/unit/compat/test_registry.py`

**Interfaces:**
- Consumes: `packaging.version.Version` (stdlib dependency already used by `feu.package`).
- Produces: `CompatRegistry` class with:
  - `__init__(self, initial_state: dict[str, dict[str, dict[str, str | None]]] | None = None) -> None`
  - `registry: dict[str, dict[str, dict[str, str | None]]]` (public attribute, copy of `initial_state` or `{}`)
  - `register(self, pkg_name: str, python_version: str, pkg_version_min: str | None, pkg_version_max: str | None, exist_ok: bool = False) -> None`
  - `register_many(self, mapping: dict[str, dict[str, dict[str, str | None]]], exist_ok: bool = False) -> None`
  - `get_config(self, pkg_name: str, python_version: str) -> dict[str, str | None]`
  - `get_min_and_max_versions(self, pkg_name: str, python_version: str) -> tuple[Version | None, Version | None]`
  - `find_closest_version(self, pkg_name: str, pkg_version: str, python_version: str) -> str`
  - `is_valid_version(self, pkg_name: str, pkg_version: str, python_version: str) -> bool`
  - `__repr__(self) -> str` and `__str__(self) -> str`
  These are used by Task 2 (`defaults.py`) and Task 3 (`interface.py`).

- [ ] **Step 1: Write the failing tests for `CompatRegistry`**

Create `tests/unit/compat/__init__.py` (empty file).

Create `tests/unit/compat/test_registry.py`:

```python
from __future__ import annotations

import pytest
from packaging.version import Version

from feu.compat.registry import CompatRegistry

##################################
#     Tests for CompatRegistry     #
##################################


def test_compat_registry_init_empty() -> None:
    registry = CompatRegistry()
    assert registry.registry == {}


def test_compat_registry_init_with_state() -> None:
    registry = CompatRegistry({"numpy": {"3.11": {"min": "1.0.0", "max": None}}})
    assert registry.registry == {"numpy": {"3.11": {"min": "1.0.0", "max": None}}}


def test_compat_registry_init_copies_state() -> None:
    state = {"numpy": {"3.11": {"min": "1.0.0", "max": None}}}
    registry = CompatRegistry(state)
    registry.register("torch", "3.11", "2.0.0", None)
    assert "torch" not in state


def test_compat_registry_repr() -> None:
    registry = CompatRegistry()
    assert repr(registry).startswith("CompatRegistry(")


def test_compat_registry_str() -> None:
    registry = CompatRegistry()
    assert str(registry).startswith("CompatRegistry(")


def test_compat_registry_register() -> None:
    registry = CompatRegistry()
    registry.register(
        pkg_name="my_package",
        python_version="3.11",
        pkg_version_min="1.2.0",
        pkg_version_max="2.0.2",
    )
    assert registry.registry == {"my_package": {"3.11": {"min": "1.2.0", "max": "2.0.2"}}}


def test_compat_registry_register_multiple() -> None:
    registry = CompatRegistry()
    registry.register(
        pkg_name="my_package",
        python_version="3.11",
        pkg_version_min="1.2.0",
        pkg_version_max="2.0.2",
    )
    registry.register(
        pkg_name="my_package",
        python_version="3.10",
        pkg_version_min="1.1.0",
        pkg_version_max="1.5.2",
    )
    assert registry.registry == {
        "my_package": {
            "3.10": {"min": "1.1.0", "max": "1.5.2"},
            "3.11": {"min": "1.2.0", "max": "2.0.2"},
        }
    }


def test_compat_registry_register_exist_ok_false() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.1.0", "max": "1.5.2"}}})
    with pytest.raises(
        RuntimeError, match=r"A package configuration .* is already registered for package"
    ):
        registry.register(
            pkg_name="my_package",
            python_version="3.11",
            pkg_version_min="1.2.0",
            pkg_version_max="2.0.2",
        )


def test_compat_registry_register_exist_ok_true() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.1.0", "max": "1.5.2"}}})
    registry.register(
        pkg_name="my_package",
        python_version="3.11",
        pkg_version_min="1.2.0",
        pkg_version_max="2.0.2",
        exist_ok=True,
    )
    assert registry.registry == {"my_package": {"3.11": {"min": "1.2.0", "max": "2.0.2"}}}


def test_compat_registry_register_many() -> None:
    registry = CompatRegistry()
    registry.register_many(
        {
            "numpy": {"3.11": {"min": "1.23.2", "max": "2.4.6"}},
            "torch": {"3.11": {"min": "2.0.0", "max": None}},
        }
    )
    assert registry.registry == {
        "numpy": {"3.11": {"min": "1.23.2", "max": "2.4.6"}},
        "torch": {"3.11": {"min": "2.0.0", "max": None}},
    }


def test_compat_registry_register_many_exist_ok_false() -> None:
    registry = CompatRegistry({"numpy": {"3.11": {"min": "1.0.0", "max": None}}})
    with pytest.raises(
        RuntimeError, match=r"A package configuration .* is already registered for package"
    ):
        registry.register_many({"numpy": {"3.11": {"min": "2.0.0", "max": None}}})


def test_compat_registry_register_many_exist_ok_true() -> None:
    registry = CompatRegistry({"numpy": {"3.11": {"min": "1.0.0", "max": None}}})
    registry.register_many(
        {"numpy": {"3.11": {"min": "2.0.0", "max": None}}}, exist_ok=True
    )
    assert registry.registry == {"numpy": {"3.11": {"min": "2.0.0", "max": None}}}


def test_compat_registry_get_config() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.0.2"}}})
    assert registry.get_config(pkg_name="my_package", python_version="3.11") == {
        "min": "1.2.0",
        "max": "2.0.2",
    }


def test_compat_registry_get_config_empty_registry() -> None:
    registry = CompatRegistry()
    assert registry.get_config(pkg_name="my_package", python_version="3.11") == {}


def test_compat_registry_get_config_empty_pkg_name() -> None:
    registry = CompatRegistry({"my_package": {}})
    assert registry.get_config(pkg_name="my_package", python_version="3.11") == {}


def test_compat_registry_get_config_empty_python_version() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {}}})
    assert registry.get_config(pkg_name="my_package", python_version="3.11") == {}


def test_compat_registry_get_min_and_max_versions() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert registry.get_min_and_max_versions(pkg_name="my_package", python_version="3.11") == (
        Version("1.2.0"),
        Version("2.2.0"),
    )


def test_compat_registry_get_min_and_max_versions_min_only() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": None}}})
    assert registry.get_min_and_max_versions(pkg_name="my_package", python_version="3.11") == (
        Version("1.2.0"),
        None,
    )


def test_compat_registry_get_min_and_max_versions_max_only() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": None, "max": "2.2.0"}}})
    assert registry.get_min_and_max_versions(pkg_name="my_package", python_version="3.11") == (
        None,
        Version("2.2.0"),
    )


def test_compat_registry_get_min_and_max_versions_empty() -> None:
    registry = CompatRegistry()
    assert registry.get_min_and_max_versions(pkg_name="my_package", python_version="3.11") == (
        None,
        None,
    )


def test_compat_registry_find_closest_version_valid() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert (
        registry.find_closest_version(
            pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
        )
        == "2.0.0"
    )


def test_compat_registry_find_closest_version_missing() -> None:
    registry = CompatRegistry()
    assert (
        registry.find_closest_version(
            pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
        )
        == "2.0.0"
    )


def test_compat_registry_find_closest_version_lower() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert (
        registry.find_closest_version(
            pkg_name="my_package", pkg_version="1.0.0", python_version="3.11"
        )
        == "1.2.0"
    )


def test_compat_registry_find_closest_version_higher() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert (
        registry.find_closest_version(
            pkg_name="my_package", pkg_version="3.0.0", python_version="3.11"
        )
        == "2.2.0"
    )


def test_compat_registry_is_valid_version_true() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert registry.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )


def test_compat_registry_is_valid_version_false_min() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert not registry.is_valid_version(
        pkg_name="my_package", pkg_version="1.0.0", python_version="3.11"
    )


def test_compat_registry_is_valid_version_false_max() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert not registry.is_valid_version(
        pkg_name="my_package", pkg_version="3.0.0", python_version="3.11"
    )


def test_compat_registry_is_valid_version_empty() -> None:
    registry = CompatRegistry()
    assert registry.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/thibaut/workspace/code/feu && python -m pytest tests/unit/compat/test_registry.py -v`
Expected: FAIL/ERROR with `ModuleNotFoundError: No module named 'feu.compat'`

- [ ] **Step 3: Implement `CompatRegistry`**

Create `src/feu/compat/__init__.py`:

```python
r"""Contain a registry-based system for package/Python-version
compatibility resolution."""

from __future__ import annotations

__all__ = ["CompatRegistry"]

from feu.compat.registry import CompatRegistry
```

Create `src/feu/compat/registry.py`:

```python
r"""Define the compatibility registry for package version resolution.

This module provides a registry system that manages and resolves valid
package version ranges per Python version, enabling lookup of the
closest valid version and validation of a given version.
"""

from __future__ import annotations

__all__ = ["CompatRegistry"]

import copy
from typing import ClassVar

from packaging.version import Version


class CompatRegistry:
    r"""Manage package version compatibility across different Python
    versions.

    This registry maintains package version constraints indexed by
    package name and Python version. Each entry specifies the minimum
    and maximum compatible versions for a package on a specific Python
    version.

    The registry state is structured as a nested dictionary::

        {
            package_name: {
                python_version: {
                    "min": minimum_version_string or None,
                    "max": maximum_version_string or None,
                },
                ...
            },
            ...
        }

    Args:
        initial_state: Optional initial mapping of package constraints.
            If provided, the state is copied to prevent external
            mutations.

    Example:
        ```pycon
        >>> from feu.compat import CompatRegistry
        >>> registry = CompatRegistry()
        >>> registry.register(
        ...     pkg_name="numpy",
        ...     python_version="3.11",
        ...     pkg_version_min="1.23.2",
        ...     pkg_version_max="2.4.6",
        ... )
        >>> registry.is_valid_version("numpy", "2.0.2", "3.11")
        True

        ```
    """

    def __init__(
        self, initial_state: dict[str, dict[str, dict[str, str | None]]] | None = None
    ) -> None:
        self.registry: dict[str, dict[str, dict[str, str | None]]] = copy.deepcopy(
            initial_state or {}
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(\n  (registry): {self.registry}\n)"

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}(\n  (registry): {self.registry}\n)"

    def register(
        self,
        pkg_name: str,
        python_version: str,
        pkg_version_min: str | None,
        pkg_version_max: str | None,
        exist_ok: bool = False,
    ) -> None:
        r"""Register a package configuration for a Python version.

        Args:
            pkg_name: The package name to register (e.g., ``"numpy"``).
            python_version: The Python version (e.g., ``"3.11"``).
            pkg_version_min: The minimum valid package version for this
                Python version, or ``None`` for no minimum.
            pkg_version_max: The maximum valid package version for this
                Python version, or ``None`` for no maximum.
            exist_ok: If ``False``, a ``RuntimeError`` is raised when a
                configuration already exists for this package and
                Python version. Set to ``True`` to overwrite.

        Raises:
            RuntimeError: If a configuration already exists for the
                given package name and Python version, and
                ``exist_ok`` is ``False``.
        """
        self.registry[pkg_name] = self.registry.get(pkg_name, {})

        if python_version in self.registry[pkg_name] and not exist_ok:
            msg = (
                f"A package configuration ({self.registry[pkg_name][python_version]}) is "
                f"already registered for package {pkg_name} and python {python_version}. "
                f"Please use `exist_ok=True` if you want to overwrite the package config"
            )
            raise RuntimeError(msg)

        self.registry[pkg_name][python_version] = {
            "min": pkg_version_min,
            "max": pkg_version_max,
        }

    def register_many(
        self,
        mapping: dict[str, dict[str, dict[str, str | None]]],
        exist_ok: bool = False,
    ) -> None:
        r"""Register multiple package configurations at once.

        Args:
            mapping: Mapping of package name to Python version to
                ``{"min": ..., "max": ...}`` constraints.
            exist_ok: If ``False``, a ``RuntimeError`` is raised when
                any entry already exists. Set to ``True`` to overwrite.
        """
        for pkg_name, versions in mapping.items():
            for python_version, config in versions.items():
                self.register(
                    pkg_name=pkg_name,
                    python_version=python_version,
                    pkg_version_min=config.get("min"),
                    pkg_version_max=config.get("max"),
                    exist_ok=exist_ok,
                )

    def get_config(self, pkg_name: str, python_version: str) -> dict[str, str | None]:
        r"""Get the package version configuration for a package and
        Python version.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            python_version: The Python version (e.g., ``"3.11"``).

        Returns:
            A dictionary with ``"min"`` and ``"max"`` keys, or an empty
            dictionary if no configuration exists.
        """
        if pkg_name not in self.registry:
            return {}
        return self.registry[pkg_name].get(python_version, {})

    def get_min_and_max_versions(
        self, pkg_name: str, python_version: str
    ) -> tuple[Version | None, Version | None]:
        r"""Get the minimum and maximum versions as ``Version``
        objects.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            python_version: The Python version (e.g., ``"3.11"``).

        Returns:
            A tuple ``(min_version, max_version)``, either value being
            ``None`` if unconstrained or unconfigured.
        """
        config = self.get_config(pkg_name=pkg_name, python_version=python_version)
        min_version = config.get("min", None)
        max_version = config.get("max", None)
        if min_version is not None:
            min_version = Version(min_version)
        if max_version is not None:
            max_version = Version(max_version)
        return min_version, max_version

    def find_closest_version(self, pkg_name: str, pkg_version: str, python_version: str) -> str:
        r"""Find the closest valid version for a package.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The requested package version.
            python_version: The Python version (e.g., ``"3.11"``).

        Returns:
            The closest valid version as a string.
        """
        version = Version(pkg_version)
        min_version, max_version = self.get_min_and_max_versions(
            pkg_name=pkg_name, python_version=python_version
        )
        if min_version is not None and version < min_version:
            return min_version.base_version
        if max_version is not None and version > max_version:
            return max_version.base_version
        return pkg_version

    def is_valid_version(self, pkg_name: str, pkg_version: str, python_version: str) -> bool:
        r"""Check if a package version is valid for a Python version.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The package version to validate.
            python_version: The Python version (e.g., ``"3.11"``).

        Returns:
            ``True`` if valid or unconfigured, ``False`` otherwise.
        """
        version = Version(pkg_version)
        min_version, max_version = self.get_min_and_max_versions(
            pkg_name=pkg_name, python_version=python_version
        )
        return (min_version is None or min_version <= version) and (
            max_version is None or version <= max_version
        )
```

Note: remove the stray `ClassVar` import if unused — the class no longer uses class-level state, so drop `from typing import ClassVar` from the final file.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/thibaut/workspace/code/feu && python -m pytest tests/unit/compat/test_registry.py -v`
Expected: PASS (all tests green)

- [ ] **Step 5: Commit**

Do not commit — the user will review and commit changes themselves. Leave the working tree as-is and move to the next task.

---

### Task 2: `defaults.py` with built-in constraints

**Files:**
- Create: `src/feu/compat/defaults.py`
- Test: `tests/unit/compat/test_defaults.py`

**Interfaces:**
- Consumes: `CompatRegistry` (Task 1) — specifically `CompatRegistry.register_many(mapping, exist_ok=False)`.
- Produces: `DEFAULT_COMPAT: dict[str, dict[str, dict[str, str | None]]]` (module-level constant, the constraints table copied verbatim from the old `PackageConfig.registry`) and `register_defaults(registry: CompatRegistry) -> None`. Task 3's `get_default_registry()` calls `register_defaults`.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/compat/test_defaults.py`:

```python
from __future__ import annotations

from feu.compat.defaults import DEFAULT_COMPAT, register_defaults
from feu.compat.registry import CompatRegistry

#############################################
#     Tests for register_defaults           #
#############################################


def test_register_defaults_populates_registry() -> None:
    registry = CompatRegistry()
    register_defaults(registry)
    assert registry.registry == DEFAULT_COMPAT


def test_register_defaults_numpy_entry() -> None:
    registry = CompatRegistry()
    register_defaults(registry)
    assert registry.get_config(pkg_name="numpy", python_version="3.11") == {
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

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/thibaut/workspace/code/feu && python -m pytest tests/unit/compat/test_defaults.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'feu.compat.defaults'`

- [ ] **Step 3: Implement `defaults.py`**

Create `src/feu/compat/defaults.py` by copying the `PackageConfig.registry` dict body verbatim from `src/feu/package.py` (lines 74-202) into a module-level constant, plus a small registration helper:

```python
r"""Contain the default package version compatibility constraints."""

from __future__ import annotations

__all__ = ["DEFAULT_COMPAT", "register_defaults"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feu.compat.registry import CompatRegistry

DEFAULT_COMPAT: dict[str, dict[str, dict[str, str | None]]] = {
    # https://click.palletsprojects.com/en/stable/changes/
    "click": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": None, "max": None},
        "3.13": {"min": None, "max": None},
        "3.12": {"min": None, "max": None},
        "3.11": {"min": None, "max": None},
        "3.10": {"min": None, "max": None},
        "3.9": {"min": None, "max": "8.1.8"},
    },
    # https://github.com/duckdb/duckdb-python/releases
    "duckdb": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "1.4.2", "max": None},
        "3.13": {"min": None, "max": None},
        "3.12": {"min": None, "max": None},
        "3.11": {"min": None, "max": None},
        "3.10": {"min": None, "max": None},
    },
    # https://pypi.org/project/jaxlib/#history
    "jax": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "0.7.1", "max": None},
        "3.13": {"min": "0.4.34", "max": None},
        "3.12": {"min": "0.4.17", "max": None},
        "3.11": {"min": "0.4.6", "max": None},
        "3.10": {"min": "0.4.6", "max": "0.6.2"},
        "3.9": {"min": "0.4.6", "max": "0.4.30"},
    },
    # https://matplotlib.org/stable/users/release_notes.html
    "matplotlib": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "3.10.5", "max": None},
        "3.13": {"min": None, "max": None},
        "3.12": {"min": None, "max": None},
        "3.11": {"min": None, "max": None},
        "3.10": {"min": None, "max": None},
        "3.9": {"min": None, "max": "3.9.4"},
    },
    # https://numpy.org/devdocs/release.html
    "numpy": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "2.3.0", "max": None},
        "3.13": {"min": "2.1.0", "max": None},
        "3.12": {"min": "1.26.0", "max": None},
        "3.11": {"min": "1.23.2", "max": "2.4.6"},
        "3.10": {"min": "1.21.3", "max": "2.2.6"},
        "3.9": {"min": "1.19.3", "max": "2.0.2"},
    },
    # https://github.com/pandas-dev/pandas/releases
    # https://pandas.pydata.org/docs/whatsnew/index.html
    "pandas": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "2.3.3", "max": None},
        "3.13": {"min": "2.2.3", "max": None},
        "3.12": {"min": "2.1.1", "max": None},
        "3.11": {"min": "1.3.4", "max": None},
        "3.10": {"min": "1.3.3", "max": "2.3.3"},
        "3.9": {"min": None, "max": "2.3.3"},
    },
    # https://arrow.apache.org/release/
    "pyarrow": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "22.0.0", "max": None},
        "3.13": {"min": "18.0.0", "max": None},
        "3.12": {"min": "14.0.0", "max": None},
        "3.11": {"min": "10.0.1", "max": None},
        "3.10": {"min": "6.0.0", "max": None},
        "3.9": {"min": "3.0.0", "max": "16.1.0"},
    },
    "pydantic": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "2.12.0", "max": None},
        "3.13": {"min": "2.8.0", "max": None},
        "3.12": {"min": None, "max": None},
        "3.11": {"min": None, "max": None},
        "3.10": {"min": None, "max": None},
    },
    "requests": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": None, "max": None},
        "3.13": {"min": None, "max": None},
        "3.12": {"min": None, "max": None},
        "3.11": {"min": None, "max": None},
        "3.10": {"min": None, "max": None},
        "3.9": {"min": None, "max": None},
    },
    # https://github.com/scikit-learn/scikit-learn/releases
    "scikit-learn": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "1.7.2", "max": None},
        "3.13": {"min": "1.6.0", "max": None},
        "3.12": {"min": "1.3.1", "max": None},
        "3.11": {"min": "1.2.0", "max": None},
        "3.10": {"min": "1.1.0", "max": "1.7.2"},
        "3.9": {"min": None, "max": "1.6.1"},
    },
    # https://github.com/scipy/scipy/releases/
    "scipy": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "1.16.1", "max": None},
        "3.13": {"min": "1.14.1", "max": None},
        "3.12": {"min": "1.12.0", "max": None},
        "3.11": {"min": "1.10.0", "max": "1.17.1"},
        "3.10": {"min": "1.8.0", "max": "1.15.3"},
        "3.9": {"min": None, "max": "1.13.1"},
    },
    # https://github.com/pytorch/pytorch/releases
    "torch": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": "2.9.0", "max": None},
        "3.13": {"min": "2.6.0", "max": None},
        "3.12": {"min": "2.4.0", "max": None},
        "3.11": {"min": "2.0.0", "max": None},
        "3.10": {"min": "1.11.0", "max": None},
        "3.9": {"min": None, "max": "2.8.0"},
    },
    # https://docs.xarray.dev/en/stable/whats-new.html
    "xarray": {
        "3.15": {"min": None, "max": None},
        "3.14": {"min": None, "max": None},
        "3.13": {"min": None, "max": None},
        "3.12": {"min": None, "max": None},
        "3.11": {"min": None, "max": None},
        "3.10": {"min": None, "max": "2025.6.1"},
        "3.9": {"min": None, "max": "2024.7.0"},
    },
}


def register_defaults(registry: CompatRegistry) -> None:
    r"""Populate a registry with the default package compatibility
    constraints.

    Args:
        registry: The registry to populate.
    """
    registry.register_many(DEFAULT_COMPAT)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/thibaut/workspace/code/feu && python -m pytest tests/unit/compat/test_defaults.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

Do not commit — the user will review and commit changes themselves. Leave the working tree as-is and move to the next task.

---

### Task 3: `interface.py` — default singleton and convenience functions

**Files:**
- Create: `src/feu/compat/interface.py`
- Modify: `src/feu/compat/__init__.py`
- Test: `tests/unit/compat/test_interface.py`

**Interfaces:**
- Consumes: `CompatRegistry` (Task 1: `CompatRegistry()`, `.register_many`, `.find_closest_version`, `.is_valid_version`); `register_defaults` (Task 2: `register_defaults(registry: CompatRegistry) -> None`).
- Produces: `get_default_registry() -> CompatRegistry`, `register_compat(mapping: dict[str, dict[str, dict[str, str | None]]], exist_ok: bool = False) -> None`, `find_closest_version(pkg_name: str, pkg_version: str, python_version: str) -> str`, `is_valid_version(pkg_name: str, pkg_version: str, python_version: str) -> bool`. Task 5 (`feu/install/utils.py`) and Task 6 (`feu/__main__.py`) import `find_closest_version` and `is_valid_version` from `feu.compat`.

- [ ] **Step 1: Write the failing tests**

Create `tests/unit/compat/test_interface.py`:

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
from feu.compat.registry import CompatRegistry

######################################
#     Tests for get_default_registry #
######################################


@pytest.fixture(autouse=True)
def _reset_default_registry() -> None:
    # Ensure each test starts from a fresh singleton.
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
    assert registry.get_config(pkg_name="numpy", python_version="3.11") == {
        "min": "1.23.2",
        "max": "2.4.6",
    }


#################################
#     Tests for register_compat #
#################################


def test_register_compat_adds_to_default_registry() -> None:
    register_compat({"my_package": {"3.11": {"min": "1.0.0", "max": None}}})
    assert get_default_registry().get_config(
        pkg_name="my_package", python_version="3.11"
    ) == {"min": "1.0.0", "max": None}


def test_register_compat_exist_ok_false_raises() -> None:
    register_compat({"my_package": {"3.11": {"min": "1.0.0", "max": None}}})
    with pytest.raises(RuntimeError, match=r"A package configuration .* is already registered"):
        register_compat({"my_package": {"3.11": {"min": "2.0.0", "max": None}}})


########################################
#     Tests for find_closest_version   #
########################################


def test_find_closest_version_delegates_to_default_registry() -> None:
    with patch.object(
        CompatRegistry, "find_closest_version", return_value="1.2.3"
    ) as mock_find:
        result = find_closest_version(
            pkg_name="numpy", pkg_version="2.0.2", python_version="3.11"
        )
    assert result == "1.2.3"
    mock_find.assert_called_once_with(
        pkg_name="numpy", pkg_version="2.0.2", python_version="3.11"
    )


def test_find_closest_version_uses_defaults() -> None:
    assert (
        find_closest_version(pkg_name="numpy", pkg_version="0.1.0", python_version="3.11")
        == "1.23.2"
    )


##################################
#     Tests for is_valid_version #
##################################


def test_is_valid_version_delegates_to_default_registry() -> None:
    with patch.object(CompatRegistry, "is_valid_version", return_value=False) as mock_valid:
        result = is_valid_version(pkg_name="numpy", pkg_version="2.0.2", python_version="3.11")
    assert result is False
    mock_valid.assert_called_once_with(
        pkg_name="numpy", pkg_version="2.0.2", python_version="3.11"
    )


def test_is_valid_version_uses_defaults() -> None:
    assert not is_valid_version(pkg_name="numpy", pkg_version="0.1.0", python_version="3.11")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/thibaut/workspace/code/feu && python -m pytest tests/unit/compat/test_interface.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'feu.compat.interface'`

- [ ] **Step 3: Implement `interface.py`**

Create `src/feu/compat/interface.py`:

```python
r"""Define the public interface for package/Python-version
compatibility resolution."""

from __future__ import annotations

__all__ = [
    "find_closest_version",
    "get_default_registry",
    "is_valid_version",
    "register_compat",
]

from feu.compat.defaults import register_defaults
from feu.compat.registry import CompatRegistry


def get_default_registry() -> CompatRegistry:
    r"""Return the default global compatibility registry.

    The registry is created on the first call and reused on all
    subsequent calls (singleton pattern). It is pre-configured with
    the default package version constraints.

    Returns:
        A singleton ``CompatRegistry`` configured with the default
        package version constraints.

    Example:
        ```pycon
        >>> from feu.compat import get_default_registry
        >>> registry = get_default_registry()
        >>> registry.is_valid_version("numpy", "2.0.2", "3.11")
        True

        ```
    """
    if not hasattr(get_default_registry, "_registry"):
        registry = CompatRegistry()
        register_defaults(registry)
        get_default_registry._registry = registry
    return get_default_registry._registry


def register_compat(
    mapping: dict[str, dict[str, dict[str, str | None]]],
    exist_ok: bool = False,
) -> None:
    r"""Register custom package configurations into the default global
    registry.

    Args:
        mapping: Mapping of package name to Python version to
            ``{"min": ..., "max": ...}`` constraints.
        exist_ok: If ``False`` (default), raises an error if any entry
            is already registered. If ``True``, overwrites existing
            registrations silently.

    Raises:
        RuntimeError: If any entry is already registered and
            ``exist_ok`` is ``False``.

    Example:
        ```pycon
        >>> from feu.compat import register_compat
        >>> register_compat({"my_package": {"3.11": {"min": "1.0.0", "max": None}}})

        ```
    """
    get_default_registry().register_many(mapping, exist_ok=exist_ok)


def find_closest_version(pkg_name: str, pkg_version: str, python_version: str) -> str:
    r"""Find the closest valid version for a package using the default
    registry.

    Args:
        pkg_name: The package name to check (e.g., ``"numpy"``).
        pkg_version: The requested package version.
        python_version: The Python version (e.g., ``"3.11"``).

    Returns:
        The closest valid version as a string.

    Example:
        ```pycon
        >>> from feu.compat import find_closest_version
        >>> find_closest_version(pkg_name="numpy", pkg_version="2.0.2", python_version="3.11")
        '2.0.2'

        ```
    """
    return get_default_registry().find_closest_version(
        pkg_name=pkg_name, pkg_version=pkg_version, python_version=python_version
    )


def is_valid_version(pkg_name: str, pkg_version: str, python_version: str) -> bool:
    r"""Check if a package version is valid for a Python version using
    the default registry.

    Args:
        pkg_name: The package name to check (e.g., ``"numpy"``).
        pkg_version: The package version to validate.
        python_version: The Python version (e.g., ``"3.11"``).

    Returns:
        ``True`` if valid or unconfigured, ``False`` otherwise.

    Example:
        ```pycon
        >>> from feu.compat import is_valid_version
        >>> is_valid_version(pkg_name="numpy", pkg_version="2.0.2", python_version="3.11")
        True

        ```
    """
    return get_default_registry().is_valid_version(
        pkg_name=pkg_name, pkg_version=pkg_version, python_version=python_version
    )
```

Update `src/feu/compat/__init__.py` to export the full public surface:

```python
r"""Contain a registry-based system for package/Python-version
compatibility resolution."""

from __future__ import annotations

__all__ = [
    "CompatRegistry",
    "find_closest_version",
    "get_default_registry",
    "is_valid_version",
    "register_compat",
]

from feu.compat.interface import (
    find_closest_version,
    get_default_registry,
    is_valid_version,
    register_compat,
)
from feu.compat.registry import CompatRegistry
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/thibaut/workspace/code/feu && python -m pytest tests/unit/compat/ -v`
Expected: PASS (all tests in `tests/unit/compat/` green)

- [ ] **Step 5: Commit**

Do not commit — the user will review and commit changes themselves. Leave the working tree as-is and move to the next task.

---

### Task 4: Delete `feu.package` and its tests

**Files:**
- Delete: `src/feu/package.py`
- Delete: `tests/unit/test_package.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: nothing new — this task removes the old module now that Tasks 1-3 provide equivalent functionality under `feu.compat`. Tasks 5 and 6 depend on this deletion being safe (i.e., all imports moved first — see order note below).

**Note on ordering:** Do this task *after* Tasks 5 and 6 update the remaining import sites, so the tree never has a moment where `feu/install/utils.py` or `feu/__main__.py` import a deleted module. Run Task 5 and Task 6 first, then come back and do this deletion last, or interleave: update imports (Tasks 5/6 Step 1), then delete (this task), then verify (Tasks 5/6 remaining steps). The step list below assumes Tasks 5 and 6 have already been completed.

- [ ] **Step 1: Delete the old module and test file**

Run: `cd /Users/thibaut/workspace/code/feu && rm src/feu/package.py tests/unit/test_package.py`

- [ ] **Step 2: Search for any remaining references**

Run: `cd /Users/thibaut/workspace/code/feu && grep -rn "feu\.package\b\|PackageConfig" src tests docs || echo "no matches"`
Expected: `no matches` (Task 7 handles the remaining `docs/docs/usage.md` reference — if this search finds it, that's expected until Task 7 runs; confirm it's *only* `docs/docs/usage.md`).

- [ ] **Step 3: Run the full test suite**

Run: `cd /Users/thibaut/workspace/code/feu && python -m pytest tests/unit -v`
Expected: PASS, no `ModuleNotFoundError` for `feu.package`

- [ ] **Step 4: Commit**

Do not commit — the user will review and commit changes themselves. Leave the working tree as-is and move to the next task.

---

### Task 5: Update `feu/install/utils.py`

**Files:**
- Modify: `src/feu/install/utils.py:18`
- Test: `tests/unit/install/test_utils.py` (verify existing tests still pass; no new tests needed since behavior is unchanged)

**Interfaces:**
- Consumes: `feu.compat.find_closest_version(pkg_name: str, pkg_version: str, python_version: str) -> str` (Task 3).
- Produces: nothing new — this task is a pure import-path update.

- [ ] **Step 1: Update the import**

In `src/feu/install/utils.py`, change:

```python
from feu.package import find_closest_version
```

to:

```python
from feu.compat import find_closest_version
```

- [ ] **Step 2: Run the existing tests for this module**

Run: `cd /Users/thibaut/workspace/code/feu && python -m pytest tests/unit/install/test_utils.py -v`
Expected: PASS (no behavior change, only import path)

- [ ] **Step 3: Commit**

Do not commit — the user will review and commit changes themselves. Leave the working tree as-is and move to the next task.

---

### Task 6: Update `feu/__main__.py`

**Files:**
- Modify: `src/feu/__main__.py:7-8`
- Test: `tests/unit/test_main.py` if it exists (verify existing CLI tests still pass; check for the file first)

**Interfaces:**
- Consumes: `feu.compat.find_closest_version(pkg_name: str, pkg_version: str, python_version: str) -> str` and `feu.compat.is_valid_version(pkg_name: str, pkg_version: str, python_version: str) -> bool` (Task 3).
- Produces: nothing new — pure import-path update.

- [ ] **Step 1: Check for an existing CLI test file**

Run: `cd /Users/thibaut/workspace/code/feu && find tests -iname "*main*"`

- [ ] **Step 2: Update the imports**

In `src/feu/__main__.py`, change:

```python
from feu.package import find_closest_version as find_closest_version_
from feu.package import is_valid_version
```

to:

```python
from feu.compat import find_closest_version as find_closest_version_
from feu.compat import is_valid_version
```

- [ ] **Step 3: Run the CLI tests (if a test file was found in Step 1) and the full suite**

Run: `cd /Users/thibaut/workspace/code/feu && python -m pytest tests/unit -v`
Expected: PASS

- [ ] **Step 4: Manually smoke-test the CLI entry points**

Run: `cd /Users/thibaut/workspace/code/feu && python -m feu find-closest-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10`
Expected: prints a version string (e.g. `2.0.2` or the closest constrained version), no traceback

Run: `cd /Users/thibaut/workspace/code/feu && python -m feu check-valid-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10`
Expected: prints `True` or `False`, no traceback

- [ ] **Step 5: Commit**

Do not commit — the user will review and commit changes themselves. Leave the working tree as-is and move to the next task.

---

### Task 7: Update documentation

**Files:**
- Modify: `docs/docs/usage.md:97-122`

**Interfaces:**
- Consumes: `feu.compat.get_default_registry() -> CompatRegistry` (Task 3), `CompatRegistry.register` and `.get_config`/`.get_min_and_max_versions` (Task 1).
- Produces: nothing new — documentation-only change.

- [ ] **Step 1: Replace the `PackageConfig` example**

In `docs/docs/usage.md`, replace the "Managing Package Configurations" section (currently lines 97-122):

```markdown
## Managing Package Configurations

Add custom package configurations to the registry:

```python
from feu.package import PackageConfig

# Add a custom package configuration
PackageConfig.add_config(
    pkg_name="my_package",
    python_version="3.11",
    pkg_version_min="1.2.0",
    pkg_version_max="2.0.0",
    exist_ok=True,
)

# Get the configuration for a package
config = PackageConfig.get_config(pkg_name="my_package", python_version="3.11")
print(config)  # {'min': '1.2.0', 'max': '2.0.0'}

# Get min and max versions
min_version, max_version = PackageConfig.get_min_and_max_versions(
    pkg_name="numpy", python_version="3.11"
)
print(f"Min: {min_version}, Max: {max_version}")
```
```

with:

```markdown
## Managing Package Configurations

Add custom package configurations to the default compatibility registry:

```python
from feu.compat import get_default_registry

registry = get_default_registry()

# Add a custom package configuration
registry.register(
    pkg_name="my_package",
    python_version="3.11",
    pkg_version_min="1.2.0",
    pkg_version_max="2.0.0",
    exist_ok=True,
)

# Get the configuration for a package
config = registry.get_config(pkg_name="my_package", python_version="3.11")
print(config)  # {'min': '1.2.0', 'max': '2.0.0'}

# Get min and max versions
min_version, max_version = registry.get_min_and_max_versions(
    pkg_name="numpy", python_version="3.11"
)
print(f"Min: {min_version}, Max: {max_version}")
```
```

- [ ] **Step 2: Verify no remaining references to the old API**

Run: `cd /Users/thibaut/workspace/code/feu && grep -rn "feu\.package\b\|PackageConfig" src tests docs || echo "no matches"`
Expected: `no matches`

- [ ] **Step 3: Commit**

Do not commit — the user will review and commit changes themselves. Leave the working tree as-is. This is the final task in the plan.

---

## Final Verification

- [ ] **Run the full test suite with coverage**

Run: `cd /Users/thibaut/workspace/code/feu && python -m pytest tests/unit --cov=feu --cov-report=term-missing`
Expected: PASS, `src/feu/compat/` modules show high coverage, no reference to `src/feu/package.py` remains in the coverage report.

- [ ] **Run linters if configured**

Run: `cd /Users/thibaut/workspace/code/feu && python -m ruff check src/feu/compat tests/unit/compat src/feu/install/utils.py src/feu/__main__.py` (adjust to whatever linter/config this repo uses — check `pyproject.toml` for the configured tool if `ruff` is not it).
Expected: no errors.
