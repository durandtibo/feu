# Usage Guide

This guide shows the main features of `feu`. The examples are doctests: they are run by the test
suite (`tests/unit/test_docs.py`), so they cannot drift from the code. The examples that need the
network are marked as skipped. The rules the package follows are in [Properties](properties.md).

## Checking Package Availability

`is_package_available` looks a package up without importing it, `is_module_available` imports the
module. The checks are cached, so call `clear_availability_caches()` if you change `sys.path` or
`sys.modules` yourself. `install_package` clears the caches after a successful installation.

```pycon
>>> from feu import is_module_available, is_package_available
>>> is_package_available("packaging")
True
>>> is_package_available("not_an_installed_package")
False
>>> is_module_available("packaging.version")
True

```

A module that is installed but broken (for example a missing shared library) is reported as not
available by `is_module_available`, and a warning is logged.

The optional libraries of `feu` (`click`, `gitpython`, `requests`, `rich`) are imported lazily:
`import feu` imports none of them. A feature that needs one of them raises
`feu.imports.MissingPackageError`, which is a `ModuleNotFoundError` and a `RuntimeError`. The message
gives the `pip install` and `uv pip install` commands:

```pycon
>>> from feu.imports import MissingPackageError, check_package
>>> try:
...     check_package("not_an_installed_package")
... except MissingPackageError as error:
...     print(error.name)
not_an_installed_package

```

## Version Comparison and Requests

`compare_version` compares the installed version of a package to a version. It returns `False` if
the package is not installed:

```pycon
>>> import operator
>>> from feu import compare_version
>>> compare_version("packaging", operator.ge, "20.0")
True
>>> compare_version("not_an_installed_package", operator.ge, "1.0")
False

```

Wherever a function takes the version of a package to install or to validate, it accepts a version
_request_: an exact version (`"2.4.0"`), a wildcard (`"2.4.*"`, `"2.*"`) or an empty string / `None`
for the latest version. A wildcard is digits and dots followed by one trailing `.*`; anything else
with a `*` raises `ValueError`:

```pycon
>>> from feu.version import parse_version_request
>>> parse_version_request("2.4.*")
VersionRequest(text='2.4.*', exact=None, prefix=(2, 4))
>>> parse_version_request("").is_latest
True
>>> parse_version_request("2.*.1")
Traceback (most recent call last):
    ...
ValueError: invalid version wildcard '2.*.1': a wildcard is digits and dots followed by one trailing '.*', e.g. '2.4.*'

```

## Finding Compatible Versions

A `Target` is the environment a constraint applies to: the Python version, the free-threaded flag,
the operating system and the CPU architecture. `os` and `arch` left to `None` mean "any platform"
when a target is used for a lookup: the answer is then the union of the versions published for at
least one platform. `resolve_target()` is the current environment (the platform is always the
current one).

```pycon
>>> from feu.compat import Target, find_closest_version, is_valid_version
>>> target = Target(python_version="3.9", os="linux", arch="x86_64")
>>> is_valid_version("numpy", "2.0.2", target)
True
>>> is_valid_version("numpy", "2.3.0", target)
False
>>> find_closest_version("numpy", "99.0.0", target)
'2.0.2'

```

The shipped data holds the compatible ranges, not a list of releases. A wildcard (`1.*`) is matched
against the releases that are **downloaded from PyPI when it is resolved**, so it never goes stale
and no new `feu` release is needed when a package publishes a version. The exact version and the
latest version (`""`) need no download: the latest version is the request itself when the last range
is open-ended (the newest release was compatible when the data was generated), so that the installer
picks the real latest release, and the highest upper bound otherwise. A wildcard resolves to the
request itself in the same case. There is no offline fallback: resolving a wildcard without network
access raises the error of the download.

```pycon
>>> find_closest_version("numpy", "1.*", target)  # doctest: +SKIP
'1.26.4'
>>> find_closest_version("numpy", "", target)
'2.0.2'
>>> find_closest_version("numpy", "1.24.*", Target("3.14", os="linux", arch="x86_64"))  # doctest: +SKIP
Traceback (most recent call last):
    ...
feu.compat.registry.UnsupportedVersionError: No version of package numpy matches '1.24.*' for target Target(python_version='3.14', free_threaded=False, os='linux', arch='x86_64')

```

A package without data accepts any version, which `has_package` lets you detect. If the package is
configured but no version supports the target, `is_valid_version` returns `False` and
`find_closest_version` raises `feu.compat.UnsupportedVersionError`.

```pycon
>>> from feu.compat import get_default_compat_registry, get_compatible_versions
>>> registry = get_default_compat_registry()
>>> registry.has_package("numpy"), registry.has_package("not-a-package")
(True, False)
>>> get_compatible_versions("numpy", target, "1.26.*")  # doctest: +SKIP
['1.26.0', '1.26.1', '1.26.2', '1.26.3', '1.26.4']

```

The built-in data is one JSON file per package in `feu/compat/data`. It is parsed the first time a
package is looked up, and `registry.packages()` lists the packages without parsing any file.

## Your Own Constraints

Register a constraint and, if you do not want them downloaded, the versions you know in a registry
instance (`CompatRegistry(version_source=...)` takes your own function to list the versions). Every function takes an
optional `registry=`; `register_compat` adds to the default registry. A registration into a shipped
package first loads it, so the conflict check sees the shipped entries (use `exist_ok=True` to
overwrite).

