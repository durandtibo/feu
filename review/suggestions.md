# Review of `feu`: suggestions

Review of the repository at `main` (`54c6bf7`). Breaking changes are allowed, so each item says
whether it would break the public API.

## Scope and method

- **Read in full:** every module under `src/feu` except the generated `compat/discovered/*.py`
  data files (I read `__init__.py` and `numpy.py`, and ran the registry built from all of them),
  plus `dev/`, `debug/`, `tasks.py`, `pyproject.toml`, the README, and `docs/docs/cli.md`.
- **Skimmed only:** `tests/` (structure, conventions, and greps against the rules in `CLAUDE.md`),
  and `.github/workflows/` (only `ci.yaml`, plus the file list). I did not audit each workflow, so
  there is no CI/CD section below.
- **Baseline:** `ruff check` and `ty check` are clean. `pytest tests/unit` gives 921 passed and
  2 skipped, with 100% line and branch coverage. The suggestions below are therefore about design
  and behaviour, not lint.
- **Verified vs. read from code:** items marked **[verified]** were reproduced by running code.
  The others come from reading the source. I did not run the network paths (PyPI, GitHub) or
  the real `pip`/`uv` commands.

## Summary, by priority

| #   | Item                                                                                       | Type                | Breaking    |
| --- | ------------------------------------------------------------------------------------------ | ------------------- | ----------- |
| P1  | `install_package_closest_version` never clamps the version **[verified]**                  | Bug                 | No          |
| P2  | Installers call `pip` from `PATH`, not the running interpreter                             | Bug / design        | Mostly no   |
| P3  | Wheel tag parsing drops `universal2`, compressed platform tags, `musllinux` **[verified]** | Bug (data quality)  | No          |
| P4  | `include_lower_bound` ignores `lower is None` in two functions                             | Bug (doc mismatch)  | No          |
| P5  | `latest_version` / `latest_*_versions` return normalized strings **[verified]**            | Bug                 | Slight      |
| P6  | Package names are normalized in some places and not in others **[verified]**               | Bug / design        | No          |
| P7  | Availability checks are cached forever, even though `feu` installs packages                | Bug                 | No          |
| P8  | Commands are built as strings and then re-split with `shlex`                               | Design / robustness | Yes (small) |
| P9  | CLI inconsistencies (`install` has no target options, `--free-threaded`, etc.)             | Design              | Yes (CLI)   |
| P10 | Four hand-written registries with the same logic                                           | Duplication         | Optional    |
| P11 | Three PyPI fetches of the same JSON; sorted-as-string API; `releases` field                | Design / perf       | Yes (small) |
| P12 | Mutable objects returned from `lru_cache`d functions                                       | Bug (latent)        | No          |
| P13 | Duplication in `imports/`, resolvers, discoverers, platform helpers                        | Duplication         | Optional    |
| P14 | Hardcoded lists that must be kept in sync by hand                                          | Maintainability     | No          |
| P15 | Smaller API, docs, and test-config items                                                   | Misc                | Mixed       |

---

## P1. `install_package_closest_version` never clamps the version **[verified]**

**Where:** `src/feu/install/utils.py` (`install_package_closest_version`), `src/feu/__main__.py`
(`install`), `src/feu/compat/registry.py` (`_matches`).

**Problem.** `install_package_closest_version` builds `Target(python_version=get_python_major_minor())`,
so `os` and `arch` are `None`. Every entry in `feu.compat.discovered` is registered with concrete
`os` and `arch`. `CompatRegistry._matches` requires an entry's `os`/`arch` to be `None` or equal to
the lookup's, so no entry matches. The package then counts as "unconfigured", which is permissive,
and the requested version is returned unchanged.

```text
find_closest_version("numpy", "2.3.0", Target(python_version="3.9"))
    -> '2.3.0'      # wrong: numpy on 3.9 tops out at 2.0.2
find_closest_version("numpy", "2.3.0", Target(python_version="3.9", os="linux", arch="x86_64"))
    -> '2.0.2'
```

So the headline feature of the library ("install the closest compatible version", and the CLI
`install` command) is currently a no-op for every package in the built-in registry. The unit tests
pass because they use `Mock`/`patch` or hand-built registries with `os=None` entries.

**Proposal.**

