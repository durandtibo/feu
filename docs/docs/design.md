# Design

This page describes how `feu` is designed: the properties you can rely on, the examples that
show them, and the main design choices with their trade-offs. The trade-offs are there so you can
judge whether the current design fits your use case.

## Properties

These are the rules `feu` follows. Each one is enforced in one place, not by the discipline of each
function.

| #   | Property                                  | What you can rely on                                                                                                                                                                                                                                                      |
| --- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Lightweight**                           | The only required dependency is `packaging`. `import feu`, `import feu.compat` and `import feu.install` import no optional library, read no file other than code, and do no network call.                                                                                 |
| 2   | **Explicit optional dependencies**        | A feature that needs `click`, `gitpython`, `requests` or `rich` checks it first. A missing package raises `MissingPackageError` (a `ModuleNotFoundError` and a `RuntimeError`) whose message gives the `pip` and `uv pip` command.                                        |
| 3   | **Target-aware**                          | A compatibility answer is a function of `(package, version, Target)`. Code that acts on the current environment uses the full current target (`resolve_target()`).                                                                                                        |
| 4   | **No silent no-op**                       | Every field of the target is used or the call fails. A field left to `None` means "any platform". An unknown package is permissive and can be detected with `registry.has_package`.                                                                                       |
| 5   | **Data-driven and reproducible**          | The built-in constraints are generated from the wheels published on PyPI by one command (`dev/generate_compat_data.py`), sorted and dated. No constraint is written by hand.                                                                                              |
| 6   | **Extensible by registration**            | A package constraint, an installer or a dependency resolver is added by registering one value in a registry instance. No subclassing is needed to add data, and no registry is process-global class state.                                                                |
| 7   | **Standards compliant**                   | Package names are canonicalised once (PEP 503), versions are `packaging` versions (PEP 440), requirements are `packaging` requirements (PEP 508) and wheel names are parsed by `packaging`.                                                                               |
| 8   | **No shell, no string-built command**     | An external command is an argument vector. `pip` runs as `sys.executable -m pip`, so it installs into the interpreter that runs `feu`. The command is logged before it runs.                                                                                              |
| 9   | **Fresh and immutable**                   | The checks of packages, modules and optional libraries are cached and `clear_availability_caches()` resets them (`install_package` calls it after a success). The PyPI and GitHub values that are cached are immutable, so no caller can corrupt a cache.                 |
| 10  | **Deterministic order**                   | Versions are ordered by PEP 440, never as strings. A mapping that is returned or written is sorted. The generated data has a date and no timestamp.                                                                                                                       |
| 11  | **A thin CLI**                            | The CLI is the same API behind `click`. Standard output holds only the answer (it is used in `$(...)`), logs go to standard error, the exit status carries the result (`0` ok, `1` negative answer, `2` usage error).                                                     |
| 12  | **Strict, typed, documented**             | New options are keyword-only. Invalid input raises `ValueError` or `TypeError` with an explicit message. Every public function has a doctest, and the examples of this guide are doctests too.                                                                            |
| 13  | **Layered**                               | The imports go one way: `imports`, `utils`, `version`, `compat`, `install`, `cli`. `imports` imports nothing from `feu`. A test checks it.                                                                                                                                |
| 14  | **Cross-platform, Python 3.11 and newer** | Linux, macOS and Windows behave the same: there is no `shlex` rule that depends on `os.name` and no `PATH` lookup of `pip`.                                                                                                                                               |
| 15  | **A version is a request**                | Wherever a function takes the version of a package to install or to validate, it accepts an exact version (`2.4.0`), a wildcard (`2.4.*`) or an empty string / `None` (the latest). A request with no compatible version raises `UnsupportedVersionError`, never crashes. |

The target is used entirely (property 4), and the answer for a target without a platform is the
union over the platforms:

```pycon
>>> from feu.compat import Target, find_closest_version
>>> find_closest_version("numpy", "99.0.0", Target("3.9"))
'2.0.2'

```

Package names are canonical (property 7), so the spelling does not matter:

```pycon
>>> from feu.compat import get_default_compat_registry
>>> registry = get_default_compat_registry()
>>> registry.has_package("Scikit_Learn")
True

```

A version request is parsed by one parser (property 15):

```pycon
>>> from feu.version import parse_version_request
>>> [str(parse_version_request(text)) for text in (None, "", "2.4.0", "2.*")]
['', '', '2.4.0', '2.*']

```

The orders are PEP 440 orders (property 10):

