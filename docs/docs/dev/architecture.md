# Architecture

## Layers

The imports go one way (property 13). A module imports only the layers on its left; `imports`
imports nothing from `feu`. `tests/unit/test_layers.py` checks it.

```text
imports  ->  utils  ->  version  ->  compat  ->  install  ->  cli
```

| Layer     | What it does                                                                                                            | I/O                                                |
| --------- | ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| `imports` | Availability checks of the optional libraries (a port of `coola.utils.imports`), `MissingPackageError`, `lazy_exports`. | none                                               |
| `utils`   | `Registry[T]`, `run_command`, `fetch_data`/`fetch_response`, `PackageSpec`, the platform of the interpreter.            | `command.py` (subprocess), `http.py` (network)     |
| `version` | Version comparison and filtering, the version request, `pyproject` bounds, PyPI metadata (`fetch_pypi_project`).        | `pypi.py`, `package.py` (network)                  |
| `compat`  | `Target`, the registry, the shipped data, the discovery from PyPI, the wheel tags.                                      | `discover.py` (network), `shipped.py` (read files) |
| `install` | The installers, the dependency resolvers, `install_package` and friends.                                                | `installer.py` (subprocess)                        |
| `cli`     | The `click` commands; they only parse and print.                                                                        | none of its own                                    |

`feu.github` and `feu.local_git` are outside the chain and only use the lower layers.

## Data flow

1. `dev/generate_compat_data.py` calls `discover_compat_targets(package)`. It fetches the project
   once with the Simple API (`fetch_pypi_project`), parses the wheel file names
   (`parse_wheel_filename`) and writes `feu/compat/data/<package>.json`.
2. `get_default_compat_registry()` lists the files with `importlib.resources` (nothing is parsed).
   The first lookup of a package parses its file.
3. `find_closest_version(package, request, target)` resolves the version request against the known
   versions and the ranges of the target. `install_package_closest_version` calls it with the full
   current target.
4. The `Installer` resolves the dependencies with the resolver registry and runs one command:
   `<sys.executable> -m pip install ...` or `uv pip install --python <sys.executable> ...`.

## How to add a package

Run the generator with the name of the package. The list of packages is the list of files, so
nothing else is edited:

```shell
python dev/generate_compat_data.py --new my-package
```

The bot workflow `bot-update-discovered-compat` refreshes every file each week.

## How to add a companion or an ignored version

Some packages publish their platform wheels in another package. `COMPANIONS` in
`feu/compat/discover.py` describes them with data:

```pycon
>>> from feu.compat import COMPANIONS
>>> COMPANIONS["jax"]
SameVersion(package='jaxlib')
>>> COMPANIONS["pydantic"]
PinnedDependency(package='pydantic-core')

```

`SameVersion` means that the companion has a release with the same version, `PinnedDependency` that
the release pins the companion release. For such a package a pure-Python wheel never counts: the
release is judged by its platform wheels, or by the wheels of the companion release. A one-off case
does not need an edit of the table, pass `companion=` or `ignore_versions=` to
`discover_compat_targets`.

## How to add an installer

An installer is a subclass of `Installer` that only differs by its `prefix`. Register the class
under a name:

```pycon
>>> from feu.install import Installer, get_default_installer_registry, register_installer
>>> class PdmInstaller(Installer):
...     prefix = ("pdm", "add")
>>> register_installer("pdm", PdmInstaller)
>>> get_default_installer_registry().find("pdm") is PdmInstaller
True
>>> from packaging.requirements import Requirement
>>> PdmInstaller("--dev").command([Requirement("numpy==2.0.2")])
['pdm', 'add', '--dev', 'numpy==2.0.2']

```

Override `check_available()` to raise a `RuntimeError` when the tool is missing. Every function
that installs takes an optional `registry=` if you do not want to change the default registry.

## How to add a resolver

A resolver is a function from a `PackageSpec` to a list of requirements. It receives a version
request and should reason on the whole request (`pandas==2.*` straddles the threshold of
`numpy<2.0.0`, `""` is the latest version):

```pycon
>>> from packaging.requirements import Requirement
>>> from feu.install import register_resolver
>>> from feu.install.resolver import default_resolver, resolve
>>> from feu.utils.package import PackageSpec
>>> def my_resolver(package):
...     return [*default_resolver(package), Requirement("typing-extensions>=4")]
>>> register_resolver("my-package", my_resolver)
>>> resolve(PackageSpec("My_Package", "1.0"))
[<Requirement('My_Package==1.0')>, <Requirement('typing-extensions>=4')>]

```

For a package that needs `numpy<2.0.0` below a version, add the version to `NUMPY2_MIN_VERSION` in
`feu/install/resolver.py` or use `numpy2_resolver(min_version)`.

## Tests

Unit tests mirror the source tree and are fast: no network, no real installer. Every patched
behaviour has an integration test in `tests/integration/` that exercises the real thing, for
example `tests/integration/install/test_pip_offline.py` builds a wheel and runs the real `pip` and
`uv` with `--dry-run --no-index --find-links`. The shipped data is asked real questions in
`tests/integration/compat/test_data.py` and its contract is checked by
`tests/unit/compat/test_shipped_data.py`.