1. Use `resolve_target()` in `install_package_closest_version`, so the target is the current
   Python, free-threaded status, OS, and arch. Add an optional `target: Target | None = None`
   keyword so callers can override it. The docstring says "the OS and the CPU architecture are not
   considered", which should become either false or an explicit opt-out.
2. Make an under-specified lookup meaningful in the registry. Options: (a) a lookup with
   `os=None` matches any entry and uses the intersection or union of the ranges, or (b) raise
   `ValueError` when the lookup target is under-specified and the package has only concrete
   entries. Option (b) is a loud failure instead of a silent no-op, which is better here.
3. Add a real integration test, with no mock, that asserts
   `find_closest_version("numpy", "99.0.0", Target("3.9", os="linux", arch="x86_64")) == "2.0.2"`
   against the shipped data, and one that goes through `install_package_closest_version` with only
   `installer.install` patched.

**Breaking:** no (behaviour fix).

## P2. Installers call `pip`/`uv`/`pipx` from `PATH`, not the running interpreter

**Where:** `src/feu/install/pip/installer.py`, `src/feu/install/utils.py`
(`is_pip_available`, `is_uv_available`, ...).

**Problem.** `PipInstaller` emits `pip install ...`. `pip` on `PATH` is often a different
interpreter from the one running `feu` (system `pip`, a different venv, `pyenv` shims). The
compatibility check uses `sys.version_info` of the _current_ interpreter, but the install may
target another one. `is_pip_available()` uses `shutil.which("pip")`, which has the same mismatch.
A venv with `pip` installed but not on `PATH` (for example when run as `python -m feu`) is
reported as having no pip.

**Proposal.**

- `PipInstaller` should run `[sys.executable, "-m", "pip", "install", ...]`.
- `UvInstaller` should pass `--python sys.executable`, and `uv` itself is found with `shutil.which`.
- `PipxInstaller` is a different tool: `pipx install` installs an application into an isolated
  venv, so "install `numpy==2.0.2` with pipx" is rarely what anyone wants, and it ignores the
  environment. Consider documenting this or removing it.
- Make `is_pip_available` check `importlib.util.find_spec("pip")`.
- Optionally let `InstallerSpec` or the installer take an explicit `python` executable.

**Breaking:** mostly no. The `pip` command line changes, and tests asserting the exact string
change.

## P3. Wheel tag parsing drops wheels it should keep **[verified]**

**Where:** `src/feu/compat/wheel_tags.py` (`parse_wheel_filename`, `parse_os`, `parse_arch`).

Checked with real filenames:

| Filename platform tag                  | Result        | Expected                                   |
| -------------------------------------- | ------------- | ------------------------------------------ |
| `macosx_11_0_universal2`               | `[]`          | macOS `x86_64` **and** `arm64`             |
| `macosx_10_9_x86_64.macosx_11_0_arm64` | only `x86_64` | both architectures                         |
| `musllinux_1_2_x86_64`                 | `[]`          | Linux `x86_64` (or a documented exclusion) |

- `universal2` has no `x86_64`/`arm64` substring, so `parse_arch` returns `None` and the whole
  wheel is dropped. A package that only published `universal2` macOS wheels for some releases
  looks unsupported on macOS for those releases.
- Only the first dot-separated platform component is read (`platform_tag.split(".")[0]`), but PEP
  425 compressed tags can list several platforms with different architectures.
- Because `discovered/*.py` is generated from this parser, the errors are baked into the shipped
  data (for example the `macos`/`arm64` minimum versions in `numpy.py` may be too high).

**Proposal.**

- Return one `WheelTags` per platform component, and map `universal2` (and `universal`, `intel`,
  `fat64`, ...) to the set of architectures it contains.
- Decide explicitly about `musllinux`. Either treat it as `linux` (if the registry only has
  `linux`) or document that musl is out of scope and add it to a test. Today it is dropped silently
  because it does not start with `linux` or `manylinux`.
- Prefer `packaging.tags.parse_tag` and `packaging.utils.parse_wheel_filename` over a hand-rolled
  split. They handle compressed tag sets and name normalization. `packaging` is already a
  dependency.
- `free_threaded = abi_tag.endswith("t")` also matches any other ABI tag ending in `t`. Compare
  against the `cpXYZt` pattern instead.