```pycon
>>> from feu.version import sort_versions
>>> sort_versions(["1.10.0", "1.9.0", "1.2.0"])
['1.2.0', '1.9.0', '1.10.0']

```

An external command is an argument vector built from the interpreter (property 8):

```pycon
>>> import sys
>>> from feu.install import PipInstaller
>>> PipInstaller.prefix == (sys.executable, "-m", "pip", "install")
True

```

## Benchmark properties

`feu.benchmark` (the `feu benchmark-trend` command) follows the properties above and adds the ones of
this table. Each one is true by construction in one place, not by the discipline of each function.

| #   | Property                           | What you can rely on                                                                                                                                                                                                                               |
| --- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B1  | **Lightweight**                    | `feu.benchmark` uses only the standard library. Importing it imports no optional library, reads no file and does no network call. The command needs `click` like every command.                                                                    |
| B2  | **Read-only unless asked**         | Loading and reporting never change the storage. Files are deleted only by `prune_runs`, which the command calls only with `--prune`, and only after the report was built.                                                                          |
| B3  | **Strict input, loud failure**     | A file that looks like a `pytest-benchmark` result is validated. A malformed file, a time that is not a finite number greater than zero or an invalid argument raises `ValueError` that names the file or the argument. No result gives a message. |
| B4  | **One stable label per benchmark** | The label is a function of the entry, so it is the same in every run. Two entries of a run with the same label make the load fail instead of keeping one of them.                                                                                  |
| B5  | **Comparable runs only**           | A run is compared only with runs of the same machine (the directory of `pytest-benchmark`), the same kind and the same statistic.                                                                                                                  |
| B6  | **Honest numbers**                 | A time has three significant digits in `s`, `ms`, `us` or `ns`. A change is never computed from a zero.                                                                                                                                            |
| B7  | **Deterministic output**           | The same storage gives the same bytes: rows are sorted by `(value, label)`, regressions by `(-change, label, machine)`, files by path and runs by `(date, machine)`.                                                                               |
| B8  | **Safe, portable output**          | A label cannot break a Markdown table or a GitHub workflow command (both are escaped). Files are read and the report is written as UTF-8 on every platform.                                                                                        |
| B9  | **A thin command**                 | The standard output holds only the Markdown report, annotations and messages go to the standard error, and the exit status carries the result: `0` ok, `1` a regression with `--fail-on-regression`, `2` a usage error.                            |
| B10 | **Pure core, I/O at the edge**     | One module reads and deletes files. The analysis and the rendering are pure functions of values. The results are frozen dataclasses.                                                                                                               |
| B11 | **Strict, typed, documented**      | Options are keyword-only and every public function has a doctest. The format is tested against a result written by the real `pytest-benchmark`, not only against hand-written dictionaries.                                                        |

The label of a benchmark is the same for a parametrized and a plain test (B4), and a run is a value
with a machine (B5):

```pycon
>>> from datetime import UTC, datetime
>>> from feu.benchmark import Run, find_regressions
>>> date = datetime(2026, 1, 1, tzinfo=UTC)
>>> runs = [
...     Run(date, "linux", {"sort[10]": 0.001}),
...     Run(date, "linux", {"sort[10]": 0.003}),
...     Run(date, "mac", {"sort[10]": 0.010}),
... ]
>>> [(item.machine, item.label, item.change) for item in find_regressions(runs)]
[('linux', 'sort[10]', 200.0)]

```

## Design choices and trade-offs

### A target without a platform means "any platform"

`Target("3.12")` leaves `os` and `arch` to `None`. In a lookup, `None` means "any platform", and the
answer is the union of the ranges of the most specific matching entries. A package is therefore never
reported as unsupported because one platform lacks a wheel.

- _Alternative: raise `ValueError` for an under-specified target._ It is loud, but every call that
  only cares about the Python version needs the platform too.
- _Alternative: the intersection ("valid on every platform")._ It is strict, but a package such as
  `torch` becomes unsupported on a Python version because of a single missing platform.
- _Consequence:_ the answer of a lookup without a platform is optimistic. Code that acts on the
  current environment (`install_package_closest_version`, the CLI `install` command) always uses the
  full current target, so it never installs a version that the platform cannot run.

### Only the current platform is a target

The platform is not an option of `resolve_target` or of the CLI (no `--os`, no `--arch`): it is the
platform of the interpreter. `Target.os` and `Target.arch` still exist, so the data and the lookups
can be about another platform, and more platforms can be added without changing the model. The
vocabulary is closed (`linux`, `macos`, `windows`; `x86_64`, `arm64`): `linux` means glibc, and the
`musllinux`, `win32`, `i686`, `armv7l`, `ppc64le` and `s390x` wheels are out of scope. Mapping
`musllinux` to `linux` would over-report the support of Alpine.

