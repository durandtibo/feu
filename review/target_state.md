# `feu`: target state and the changes to reach it

This document describes the design `feu` should have, then the changes to make to the current
implementation (`main`, `9e473b2`) to get there. The aim is a small package that is easy to
maintain: **one registry type, one HTTP path, one wheel-tag parser, one discovery algorithm, one
data format, argv lists instead of command strings**. Breaking changes are accepted (`feu` is
`0.x` and says so in `docs/docs/index.md`), and the future state is more important than the past
one. The part of the past that is kept is the part other repositories depend on (section 5).

Two requirements were added after the first version of this document: **(a)** optional dependencies
are managed like `coola` does it (`coola.utils.imports`: `availability_cache`, `package_available`,
`module_available`, `check_package`, `MissingPackageError`, `lazy_exports`), instead of a design of
our own (3.2); **(b)** a version can be given as an exact version, a **wildcard** (`1.*`) or an
**empty string**, for installing and for validating (issue
[#1032](https://github.com/durandtibo/feu/issues/1032), 3.9).

The documentation of `feu` has no "Properties" section (searched `README.md`, `docs/`,
`CONTRIBUTING.md`, `CLAUDE.md`). The properties of section 1 are therefore **derived** from what
the README, the user guide and `CLAUDE.md` promise, and from the findings of section 2. Each one
says where it comes from.

Evidence comes from probes run on `main` (Python 3.14.10, `.venv`) and from reading the code. Items
are marked **[verified]** (reproduced by running code or a command), **[reading]** (from the code
only) or **[downstream]** (from a search of the other repositories of the owner). Nothing in `src`,
`tests` or `docs` was changed. `review/suggestions.md` (written at `54c6bf7`) was used as a
starting point; every item that this document relies on was checked again on `9e473b2`.

## 1. Properties of the package

These are the rules the package must satisfy. Every design choice below exists to make one of them
true **by construction** (in one place) instead of by the discipline of each function.

| #   | Property                                  | Statement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Enforced by                                                                                                            | Comes from                                         |
| --- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| 1   | **Lightweight**                           | The only required dependency is `packaging`. `import feu`, `import feu.compat` and `import feu.install` import no optional library, read no file other than code, and do no network call.                                                                                                                                                                                                                                                                                                                      | `lazy_exports` in `feu/__init__.py`; imports of optional libraries inside the function that needs them; an import test | README, `CLAUDE.md`                                |
| 2   | **Explicit optional dependencies**        | Optional dependencies are managed by the design of `coola.utils.imports`, not by a design of our own. A feature that needs an extra calls `check_<package>()` first. A missing package raises `MissingPackageError` (a `ModuleNotFoundError` and a `RuntimeError`) whose message gives the `pip`/`uv pip` command. It never fails later on a stand-in module.                                                                                                                                                  | `feu.imports` (a port of `coola.utils.imports`); no fallback modules                                                   | `CLAUDE.md`, user guide, maintainer request        |
| 3   | **Target-aware**                          | A compatibility answer is a function of `(package, version, Target)`, where a `Target` is `(python_version, free_threaded, os, arch)`. Code that acts on the current environment always uses the **full** current target.                                                                                                                                                                                                                                                                                      | `resolve_target()` is the only way the current environment enters; `install_package_closest_version` calls it          | README ("Target-aware")                            |
| 4   | **No silent no-op**                       | Every field of the target is used or the call fails. A field left to `None` has one documented meaning ("any platform"), not "ignored". An unknown package has one documented answer (permissive) and can be detected (`registry.has_package`).                                                                                                                                                                                                                                                                | `CompatRegistry` matching rule; a test on the shipped data                                                             | finding F1                                         |
| 5   | **Data-driven and reproducible**          | The built-in constraints are generated from the wheels published on PyPI by one command. The output is deterministic (sorted, same bytes for the same input) and dated. No constraint is written by hand.                                                                                                                                                                                                                                                                                                      | `dev/generate_compat_data.py`; a data-contract test; the weekly bot                                                    | README ("PyPI-backed discovery")                   |
| 6   | **Extensible by registration**            | A package constraint, an installer or a dependency resolver is added by registering **one value** in a registry **instance**. No subclassing is needed to add data. No registry is process-global class state.                                                                                                                                                                                                                                                                                                 | `Registry[T]`; `get_default_*_registry()` returns an instance; every entry point takes an optional `registry=`         | README ("Extensible"), user guide                  |
| 7   | **Standards compliant**                   | Package names are canonicalised once, at the boundary (PEP 503). Versions are `packaging.version.Version` (PEP 440), requirements `packaging.requirements.Requirement` (PEP 508), wheel names are parsed by `packaging`. A function that returns a version returns the input.                                                                                                                                                                                                                                  | `packaging.utils.canonicalize_name` in the registries; no hand-written parser of a standard                            | findings F3, F4, F5                                |
| 8   | **No shell, no string-built command**     | An external command is an argv list. `pip` runs as `sys.executable -m pip`, so it installs into the interpreter that runs `feu` (the one the compatibility check used). The command is logged before it runs.                                                                                                                                                                                                                                                                                                  | `feu.utils.command.run_command(argv)`; installers return `list[str]`                                                   | finding F7                                         |
| 9   | **Fresh and immutable**                   | Availability checks are cached with `availability_cache` (as in `coola`) and the caches are reset by `clear_availability_caches()`, which `install_package` calls after a successful installation and tests call when they change `sys.path`. The PyPI fetches are cached per canonical name and return immutable values, so no caller can corrupt a cache.                                                                                                                                                    | `availability_cache` registers every cached check; frozen dataclasses and `MappingProxyType` on cached values          | finding F12, F13                                   |
| 10  | **Deterministic order**                   | Versions are ordered by PEP 440 everywhere (never as strings). A mapping that is returned or written is sorted by key. The generated data has no timestamp inside the data (only a date field) and is stable across runs.                                                                                                                                                                                                                                                                                      | `sort_versions`; the generator sorts; a golden test                                                                    | finding F12                                        |
| 11  | **A thin CLI**                            | The CLI is the same API behind click. Stdout holds only the answer (it is used in `$(...)`), logs go to stderr, and the exit status carries the result (`0` ok, `1` negative answer, `2` usage error).                                                                                                                                                                                                                                                                                                         | `feu/cli.py` only parses and prints; tests with `CliRunner` and a subprocess                                           | findings F14, F16 ([downstream] action)            |
| 12  | **Strict, typed, documented**             | Options are keyword-only (booleans always). Invalid input raises `ValueError`/`TypeError` with an explicit message. Every public function has a doctest. Every patched behaviour has an integration test without the patch.                                                                                                                                                                                                                                                                                    | `FBT` ruff rules; `ty`; `CLAUDE.md` test rules                                                                         | `CLAUDE.md`                                        |
| 13  | **Layered**                               | The imports go one way: `imports`, then `utils`, `version`, `compat`, `install`, `cli`. `imports` imports nothing from `feu`. I/O is confined to `utils/http.py`, `utils/command.py`, `local_git.py` and the few functions that call them (`version/pypi.py`, `version/package.py`, `install`).                                                                                                                                                                                                                | an import-graph test                                                                                                   | derived                                            |
| 14  | **Cross-platform, Python 3.11 and newer** | Linux, macOS and Windows behave the same (no `shlex` rule that depends on `os.name`, no `PATH` lookup of `pip`). Python 3.11+.                                                                                                                                                                                                                                                                                                                                                                                 | argv lists; CI matrix                                                                                                  | `pyproject.toml`, README                           |
| 15  | **A version is a request**                | Wherever a function takes the version of a package to install or to validate, it accepts three forms: an exact version (`2.4.0`), a release-prefix wildcard (`2.4.*`, `2.*`) and an empty string or `None` (the latest). A request is resolved to the latest compatible version. A request with no compatible version gives an explicit answer (`False`, `UnsupportedVersionError`), never a crash; a malformed request raises `ValueError`. Install and validate use the same parser and the same resolution. | `feu.version.request.parse_version_request`; `CompatRegistry.find_closest_version` / `is_valid_version`                | issue #1032, README ("version-aware installation") |

Properties 1, 2, 3, 6, 12 and 14 are promises that exist today. Properties 4, 5, 7 to 11, 13 and 15
are new rules. Today the package breaks properties 1, 3, 4, 6, 7, 8, 9, 11, 14 and 15 (section 2).

## 2. What differs today

| #   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Evidence                        | Property |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------- | -------- |
| F1  | **The headline feature is a no-op without `os` and `arch`.** All 1,020 shipped targets have a concrete `os` and `arch`; `CompatRegistry._matches` needs equality, so `Target(python_version="3.9")` matches nothing, the package counts as "unconfigured" and the input is returned. `find_closest_version("numpy", "2.3.0", Target("3.9"))` returns `'2.3.0'`; with `os="linux", arch="x86_64"` it returns `'2.0.2'`. `install_package_closest_version` builds exactly such a target, and **every example of the README and of `usage.md` does too**: the documented `# Will return "1.23.2"` example returns `'1.0.0'`. Only the CLI (which calls `resolve_target`) is correct.                                                                                                                                                                                                                                                                                                                            | **[verified]**                  | 3, 4     |
| F2  | **Wheel tags are dropped.** `parse_wheel_filename` returns `[]` for `macosx_11_0_universal2`, for `cp39-abi3-macosx_10_9_universal2` (a very common wheel), for `musllinux_*`; it keeps only the first platform of a compressed tag (`macosx_10_9_x86_64.macosx_11_0_arm64` gives only `x86_64`); `abi3t` (the free-threaded stable ABI) is parsed as an exact-version tag with `abi3=False`; `free_threaded` is `abi_tag.endswith("t")`. The shipped data is generated by this parser.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | **[verified]**                  | 5, 7     |
| F3  | **Package names are normalised three ways.** The registries, the resolver registry and `fetch_pypi_*` use the name verbatim; `normalize_package_name` lowercases and replaces `-` (`zope.interface` stays, `a--b` becomes `a__b`, PEP 503 gives `a-b`); the resolver table has a `sklearn` key (a module name, not the project name). With a full target, `is_valid_version("scikit-learn", "0.1", ...)` is `False` but `"Scikit-Learn"` and `"scikit_learn"` are `True` (no data found, no check); `find_resolver(PackageSpec("Scikit-Learn"))` returns the default resolver.                                                                                                                                                                                                                                                                                                                                                                                                                               | **[verified]**                  | 7        |
| F4  | **Version helpers return a different string.** `latest_version(["1.0-1", "1.0"])` returns `'1.0.post1'`, which is not in the input and is not a PyPI release key.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | **[verified]**                  | 7        |
| F5  | **`include_lower_bound` contradicts its docstring.** `fetch_latest_major_versions` and `fetch_latest_minor_versions` test `include_lower_bound and versions` (no `lower is not None`), `fetch_sampled_latest_minor_versions` tests it; the two `_map` functions are copies. Six functions, one idea.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | **[reading]**                   | 7, 12    |
| F6  | **A documented example does not run.** `usage.md` shows `compare_version("2.0.0", "1.5.0")` returning `1`; the function is `compare_version(package, op, version)` and raises `TypeError`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | **[verified]**                  | 12       |
| F7  | **Commands are strings and use `pip` from `PATH`.** Installers join `["pip", "install", args, *deps]` with spaces and `run_bash_command` re-splits with `shlex` (POSIX rules on Linux/macOS, non-POSIX on Windows, so the same `--installer-args` means two things). `pip` on `PATH` can be another interpreter than the one that ran the compatibility check. The function is called `run_bash_command` and never uses a shell. `PipxInstaller` installs an _application_ into an isolated environment: "install `numpy==2.0.2` with pipx" is not an environment install.                                                                                                                                                                                                                                                                                                                                                                                                                                   | **[reading]**                   | 8, 14    |
| F8  | **`import feu` is not light.** 117 ms cumulative (`-X importtime`): `feu.compat` 70 ms (it imports the discovery code and the version fetchers), `requests` 43 ms. After `import feu`, `requests`, `urllib3` and `rich` are in `sys.modules` (`feu.compat.matrix` imports `rich` at module level, against `CLAUDE.md`). The first lookup builds the registry from 17 Python modules: 0.10 s.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | **[verified]**                  | 1, 2     |
| F9  | **The shipped data is 3,500 lines of generated Python** (172 KB, 17 modules plus `__init__`), imported whole to answer a question about one package. The list of packages is hard-coded in `compat/packages.py`, the generator reads it, the registry finds the modules with `pkgutil`: a new package needs edits in several places. Of the 1,020 targets, only 361 are distinct per `(package, python, free_threaded)` (the platforms mostly agree). The generator writes `repr(dict)` and relies on the pre-commit formatter.                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | **[verified]**/**[reading]**    | 5, 10    |
| F10 | **Four registries, four implementations.** `InstallerRegistry` and `DependencyResolverRegistry` are class-level global state (`ClassVar[dict]`, classmethods); `CompatRegistry` and `CompatDiscovererRegistry` are instances. Each re-implements `register`, `register_many`, `has_*`, `find_*` and the "already registered" error. There are two functions named `get_default_registry` (`feu.compat` and `feu.compat.discoverers`). `add_resolver`/`has_resolver` take a whole `PackageSpec` to read `.name`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | **[reading]**                   | 6        |
| F11 | **Discovery is 1,122 lines for one algorithm.** `CompatDiscoverer`, `DuckdbCompatDiscoverer`, `JaxCompatDiscoverer`, `PolarsCompatDiscoverer`, `PydanticCompatDiscoverer`, a base class, a registry and `utils.py`. They differ by data: a version to ignore (`duckdb 0.0.0`), a _companion_ package whose wheels carry the platform tags (`jaxlib` at the same version; `polars-runtime-32` and `pydantic-core` at the pinned version). There are two near-identical matchers (`_is_tag_compatible` in `default.py`, `tags_match_exactly` in `utils.py`) and `polars.py` and `pydantic.py` are the same file with two constants.                                                                                                                                                                                                                                                                                                                                                                            | **[reading]**                   | 5        |
| F12 | **PyPI access.** `fetch_pypi_versions`, `fetch_pypi_requires_python` and `fetch_pypi_wheel_filenames` download the same JSON document three times. All use the `releases` key, which the PyPI documentation lists as **deprecated** ("use the Index API"). The Simple API in JSON form (PEP 691 and 700) returns the version list, the file names, `requires-python`, `yanked` and `upload-time` in one request, and is smaller (numpy: 2.8 MB against 3.7 MB). `fetch_pypi_versions` returns versions sorted **as strings** (`"1.10" < "1.9"`). Cached functions return mutable `dict`s. The pinned-dependency lookup ignores environment markers. The package name is not quoted in the URL.                                                                                                                                                                                                                                                                                                               | **[verified]**/**[reading]**    | 7, 9, 10 |
| F13 | **Optional imports are five copies of one file** (`imports/{click,git,requests,rich,urllib3}.py`, about 90 lines each), plus a `decorator_package_available` that returns `None` when a package is missing (no consumer in `src`), plus four fallback modules that build fake `click`/`git`/`requests`/`urllib3` objects, plus `TYPE_CHECKING or is_x_available()` blocks in four modules. The checks are cached with `lru_cache` and nothing resets them: after `install_package("numpy")`, `is_package_available("numpy")` can stay `False`, and the tests call `cache_clear()` function by function. `is_module_available` catches only `ImportError`, so a broken install (missing shared library) crashes the caller. `coola` already solved all of this (`availability_cache`, `clear_availability_caches`, `module_available` that logs and returns `False`, `MissingPackageError`, `lazy_exports`). `requests` depends on `urllib3`, so the separate `urllib3` helper and extra entry are redundant. | **[reading]**/**[downstream]**  | 1, 2, 9  |
| F14 | **CLI.** `install` has no way to say which environment it targets and does not need one (it installs into the current interpreter); `--pkg-extras`, `--installer-name` and `--installer-args` are `required=True` **and** have defaults; `--free-threaded` is `type=bool` (`--free-threaded true`); the three commands repeat the same four options; `find-closest-version` prints the literal `None` and exits `0` for an unsupported package; `check-valid-version` always exits `0`; no `--version`; logging is never configured, so the `execute the following command` log is invisible; there is no console script, only `python -m feu`.                                                                                                                                                                                                                                                                                                                                                              | **[reading]**                   | 11       |
| F15 | **Scope.** `feu.github` (251 lines: repository metadata, repository list, a `display_repos_summary` that logs stars and forks) has no consumer in `src`, `dev` or in the repositories of the owner that were searched. `feu.local_git` is used by `iden`. `feu.utils.io` and `feu.utils.mapping` exist for `dev/generate_versions.py`, a script that is **copied in at least ten repositories**. `PackageSpec` and `PackageDependency` overlap; `extract_package_name`/`extract_package_extras` re-implement `Requirement`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | **[downstream]**/**[reading]**  | 13       |
| F16 | **The only external consumer of the CLI parses stdout.** `pip-install-package-action` runs `VERSION=$(python -m feu find-closest-version ...)` and passes `$VERSION` to `install`. An unsupported package makes `VERSION` the string `None`, and `pip install pkg==None` fails later, far from the cause.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | **[downstream]**                | 11       |
| F17 | **Tests hide F1.** 924 unit tests pass in 0.6 s (verified), but 432 lines use `patch`/`monkeypatch`, and the registry tests use hand-built registries with `os=None` entries. No test asks a question of the shipped data. `tests/package_checks.py` (the check of the built wheel) calls neither `find_closest_version` nor the registry, so a missing data file would not be caught.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | **[verified]**/**[reading]**    | 12       |
| F18 | **Smaller items.** `Target` accepts `"3.11\n"` (`re.match` with `$`); `register` creates the per-package dict before checking for a conflict and does not validate ranges (a range with `min > max` fails at lookup); `CompatRegistry.__str__` dumps the whole state; `find_closest_version` returns `Version.base_version` of a boundary instead of the registered string; `get_python_major_minor` and `get_python_version` are the same function; `DEFAULT_PYTHON_VERSIONS` starts at 3.9 while `requires-python` is `>=3.11` and the classifiers omit Windows although Windows is handled; `local_git` raises the same message for "no tag" and "no version tag".                                                                                                                                                                                                                                                                                                                                        | **[reading]**                   | 12, 14   |
| F19 | **A version request is not supported.** `is_valid_version` and `find_closest_version` call `Version(pkg_version)`: `"2.4.*"`, `""` and `None` all raise `InvalidVersion`. `install_package_closest_version` raises `RuntimeError` for `None`, passes `""` to `Version` (`InvalidVersion`), and **skips the compatibility check** for a wildcard, so `numpy==2.*` on Python 3.9 is installed unchecked. `PackageSpec("numpy", "")` prints `numpy` and `PackageSpec("numpy", "2.*")` prints `numpy==2.*`, so the install layer already half-supports requests. The resolvers skip the `numpy<2` pin for any wildcard. Callers work around it: `setup-venv-uv-action` bypasses the check for these cases (issue #1032).                                                                                                                                                                                                                                                                                         | **[verified]**/**[downstream]** | 15       |

What is already right and must not regress: the "most specific entry wins" rule of `CompatRegistry`;
the validation of `Target` (`os`, `arch`); `UnsupportedVersionError` for "no version at all";
`PackageBounds` and `Target` as frozen dataclasses; the doctests; the 100 % coverage; keyword-only
options in most of the API; the lazy import of `git`/`click`/`requests`/`rich` _inside_ the helpers
of `local_git`, `http` and the CLI as a goal (it is the guards that are wrong).

## 3. Architecture

### 3.1 Layout

```
feu/
  __init__.py          lazy re-exports with lazy_exports (PEP 562): 12 names
  __main__.py          python -m feu  ->  feu.cli.main()  (check_click() first)
  cli.py               click group; only parses and prints            (imports click at top)
  testing.py           pytest marks                                    (imports pytest at top)
  imports/             package.py  (port of coola: availability_cache, package_available, module_available,
                                      check_package, raise_package_missing_error, MissingPackageError)
                       optional.py (is_<pkg>_available / check_<pkg>: click, git, requests, rich)
                       lazy.py     (lazy_exports)
  utils/               registry.py  Registry[T]
                       command.py   run_command(argv)
                       http.py      fetch_data / fetch_response (requests imported inside)
                       platform.py  current os / arch / python / free-threaded
                       package.py   PackageSpec
                       io.py, mapping.py   (kept until the downstream scripts are migrated, 3.8)
  version/             comparison.py  filtering.py  runtime.py  bounds.py  pyproject.py
                       request.py     (pure: the version request, 3.9)
                       pypi.py        package.py                                      (network)
  compat/              target.py      registry.py   data/<package>.json   data.py
                       wheel_tags.py  discover.py   display.py
  install/             installer.py   resolver.py   api.py   all_versions.py
  local_git.py
```

Removed: `feu.github`, `feu.utils.fallback`, `feu.imports.{click,git,requests,rich,urllib3}`,
`feu.compat.discoverers`, `feu.compat.discovered`, `feu.compat.packages`, `feu.compat.matrix`,
`feu.install.pip`, `feu.install.registry`, `feu.install.utils`, `feu.utils.installer`.

### 3.2 `feu.imports` (property 1, 2, 9)

`feu.imports` is a **port of `coola.utils.imports`** (`package.py`, `optional.py`, `lazy.py`), not a
new design. `feu` cannot depend on `coola` for it (`coola` is the heavier library, and its own dev
scripts use `feu`), so the three modules are copied, with the docstrings and tests, and kept in
step by hand; this is the cost of the copy and it is small (about 400 lines in total). What `feu`
gets from it:

```python
# feu.imports.package
@availability_cache  # functools.cache + registration, so clear_availability_caches() needs no list
def package_available(name: str) -> bool:  # find_spec, the package is not imported
    ...


@availability_cache
def module_available(name: str) -> bool:  # imports the module; any failure of a broken install is False
    ...  # and is logged with logger.warning(..., exc_info=True)


def clear_availability_caches() -> None: ...
def check_package(package: str, *, install: str | None = None) -> None: ...
def raise_package_missing_error(package: str, *, install: str | None = None) -> Never: ...


class MissingPackageError(ModuleNotFoundError, RuntimeError):
    """`except ImportError` and the current `except RuntimeError` both keep working."""
```

- `optional.py` has `is_click_available()`/`check_click()` and the same pairs for `git`
  (`install="gitpython"`), `requests` and `rich`; each `is_<pkg>_available` is `module_available`
  under `@availability_cache`, so a broken `requests` is reported as unavailable. There is no
  `urllib3` pair (it comes with `requests`), no `*_available` decorator and no
  `decorator_package_available`.
- `lazy.py` is `lazy_exports(package, exports, namespace)`. `feu/__init__.py` uses it for its 12
  names, so `import feu` imports none of the submodules, and `from feu import compare_version` still
  works (four repositories use it, section 5). `is_module_imported` is not ported (no use in `feu`).
- **Names.** `feu` adopts the `coola` names `package_available` and `module_available`.
  `is_package_available` and `is_module_available` stay as public aliases because `arkas` imports
  `feu.imports.is_package_available` (section 5); they are not deprecated (D13).
- **Cache.** The measurement of section 6 shows that `find_spec` costs 36 µs, so the cache is not
  needed for speed. It is kept for **consistency with `coola`** (one behaviour across the sibling
  libraries, one `clear_availability_caches` for tests), and the staleness it creates is removed
  at the source: `install_package` calls `clear_availability_caches()` after a successful
  installation. The `feu` tests that patch `sys.path` or `sys.modules` call it instead of
  `cache_clear()` function by function.
- The message of `MissingPackageError` is the one of `coola`: it gives `pip install <name>` and
  `uv pip install <name>`. The extra that bundles the library (`feu[cli]`, `feu[git]`,
  `feu[requests]`, `feu[rich]`) is in the docstrings of the feature and in `get_started.md`.

### 3.3 `feu.utils`

- **`Registry[T]`** (about 50 lines): `register(key, value, *, exist_ok=False)`,
  `register_many(mapping, *, exist_ok=False)`, `find(key)` (raises `KeyError` with the known keys),
  `get(key, default)`, `__contains__`, `__len__`, `keys()`. The constructor takes the `kind` (for the
  error message) and a `normalize` function (`canonicalize_name` for packages, `str.lower` for
  installer names). It is the **only** implementation of "register and look up by name". The
  installer registry and the resolver registry are instances of it; the discoverer registry
  disappears (3.6); `CompatRegistry` keeps its own class because its key is a pair
  (package, target).
- **`run_command(argv: Sequence[str]) -> None`**: logs `shlex.join(argv)`, runs
  `subprocess.run(argv, check=True)`. No string form. `capture_output`, `cwd` and `env` are not added
  until a caller needs them.
- **`fetch_data(url, *, timeout=10.0, headers=None, params=None, accept=None)`** and
  `fetch_response(...)`: explicit keyword arguments instead of `**kwargs` (a `timeout` passed twice
  today raises a confusing `TypeError`), one `requests.Session` in a `with` block, the retry policy
  mounted on `https://` **and** `http://`, a `User-Agent: feu/<version>`. `requests` and
  `urllib3.util.retry.Retry` are imported inside the function after `check_requests()`; no
  `is_urllib3_available` branch (requests depends on urllib3).
- **`PackageSpec(name, version="", extras=())`**, frozen, with `__str__`. `version` is a version
  _request_ (3.9): `""` and `None` both mean "the latest" and print as `name` (no pin), `"2.*"` prints
  `name==2.*`, `"2.4.0"` prints `name==2.4.0`. `PackageDependency`,
  `extract_package_name`, `extract_package_extras` and `generate_extras_string` are deleted: a
  resolver returns `packaging.requirements.Requirement` objects, and a string such as
  `"pandas[performance]"` is parsed by `Requirement`. `is_wildcard_version` is replaced by the parser of 3.9.
- **`feu.utils.platform`** keeps `get_current_os`, `get_current_arch`, `get_python_version`,
  `is_free_threaded`; `get_python_major_minor` (in `version/runtime.py`) is deleted.

### 3.4 `feu.version` (property 7, 9, 10)

Pure modules (no I/O): `comparison`, `filtering`, `runtime`, `bounds`, `pyproject`.

- `compare_version(package, op, version)` is unchanged (four repositories use it, section 5).
  `get_package_version` returns `None` for an installed distribution whose version is not PEP 440
  (today `InvalidVersion`).
- `latest_version`, `latest_major_versions`, `latest_minor_versions` return **the input strings**
  (`max(versions, key=Version)`, and a `{Version: original}` map). `sort_versions(versions, *,
reverse=False)`.
- `normalize_package_name` is deleted in favour of `packaging.utils.canonicalize_name`.
- `read_pyproject_bounds(path, *, package=None) -> list[PackageBounds]` replaces
  `read_pyproject_dependencies`, `read_pyproject_optional_dependencies` and
  `read_pyproject_package_bounds`: the file is parsed once, the sections are
  `project.dependencies`, `project.optional-dependencies.*` and `dependency-groups.*`, the name is
  canonical, `package` filters. `partition_package_bounds` and `get_package_bounds` are deleted (a
  list comprehension).

Network modules:

```python
@dataclass(frozen=True)
class PypiFile:
    filename: str
    requires_python: str | None
    yanked: bool
    uploaded: datetime | None  # UTC, from `upload-time`


@dataclass(frozen=True)
class PypiProject:
    name: str  # canonical
    releases: Mapping[str, tuple[PypiFile, ...]]  # MappingProxyType, PEP 440 order


def fetch_pypi_project(package: str) -> PypiProject:  # ONE request, cached by canonical name
    ...
```

`fetch_pypi_project` calls `https://pypi.org/simple/<canonical-name>/` with
`Accept: application/vnd.pypi.simple.v1+json` (not the deprecated `releases` key). Everything else
is derived from it, with no further request:

- `fetch_pypi_versions(package, *, start_date=None, end_date=None, ignore_yanked=True)`: PEP 440
  ascending (no `reverse` option: `[::-1]`); dates are UTC dates, documented.
- `fetch_pypi_wheel_filenames(package)` and `fetch_pypi_requires_python(package)`: read-only
  mappings.
- `fetch_pypi_pinned_dependency_version(package, version, dependency)`: the only call that needs a
  second endpoint (`/pypi/<package>/<version>/json`, `info.requires_dist`, which is not deprecated).
  Names are compared canonically; a requirement **with an environment marker** is skipped and the
  docstring says so.
- `fetch_versions(package, *, lower=None, upper=None)`, `fetch_latest_version`,
  `fetch_latest_stable_version`, and **one** `fetch_latest_versions(package, *, group, lower=None,
upper=None, include_lower_bound=False)` with `group` in `{"major", "minor"}`, which replaces the
  four `fetch_latest_{major,minor}_versions[_map]` and `fetch_sampled_latest_minor_versions`.
  `include_lower_bound` is applied in one place, with `lower is not None`.
- `fetch_package_versions(pyproject, *, major_only=("packaging",), include_lower_bound=True)
-> dict[str, list[str]]`: the body of the `dev/generate_versions.py` that ten repositories copy
  (3.8).

### 3.5 `feu.compat` (property 3, 4, 5, 7)

**Target.** `Target(python_version, free_threaded=False, os=None, arch=None)` is unchanged (frozen,
validated with `fullmatch`). `resolve_target(python_version=None, *, free_threaded=None, os=None,
arch=None)` makes the options keyword-only and stays the only way to get the current environment.

**Matching rule (fixes F1).** A lookup field set to `None` means "any". An entry matches a lookup
when `python_version` and `free_threaded` are equal and each of `os`/`arch` is `None` in the entry,
`None` in the lookup, or equal. Among the matching entries, the ones with the **highest
specificity** (number of non-`None` `os`/`arch` in the entry) are kept, and the answer is the
**union** of their ranges (interval merge). Consequences:

| Lookup                                      | Answer                                                                   |
| ------------------------------------------- | ------------------------------------------------------------------------ |
| fully specified (`resolve_target()`)        | the entry of that platform, as today (a concrete entry beats a wildcard) |
| `Target("3.9")` (platform unspecified)      | versions published for 3.9 on **at least one** platform                  |
| two entries of equal specificity both match | their union (today: the last registered wins, which is arbitrary)        |
| package without entry for the target        | permissive, as today; `registry.has_package(name)` tells the caller      |
| entry registered with `[]`                  | unsupported (`UnsupportedVersionError`), as today                        |

The union is the permissive reading of "I did not say which platform", consistent with the
"unconfigured is permissive" rule; the strict reading (intersection) would make `Target("3.12")`
unsupported for `torch` because one platform has no wheel. See D1.

**Registry.** `CompatRegistry` keeps its public methods (`register`, `register_many`, `get_config`,
`is_unsupported`, `get_version_ranges`, `find_closest_version`, `is_valid_version`) with these
changes: package names are canonicalised; `register` validates the ranges (parseable, `min <= max`)
and does not create state before failing; ranges are parsed once at registration (the lookup does
not call `Version(...)` per range); `find_closest_version` returns the **registered string** of a
boundary; `state` returns a read-only view; `__str__` is a one-line summary; `exist_ok` is
keyword-only; `has_package(name)`, `packages()` (the canonical names), `register_versions(pkg_name,
versions, *, exist_ok=False)` and `get_compatible_versions(pkg_name, target, pkg_version="")` are
new. `find_closest_version` and `is_valid_version` take a version **request**, not only a version
(3.9).

**Shipped data.** One JSON file per package in `feu/compat/data/<canonical-name>.json`:

```json
{
  "package": "numpy",
  "generated": "2026-11-09",
  "versions": ["1.26.0", "1.26.4", "2.0.0", "2.0.2", "2.3.2"],
  "targets": [
    {
      "python": "3.12",
      "free_threaded": false,
      "os": "linux",
      "arch": "x86_64",
      "ranges": [["1.26.0", null]]
    }
  ]
}
```

`versions` is the list of the stable, valid, non-ignored releases that existed when the file was
generated, in PEP 440 order: it is the "versions the registry knows" that a wildcard is matched
against (3.9), and every `min`/`max` of a range is one of them (a data-contract test). Entries are
sorted by `(python, free_threaded, os, arch)`; a range whose `max` is `null` is open (the latest
release was compatible when the file was generated). The default registry
(`get_default_compat_registry()`) lists the file names with `importlib.resources` (no parsing) and
parses **one file on the first lookup of that package**. `import feu.compat` and the creation of the
registry no longer cost anything; a lookup costs one small `json.loads`. The list of packages is
the list of files: a new package is added by running the generator with its name, and nothing else
is edited. `register_compat(mapping, *, exist_ok=False)` adds user data on top, as today.

**Wheel tags.** `wheel_tags.py` uses `packaging.utils.parse_wheel_filename` (which expands
compressed tag sets) and maps each `(interpreter, abi, platform)` to a `WheelTag(python, abi3,
free_threaded, os, arch)` through three small tables:

| Platform tag                                           | Result                                                           |
| ------------------------------------------------------ | ---------------------------------------------------------------- |
| `manylinux*`, `linux_*` with `x86_64` / `aarch64`      | `linux`, `x86_64` / `arm64`                                      |
| `macosx_*_x86_64`, `macosx_*_arm64`                    | `macos`, `x86_64` / `arm64`                                      |
| `macosx_*_universal2`                                  | `macos`, **both** `x86_64` and `arm64`                           |
| `win_amd64`, `win_arm64`                               | `windows`, `x86_64` / `arm64`                                    |
| `any`                                                  | pure Python: `os=None`, `arch=None`                              |
| `musllinux_*`, `win32`, `i686`, `armv7l`, `ppc64le`, … | **out of scope, documented and tested**, not dropped by accident |

`free_threaded` is `abi in {"cp3Xt", "abi3t"}` (a regular expression, not `endswith("t")`); `abi3t`
is a stable-ABI tag like `abi3`. `parse_wheel_filename` returns a tuple of tags (empty only for the
documented out-of-scope platforms). See D6 and D7.

**Discovery.** One function replaces 1,122 lines:

```python
def discover_compat_targets(
    pkg_name: str,
    targets: Sequence[Target] = DEFAULT_TARGETS,
    *,
    companion: Companion | None = None,  # None: look up COMPANIONS
    ignore_versions: Collection[str] | None = None,  # None: look up IGNORED_VERSIONS
) -> Discovery: ...


class Discovery(NamedTuple):
    versions: tuple[str, ...]  # the releases that were considered (stable, valid, not ignored)
    targets: dict[Target, list[VersionRange]]  # what `discover_compat_targets` returned before


@dataclass(frozen=True)
class SameVersion:  # the companion release has the same version (jax -> jaxlib)
    package: str


@dataclass(frozen=True)
class PinnedDependency:  # the companion release is pinned by the release (polars, pydantic)
    package: str


COMPANIONS = {
    "jax": SameVersion("jaxlib"),
    "polars": PinnedDependency("polars-runtime-32"),
    "pydantic": PinnedDependency("pydantic-core"),
}
IGNORED_VERSIONS = {"duckdb": frozenset({"0.0.0"})}
```

Algorithm (written once, in the order of the code):

1. `project = fetch_pypi_project(pkg_name)`; keep the stable, valid versions that are not ignored.
2. `tags(version)` = the tags of the wheels of that release.
3. If **every** tag of the release is pure Python (or the release has no wheel) and a companion is
   registered, `tags(version)` = the tags of the companion release (same version, or the pinned
   version found with `fetch_pypi_pinned_dependency_version`).
4. A release is compatible with a target if one tag matches exactly (`python`, `free_threaded`,
   `os`, `arch`), or is `abi3` with a minimum Python at or below the target, or is pure Python and
   `requires-python` allows the target. A release with **no** wheel at all is treated as pure
   Python only if some other release of the package published a pure-Python wheel (the rule of
   `treat_sdist_as_pure_python` today, kept and documented).
5. `group_into_ranges` (unchanged) builds the ranges; the range that reaches the latest release is
   open. The versions of step 1 are returned with the ranges (`Discovery`), because a wildcard
   needs them.

`jax` falls out of step 3 (its own wheels are always pure), `polars` and `pydantic` also (their
older releases ship platform wheels and are matched directly), `duckdb` is a table entry. There is
no discoverer base class, no discoverer registry and no `register_discoverers`; a user who needs a
new case passes `companion=`. `matrix.py` is split: `DEFAULT_TARGETS`/`PYTHON_VERSIONS` move to
`target.py`, `is_compatible` to `discover.py`, `show_compat_targets` to `display.py` (imports `rich`
inside the function).

### 3.6 `feu.install` (property 6, 8)

```python
@dataclass(frozen=True)
class InstallerSpec:
    name: str
    arguments: tuple[str, ...] = ()  # was: a str re-split with shlex


@dataclass(frozen=True)
class Installer:  # one class, no ABC: the subclasses differ by a prefix
    arguments: tuple[str, ...] = ()
    prefix: ClassVar[tuple[str, ...]]

    def command(self, requirements: Sequence[Requirement]) -> list[str]:
        return [*self.prefix, *self.arguments, *map(str, requirements)]

    def install(self, package: PackageSpec, *, resolvers: Registry[Resolver]) -> None:
        run_command(self.command(resolve(package, resolvers)))


class PipInstaller(Installer):
    prefix = (sys.executable, "-m", "pip", "install")


class UvInstaller(Installer):
    prefix = ("uv", "pip", "install", "--python", sys.executable)
```

- `PipxInstaller` is removed (D2). A user who wants it registers it.
- `install_package(installer, package, *, registry=None)` and
  `install_package_closest_version(installer, package, *, target=None, registry=None)`: `target`
  defaults to `resolve_target()` (the full current target, fixing F1). `package.version` is a version
  request (3.9): `None`, `""`, `"1.*"` and `"1.2.3"` are all checked against the registry and
  resolved by `find_closest_version`; the exemption of wildcards and the `RuntimeError` for a
  missing version are gone. A request with no compatible version raises `UnsupportedVersionError`.
  `install_package` (no check) installs the request as written.
- **Resolvers.** A resolver is a function `(PackageSpec) -> list[Requirement]`. The default returns
  the package itself. The seven `Numpy2DependencyResolver` subclasses become one table and one
  factory:

  ```python
  NUMPY2_MIN_VERSION = {
      "matplotlib": "3.8.4",
      "pandas": "2.2.2",
      "pyarrow": "16.0",
      "scikit-learn": "1.4.2",
      "scipy": "1.13.0",
      "torch": "2.3.0",
      "xarray": "2024.6.0",
  }
  ```

  plus `jax_resolver` (adds `jaxlib==v`, `numpy<2.0.0` below 0.4.26, `ml_dtypes<=0.2.0` for
  0.4.9 to 0.4.11). The resolvers receive a version **request** and reason on the whole request: a
  pin is added when the **entire** request lies on the old side of the threshold (`pandas==2.1.*` is
  below `2.2.2`, so `numpy<2.0.0`; `pandas==2.*` straddles it, and pip's latest `2.x` is above it, so
  no pin; `""` is the latest, so no pin; `jax==0.4.*` straddles `0.4.26`, no pin). `jaxlib` is
  pinned to the same request (`jaxlib==0.4.25`, `jaxlib==0.4.*`), and not at all for `""`. Today both
  resolvers raise `RuntimeError("Missing package version")` for no version and skip every pin for a
  wildcard.

- Registries are `Registry[type[Installer]]` and `Registry[Resolver]`, created by
  `get_default_installer_registry()` and `get_default_resolver_registry()`, extended with
  `register_installer(name, installer, *, exist_ok=False)` and
  `register_resolver(package, resolver, *, exist_ok=False)`.
- `install/utils.py` (four responsibilities) is split: `api.py` (the two install functions),
  `all_versions.py` (`get_installable_versions`, `install_all_versions`, `InstallResult`; the
  `install_packages_all_versions` comprehension is left to its one caller, `dev/install_all_versions.py`),
  availability (`is_pip_available` is `find_spec("pip")`, `is_uv_available` is `shutil.which("uv")`;
  `get_available_installers` has no consumer and is deleted). `get_installable_versions` returns
  PEP 440 order.

### 3.7 `feu.cli` (property 11)

`feu/cli.py` imports `click` at the top; `__main__.py` calls `check_click()` and then imports it, so
there is no fallback module and no undecorated functions. `[project.scripts] feu = "feu.__main__:main"`
is added; `python -m feu` keeps working.

| Command                  | Options                                                                                                                                                                                                                      | Output and exit status                                                                                                                               |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `install`                | `-n/--pkg-name`, `-v/--pkg-version` (a version request, default `""` = latest), `-e/--pkg-extras` (default `""`), `-i/--installer-name` (default `pip`), `-a/--installer-args` (default `""`, split with `shlex.split` once) | installs into the **current** interpreter, for the **current** target; `1` on `UnsupportedVersionError`                                              |
| `find-closest-version`   | `-n`, `-v` (a request, default `""`), `-p/--python-version`, `--free-threaded/--no-free-threaded`, `-o/--os`, `-r/--arch` (one shared `target_options` decorator)                                                            | stdout: the version to install (for an open-ended wildcard or `""`: the request itself, 3.9); unsupported: message on stderr, empty stdout, exit `1` |
| `check-valid-version`    | same as above                                                                                                                                                                                                                | stdout `True`/`False` (unchanged); exit `0` when valid, `1` when not                                                                                 |
| `package-versions` (new) | `--pyproject`, `--output`, `--major-only` (repeatable, default `packaging`)                                                                                                                                                  | writes the JSON of `fetch_package_versions` (3.4)                                                                                                    |

Global: `--version`, `--verbose` (configures logging to stderr; no short flag, `-v` is the
package version). All short and long names of the three existing commands are unchanged, because an
external action uses them (section 5). `install` does **not** get target options: it installs into
the interpreter that runs it, so any other target would contradict property 8; installing into
another environment is a different feature (section 10).

### 3.8 Generating the package versions (the script that is copied ten times)

`dev/generate_versions.py` is copied into at least ten repositories and imports
`feu.utils.io.save_json`, `feu.utils.mapping.sort_by_keys` and five functions of `feu.version`.
That is public API in everything but name. The target gives it one home, `fetch_package_versions`
and `python -m feu package-versions --pyproject pyproject.toml --output dev/config/package_versions.json`,
so a downstream script becomes one CLI call in its workflow, and `save_json`, `sort_by_keys`, the
`_map` functions and `partition_package_bounds` have no consumer left. They are kept until the
downstream repositories are migrated and then deleted (section 7, step 11).

### 3.9 Version requests: exact, wildcard, empty (property 15, issue #1032)

A version argument is a **request**, not a version. One parser, in the pure module
`feu/version/request.py`, is shared by `PackageSpec`, the registry, the resolvers and the CLI:

```python
@dataclass(frozen=True)
class VersionRequest:
    text: str  # as given, stripped: "" | "2.4.*" | "2.4.0"
    exact: Version | None  # set for "2.4.0"
    prefix: tuple[int, ...] | None  # set for "2.4.*" -> (2, 4); "2.*" -> (2,)

    @property
    def is_latest(self) -> bool: ...  # text == ""

    def matches(self, version: Version) -> bool: ...  # exact equality, or release-prefix match

    def entirely_below(self, version: Version) -> bool: ...  # for the resolvers


def parse_version_request(text: str | None) -> VersionRequest: ...
```

| Input                                                                        | Parsed as               | Notes                                                                                                    |
| ---------------------------------------------------------------------------- | ----------------------- | -------------------------------------------------------------------------------------------------------- |
| `None`, `""`, `"  "`                                                         | latest                  |                                                                                                          |
| `"2.4.0"`, `"2.4.0rc1"`, `"1!2.0"`                                           | exact                   | any PEP 440 version, as today (`InvalidVersion`, a `ValueError`, if it is not one)                       |
| `"2.4.*"`, `"2.*"`                                                           | prefix `(2, 4)`, `(2,)` | the prefix is digits and dots followed by one trailing `.*`, as in the `==` clause of PEP 440            |
| `"*"`, `"2.*.1"`, `"2.4.*.dev"`, `"2.4*"`, `".*"`, `"2.4.0rc1.*"`, `"1!2.*"` | `ValueError`            | explicit message ("a wildcard is digits and dots followed by one trailing '.*'"); never `InvalidVersion` |

**Matching.** A prefix `(2, 4)` matches a version whose release segment, zero-padded, starts with
`2.4` (`2.4`, `2.4.0`, `2.4.17`; not `2.40`, not `2.5`). Pre-releases never match a wildcard: the
shipped `versions` list contains stable releases only (so a wildcard that names a pre-release is
rejected at parse time instead of silently matching nothing; this is stricter than the text of the
issue, D15).

**Resolution (registry).** `get_compatible_versions(pkg_name, target, pkg_version="")` returns the
known versions (the `versions` of the data file) that lie in a valid range of the target **and**
match the request, in PEP 440 order. From it:

| Request                                                                        | `is_valid_version`                                                                    | `find_closest_version` (the version to install)                                                                                                                      |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| exact                                                                          | as today (an unknown package or a package with no entry for the target is permissive) | as today (itself if valid, else the nearest boundary)                                                                                                                |
| prefix or latest, known package                                                | `True` if `get_compatible_versions(...)` is not empty, else `False`                   | the latest compatible match; **if it lies in the open-ended last range, the request itself** (`"2.*"`, or `""`) so that pip picks the real latest; else that version |
| prefix or latest, no data for the package (or none registered with `versions`) | `False` (issue: "True only if the registry has a compatible version")                 | the request unchanged (the registry cannot resolve it; `pip` will)                                                                                                   |
| entry registered with `[]`                                                     | `False`                                                                               | `UnsupportedVersionError`                                                                                                                                            |
| prefix or latest, known package, no compatible match                           | `False`                                                                               | `UnsupportedVersionError("no compatible version of numpy matches '1.24.*' for Python 3.14 ...")`                                                                     |

The open-ended rule is what keeps "latest" meaning latest: a range that ends at the newest release
known when the data was generated is open (`max=None`), so every later release is assumed
compatible, and a release published after the data was generated must stay installable. Resolving
`""` to the newest _known_ version would silently pin to an old release, which defeats the common
use of `""` (test against the freshest release). A closed range cannot go stale in that way: its
`max` is a real upper limit, so the concrete version is exact.

**Examples** (`numpy` on Python 3.14, `linux`/`x86_64`, where the data says `[2.3.2, open)`):

```text
is_valid_version("numpy", "2.4.*", t)  -> True      (2.4.x exists in `versions` and is in the range)
is_valid_version("numpy", "",      t)  -> True
is_valid_version("numpy", None,    t)  -> True
is_valid_version("numpy", "1.24.*", t) -> False     (no 1.24 release is in a valid range for 3.14)
is_valid_version("numpy", "2.*.1", t)  -> ValueError
find_closest_version("numpy", "2.*", t)  -> "2.*"   (open range: pip chooses the latest 2.x)
find_closest_version("numpy", "",    t)  -> ""
find_closest_version("numpy", "1.*", Target("3.9", ...)) -> "1.26.4"  (closed range: the latest 1.x
                                                                       that supports 3.9, concrete)
find_closest_version("numpy", "1.24.*", t) -> UnsupportedVersionError
```

**Why a list of versions in the data (D14).** The registry stores _ranges_, and a range alone cannot
say whether a release exists in a prefix: `"2.9.*"` against `[2.3.2, open)` would be "valid" for a
package that never had a `2.9`. The issue words it as matching "against the versions the registry
knows", which requires the registry to know them. One list of strings per package (a few hundred
bytes to a few KB) is the smallest data that makes the answer true, deterministic and testable
offline, and it gives the helper that the issue asks for (`get_compatible_versions`) for free.
A package registered by the user with `register(...)` and no `register_versions(...)` has no list,
so a wildcard or empty request for it is "no data" (second row of the table), which is the
behaviour the issue asks for.

**CLI.** `--pkg-version` is optional (default `""`) in the three commands that take it. An empty
value is accepted (`--pkg-version=`), so a workflow can pass an unset input straight through.
`check-valid-version` answers like `is_valid_version` and exits `0`/`1`.

## 4. Public API after the change

```text
# feu  (lazy: `import feu` imports none of the submodules)
from feu import (
    compare_version,
    get_package_version,
    is_module_available,
    is_package_available,
    install_package,
    install_package_closest_version,
    find_closest_version,
    is_valid_version,
    resolve_target,
    Target,
    InstallerSpec,
    PackageSpec,
)

# feu.imports
package_available(name), module_available(name)  # is_package_available / is_module_available: aliases
availability_cache, clear_availability_caches(), lazy_exports(package, exports, namespace)
check_package(package, *, install=None), raise_package_missing_error(...), MissingPackageError
is_click_available(), check_click()  # also git, requests, rich

# feu.compat
Target, resolve_target(python_version=None, *, free_threaded=None, os=None, arch=None)
VersionRange, CompatRegistry, UnsupportedVersionError
get_default_compat_registry(), register_compat(mapping, *, exist_ok=False)
find_closest_version(pkg_name, pkg_version, target, *, registry=None)  # pkg_version: a version request
is_valid_version(pkg_name, pkg_version, target, *, registry=None)  # pkg_version: str | None
get_compatible_versions(pkg_name, target, pkg_version="", *, registry=None)
discover_compat_targets(pkg_name, targets=DEFAULT_TARGETS, *, companion=None, ignore_versions=None) -> Discovery
SameVersion, PinnedDependency, WheelTag, parse_wheel_filename, show_compat_targets

# feu.install
InstallerSpec, Installer, PipInstaller, UvInstaller
install_package(installer, package, *, registry=None)
install_package_closest_version(installer, package, *, target=None, registry=None)
get_default_installer_registry(), register_installer(name, installer, *, exist_ok=False)
get_default_resolver_registry(), register_resolver(package, resolver, *, exist_ok=False)
get_installable_versions(pkg_name, target, *, start_date=None)
install_all_versions(installer, package, target, *, start_date=None), InstallResult
is_pip_available(), is_uv_available()

# feu.version
compare_version(package, op, version), get_package_version(package)
latest_version, sort_versions(versions, *, reverse=False), filter_*, latest_{major,minor}_versions
PackageBounds, read_pyproject_bounds(path, *, package=None)
VersionRequest, parse_version_request(text)
fetch_pypi_project, fetch_pypi_versions, fetch_pypi_wheel_filenames, fetch_pypi_requires_python
fetch_pypi_pinned_dependency_version, fetch_versions, fetch_latest_version
fetch_latest_stable_version, fetch_latest_versions, fetch_package_versions

# feu.utils
Registry, run_command, fetch_data, fetch_response, PackageSpec
# feu.local_git: get_tags, get_last_tag_name(*, raise_error=True), get_last_version_tag_name(*, raise_error=True)
# feu.testing: pytest marks (no `pipx`, no `urllib3`)
```

Old to new, for the migration page:

| Old                                                                                                                                 | New                                                                                                                          |
| ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `feu.compat.get_default_registry`, `feu.compat.discoverers.get_default_registry`                                                    | `get_default_compat_registry`; the second one is deleted                                                                     |
| `InstallerRegistry.add_installer(...)`, `DependencyResolverRegistry.add_resolver(PackageSpec, ...)`                                 | `register_installer(name, ...)`, `register_resolver(name, ...)`                                                              |
| `BaseInstaller`, `BasePipInstaller`, `PipxInstaller`, `BaseDependencyResolver`, the seven `*DependencyResolver`                     | `Installer`, `PipInstaller`, `UvInstaller`; a resolver is a function                                                         |
| `InstallerSpec("pip", arguments="-U")`                                                                                              | `InstallerSpec("pip", arguments=("-U",))`                                                                                    |
| `run_bash_command("pip install x")`                                                                                                 | `run_command(["pip", "install", "x"])`                                                                                       |
| `BaseCompatDiscoverer`, `CompatDiscoverer`, `*CompatDiscoverer`, `CompatDiscovererRegistry`, `register_discoverers`                 | `discover_compat_targets(..., companion=...)`                                                                                |
| `feu.compat.discovered`, `feu.compat.packages.get_package_names`                                                                    | `feu/compat/data/*.json`, `CompatRegistry.packages()`                                                                        |
| `feu.version.normalize_package_name`                                                                                                | `packaging.utils.canonicalize_name`                                                                                          |
| `read_pyproject_dependencies`, `read_pyproject_optional_dependencies`, `read_pyproject_package_bounds`                              | `read_pyproject_bounds`                                                                                                      |
| `fetch_latest_{major,minor}_versions[_map]`, `fetch_sampled_latest_minor_versions`                                                  | `fetch_latest_versions(group=...)`, `fetch_package_versions`                                                                 |
| `feu.version.get_python_major_minor`                                                                                                | `feu.utils.platform.get_python_version`                                                                                      |
| `feu.imports.{click,git,requests,rich,urllib3}`; `decorator_package_available`; `raise_*_missing_error`; `@lru_cache` on the checks | `feu.imports.optional`, `package.py` (port of `coola.utils.imports`), `availability_cache`, `check_*`, `MissingPackageError` |
| `feu[requests]` pulling `urllib3` explicitly                                                                                        | `feu[requests]` = `requests`                                                                                                 |
| `is_wildcard_version`, a wildcard skipped by the compatibility check and by the resolvers, `RuntimeError` for no version            | `parse_version_request`; a wildcard, `""` and `None` are resolved and checked like a version                                 |
| `feu.github`                                                                                                                        | deleted (D3)                                                                                                                 |

## 5. Dependents

Found by a code search of the repositories of the owner (limited to the top results, and stopped by
the API rate limit before the query `import feu` finished; other owners were not searched).
**[downstream]**

| Consumer                                                                                                                                   | Uses                                                                                                                                                                                                        | Impact of the target state                                                                                                                                                                                                                                                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pip-install-package-action` (`action.yaml`)                                                                                               | `pip install "feu[cli]>=0.4.2"`; `python -m feu find-closest-version --pkg-name --pkg-version --python-version`; `python -m feu install --installer-name=pip --installer-args=... --pkg-name --pkg-version` | Flags unchanged. Stdout of `find-closest-version` is still only the version; an unsupported package now **fails the step** (exit `1`) instead of installing `==None`. `install` now clamps (F1 fixed). `--installer-args` is split once with `shlex` on every OS: check the quoting of `inputs.pip-args`. |
| its `tests/functional/test_package.py`                                                                                                     | `feu.testing` marks                                                                                                                                                                                         | Unchanged.                                                                                                                                                                                                                                                                                                |
| `iden`, `batchtensor`, `grizz`, `arkas` (`tests/conftest.py`)                                                                              | `from feu import compare_version`                                                                                                                                                                           | Unchanged (signature kept).                                                                                                                                                                                                                                                                               |
| `arkas`                                                                                                                                    | `feu.imports.is_package_available`, `feu.testing.numpy_available`                                                                                                                                           | Unchanged.                                                                                                                                                                                                                                                                                                |
| `iden` (`tasks.py:364`)                                                                                                                    | `feu.local_git.get_last_version_tag_name`                                                                                                                                                                   | Name kept. `raise_error` becomes keyword-only: check that the call does not pass it positionally.                                                                                                                                                                                                         |
| `coola`, `hya`, `objectory`, `batcharray`, `evalix`, `metriclab`, `minrecord`, `mlev`, `startorch`, `zenpyre` (`dev/generate_versions.py`) | `feu.utils.io.save_json`, `feu.utils.mapping.sort_by_keys`, `feu.version.{fetch_latest_*_map, partition_package_bounds, read_pyproject_*}`                                                                  | Replaced by `python -m feu package-versions` (3.8). The old names stay until each repository is migrated (step 11).                                                                                                                                                                                       |
| `analora` (`tasks.py`)                                                                                                                     | matched `from feu`; the import was not read                                                                                                                                                                 | To check before step 11.                                                                                                                                                                                                                                                                                  |
| `uv-install-package-action`, `setup-venv-uv-action` (issue #1032, not read)                                                                | `feu.compat.is_valid_version(pkg_name, pkg_version, python_version, ...)`, with a bypass in `setup-venv-uv-action` (its PR 161) for `""` and wildcards                                                      | The bypass can be removed once step 2b is released. The call used the signature of the issue; the target signature takes a `Target` (`resolve_target(python_version)`).                                                                                                                                   |

Inside the repository: `dev/generate_discovered_compat.py` becomes `dev/generate_compat_data.py`,
`dev/install_all_versions.py` and `debug/compat_targets.py` follow the renames,
`tests/package_checks.py` gets the checks of section 8, and `.github/workflows/bot-update-discovered-compat.yaml`
runs the new generator (not read in detail; to adapt in step 7).

## 6. Evidence

All on `main` `9e473b2`, Python 3.14.10, no code changed. **[verified]**

| Probe                                                                                                                                   | Result                                                                                                                                                        |
| --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `find_closest_version("numpy", "2.3.0", Target(python_version="3.9"))`                                                                  | `'2.3.0'`                                                                                                                                                     |
| same with `os="linux", arch="x86_64"`                                                                                                   | `'2.0.2'`                                                                                                                                                     |
| `find_closest_version("numpy", "1.0.0", Target(python_version="3.11"))` (the `usage.md` example)                                        | `'1.0.0'` (the guide says `"1.23.2"`); with `resolve_target("3.11")`: `'1.23.2'`                                                                              |
| registered targets, by `(os, arch)`                                                                                                     | 1,020 = 6 combinations x 170, none with `os=None`; 361 distinct `(package, python, free_threaded, ranges)`                                                    |
| `parse_wheel_filename` on `macosx_11_0_universal2`, `cp39-abi3-macosx_10_9_universal2`, `musllinux_1_2_x86_64`, `win32`, `linux_armv7l` | `[]` for all five                                                                                                                                             |
| same on `macosx_10_9_x86_64.macosx_11_0_arm64`                                                                                          | one tag, `x86_64` only                                                                                                                                        |
| same on `cp315-abi3t-manylinux_2_17_x86_64`                                                                                             | `python_version='3.15', free_threaded=True, abi3=False`                                                                                                       |
| `latest_version(["1.0-1", "1.0"])`                                                                                                      | `'1.0.post1'`                                                                                                                                                 |
| `compare_version("2.0.0", "1.5.0")` (the `usage.md` example)                                                                            | `TypeError: compare_version() missing 1 required positional argument: 'version'`                                                                              |
| `is_valid_version(name, "0.1", resolve_target("3.14", os="linux", arch="x86_64"))` for `scikit-learn`, `Scikit-Learn`, `scikit_learn`   | `False`, `True`, `True` (no data found for the last two); `find_resolver(PackageSpec("Scikit-Learn"))` is the default `DependencyResolver()`                  |
| `normalize_package_name("zope.interface")`, `("a--b")` against `canonicalize_name`                                                      | `zope.interface`, `a__b` against `zope-interface`, `a-b`                                                                                                      |
| `python -X importtime -c "import feu"`                                                                                                  | 117 ms cumulative; `feu.compat` 70 ms; `requests` 43 ms; `requests`, `urllib3`, `rich` are in `sys.modules` afterwards                                        |
| first `get_default_registry()`                                                                                                          | 0.10 s                                                                                                                                                        |
| `importlib.util.find_spec` on a present and on a missing package, 2,000 calls                                                           | 36 µs and 32 µs (a cache is not needed for speed; it is kept for consistency with `coola`, 3.2)                                                               |
| `is_valid_version("numpy", v, t)` and `find_closest_version("numpy", v, t)` for `v` in `"2.4.*"`, `""`, `None`                          | `InvalidVersion: Invalid version: '2.4.*'` / `''` / `None` (all six calls raise)                                                                              |
| `Version("2.4.0rc1.*")`, `Version("1!2.*")`                                                                                             | `InvalidVersion` (the `==` wildcard exists only in specifiers, not in `Version`)                                                                              |
| `str(PackageSpec("numpy", ""))`, `str(PackageSpec("numpy", "2.*"))`; the registry range of `numpy` for 3.14 on linux/x86_64             | `numpy`, `numpy==2.*`; `[VersionRange(min='2.3.2', max=None)]` (open-ended)                                                                                   |
| `docs.pypi.org/api/json`                                                                                                                | "Deprecated keys: `releases` ... use the Index API"; the key is present today (66 releases for `click`)                                                       |
| `GET https://pypi.org/simple/click/` with `Accept: application/vnd.pypi.simple.v1+json`                                                 | keys `files`, `meta`, `name`, `project-status`, `versions`; each file has `filename`, `requires-python`, `upload-time`, `yanked`, `hashes`, `url` (130 files) |
| size of the `numpy` document                                                                                                            | 2.8 MB (Simple, JSON) against 3.7 MB (project JSON)                                                                                                           |
| `.venv/bin/pytest tests/unit -q`                                                                                                        | 924 passed, 2 skipped, 0.63 s                                                                                                                                 |
| lines of `src/feu` by area (without the data)                                                                                           | `imports` 692, `utils` 827, `version` 1,517, `compat` 1,096, `compat/discoverers` 1,122, `install` 1,339, `github` 251, root files 589; data 3,546            |

**Not read:** `coola.utils.imports` was read (`package.py`, `optional.py`, `lazy.py`, `__init__.py`); its tests were not. Issue #1032 was read; the two actions it names were not.

**Not run:** a real `pip`/`uv install` (needs the network and mutates the environment), the GitHub
functions, the discovery against live PyPI, Windows. The design of 3.5 (one discovery algorithm that
reproduces the four discoverers) was **not prototyped**: it is the claim of this document with the
least evidence (together with the open-ended rule of 3.9, which no probe exercises), and step 7 therefore starts by a refactor whose gate is an **empty diff** of the
generated data (section 8).

## 7. Changes to reach the target state

One branch and one pull request per step (`CLAUDE.md`), stacked where a step needs the previous
one. The order keeps every step releasable and puts the correctness fixes first.

| Step | Change                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Fixes       | Breaking                                                                |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ----------------------------------------------------------------------- |
| 1    | **Fix F1.** The matching rule of 3.5 (union of the most specific entries), `install_package_closest_version(*, target=None)` with `resolve_target()`, `has_package`. Integration tests on the shipped data. Fix the examples of `README.md`/`usage.md` (F6) in the same PR.                                                                                                                                                                                                                                                                                                                                                                               | F1, F6      | behaviour (a fix)                                                       |
| 2    | **Names and version strings.** `canonicalize_name` in the registries, the resolver registry, the pyproject reader and `fetch_pypi_*`; drop the `sklearn` key; `latest_*` return the input; `fullmatch` in `Target`; validate ranges in `register`; return the registered boundary string.                                                                                                                                                                                                                                                                                                                                                                 | F3, F4, F18 | slight                                                                  |
| 2b   | **Version requests (issue #1032).** `version/request.py` (`parse_version_request`), `PackageSpec.version` as a request, `get_compatible_versions`, `is_valid_version`/`find_closest_version` on requests with the open-ended rule, `register_versions`, resolvers that reason on the whole request, remove the wildcard exemption and the `RuntimeError` in `install_package_closest_version`, `--pkg-version` optional in the CLI. The data gets its `versions` list: the generator adds a `VERSIONS` constant to the current Python modules and is re-run (the diff is only the new constant), so the step does not wait for the JSON format of step 7. | F19         | slight (inputs that raised now work; wildcard installs are now checked) |
| 3    | **Commands.** `run_command(argv)`, installers return argv lists, `sys.executable -m pip`, `uv pip install --python`, `InstallerSpec.arguments` as a tuple, delete `PipxInstaller`. Integration test with an offline `pip install --dry-run` (section 8).                                                                                                                                                                                                                                                                                                                                                                                                  | F7          | yes (installers)                                                        |
| 4    | **`Registry[T]`**, registries as instances, the `get_default_*_registry` names, `register_installer`/`register_resolver`, the resolver table and the two functions, `PackageSpec` frozen, `Requirement` instead of `PackageDependency`.                                                                                                                                                                                                                                                                                                                                                                                                                   | F10, F15    | yes                                                                     |
| 5    | **Imports: port `coola.utils.imports`** (`package.py`, `optional.py`, `lazy.py`, with their docstrings and tests): `availability_cache`, `clear_availability_caches` (called after a successful `install_package`), `MissingPackageError`, `check_*`; keep `is_package_available`/`is_module_available` as aliases; no `urllib3` helper, no decorators; delete `utils/fallback`; lazy `requests`/`git`/`rich`; `lazy_exports` in `feu/__init__.py`. Import test.                                                                                                                                                                                          | F8, F13     | yes (small)                                                             |
| 6    | **PyPI.** `fetch_pypi_project` on the Simple API, frozen types, PEP 440 order, one `fetch_latest_versions`, `read_pyproject_bounds`, `fetch_package_versions`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | F5, F12     | yes                                                                     |
| 7    | **Discovery and data**, in three commits: (a) one discovery function with `companion=` on top of the **current** tag parser, data regenerated: the diff must be **empty**; (b) the `packaging`-based tag parser, data regenerated, the diff is reviewed and explained in the PR; (c) JSON data, lazy loader, delete `discovered/`, `packages.py`, `matrix.py`, `discoverers/`; adapt the bot workflow.                                                                                                                                                                                                                                                    | F2, F9, F11 | yes (data format, discoverers)                                          |
| 8    | **CLI.** `feu/cli.py`, exit codes, `target_options`, `--version`, `--verbose`, the console script, `package-versions`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | F14, F16    | yes (CLI exit codes)                                                    |
| 9    | **Scope.** Delete `feu.github` (D3). Keyword-only `raise_error`, distinct messages in `local_git`. Classifiers (Windows), `docs/docs/refs/*`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | F15, F18    | yes                                                                     |
| 10   | **Documentation.** Rewrite the user guide around the properties of section 1, add `docs/docs/dev/architecture.md` (layers, data flow, how to add a package, an installer, a resolver, a companion), the migration page, the README, `cli.md` (generated with `mkdocs-click` so it cannot drift).                                                                                                                                                                                                                                                                                                                                                          | F6          | no                                                                      |
| 11   | **Downstream and cleanup.** Migrate the ten `dev/generate_versions.py` and the action; then delete `utils/io.py`, `utils/mapping.py`, `bounds.get_package_bounds`. Declare `1.0.0` when the properties hold and the downstream repositories run on the new API.                                                                                                                                                                                                                                                                                                                                                                                           | F15         | yes                                                                     |

Steps 1 and 2 need no other step; 2b needs 2 (the registry keys are canonical before the new methods
are added). Steps 3 to 6 are independent of each other except that 4 uses the
`Requirement` change of 3. Step 7 needs 2 (names), 2b (the `versions` list moves into the JSON) and 6 (the project fetch). Step 8 needs 1 and 3.

## 8. Tests and gates

The conventions of `CLAUDE.md` apply: one behaviour per test, literal expected values, a regression
test for every bug (checked to fail on `main` with `git stash push src`), no local imports, no
unseeded randomness, 100 % coverage of what changes, no `# pragma: no cover` on code that can be
tested.

- **The shipped data, asked real questions (F1, F17).** `tests/integration/compat/test_data.py`, no
  patch, no network:
  - `find_closest_version("numpy", "99.0.0", Target("3.9", os="linux", arch="x86_64")) == "2.0.2"`;
  - the same with `Target("3.9")` (platform unspecified) gives `"2.0.2"`;
  - `find_closest_version` through `install_package_closest_version` with only `run_command` patched
    receives the clamped version (the unit test), and the offline integration test below receives
    the real command.
- **Data contract** (unit, fast): every `data/*.json` parses; the file name is the canonical name;
  every entry is a valid `Target`; the entries are exactly the grid `PYTHON_VERSIONS` x free-threaded
  x platforms (60 per package today); every range has `min <= max` and parses; the entries are
  sorted; `generated` is an ISO date. This replaces a test per generated module.
- **Registry** (`test_registry.py`): the table of 3.5 as parametrised tests (fully specified,
  platform unspecified, equal specificity, an entry with `os=None` beaten by a concrete entry, explicit `[]`,
  unknown package); `has_package`; canonical names; invalid range at `register`; the state is not
  created on a failed `register`; `state` is read-only.
- **Version requests (issue #1032)**, `tests/unit/version/test_request.py` and the registry tests,
  one behaviour per test, with the acceptance list of the issue:
  - the parser: `None`, `""` and `"  "` are latest; `"2.4.0"` and `"2.4.0rc1"` are exact; `"2.4.*"`
    and `"2.*"` are prefixes `(2, 4)` and `(2,)`; `"*"`, `"2.*.1"`, `"2.4.*.dev"`, `"2.4*"`,
    `".*"`, `"2.4.0rc1.*"`, `"1!2.*"` raise `ValueError` with `match` on the message and are **not**
    `InvalidVersion`; a malformed exact version raises `InvalidVersion`;
  - `matches`: `2.4`, `2.4.0` and `2.4.17` match `2.4.*`; `2.40`, `2.5` and `2.3.9` do not; the
    zero padding (`2` matches `2.*`); `entirely_below` for the three kinds;
  - `is_valid_version` on a hand-built registry **and** on the shipped data: `2.4.*`, `2.*`, `""`,
    `None`, a wildcard with no match (`1.24.*` on Python 3.14), a wildcard on a package with no data,
    on a package with ranges but no `versions`, on an entry registered with `[]`, and the exact
    version (unchanged);
  - `find_closest_version`: an open-ended range returns the request (`"2.*"`, `""`); a closed range
    returns the concrete latest match (`1.*` on 3.9 gives the last `1.x` that supports 3.9); no
    match raises `UnsupportedVersionError` with a message that names the request and the target;
  - `get_compatible_versions` as a whole literal for one package and one target, ascending order,
    pre-releases absent, the input list not mutated;
  - `install_package_closest_version` with only `run_command` patched: `""` and `None` install the
    package without a pin, `"2.*"` installs `==2.*` (open) or `==1.26.4` (closed), a wildcard with no
    match raises before any command runs (the unit test), and the offline integration test below runs
    the real command for `""`;
  - the resolvers: `pandas==2.1.*` pins `numpy<2.0.0`, `pandas==2.*` and `""` do not,
    `jax==0.4.*` adds `jaxlib==0.4.*` and no `numpy` pin;
  - the CLI: `--pkg-version=` (empty), no `--pkg-version`, `--pkg-version='1.*'`, and the exit codes;
  - the data contract: `versions` is sorted, unique, stable and PEP 440 valid, and every `min`/`max`
    is in it. **Regression test** (fails on `main`): `is_valid_version("numpy", "2.4.*", t)` and `""`
    no longer raise `InvalidVersion`.
- **Wheel tags**: one parametrised test over real file names: `manylinux` x86_64 and aarch64,
  `macosx_*_x86_64`, `macosx_*_arm64`, `universal2` (two tags), `cp39-abi3-macosx_10_9_universal2`,
  a compressed macOS tag (two tags), `cp313t`, `cp315-abi3t` (`abi3=True, free_threaded=True`),
  `win_amd64`, `win_arm64`, `py3-none-any`, `py2.py3-none-any`, and the out-of-scope `musllinux`,
  `win32`, `i686`, `armv7l` (empty, asserted).
- **Discovery**: a trimmed recording of the Simple API response of one package of each kind
  (`numpy`, `jax` + `jaxlib`, `polars` + `polars-runtime-32`, `pydantic` + `pydantic-core`,
  `duckdb`), stored in `tests/data/`, served by a patched `fetch_pypi_project`; the **whole** output
  of `discover_compat_targets` is asserted against a literal (the `CLAUDE.md` rule for composite
  values). One network test in `tests/integration/` regenerates a small package and checks the shape.
  **Gate of step 7(a):** `python dev/generate_compat_data.py` on the old and the new code gives
  byte-identical files.
- **Installers**: unit tests of `command()` as a whole list; `PipInstaller` starts with
  `sys.executable`; `InstallerSpec` arguments are not re-split. **Integration**
  (`tests/integration/install/test_pip_offline.py`): build a pure-Python wheel with `zipfile` in
  `tmp_path` (about 20 lines), run `install_package` with
  `--dry-run --no-index --find-links <tmp_path>`; the test fails if the command does not target the
  interpreter that runs the test. A second test does the same with `uv` (`uv_available` mark).
- **Resolvers**: the table as a whole against a literal; each of the seven packages below and at the
  minimum version; the jax cases (`0.4.25`, `0.4.26`, `0.4.9`, a wildcard); a spec with no version
  returns the package alone.
- **Imports** (the tests of `coola.utils.imports` are ported with the code): `availability_cache` registers
  the function and `clear_availability_caches` resets it; a patched `find_spec` is re-read after the
  clear; `module_available` returns `False` and logs for a module that raises on import;
  `package_available` returns `False` for `ImportError` and `ValueError`; `MissingPackageError`
  is a `ModuleNotFoundError` with `.name` and a `RuntimeError`; `install_package` clears the caches
  after a success and not after a failure; `lazy_exports` (`__getattr__`, `__dir__`, unknown name).
- **Import weight** (`tests/integration/test_import_weight.py`, subprocess): after `import feu`,
  `import feu.compat` and `import feu.install`, none of `requests`, `urllib3`, `click`, `git`,
  `rich`, `pytest` is in `sys.modules`. It asserts a **set of modules**, not a duration (no flaky
  timing test); the PR description reports the `-X importtime` numbers.
- **Layering**: a test that parses the imports of `src/feu` (with `ast`) and checks the order of
  property 13 (a lower layer never imports a higher one).
- **PyPI**: unit tests on a recorded Simple API document: PEP 440 order, `start_date`/`end_date` in
  UTC, yanked, a release without files, canonical name in the URL, immutability of the returned
  mappings, the cache key is the canonical name.
- **CLI**: `CliRunner` for each command and each exit code (`0`, `1`, `2`), stdout holds only the
  answer, stderr holds the message; a subprocess test of `python -m feu find-closest-version ...`
  with real data (the contract of the external action); `--version`; `package-versions` on a
  `pyproject.toml` in `tmp_path`.
- **`tests/package_checks.py`** (run on the built wheel): add `find_closest_version("numpy", "99.0.0",
resolve_target("3.12", os="linux", arch="x86_64"))` and `get_default_compat_registry().packages()`
  so that a wheel without the JSON files fails.
- **Docs**: the examples of the user guide are doctests (`xdoctest` is already a dev dependency), so
  F6 cannot come back.
- Coverage: 100 % of what changes (`--cov=feu --cov-report=term-missing`). Mind the existing
  ruff rule that ignores `PLC0415` in tests (it contradicts `CLAUDE.md`): remove the ignore.

## 9. Decisions for the maintainers

**D1. What does `Target("3.12")` (platform unspecified) mean?** _Recommended: "any platform", answered
by the union of the most specific entries._ It fixes F1 for the documented examples without
changing them, it is consistent with "an unknown package is permissive", and it cannot turn a
supported Python into "unsupported" because one platform lacks a wheel. Alternatives: raise
`ValueError` for an under-specified lookup (loud, but every example of the guide must be rewritten
and `Target(python_version=...)` becomes a trap); the intersection ("valid on every platform"),
which is strict but returns `UnsupportedVersionError` for `torch` on 3.12 because of one missing
platform. Whichever is chosen, `install_package_closest_version` and the CLI use the full current
target.

**D2. Remove `PipxInstaller`?** _Recommended: yes._ `pipx install numpy==2.0.2` creates an isolated
application environment; it does not install into the environment whose compatibility `feu`
checked. No consumer was found. The registry stays open for anyone who registers one.

**D3. Remove `feu.github`?** _Recommended: yes (251 lines, no consumer found in `src`, `dev` or the
searched repositories; it is not about packages or versions)._ If it is used somewhere not searched,
move it to its own distribution instead of keeping it in a package that promises to be light.
`feu.local_git` stays (`iden` uses it, and version tags are version management). The repositories of
other owners and private repositories were not searched.

**D4. HTTP: keep `requests` as the optional dependency?** _Recommended: yes, imported lazily._ The
alternative is the standard library (`urllib.request`): no extra, no fallback, fewer lines. The
reason not to is TLS certificates: `requests` carries its own CA bundle, `urllib` uses the system
store, and some macOS Python distributions are known to fail on `https://` until a certificate step is run (from experience, not tested here); a
package that exists to manage environments should not fail there. If the maintainers accept that
risk, `feu[requests]` can disappear and property 1 gets stronger.

**D5. Discoverers as data instead of classes?** _Recommended: yes (3.5)._ It removes the base
class, the registry, four subclasses and about 750 lines, and a new case is a table entry. The cost
is that a user cannot plug a custom discoverer _class_; they pass `companion=` or call the building
blocks. If a plugin point is wanted, keep `Registry[Callable]` keyed by package: it is one line
once `Registry[T]` exists.

**D6. Out-of-scope platforms.** _Recommended: `musllinux`, `win32`, `i686`, `armv7l`, `ppc64le`,
`s390x` are explicitly out of scope and tested._ `Target.os == "linux"` means glibc (`get_current_os`
returns `linux` on Alpine too). Ignoring musl is safe in practice (a release that only has musl
wheels is rare) and keeps the vocabulary (`linux`/`macos`/`windows`, `x86_64`/`arm64`) closed. The
alternative is to map `musllinux` to `linux`, which over-reports support for Alpine users.

**D7. `abi3t`.** _Recommended: parse it as a free-threaded stable-ABI tag._ It is a wheel tag for
the free-threaded stable ABI; today it is read as an exact-version tag, which under-reports forward
compatibility. This was observed on the parser only; check the final tag spelling against the PEP
and against the first real wheel before relying on it.

**D8. The behaviour change of a resolver without a version.** _Recommended: no pin._ A spec without
a version asks pip for the latest release, which satisfies every `numpy<2` rule; the two
`RuntimeError("Missing package version")` are removed. Alternative: keep raising.

**D9. CLI exit codes.** _Recommended: `1` for "unsupported" and for "invalid", `2` for usage._
This is breaking for any script that reads stdout and ignores the status. The one consumer found
benefits (F16). `check-valid-version` keeps printing `True`/`False`.

**D10. Python versions in the data.** _Recommended: one constant, `PYTHON_VERSIONS`, in
`compat/target.py`; oldest is the oldest version that downstream CI matrices still ask for, newest
is the latest release plus the next pre-release; the data-contract test fails when the files and the
constant disagree._ Today it is `3.9` to `3.15` while `requires-python` is `>=3.11`; the maintainers
know whether `3.9` and `3.10` are still requested (they are EOL). The yearly edit is one line plus a
regeneration.

**D11. Shipped data as JSON rather than Python.** _Recommended: JSON, one file per package,
flat._ Lazy per-package loading is the gain (no 0.10 s, no 3,500 lines of generated code in the
diff); the flat layout is chosen over grouping platforms with equal ranges (361 distinct groups for
1,020 entries) because it is trivial to read and to diff, and its size is small. Alternative: keep
Python modules and only fix the generator (sorted, formatted, dated). It works, but keeps the import
cost and the list-in-three-places problem.

**D13. Names of the availability checks.** _Recommended: adopt the `coola` names
(`package_available`, `module_available`) as the main ones and keep `is_package_available` and
`is_module_available` as public aliases._ The aliases cost two lines and spare `arkas` and the
`feu.testing` marks a rename; they can be deprecated in the migration page later. Alternative: keep
the `is_*` names only (no change for users, but two vocabularies across the sibling libraries).

**D14. Where does a wildcard find its versions?** _Recommended: a `versions` list in each data file
(3.9)._ Alternatives: (a) match the prefix against the **ranges** only (no data change): offline and
tiny, but `"2.9.*"` is "valid" for a package that never had a `2.9`, so `is_valid_version` can say
`True` for an uninstallable request, which is the failure the issue wants to remove; (b) ask PyPI
(`fetch_pypi_versions`) at call time: exact, but it makes `is_valid_version` a network call, which
breaks properties 1 and 9 and the offline tests. The list can be stale between two weekly
refreshes, which is why an open-ended range is handed to `pip` (3.9).

**D15. Where we deviate from the text of the issue.** _Recommended: accept the deviations._
(1) A wildcard that names a pre-release segment (`2.4.0rc1.*`) raises `ValueError` at parse time;
the issue says pre-releases are ignored "unless the wildcard itself names one", but PEP 440 has no
such wildcard and the data holds stable releases only. (2) The function takes a `Target`, not a
`python_version`, because the signature on `main` already does (the issue quotes an older one).
(3) `find_closest_version` is extended to requests too (the issue is about `is_valid_version`),
because "it should install the latest valid version" needs the same resolution. (4) An epoch
(`1!2.*`) is rejected.

**D16. Wildcard or empty request for a package with no data.** _Recommended: as the issue says,
`is_valid_version` is `False` and `find_closest_version` returns the request unchanged, so the
caller decides._ This is deliberately not the permissive answer that an unknown package gets for an
**exact** version (property 4): an exact version can be installed and pip will fail loudly if it
does not exist, but "is there at least one compatible version?" cannot be answered without data.
`registry.has_package(name)` lets a caller tell "no data" from "no match". Alternative: raise
`ValueError` for "no data".

**D12. Release number.** _Recommended: release steps 1 and 2 as patch/minor versions (they are
fixes), steps 3 to 9 as `0.9.0`, and call it `1.0.0` when step 11 is done._ The docs already say no
API is stable before 1.0.

## 10. Not covered

- **Installing into another environment** (`--python /path`): a different feature from "install into
  the environment that runs `feu`". If wanted, it is one `target` plus one `python` on
  `InstallerSpec`, designed together.
- **Other installers** (`poetry`, `conda`, `uv add`): the registry accepts them; none is built in.
- **musl and 32-bit platforms**, **PyPy**, **GraalPy**: D6. The data covers CPython only.
- **Compatibility dimensions other than Python/free-threading/OS/arch**: CUDA builds of `torch`,
  BLAS flavours, macOS minimum versions, glibc versions. The tags that encode them are ignored.
- **Staleness of the data.** A range that ends at the latest release is open, which assumes future
  releases keep supporting the Python version. The `generated` date is stored in each file; exposing
  it (`CompatRegistry.generated(package)`) is cheap and is left for when someone needs it.
- **The PyPI Simple API for the pinned-dependency lookup.** `core-metadata` (PEP 658) would avoid
  the per-release JSON request, but the `.metadata` file must then be downloaded and parsed; the
  per-release JSON endpoint is not deprecated and is kept.
- **Full specifiers as a request** (`>=2,<3`, `~=2.4`, `!=2.4.1`): the request has three forms. A
  specifier set would be a fourth form (`SpecifierSet.filter` on the known versions) and is a clean
  extension of `VersionRequest`; it is left out because the issue asks for the three.
- **Other index servers** (`--index-url`): `feu` talks to `pypi.org` only.
- **The GitHub Actions workflows** (`.github/workflows/`), the `.make/` subtree and `docs/mkdocs.yml`
  were not audited; only the files named in section 5 were looked at. `review/suggestions.md` made
  the same exclusion.
- **Verification of the shipped values** against PyPI: F2 shows the generator was wrong for some
  wheels, so a spot check after step 7(b) is part of that step.

## Appendix: effect on the size of the package

Lines of `src/feu`, today (counted) and expected (**estimates**, from the code to delete and the
sketches above; the gate is the behaviour of sections 1 and 8, not the size).

| Area                                                  | Today  | Expected    | Why                                                                                                                                                            |
| ----------------------------------------------------- | ------ | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `imports`                                             | 692    | about 400   | the port of `coola.utils.imports` (about 200 for `package.py`, 120 for `optional.py` with four pairs, 60 for `lazy.py`); the five copies and the decorators go |
| `utils` (with `fallback`)                             | 827    | about 520   | no fallback modules, no `PackageDependency`/`extract_*`; plus `Registry` (50) and `run_command`                                                                |
| `version`                                             | 1,517  | about 1,030 | one `fetch_latest_versions`, one pyproject reader, one project fetch; plus the frozen types and `request.py` (about 80)                                        |
| `compat` without discovery or data                    | 1,096  | about 700   | `matrix.py` split and shrunk, `packages.py` gone, wheel tags on `packaging`; plus `get_compatible_versions` and the request resolution (about 60)              |
| `compat/discoverers`                                  | 1,122  | about 300   | one algorithm and two tables                                                                                                                                   |
| `compat/discovered` (Python data)                     | 3,546  | 0           | 17 JSON files (a few KB each) read lazily                                                                                                                      |
| `install`                                             | 1,339  | about 480   | one `Installer`, one resolver table, no ABC, no class-level registries; resolvers reason on requests (about 30 more)                                           |
| `github`                                              | 251    | 0           | D3                                                                                                                                                             |
| root (`__main__`, `local_git`, `testing`, `__init__`) | 589    | about 560   | `cli.py` gains `target_options` and `package-versions`; the fallback branches go away                                                                          |
| **Total**                                             | 10,979 | about 4,000 | about 3,400 of the 7,400 lines of code go, and the 3,500 lines of data leave the code                                                                          |

The unit tests shrink in the same places (one test per generated data module, one per resolver
subclass, one per `imports/*` copy are replaced by parametrised tests), and the tests that patch the
collaborator are completed by the integration tests of section 8, so that a defect like F1 is caught
by a test that asks a question of the real data.