- Regenerate `discovered/*.py` afterwards, and review the diff, since it will change.

**Breaking:** no for the API. The shipped data changes.

## P4. `include_lower_bound` contradicts its documentation

**Where:** `src/feu/version/package.py`, `fetch_latest_major_versions`,
`fetch_latest_minor_versions` (and `*_map`).

The docstrings say the flag "has no effect if `lower` is `None`". The code is
`if include_lower_bound and versions:` with no `lower is not None` check, so with `lower=None` it
prepends the oldest stable version. `fetch_sampled_latest_minor_versions` does check
`lower is not None`, so the three functions disagree. `dev/generate_versions.py` passes
`include_lower_bound=True` for dependencies that may have no lower bound, so this affects the
generated `dev/config/package_versions.json`.

**Proposal.** Add `lower is not None and` to both functions (or change the docs, if the current
behaviour is wanted). Add a regression test for `lower=None, include_lower_bound=True`. Also pull
the shared "latest per group, optionally plus the first version" logic into one helper, since
`fetch_latest_major_versions`, `fetch_latest_minor_versions`, and their two `_map` functions are
four copies of each other.

**Breaking:** no.

## P5. Version helpers return re-serialized strings **[verified]**

**Where:** `src/feu/version/comparison.py` (`latest_version`), `src/feu/version/filtering.py`
(`latest_major_versions`, `latest_minor_versions`).

These return `str(Version(v))`, not the input string. `latest_version(["1.0-1", "1.0"])` returns
`'1.0.post1'`, which is not a string that was in the input and may not be a valid PyPI release key.
Code such as `fetch_pypi_wheel_filenames(pkg)[latest]` can then raise `KeyError`. The other
filters (`filter_*`) return the original strings, so the module is inconsistent.

**Proposal.** Return the original string: `max(versions, key=Version)`; keep a
`{Version: original}` map in the `latest_*_versions` functions. Parse each version once in
`filter_*` instead of repeatedly.

**Breaking:** slight (output spelling for non-canonical input only).

## P6. Package names: inconsistent normalization **[verified]**

Python package names are case-insensitive and treat `-`, `_`, `.` as equivalent (PEP 503).
`feu` has three behaviours:

- `version.bound.normalize_package_name` lowercases and replaces `-` with `_`. It does not collapse
  `.` or runs of separators, and its own docstring says it is "unlike the full PEP 503
  normalization".
- `CompatRegistry`, `CompatDiscovererRegistry`, `DependencyResolverRegistry`, and
  `fetch_pypi_pinned_dependency_version` use the name verbatim. For example,
  `is_valid_version("Scikit-Learn", ...)` is `True` for any version because the name is not found,
  while `is_valid_version("scikit-learn", ...)` is `False` (checked for `0.1` on Python 3.14). A
  caller typing `Scikit-Learn`, `scikit_learn`, or `sklearn` silently gets no checks. The resolver
  registry works around this for `sklearn` with a duplicate entry.
- `compat/packages.get_package_names` and `module_name()` in `dev/generate_discovered_compat.py`
  each do a third kind of normalization.

**Proposal.** Use `packaging.utils.canonicalize_name` everywhere, once, at the boundary: in the
registries' `register`/lookup methods, in the resolver registry, and in the pyproject readers.
Replace `normalize_package_name` with it (or have it delegate). Also make unknown names visible:
`find_closest_version` returns the input unchanged for an unconfigured package, which is the right
default, but `is_valid_version` and the CLI could log at `DEBUG` that the package has no data, and
the CLI could offer `--strict` to fail on unknown packages.

**Breaking:** `normalize_package_name` output changes for names with dots (small).

## P7. Availability checks are cached for the life of the process

**Where:** `src/feu/imports/universal.py` (`is_package_available`, `is_module_available`),
`imports/{click,git,requests,rich,urllib3}.py` (`@cache`), `install/utils.py`
(`is_pip_available`, `is_uv_available`, ...).

`feu` is a package that installs packages. After `install_package(...)` in the same process,
`is_package_available("numpy")` still returns the stale `False`, and `feu.testing` evaluates the
marks at import time. `lru_cache` also makes monkeypatching painful, which is why the tests call
`cache_clear()` (`tests/unit/compat/test_interface.py`, `tests/unit/install/test_utils.py`, ...).