### Shipped data is generated JSON, one file per package

The built-in constraints are `feu/compat/data/<package>.json`, regenerated from the wheels on PyPI.
The list of packages is the list of files, and a file is parsed the first time its package is looked
up, so importing `feu` costs nothing.

- _Benefit:_ no hand-written constraint, a small diff for each regeneration, and a lazy load.
- _Cost:_ the data is as old as the installed release of `feu` (it holds a date), and the files are
  flat (one entry per target), which is simple to read and diff but larger than grouped ranges.
  Register your own constraints in a `CompatRegistry` to correct or extend it.

### Wildcards are matched against PyPI at call time

The data holds compatible _ranges_, not a list of releases. A wildcard (`1.*`) is matched against the
versions downloaded from PyPI when it is resolved. Exact versions and the empty request need no
download.

- _Benefit:_ a release published after the data was generated is found, and `"2.9.*"` is not valid
  for a package that never had a `2.9`.
- _Cost:_ a network call (cached per process) for a wildcard, and no offline fallback: without
  network access, the error of the download is raised. Pass your own `version_source` to a
  `CompatRegistry` to avoid the network.

### A request with no data

An unknown package is permissive for an exact version: it can be installed, and `pip` fails loudly if
the version does not exist. A wildcard or an empty request cannot be answered without data:
`is_valid_version` is `False` and `find_closest_version` returns the request unchanged, so the caller
decides. `registry.has_package(name)` tells "no data" from "no match".

### Discovery is data, not classes

The packages whose wheels do not carry the platform tags (`jax`, `polars`, `pydantic`, ...) are
described by a table (`COMPANIONS`) and a list of ignored releases, and one algorithm handles every
package. A new case is a table entry, or the `companion=` and `ignore_versions=` arguments.

- _Cost:_ you cannot plug a custom discoverer class. If you need a different algorithm, call the
  building blocks (`parse_wheel_filename`, `is_compatible`) yourself.

### Installers are `pip` and `uv`

An installer builds one argument vector and installs into the interpreter that runs `feu`, the one
the compatibility check was made for. `pipx` is not built in: it creates an isolated application
environment, which is not the environment that was checked. The installer registry stays open, so you
can register another one (see the [architecture](dev/architecture.md) page).

### Dependency resolvers are functions

A resolver maps a `PackageSpec` to a list of requirements (`pandas` before 2.2.2 adds `numpy<2.0.0`).
It reasons on the whole version request, so `pandas==2.*`, which straddles the threshold, gets no
pin. A spec without a version asks `pip` for the latest release and gets no pin either.

### HTTP uses `requests`, imported lazily

`feu[requests]` is optional and imported only when a PyPI or GitHub call is made.

- _Alternative:_ the standard library (`urllib.request`) would remove the extra. `requests` is kept
  because it carries its own CA bundle, while `urllib` uses the system store, which fails on some
  macOS Python distributions. A package that manages environments should not fail there.

### `feu.local_git` and `feu.github` are kept in the package

They are not about packages or versions, but they serve release tooling (the last version tag of a
repository, the metadata of a GitHub repository). They live behind the `git` and `requests` extras,
so they cost nothing when unused. If you only need package management, you never import them.

### The CLI exit status carries the answer

`0` is a success, `1` is a negative answer (an unsupported request, an invalid version) and `2` is a
usage error. `find-closest-version` prints only the version, so `$(...)` captures it and a failing
request stops a script instead of installing `pkg==None`. `check-valid-version` prints `True` or
`False` and uses the same status.

### Availability checks keep the `is_*` names

`is_package_available` and `is_module_available` are the public names, as in the `feu.testing`
marks. The checks of packages, modules and optional libraries are cached with `availability_cache`
(the design of `coola.utils.imports`), so that one call, `clear_availability_caches()`, resets all
of them. The checks of the installer tools (`is_pip_available`, `is_uv_available`) are cached
separately and are not reset by it.

### Python versions of the data

The shipped data covers the Python versions of one constant, `PYTHON_VERSIONS`, in
`feu/compat/target.py`: from the oldest version that CI matrices still ask for to the newest release
and the next pre-release. A test fails when the files and the constant disagree. A Python version
outside the constant has no data, and the package is treated as unconfigured.
