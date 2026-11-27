# Usage Guide

This guide shows the main features of `feu`. The examples are doctests: they are run by the test
suite (`tests/unit/test_docs.py`), so they cannot drift from the code. The examples that need the
network are marked as skipped. The rules the package follows, and the design choices behind them,
are in [Design](design.md).

| I want to ...                               | Section                                                                          |
| ------------------------------------------- | -------------------------------------------------------------------------------- |
| know if a package can be used               | [Checking Package Availability](#checking-package-availability)                  |
| compare an installed version                | [Version Comparison and Requests](#version-comparison-and-requests)              |
| find a version that works on an environment | [Targets](#targets), [Finding Compatible Versions](#finding-compatible-versions) |
| correct or extend the compatibility data    | [Your Own Constraints](#your-own-constraints)                                    |
| install a package                           | [Installing Packages](#installing-packages)                                      |
| compute the data from the wheels on PyPI    | [Discovering Compatibility from PyPI](#discovering-compatibility-from-pypi)      |
| test a library against many versions        | [Installing Every Compatible Version](#installing-every-compatible-version)      |
| sort, filter and fetch versions             | [Version Utilities](#version-utilities)                                          |
| reuse the helpers of `feu`                  | [Shared Utilities](#shared-utilities)                                            |
| follow the speed of my code                 | [Benchmark Trend](#benchmark-trend)                                              |
| read git tags or GitHub repositories        | [Git](#working-with-git-repositories), [GitHub](#working-with-github)            |
| skip tests without an optional library      | [Testing Utilities](#testing-utilities)                                          |

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

### Optional libraries

The optional libraries of `feu` (`click`, `gitpython`, `requests`, `rich`) are imported lazily:
`import feu` imports none of them. A feature that needs one of them raises
`feu.imports.MissingPackageError`, which is a `ModuleNotFoundError` and a `RuntimeError`. The
message gives the `pip install` and `uv pip install` commands:

```pycon
>>> from feu.imports import MissingPackageError, check_package
>>> try:
...     check_package("not_an_installed_package")
... except MissingPackageError as error:
...     print(error.name)
not_an_installed_package

```

Each optional library has an `is_<name>_available` check and a `check_<name>` function that raises
`MissingPackageError`, for `click`, `git` (installed as `gitpython`), `requests` and `rich`:

```pycon
>>> from feu.imports import is_requests_available
>>> isinstance(is_requests_available(), bool)
True

```

The same building blocks work for your own optional dependencies. `check_package` takes the name to
install when it differs from the name to import, and `availability_cache` caches a check so that
`clear_availability_caches()` resets it with the others:

```pycon
>>> from feu.imports import availability_cache, clear_availability_caches
>>> try:
...     check_package("not_an_installed_module", install="not-an-installed-package")
... except MissingPackageError as error:
...     print("pip install not-an-installed-package" in str(error))
True
>>> @availability_cache
... def is_tomllib_available() -> bool:
...     return is_module_available("tomllib")
>>> is_tomllib_available()
True
>>> clear_availability_caches()

```

A package that exposes names from heavy modules can import them on first use with
`feu.imports.lazy_exports`, which builds the `__getattr__` and `__dir__` of the package (this is how
`import feu` stays cheap):

```python
# In the __init__.py of your package
from feu.imports import lazy_exports

__all__ = ["OrderedDict"]

__getattr__, __dir__ = lazy_exports(__name__, {"OrderedDict": "collections"}, globals())
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

`get_package_version` returns the installed version as a `packaging` `Version`, or `None` if the
package is not installed:

```pycon
>>> from feu import get_package_version
>>> get_package_version("packaging")
<Version('...')>
>>> get_package_version("not_an_installed_package") is None
True

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

A parsed request answers whether a version satisfies it, and whether the whole request lies below a
version (a wildcard never matches a pre-release):

```pycon
>>> from packaging.version import Version
>>> request = parse_version_request("2.1.*")
>>> request.matches(Version("2.1.4")), request.matches(Version("2.1.0rc1"))
(True, False)
>>> request.entirely_below(Version("2.2.2"))
True
>>> parse_version_request("2.*").entirely_below(Version("2.2.2"))
False

```

## Targets

A `Target` is the environment a compatibility answer is about: the Python version
(`"major.minor"`), the free-threaded flag, the operating system (`linux`, `macos` or `windows`) and
the CPU architecture (`x86_64` or `arm64`). `os` and `arch` left to `None` mean "any platform" when
a target is used for a lookup: the answer is then the union of the versions published for at least
one platform.

```pycon
>>> from feu.compat import Target
>>> Target("3.12")
Target(python_version='3.12', free_threaded=False, os=None, arch=None)
>>> Target("3.14", free_threaded=True, os="linux", arch="arm64")
Target(python_version='3.14', free_threaded=True, os='linux', arch='arm64')
>>> Target("3.14t")
Traceback (most recent call last):
    ...
ValueError: invalid python_version '3.14t': expected a 'major.minor' string, e.g. '3.11'

```

`resolve_target()` is the current environment. The Python version and the free-threaded flag can be
chosen, and a `t` suffix means free-threaded; the platform is always the current one (it is `None`
if `feu` does not know it):

```pycon
>>> from feu.compat import resolve_target
>>> target = resolve_target("3.14t")
>>> target.python_version, target.free_threaded
('3.14', True)

```

## Finding Compatible Versions

`is_valid_version` checks a version request for a [target](#targets), and `find_closest_version`
returns the version to install:

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

A package without data accepts any exact version, which `has_package` lets you detect. A wildcard or
an empty request cannot be answered without data: `is_valid_version` returns `False` and
`find_closest_version` returns the request unchanged. If the package is configured but no version
supports the target, `is_valid_version` returns `False` and
`find_closest_version` raises `feu.compat.UnsupportedVersionError`.

```pycon
>>> from feu.compat import get_default_compat_registry, get_compatible_versions
>>> registry = get_default_compat_registry()
>>> registry.has_package("numpy"), registry.has_package("not-a-package")
(True, False)
>>> get_compatible_versions("numpy", target, "1.26.*")  # doctest: +SKIP
['1.26.0', '1.26.1', '1.26.2', '1.26.3', '1.26.4']

```

### Shipped data

The built-in data is one JSON file per package in `feu/compat/data`. It is parsed the first time a
package is looked up, and `registry.packages()` lists the packages without parsing any file:

```pycon
>>> packages = get_default_compat_registry().packages()
>>> {"numpy", "pandas", "torch"} <= set(packages)
True

```

The shipped packages are `bokeh`, `click`, `duckdb`, `jax`, `matplotlib`, `numpy`, `pandas`,
`polars`, `pyarrow`, `pydantic`, `requests`, `safetensors`, `scikit-learn`, `scipy`, `torch`,
`xarray` and `xy`. The data covers Python 3.9 to 3.15 (with the free-threaded builds from 3.13) on
Linux (glibc), macOS and Windows, on `x86_64` and `arm64`.

## Your Own Constraints

Register a constraint and, if you do not want them downloaded, the versions you know in a registry
instance (`CompatRegistry(version_source=...)` takes your own function to list the versions). Every
function takes an optional `registry=`; `register_compat` adds to the default registry. A
registration into a shipped package first loads it, so the conflict check sees the shipped entries
(use `exist_ok=True` to overwrite).

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

A range has inclusive bounds, and `None` is unbounded. A package can have several ranges, and an
empty list means that no version supports the target. A target that is more specific (it names an
`os` or an `arch`) wins over a generic one:

```pycon
>>> from feu.compat import UnsupportedVersionError
>>> registry = CompatRegistry()
>>> registry.register_many(
...     {
...         "my_package": {
...             Target("3.11"): [VersionRange("1.0", "1.5"), VersionRange("2.0", None)],
...             Target("3.11", os="windows"): [],
...         }
...     }
... )
>>> linux = Target("3.11", os="linux", arch="x86_64")
>>> find_closest_version("my_package", "1.7", linux, registry=registry)
'2.0'
>>> windows = Target("3.11", os="windows", arch="x86_64")
>>> registry.is_unsupported("my_package", windows)
True
>>> try:
...     find_closest_version("my_package", "2.0", windows, registry=registry)
... except UnsupportedVersionError as error:
...     print(str(error).split(" with ")[0])
No version of package my_package is compatible
>>> registry.get_config("my_package", linux)
[VersionRange(min='1.0', max='1.5'), VersionRange(min='2.0', max=None)]

```

Registering the same package and target twice raises a `RuntimeError` unless `exist_ok=True`:

```pycon
>>> registry.register("my_package", Target("3.11"), ranges=[VersionRange("3.0", None)])
Traceback (most recent call last):
    ...
RuntimeError: A package configuration (...) is already registered for package my-package and target ...
>>> registry.register("my_package", Target("3.11"), ranges=[VersionRange("3.0", None)], exist_ok=True)
>>> find_closest_version("my_package", "1.7", linux, registry=registry)
'3.0'

```

To read the data from your own storage, give a `loader` (an object with `packages()` and
`load(name)`, see `feu.compat.registry.DataLoader`). It is asked for a package the first time the
package is looked up:

```pycon
>>> from feu.compat.registry import PackageData
>>> class MyLoader:
...     def packages(self):
...         return ["my-package"]
...
...     def load(self, name):
...         return PackageData({Target("3.11"): [VersionRange("1.0", None)]})
>>> registry = CompatRegistry(loader=MyLoader(), version_source=lambda name: ["0.9", "1.0", "1.1"])
>>> registry.get_compatible_versions("my_package", Target("3.11"))
['1.0', '1.1']

```

## Installing Packages

`install_package` installs the version as written, without any compatibility check.
`install_package_closest_version` first resolves the version request for the current target (or
`target=`), and raises `UnsupportedVersionError` before running any command if no compatible version
matches. With both, the [dependency resolver](#dependency-resolvers) of the package can add
requirements.

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

`uv` builds the same kind of command, for the same interpreter:

```pycon
>>> from feu.install import UvInstaller
>>> command = UvInstaller(["--upgrade"]).command([Requirement("numpy==2.0.2")])
>>> command[:4], command[5:]
(['uv', 'pip', 'install', '--python'], ['--upgrade', 'numpy==2.0.2'])

```

A `PackageSpec` is a name, a version request and optional extras:

```pycon
>>> from feu import PackageSpec
>>> spec = PackageSpec("pandas", "2.2.*", extras=["performance", "excel"])
>>> str(spec)
'pandas[performance,excel]==2.2.*'
>>> str(spec.with_version(""))
'pandas[performance,excel]'

```

`is_pip_available()` and `is_uv_available()` tell which installer can run. `install_package` and
`install_package_closest_version` raise a `RuntimeError` for an installer name that is not
registered, and `subprocess.CalledProcessError` if the command fails.

The arguments of an installer are a string, split once with `shlex.split`, or a list of strings,
which is used as is. `pipx` is not a built-in installer: it installs an application into an isolated
environment, not into the current environment.

### Dependency resolvers

Some packages need an extra requirement: `pandas` before 2.2.2 needs `numpy<2.0.0`. A resolver is a
function from a `PackageSpec` to a list of `packaging.requirements.Requirement`. The resolver
reasons on the whole version request:

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

The built-in resolvers add these requirements when the whole version request needs them:

| Package        | Requirement added                                                   |
| -------------- | ------------------------------------------------------------------- |
| `matplotlib`   | `numpy<2.0.0` below 3.8.4                                           |
| `pandas`       | `numpy<2.0.0` below 2.2.2                                           |
| `pyarrow`      | `numpy<2.0.0` below 16.0                                            |
| `scikit-learn` | `numpy<2.0.0` below 1.4.2                                           |
| `scipy`        | `numpy<2.0.0` below 1.13.0                                          |
| `torch`        | `numpy<2.0.0` below 2.3.0                                           |
| `xarray`       | `numpy<2.0.0` below 2024.6.0                                        |
| `jax`          | `jaxlib` with the same version request (not for the latest version) |
| `jax`          | `numpy<2.0.0` below 0.4.26, `ml_dtypes<=0.2.0` from 0.4.9 to 0.4.11 |

```pycon
>>> resolve(PackageSpec("jax", "0.4.10"))
[<Requirement('jax==0.4.10')>, <Requirement('jaxlib==0.4.10')>, <Requirement('numpy<2.0.0')>, <Requirement('ml_dtypes<=0.2.0')>]

```

A resolver registry is a plain [`Registry`](#shared-utilities), so you can build one that does not
touch the defaults:

```pycon
>>> from feu.install.resolver import numpy2_resolver
>>> from feu.utils.registry import Registry
>>> resolvers = Registry("dependency resolver")
>>> resolvers.register("my-package", numpy2_resolver("3.0"))
>>> resolve(PackageSpec("my-package", "2.5"), resolvers)
[<Requirement('my-package==2.5')>, <Requirement('numpy<2.0.0')>]

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

The result of `discover_compat_targets` has the considered releases (`discovery.versions`) and the
ranges of each target (`discovery.targets`), which `CompatRegistry.register_many` accepts under a
package name. `targets=` restricts the environments to compute (each one needs an `os` and an
`arch`), and `companion=` and `ignore_versions=` handle the packages that need it (see the
[architecture](dev/architecture.md) page):

```python
from feu.compat import CompatRegistry, Target, discover_compat_targets

target = Target("3.12", os="linux", arch="x86_64")
discovery = discover_compat_targets("my-package", targets=[target])
registry = CompatRegistry()
registry.register_many({"my-package": discovery.targets})
```

The building blocks of the discovery work offline:

```pycon
>>> from feu.compat import group_into_ranges, is_compatible, parse_wheel_filename
>>> from feu.compat import tags_match_exactly
>>> (tag,) = parse_wheel_filename("pkg-1.0-cp39-abi3-manylinux_2_17_aarch64.whl")
>>> tag
WheelTag(python_version='3.9', free_threaded=False, os='linux', arch='arm64', abi3=True)
>>> from feu.compat import WheelTag
>>> tags_match_exactly(tag, WheelTag("3.12", False, "linux", "arm64"))
True
>>> is_compatible(">=3.10", "3.9")
False
>>> group_into_ranges(["1.0", "1.1", "1.2", "1.3"], {"1.0", "1.1", "1.3"}, latest="1.3")
[VersionRange(min='1.0', max='1.1'), VersionRange(min='1.3', max=None)]

```

`format_package_data` and `parse_package_data` write and read the JSON format of the shipped files:

```pycon
>>> from feu.compat import Target, VersionRange
>>> from feu.compat.shipped import format_package_data, parse_package_data
>>> target = Target("3.12", os="linux", arch="x86_64")
>>> content = format_package_data("my-package", "2026-01-01", {target: [VersionRange("1.0", None)]})
>>> parse_package_data(content).targets == {target: [VersionRange("1.0", None)]}
True

```

## Installing Every Compatible Version

`get_installable_versions` lists the stable (and not yanked) releases of a package on PyPI that are
valid for a target, and `install_all_versions` installs them one after the other, for example to
test a library against all the versions of a dependency. A failure to install one version is logged
and does not stop the others. The result lists the versions that were installed and the ones that
failed. The package can have extras (`"pandas[performance]"`); a version specifier is ignored.

```python
from feu.compat import Target
from feu.install import InstallerSpec, get_installable_versions, install_all_versions

target = Target(python_version="3.12", os="linux", arch="x86_64")
versions = get_installable_versions("numpy", target, start_date="2024-01-01")
result = install_all_versions(InstallerSpec("pip"), "pandas[performance]", target)
print(result.installed, result.failed)
```

## Version Utilities

`feu.version` has the helpers that sort, filter and select versions. They use PEP 440 order, never
the order of the strings:

```pycon
>>> from feu.version import filter_stable_versions, latest_minor_versions, sort_versions
>>> versions = ["1.10.0", "1.9.0", "1.9.1", "2.0.0rc1"]
>>> sort_versions(filter_stable_versions(versions))
['1.9.0', '1.9.1', '1.10.0']
>>> latest_minor_versions(filter_stable_versions(versions))
['1.9.1', '1.10.0']

```

The functions that read PyPI (`fetch_pypi_versions`, `fetch_versions`, `fetch_latest_version`, ...)
use the Simple API, need the `requests` extra and cache the metadata of a project for the life of the
process. `read_pyproject_bounds` reads the lower and upper bounds of the dependencies of a
`pyproject.toml`, and `fetch_package_versions` combines both to give the versions to test of a
project (the `package-versions` command):

```python
from feu.version import fetch_latest_stable_version, fetch_package_versions, read_pyproject_bounds

bounds = read_pyproject_bounds("pyproject.toml", package="numpy")  # one entry per section
latest = fetch_latest_stable_version("numpy")
to_test = fetch_package_versions("pyproject.toml")  # {"numpy": ["1.26.4", "2.0.2", ...], ...}
```

### Filtering and selecting

All the filters keep the strings as they are written. The bounds of `filter_range_versions` are
inclusive below and exclusive above:

```pycon
>>> from feu.version import (
...     filter_every_n_versions,
...     filter_last_n_versions,
...     filter_range_versions,
...     filter_valid_versions,
...     latest_major_versions,
...     latest_version,
...     unique_versions,
... )
>>> versions = ["1.0", "1.1", "1.2", "2.0", "2.1"]
>>> filter_range_versions(versions, lower="1.1", upper="2.0")
['1.1', '1.2']
>>> filter_last_n_versions(versions, n=2)
['2.0', '2.1']
>>> filter_every_n_versions(versions, n=2)
['1.0', '1.2', '2.1']
>>> latest_major_versions(versions)
['1.2', '2.1']
>>> latest_version(versions)
'2.1'
>>> filter_valid_versions(["1.0", "not-a-version"])
['1.0']
>>> unique_versions(["1.0", "1.1", "1.0"])
['1.0', '1.1']

```

### Dependency bounds of a project

`read_pyproject_bounds` returns one `PackageBounds` per occurrence of a dependency, with the section
where it was found. The names are canonical, and the operators of the bounds are not kept:

```pycon
>>> import tempfile
>>> from pathlib import Path
>>> from feu.version import get_package_bounds, partition_package_bounds, read_pyproject_bounds
>>> content = """
... [project]
... dependencies = ["NumPy>=1.26,<3.0", "packaging>=22.0"]
... [dependency-groups]
... dev = ["pytest>=9.0"]
... """
>>> with tempfile.TemporaryDirectory() as tmpdir:
...     path = Path(tmpdir, "pyproject.toml")
...     _ = path.write_text(content, encoding="utf-8")
...     bounds = read_pyproject_bounds(path)
>>> get_package_bounds(bounds, "numpy")
PackageBounds(name='numpy', lower='1.26', upper='3.0', section='project.dependencies')
>>> matched, others = partition_package_bounds(bounds, ["numpy"])
>>> [item.name for item in others]
['packaging', 'pytest']

```

### Versions published on PyPI

These functions need the `requests` extra and network access:

| Function                               | Returns                                                           |
| -------------------------------------- | ----------------------------------------------------------------- |
| `fetch_pypi_project`                   | The releases and files of a project (`PypiProject`, `PypiFile`)   |
| `fetch_pypi_versions`                  | The versions, optionally by release date, without the yanked ones |
| `fetch_pypi_requires_python`           | The `requires-python` of each release                             |
| `fetch_pypi_wheel_filenames`           | The wheel file names of each release                              |
| `fetch_pypi_pinned_dependency_version` | The version of a dependency that a release pins with `==`         |
| `fetch_versions`                       | The stable versions between two bounds                            |
| `fetch_latest_versions`                | The latest stable version of each major or minor version          |
| `fetch_latest_version`                 | The latest version, which can be a pre-release                    |
| `fetch_latest_stable_version`          | The latest stable version                                         |
| `fetch_package_versions`               | The versions to test of the dependencies of a `pyproject.toml`    |

```python
from feu.version import fetch_latest_versions, fetch_pypi_versions

fetch_pypi_versions("numpy", start_date="2025-01-01", end_date="2025-12-31")
fetch_latest_versions("numpy", group="minor", lower="2.0", include_lower_bound=True)
```

## Shared Utilities

`feu.utils` holds the helpers shared by the other modules, which you can use too.

`Registry` maps a name to a value; `normalize` is applied to every key:

```pycon
>>> from feu.utils.registry import Registry
>>> registry = Registry[int]("number", normalize=str.lower)
>>> registry.register_many({"One": 1, "Two": 2})
>>> registry.find("ONE"), registry.get("three", 3), registry.keys()
(1, 3, ['one', 'two'])

```

`save_json` creates the parent directories, writes atomically and refuses to overwrite a file unless
`exist_ok=True`:

```pycon
>>> import tempfile
>>> from pathlib import Path
>>> from feu.utils.io import load_json, save_json
>>> with tempfile.TemporaryDirectory() as tmpdir:
...     path = Path(tmpdir, "config", "versions.json")
...     save_json({"numpy": ["2.0.2"]}, path)
...     load_json(path)
{'numpy': ['2.0.2']}

```

```pycon
>>> from feu.utils.mapping import sort_by_keys, sort_by_values
>>> sort_by_keys({"b": 1, "a": 2})
{'a': 2, 'b': 1}
>>> sort_by_values({"a": 2, "b": 1})
{'b': 1, 'a': 2}

```

The other helpers describe the interpreter (`feu.utils.platform`), run a command without a shell
(`feu.utils.command.run_command`) and fetch a URL with retries (`feu.utils.http`, which needs the
`requests` extra):

```python
from feu.utils.command import run_command
from feu.utils.http import fetch_data
from feu.utils.platform import get_current_arch, get_current_os, get_python_version

print(get_current_os(), get_current_arch(), get_python_version())
run_command(["git", "--version"])  # raises subprocess.CalledProcessError if it fails
data = fetch_data("https://pypi.org/pypi/feu/json")  # raises RuntimeError if it fails
```

## Benchmark Trend

`feu.benchmark` follows the trend of the `pytest-benchmark` results (the `feu benchmark-trend`
command, see the [CLI reference](cli.md#benchmark-trend)). A `Run` is the times of the benchmarks of
one run on one machine. `find_regressions` compares the latest run of each machine with the median
of its previous runs, and `make_report` renders the Markdown report and the GitHub Actions
annotations. Both are pure functions of the runs, which must be in chronological order; `load_runs`
reads them, in that order, from a storage directory.

```pycon
>>> from datetime import UTC, datetime
>>> from feu.benchmark import Run, make_report
>>> date = datetime(2026, 1, 1, tzinfo=UTC)
>>> runs = [Run(date, "", {"sort": 0.001}), Run(date, "", {"sort": 0.003})]
>>> report = make_report(runs, threshold=100)
>>> [(item.label, item.change) for item in report.regressions]
[('sort', 200.0)]
>>> report.annotations
('::warning title=Regression::sort is 200.0%25 slower than the median of the previous runs (3000 µs instead of 1000 µs)',)

```

`load_runs` reads the result files of a storage directory and `prune_runs` deletes the ones that are
older than the window:

```pycon
>>> import json
>>> import tempfile
>>> from pathlib import Path
>>> from feu.benchmark import load_runs, prune_runs
>>> with tempfile.TemporaryDirectory() as tmpdir:
...     storage = Path(tmpdir)
...     for name, date in [("0001_old", "2000-01-01"), ("0002_new", "2999-01-01")]:
...         result = {
...             "datetime": f"{date}T00:00:00+00:00",
...             "benchmarks": [{"name": "test_sort_benchmark", "stats": {"median": 0.001}}],
...         }
...         _ = storage.joinpath(f"{name}.json").write_text(json.dumps(result), encoding="utf-8")
...     print([dict(run.times) for run in load_runs(storage, days=30)])
...     print([path.name for path in prune_runs(storage, days=30)])
[{'sort': 0.001}]
['0001_old.json']

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
from feu.github import (
    display_repos_summary,
    fetch_github_metadata,
    fetch_github_repos,
    sort_repos_by_key,
)

# The `GITHUB_TOKEN` environment variable, if set, increases the rate limit.
metadata = fetch_github_metadata(owner="durandtibo", repo="feu")  # a read-only mapping
repos = fetch_github_repos(owner="durandtibo")  # a tuple of read-only mappings
by_stars = sort_repos_by_key(repos, key="stargazers_count", reverse=True)
display_repos_summary(by_stars)  # logged at the INFO level
```

Sorting and building the request headers work without network access. Repositories without the key
are placed at the end, and `build_github_headers` adds the `Authorization` header when
`GITHUB_TOKEN` is set. `display_repos_summary` logs at the `INFO` level, so configure logging to see
it (`logging.basicConfig(level=logging.INFO)`):

```pycon
>>> from feu.github import build_github_headers, sort_repos_by_key
>>> repos = [{"name": "a", "stars": 1}, {"name": "b"}, {"name": "c", "stars": 5}]
>>> [repo["name"] for repo in sort_repos_by_key(repos, key="stars", reverse=True)]
['c', 'a', 'b']
>>> build_github_headers()["Accept"]
'application/vnd.github+json'

```

## Testing Utilities

`feu.testing` provides `pytest` marks to skip a test when an optional dependency is (not) available
(it needs `pytest`):

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
`pytest_benchmark`, `requests`, `rich`, `scipy`, `sklearn`, `torch`, `uv`, and `xarray`.

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

### Pin an old release together with a compatible NumPy

```pycon
>>> from feu import PackageSpec, Target, find_closest_version
>>> from feu.install.resolver import resolve
>>> target = Target("3.11", os="linux", arch="x86_64")
>>> version = find_closest_version("scipy", "1.11.4", target)
>>> resolve(PackageSpec("scipy", version))
[<Requirement('scipy==1.11.4')>, <Requirement('numpy<2.0.0')>]

```

### Conditional imports

```pycon
>>> from feu import is_package_available
>>> USE_FAST_PATH = is_package_available("not_an_installed_package")
>>> USE_FAST_PATH
False

```