```pycon
>>> from feu.compat import CompatRegistry, VersionRange, get_compatible_versions
>>> target = Target(python_version="3.11")
>>> registry = CompatRegistry()
>>> registry.register("my_package", target, ranges=[VersionRange("1.2.0", "2.0.0")])
>>> registry.register_versions("my_package", ["1.2.0", "1.5.0", "2.0.0", "3.0.0"])
>>> find_closest_version("my_package", "3.0.0", target, registry=registry)
'2.0.0'
>>> get_compatible_versions("my_package", target, "1.*", registry=registry)
['1.2.0', '1.5.0']

```

## Installing Packages

`install_package` installs as written. `install_package_closest_version` first resolves the
version request for the current target (or `target=`), and raises `UnsupportedVersionError` before
running any command if no compatible version matches.

```python
from feu import install_package, install_package_closest_version
from feu.install import InstallerSpec
from feu.utils.package import PackageSpec

install_package(
    installer=InstallerSpec(name="pip"),
    package=PackageSpec(name="numpy", version="2.0.2"),
)
install_package_closest_version(
    installer=InstallerSpec(name="uv", arguments="--upgrade"),
    package=PackageSpec(name="numpy", version="2.*"),
)
```

An installer builds one command, as an argument vector (never a shell string), and the packages are
installed in the interpreter that runs `feu`: `pip` runs as `<sys.executable> -m pip install ...`
and `uv` as `uv pip install --python <sys.executable> ...`. A `RuntimeError` is raised before any
command if `pip` is not available in that interpreter (for example in an environment created by
`uv venv`) or if `uv` is not on the `PATH`.

```pycon
>>> from packaging.requirements import Requirement
>>> from feu.install import InstallerSpec, PipInstaller
>>> command = PipInstaller("-U --pre").command([Requirement("numpy==2.0.2")])
>>> command[1:]
['-m', 'pip', 'install', '-U', '--pre', 'numpy==2.0.2']
>>> InstallerSpec("pip", arguments="-U --pre").arguments
('-U', '--pre')

```

The arguments of an installer are a string, split once with `shlex.split`, or a list of strings,
which is used as is. `pipx` is not a built-in installer: it installs an application into an isolated
environment, not into the current environment.

### Dependency resolvers

Some packages need an extra requirement: `pandas` before 2.2.2 needs `numpy<2.0.0`. A resolver is a
function from a `PackageSpec` to a list of `packaging.requirements.Requirement`. The resolver reasons
on the whole version request:

```pycon
>>> from feu.install.resolver import resolve
>>> from feu.utils.package import PackageSpec
>>> resolve(PackageSpec("pandas", "2.1.1"))
[<Requirement('pandas==2.1.1')>, <Requirement('numpy<2.0.0')>]
>>> resolve(PackageSpec("pandas", "2.1.*"))
[<Requirement('pandas==2.1.*')>, <Requirement('numpy<2.0.0')>]
>>> resolve(PackageSpec("pandas", "2.*"))
[<Requirement('pandas==2.*')>]

```

Register your own installer or resolver in the default registries with `register_installer(name,
installer_class)` and `register_resolver(package, resolver)`. See the
[architecture](dev/architecture.md) page.

## Discovering Compatibility from PyPI

`feu` can query PyPI to discover which package versions are compatible with each target. The result
is the data that `dev/generate_compat_data.py` writes to `feu/compat/data`:

```python
from feu.compat import discover_compat_targets, show_compat_targets

# The considered versions and the ranges of each target, from the wheels on PyPI.
discovery = discover_compat_targets("numpy")

# Pretty-print the matrix as a table (requires the `rich` extra)
show_compat_targets(discovery, pkg_name="numpy")
```

## Working with Git Repositories

If you have installed the `git` extra (`pip install 'feu[git]'`):

```python
from feu.local_git import get_last_tag_name, get_last_version_tag_name, get_tags

tags = get_tags()  # sorted by commit date
last_tag = get_last_tag_name()
last_version_tag = get_last_version_tag_name()  # e.g. "v1.2.3"

# By default, a RuntimeError is raised if no tag is found.
last_tag = get_last_tag_name(raise_error=False)  # None instead
```

## Working with GitHub

If you have installed the `requests` extra (`pip install 'feu[requests]'`):

```python
from feu.github import fetch_github_metadata, fetch_github_repos, sort_repos_by_key

# The `GITHUB_TOKEN` environment variable, if set, increases the rate limit.
metadata = fetch_github_metadata(owner="durandtibo", repo="feu")  # a read-only mapping
repos = fetch_github_repos(owner="durandtibo")  # a tuple of read-only mappings
by_stars = sort_repos_by_key(repos, key="stargazers_count", reverse=True)
```

## Testing Utilities

`feu.testing` provides `pytest` marks to skip a test when an optional dependency is (not) available:

```python
from feu.testing import click_available, requests_not_available


@click_available
def test_cli_feature(): ...


@requests_not_available
def test_error_without_requests(): ...
```

Each mark has an `..._available` variant (skips the test if the dependency is _not_ available) and
an `..._not_available` variant (skips the test if the dependency _is_ available). Marks are
provided for `click`, `git`, `jax`, `matplotlib`, `numpy`, `pandas`, `pip`, `polars`, `pyarrow`,
`requests`, `rich`, `scipy`, `sklearn`, `torch`, `uv`, and `xarray`.

## Common Use Cases

### Install the compatible version of a dependency in a CI matrix

```pycon
>>> from feu.compat import Target, find_closest_version
>>> for python_version in ("3.9", "3.10"):
...     target = Target(python_version, os="linux", arch="x86_64")
...     print(python_version, find_closest_version("numpy", "99.0.0", target))
3.9 2.0.2
3.10 2.2.6

```

### Conditional imports

```pycon
>>> from feu import is_package_available
>>> USE_FAST_PATH = is_package_available("not_an_installed_package")
>>> USE_FAST_PATH
False

```