**Proposal.**

- Drop the cache from `is_package_available` (`find_spec` is fast enough) or expose
  `invalidate_caches()` and call it after a successful install.
- `is_module_available` imports the module and so has side effects. Document that more
  prominently, and consider `find_spec` plus an optional `import_module` flag.
- `is_package_available("a.b")` will import the parent `a` to find `a.b`. This is a surprising
  side effect for a function documented as "searched without being imported".

**Breaking:** no.

## P8. Commands are built as strings, then re-split with `shlex`

**Where:** `install/pip/installer.py` (`_generate_command` returns `str`),
`utils/command.py` (`run_bash_command`).

The installers join `["pip", "install", args, *deps]` with spaces and `run_bash_command` calls
`shlex.split` on the result. This is fragile: a dependency or argument containing a space or quote
is split wrongly; `os.name == "nt"` switches to non-POSIX parsing for the whole string, including
the user-supplied `arguments`; and the function is called `run_bash_command` although it never uses
a shell. (`S603` is `noqa`'d.) The extras and version specifiers produced by `PackageDependency`
(`[a,b]`, `>=1,<2`) are only safe because nothing re-interprets them.

**Proposal.**

- Have `_generate_command` return `list[str]`. Parse the user-supplied `arguments` string once,
  with `shlex.split` in the installer constructor, and store `tuple[str, ...]`.
- Rename `run_bash_command` to `run_command(args: Sequence[str])` and make it take a list. Keep a
  thin string wrapper only if a caller needs it.
- Consider `capture_output`/`env`/`cwd` keyword options, and a `dry_run` mode that returns the
  command, which would also make the installers testable without patching.
- `BasePipInstaller` and its three subclasses differ only in the command prefix. A class attribute
  `command: ClassVar[tuple[str, ...]]` removes the three `_generate_command` copies.

**Breaking:** yes, a little (`_generate_command` is protected, `run_bash_command` is public).

## P9. CLI inconsistencies

**Where:** `src/feu/__main__.py`, `docs/docs/cli.md`.

- `install` has no `--python-version`, `--os`, `--arch`, `--free-threaded`, although
  `find-closest-version` and `check-valid-version` do. Combined with P1, `install` cannot target
  anything but "current Python, ignoring the rest".
- `--pkg-extras` and `--installer-name` are declared `required=True` **and** have defaults. The
  docs even say "required; pass an empty string for none". They should be `required=False`.
- `--free-threaded` is `type=bool` (`--free-threaded true`). Use the idiomatic boolean flag
  `--free-threaded/--no-free-threaded` with `default=None`.
- The three commands repeat the same four target options (about 40 lines each). Define one
  `target_options` decorator and apply it.
- `find-closest-version` prints the literal `None` when unsupported, and `check-valid-version`
  prints `True`/`False` and always exits 0. For scripting, exit status should carry the result
  (non-zero when unsupported or invalid) with `--quiet` for plain output. Printing to stdout via
  `print` with `# noqa: T201` could be `click.echo`.
- `feu --version` is not provided (`click.version_option`).
- Nothing configures logging, so the `logger.info("execute the following command: ...")` in
  `run_bash_command` is invisible from the CLI. Add `-v/--verbose`.
- `python -m feu` without `click` gives the fallback no-op decorators and `check_click()` in the
  `__main__` block only. Importing `feu.__main__` without click silently defines undecorated
  functions. That works for the tests, but a `console_scripts` entry point (`feu = feu.__main__:cli`)
  with a clear error would be more usable than `python -m feu`.
- `docs/docs/cli.md` describes `check-valid-version` as "for a Python version", but it takes
  OS/arch/free-threaded too.

**Breaking:** yes for the CLI (flag semantics, exit codes). Provide a migration note.

## P10. Four registries with the same logic

`InstallerRegistry`, `DependencyResolverRegistry`, `CompatDiscovererRegistry`, and `CompatRegistry`
each reimplement `register(name, obj, exist_ok)`, `register_many`, `has_*`, `find_*`, and the same
"already registered, use `exist_ok=True`" error message. They are also inconsistent:

- `InstallerRegistry` and `DependencyResolverRegistry` keep **class-level global state**
  (`ClassVar[dict]`, classmethods), so two tests or two callers cannot have independent
  registries and mutation leaks across tests. The other two are instances behind a `@cache`d
  accessor.
- `DependencyResolverRegistry.add_resolver` takes a `PackageSpec` just to read `.name`, and
  `has_resolver`/`find_resolver` do the same. A `str` is what is meant.
- Two different functions are both called `get_default_registry`: `feu.compat.get_default_registry`
  (a `CompatRegistry`) and `feu.compat.discoverers.get_default_registry` (a
  `CompatDiscovererRegistry`). Both are re-exported through different packages, which is a trap
  for autocompletion. Rename the second one (`get_default_discoverer_registry`).
- Registration helpers are named `add_installer`, `add_resolver`, `register`, `register_many`,
  `register_compat`, `register_discoverers`.

**Proposal.** Introduce one small generic `Registry[T]` in `feu.utils` (register, register_many,
`__contains__`, get with default, `exist_ok` handling, optional key normalization from P6) and
build the four on top of it. Keep module-level default instances behind one `LazySingleton`-style
accessor. Pick one naming scheme (`register`, `register_many`, `has`, `find`).

**Breaking:** optional. Can be done with aliases and deprecation warnings.

## P11. PyPI access: duplicated fetches, string sorting, legacy field

**Where:** `src/feu/version/pypi.py`.

- `fetch_pypi_versions`, `fetch_pypi_requires_python`, and `fetch_pypi_wheel_filenames` each
  download the same `https://pypi.org/pypi/{package}/json` document. Discovering one package
  (`CompatDiscoverer`) calls two of them. The polars and pydantic discoverers add one request per
  release through `fetch_pypi_pinned_dependency_version` (`.../{version}/json`). Introduce one
  `fetch_pypi_project(package)` that is cached and returns a frozen structure, and derive the rest
  from it.
- `fetch_pypi_versions` returns versions "sorted as strings, not according to PEP 440" (documented).
  `"1.10"` sorts before `"1.9"`, `reverse=True` is wrong for real ordering, and every caller has
  to remember to call `sort_versions`. Sort by `Version` (after `filter_valid_versions`, or with
  invalid ones last) and drop the caveat. Note `reverse`, `start_date`, `end_date`,
  `ignore_yanked` are also part of the `lru_cache` key, so each combination re-sorts (cheap) but
  `fetch_pypi_versions(p, reverse=True)` and `(p)` are separate cache entries.
- The package name is interpolated into the URL without `quote()`, and without normalization (P6).
- It relies on the `releases` field of the legacy JSON API. Consider the PyPI Simple API in JSON
  form (PEP 691, with `upload-time` from PEP 700), which has files, yanked flags,
  `requires-python`, and upload times in one cacheable document. Verify the current status of the
  legacy `releases` field before relying on it.
- `fetch_pypi_pinned_dependency_version` compares `requirement.name != dependency`
  case-sensitively (documented), but ignores environment markers: a requirement such as
  `pydantic-core==2.1; python_version < "3.9"` would be picked up for every Python.
  Evaluate `requirement.marker` for the target or skip requirements that have markers or extras.
- `_release_date` returns the UTC date of the earliest file, and `start_date`/`end_date` are plain
  dates; document the timezone.
- `utils/http.py`: the `Session` is never closed (use a context manager); `Retry` is mounted only
  on `https://`; `timeout` passed twice via `**kwargs` raises a confusing `TypeError`; `fetch_data`
  accepts `**kwargs` meant for `requests.get`, which makes the API surface unclear. Consider
  `User-Agent: feu/<version>` and honoring `Retry-After` (urllib3 does by default).

**Breaking:** yes, a little (ordering of `fetch_pypi_versions`).

## P12. Mutable objects returned from `lru_cache`d functions

**Where:** `fetch_pypi_requires_python` (returns `dict`), `fetch_pypi_wheel_filenames` (returns
`dict`), `fetch_github_metadata` (returns `dict`), `fetch_github_repos` (returns a `tuple` of
`dict`s), `get_default_registry` (returns a mutable `CompatRegistry`).

Any caller that mutates the returned dict corrupts the cache for the rest of the process. The
discoverers already `{...}`-copy defensively in places, but nothing enforces it.

**Proposal.** Return `MappingProxyType`/frozen dataclasses, or copy on return. Likewise
`CompatRegistry.state` exposes the internal mutable dict; return a read-only view or a deep copy.

**Breaking:** no for read-only callers.

## P13. Duplication that can be removed

- **`feu/imports/{click,git,requests,rich,urllib3}.py`** are five 90-line copies that differ in the
  package name and pip name. Generate them with a small factory (a dataclass `OptionalDependency`
  with `is_available()`, `check()`, `raise_missing_error()`, and a decorator method), keeping
  the current function names as thin aliases for compatibility. The `*_available` decorators
  silently return `None` when the dependency is missing. That is surprising for a function that
  has a return value, so consider raising by default.
- **`feu/utils/fallback/*`** build fake `click`/`git`/`requests` modules so imports succeed.
  `typing.TYPE_CHECKING or is_x_available()` blocks are repeated in `local_git.py`,
  `utils/http.py`, `__main__.py`, and `compat/matrix.py`. A lazy import inside the function that
  needs the dependency (the pattern `CLAUDE.md` already prescribes for numpy/torch/...) removes the
  fallback modules and the `# pragma: no cover` branches.
- **`install/pip/resolver.py`**: seven `Numpy2DependencyResolver` subclasses differ only by one
  constant (`min_version`). They can be one table `{"pandas": "2.2.2", "scipy": "1.13.0", ...}`
  plus the two special resolvers (jax, default). That removes about 250 lines. Also note
  `JaxDependencyResolver` and `Numpy2DependencyResolver` each repeat the
  `if package.version is None: raise RuntimeError` block, `Version(package.version)` raises
  `InvalidVersion` for non-PEP 440 versions (only wildcards are guarded), and the "numpy < 2"
  knowledge is also encoded, implicitly, in the discovered data.
- **`compat/discoverers/polars.py` and `pydantic.py`** are the same algorithm with two constants
  (`polars-runtime-32` vs `pydantic-core`). Make a `PinnedRuntimeCompatDiscoverer(runtime_pkg)`
  base and let both be two lines. Also, `_is_tag_compatible` in `default.py` and
  `tags_match_exactly` in `utils.py` differ subtly (the former allows pure-Python wheels and
  uses `abi3` the same way). Document which is meant, or unify.
- **`get_python_major_minor()`** (`version/runtime.py`) and **`get_python_version()`**
  (`utils/platform.py`) return the same string. Keep one.
- **`PackageSpec` / `PackageDependency`** overlap (`to_package_dependency` is a thin conversion),
  and `__str__` for `PackageDependency` with multiple specifiers does not insert a space. Consider
  `packaging.requirements.Requirement` for the string form. `PackageSpec.extras: list` and
  `PackageDependency.version_specifiers: list` in a non-frozen dataclass are hashable-unfriendly;
  `frozen=True` with tuples is safer (and `with_version` already copies).
- **`BaseInstaller.equal`**, **`BaseDependencyResolver.equal`** reimplement `__eq__` under another
  name. Implement `__eq__`/`__hash__` (dataclasses would do it). `BasePipInstaller.equal` uses
  `isinstance(other, self.__class__)`, which is asymmetric between parent and child classes.

## P14. Hardcoded lists to keep in sync by hand

- `compat/packages.get_package_names()` lists the 17 packages, and `compat/discovered/` holds one
  module per package. The generator reads the first list to produce the second, and the registry
  discovers the modules with `pkgutil`. A new package needs three edits, in three places, plus
  `DiscovererRegistry` if it is special. Derive the list from one source (a TOML/JSON file under
  `dev/`, or the discoverer registry) and let `get_package_names` read `pkgutil` over `discovered`.
- `compat/matrix.DEFAULT_PYTHON_VERSIONS` includes `3.9`, `3.10` (while `requires-python` is
  `>=3.11`) and `3.15`, and needs a manual edit every October. Reasonable, but document the
  policy and consider deriving the upper bound from `packaging`/`sys.version_info`.
- `dev/generate_discovered_compat.py` writes `repr(dict)` and relies on the pre-commit
  `ruff format` hook to make it readable, so the output is not reproducible without that hook.
  Run `ruff format` on the written file (or emit the formatted source directly), and make the
  output deterministic (sorted targets) so refreshes give small diffs.
- `register_discovered` imports all 17 modules and builds ~1000 `Target` objects the first time the
  registry is touched. I measured about 0.15 s for the registry plus about 50 ms `import feu.compat`
  on this machine. That is acceptable. If it grows, ship the data as a package-data JSON file and
  load it lazily per package, which also removes generated Python from the repo and from the
  line count.
- Data goes stale between releases: `group_into_ranges` makes the last range open-ended
  (`max=None`) when it reaches the latest version, which assumes that future releases keep
  supporting that Python. Consider recording the generation date in each module and exposing it, so
  users can tell how old the answer is.

## P15. Smaller items

**API and behaviour**

- `local_git.get_last_tag_name` sorts tags by the _commit date of the tagged commit_, not by tag
  creation or version. Its docstring says "the tag pointing to the most recent commit", but a
  retagged or back-ported release can win. `get_last_version_tag_name` also relies on that order
  instead of picking the highest PEP 440 version, and both functions raise the same message
  ("No tag was found") for "no tag" and "no version tag". Use `max(..., key=Version)` for version
  tags and give distinct messages. `raise_error: bool = True` is a positional boolean; make it
  keyword-only (`*`).
- Many public booleans are positional: `exist_ok`, `reverse`, `raise_error`,
  `include_lower_bound`, `ignore_yanked`. `CLAUDE.md` says new options are keyword-only. Enable
  ruff `FBT` and fix the existing ones.
- `github/repos.fetch_github_repos` parses the `Link` header by hand (and with `str.find`).
  `requests` already provides `response.links["next"]["url"]`. The endpoint `users/{owner}/repos`
  returns only public repos even though `type=all` is passed, and silently returns an empty list
  for an organization with no public repos. Use `orgs/{owner}/repos` as a fallback, or document
  it. `display_repos_summary` logs instead of printing or returning, which is surprising for a
  function with "display" in the name.
- `github/sorting.sort_repos_by_key` names its locals `repos_with_name`/`repos_without_name`
  although `key` is arbitrary.
- `utils/mapping.sort_by_values` / `sort_by_keys` are tiny and only used by `dev/`. Consider moving
  them there.
- `utils/io.save_json` checks `path.is_file() and not exist_ok` and then writes, which is a
  time-of-check/time-of-use race. For `exist_ok=False`, use `os.link`/`open(..., "x")` semantics
  on the destination. `load_json`/`save_json` use `Path.open(path, ...)` in a non-idiomatic way
  (`path.open(...)`).
- `version/pyproject.py` reads and parses the TOML file once per public function, so
  `read_pyproject_dependencies` + `read_pyproject_optional_dependencies` parse it twice.
  `read_pyproject_dependencies` / `read_pyproject_optional_dependencies` ignore
  `[dependency-groups]`, but `read_pyproject_package_bounds` includes them, so the three readers
  cover different sections. Keep only the first (lower) and first (upper) bound and drop
  `==`, `~=`, `!=` silently, and ignore environment markers (`; python_version < "3.12"`), so the
  same package listed twice with different markers comes back as two entries with no way to tell
  them apart. Also `PackageBounds.name` is documented as "canonical" but is the name as written.
  Consider a single `read_pyproject_bounds(path, sections=...)`, keep the `>`/`>=` distinction, and
  support `~=`.
- `version/runtime.get_package_version` raises `InvalidVersion` for an installed distribution with
  a non-PEP 440 version; return `None` or let the caller choose.
- `compat/target.py`: `re.match(r"^\d+\.\d+$", ...)` accepts a trailing newline (`"3.11\n"`);
  use `fullmatch`. `Target.python_version` as a `str` forces string/`Version` conversions in
  several places; a `tuple[int, int]` or a small `PythonVersion` type would remove them (breaking).
- `CompatRegistry.register` creates the empty per-package dict before checking for a conflict, and
  does not validate ranges. A range with `min > max`, a malformed version string, or overlapping
  ranges only fails at lookup time inside `Version(...)`. Validate in `register`.
- `CompatRegistry.__str__` equals `__repr__`, which dumps the entire state (about 1000 entries for
  the default registry).
- `compat/matrix.py` is documented as "functions to automatically discover" but contains
  `is_compatible`, `DEFAULT_TARGETS` and a `rich` table printer. Move the printer to its own
  module and `is_compatible` to `discoverers/`. `is_compatible` returns `True` on an invalid
  specifier, which hides bad metadata; log a warning.
- `testing.py` imports `pytest` at import time and lives in the runtime package. That is fine as a
  public helper, but `pytest` is not a dependency of `feu`, so `import feu.testing` fails for
  users without it. Document it, or ship it as an extra.
- `__init__.py` exports six names. `install_package` etc. are exported, but `Target`,
  `find_closest_version`, `is_valid_version`, and `InstallerSpec` and `PackageSpec` (needed to call
  `install_package`) are not, so the top-level API is not enough to use the top-level functions.

**Documentation**

- README: the "Code style: black" badge is still there while the project uses `ruff format`.
- `docs/docs/cli.md` repeats the option lists that `click --help` generates; consider
  `mkdocs-click` so the docs cannot drift.
- The examples in `version/pyproject.py` use ` ```python ` blocks instead of `pycon`, so they are
  not run as doctests, unlike the rest of the package.

**Tests and tooling**

- `[tool.ruff.lint.per-file-ignores]` ignores `PLC0415` (import-outside-top-level) for tests with
  the comment "lazy imports are intentional in tests", while `CLAUDE.md` forbids local imports
  in tests. Remove the ignore so the rule is enforced. I found no violations by grep, so removing
  it should be free.
- 16 `pytest.raises(...)` calls have no `match=` on their line (for example
  `tests/unit/compat/test_registry.py:78,113,360`, `test_wheel_tags.py:116`). Some are probably
  multi-line calls that do pass `match`; I did not check each. `PT011`/`PT012` already flag the
  simple cases, so a quick pass with `ruff --select PT` would settle it.
- Almost every test of the install and CLI layers patches the collaborator (333 `patch`/
  `monkeypatch` uses in `tests/unit`). P1 went unnoticed because of this. Add integration tests
  that use the real shipped registry (see P1) and a real `pip install --dry-run` for the command
  string (needs network or `--no-index`), per the "every patched behaviour needs an integration
  test" rule in `CLAUDE.md`.
- `tests/package_checks.py` only checks imports and version helpers. Add a call of
  `find_closest_version` with a concrete target and of `get_default_registry()`, so the
  wheel/sdist check catches a missing `compat/discovered` data module.
- Property-based tests (`hypothesis`) would suit `parse_wheel_filename`, `group_into_ranges`, and
  `CompatRegistry.find_closest_version` (for example "the result is always valid for the target" and
  "idempotent": `find_closest_version(find_closest_version(v)) == find_closest_version(v)`).
- Add a test that every `discovered/*.py` module imports, defines `PKG_NAME` matching
  `get_package_names()`, and that every `VersionRange` has `min <= max`.
- `requires-python` is `>=3.11` and the classifiers list 3.11 to 3.15, but
  `DEFAULT_PYTHON_VERSIONS` starts at `3.9`. Decide which is the policy and make them agree.

---

## Suggested order of work

1. **P1** (with the integration test) and **P3** (regenerate data). These make the main feature
   correct. They are the only items that change what the library tells users.
2. **P2** and **P8** together (`sys.executable -m pip`, argv lists).
3. **P4**, **P5**, **P6**, **P7**. Small, independent bug fixes with regression tests.
4. **P9** (CLI), since it depends on P1.
5. **P11**, **P12**, then the duplication work (**P10**, **P13**, **P14**) as refactors, one PR each
   as `CLAUDE.md` asks.
6. **P15** items opportunistically.

## What I did not check

- The workflow files other than `ci.yaml`, the `.make/` Makefiles, and the pre-commit config
  beyond a grep. Supply-chain, permissions, and pinning of the GitHub Actions deserve their own
  review.
- Whether the shipped `discovered/*.py` values are right for each package. P3 shows the parser
  that generated them has gaps, so a spot check against PyPI after fixing it is worthwhile.
- Behaviour on Windows (the `nt` branch in `run_bash_command`) and with free-threaded builds.
- Network behaviour of `fetch_response` under failure (retries, rate limits).
