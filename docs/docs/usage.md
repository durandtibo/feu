# Usage Guide

This guide demonstrates the main features and use cases of `feu`.

## Checking Package Availability

You can check if packages or modules are available in your environment:

```python
from feu import is_package_available, is_module_available

# Check if a package is installed
if is_package_available("numpy"):
    print("NumPy is available!")
else:
    print("NumPy is not installed")

# Check if a specific module is available
if is_module_available("numpy.linalg"):
    print("NumPy linear algebra module is available!")
```

## Version Comparison

Compare the installed version of a package to a given version. `compare_version` takes the package
name, a comparison operator and the version to compare with, and returns `False` if the package is
not installed:

```python
import operator

from feu import compare_version

# True if the installed version of numpy is at least 1.5.0
result = compare_version("numpy", operator.ge, "1.5.0")
print(result)

# True if the installed version of numpy is lower than 2.0.0
result = compare_version("numpy", operator.lt, "2.0.0")
print(result)
```

## Getting Package Version

Retrieve the installed version of a package:

```python
from feu import get_package_version

# Get the version of an installed package
version = get_package_version("numpy")
print(f"NumPy version: {version}")
```

## Finding Compatible Versions

Find the closest valid package version for your Python version:

```python
from feu.compat import Target, find_closest_version, is_valid_version

# Check if a specific version is valid for your Python version
is_valid = is_valid_version(
    pkg_name="numpy", pkg_version="2.0.2", target=Target(python_version="3.10")
)
print(f"NumPy 2.0.2 is valid for Python 3.10: {is_valid}")

# Find the closest valid version
closest = find_closest_version(
    pkg_name="numpy",
    pkg_version="1.0.0",  # This is too old for Python 3.11
    target=Target(python_version="3.11"),
)
print(f"Closest valid version: {closest}")  # Will return "1.23.2"
```

A target that leaves `os` and `arch` to `None` matches every platform: the answer is the union of
the versions published for at least one platform. `install_package_closest_version` uses the full
current target (Python version, free-threaded flag, OS and architecture) unless `target=` is given.
Use `get_default_registry().has_package(name)` to detect an unknown package.

A package that is not configured for the target accepts any version. If the package is configured
but no version of it supports the target, `is_valid_version` returns `False` and
`find_closest_version` raises `feu.compat.UnsupportedVersionError`.

`Target` also accepts the optional `free_threaded`, `os` and `arch` arguments. Use
`resolve_target` to build a target from partial inputs, falling back to the current interpreter
and platform:

```python
from feu.compat import resolve_target

target = resolve_target(python_version="3.14t", os="linux", arch="x86_64")
```

### Version Requests

Wherever a function takes the version of a package to install or to validate, it accepts a version
*request*: an exact version (`"2.4.0"`), a wildcard (`"2.4.*"`, `"2.*"`) or an empty string / `None`
for the latest version. A wildcard is digits and dots followed by one trailing `.*`; anything else
with a `*` raises `ValueError`.

```python
from feu.compat import Target, find_closest_version, is_valid_version

target = Target(python_version="3.9", os="linux", arch="x86_64")

is_valid_version("numpy", "1.*", target)  # True: a 1.x release supports Python 3.9
is_valid_version("numpy", "3.*", target)  # False: there is no 3.x release
find_closest_version("numpy", "1.*", target)  # "1.26.4": the latest compatible 1.x release
find_closest_version("numpy", "", target)  # "2.0.2": the latest release that supports Python 3.9
```

A request is resolved against the versions the registry knows. When the latest compatible release
lies in an open-ended range (the newest release was compatible when the data was generated), the
request itself is returned (`"2.*"` or `""`), so that the installer picks the real latest release.
`install_package_closest_version` checks every request this way and raises
`UnsupportedVersionError` before running any command if no compatible version matches. A package
with no registered versions has no data: a wildcard or empty request is invalid for
`is_valid_version` and is returned unchanged by `find_closest_version`. Use
`registry.register_versions(name, versions)` to give a package its versions.

## Installing Packages

Install packages with automatic version selection:

```python
from feu import install_package, install_package_closest_version
from feu.utils.package import PackageSpec
from feu.utils.installer import InstallerSpec

# Install a package with a specific version
install_package(
    installer=InstallerSpec(name="pip"),
    package=PackageSpec(name="numpy", version="2.0.2"),
)

# Install the closest valid version for your environment. The compatibility is checked
# against the current target (Python version, free-threaded flag, OS and architecture).
install_package_closest_version(
    installer=InstallerSpec(name="pip"),
    package=PackageSpec(name="numpy", version="2.0.2"),
)
```

The installers run an argument vector, never a shell string. `pip` is run as
`<sys.executable> -m pip install ...` and `uv` as `uv pip install --python <sys.executable> ...`,
so the packages are installed in the interpreter that runs `feu`. A `RuntimeError` is raised if
`pip` is not available in that interpreter (for example in an environment created by `uv venv`) or
if `uv` is not on the `PATH`. The installer arguments are a string, split once with
`shlex.split`, or a list of strings, which is used as is:

```python
InstallerSpec(name="pip", arguments="-U --pre")
InstallerSpec(name="pip", arguments=["--index-url", "https://example.com/my index"])
```

`pipx` is no longer a built-in installer: it installs an application into an isolated environment,
which is not an installation into the current environment. Register your own installer with
`InstallerRegistry.add_installer` if you need it.

## Managing Package Configurations

Add custom package configurations to the default compatibility registry:

```python
from feu.compat import Target, get_default_registry
from feu.compat.registry import VersionRange

registry = get_default_registry()

# Add a custom package configuration
registry.register(
    pkg_name="my_package",
    target=Target(python_version="3.11"),
    ranges=[VersionRange("1.2.0", "2.0.0")],
    exist_ok=True,
)

# Get the configuration for a package
config = registry.get_config(pkg_name="my_package", target=Target(python_version="3.11"))
print(config)  # [VersionRange(min='1.2.0', max='2.0.0')]

# Get version ranges as Version objects
ranges = registry.get_version_ranges(pkg_name="numpy", target=Target(python_version="3.11"))
for min_version, max_version in ranges:
    print(f"Min: {min_version}, Max: {max_version}")
```

## Working with Git Repositories

If you have installed the `git` extra (`pip install 'feu[git]'`), you can work with git repositories:

```python
from feu.local_git import get_last_tag_name, get_last_version_tag_name, get_tags

# Get all tags, sorted by date/time
tags = get_tags()
print(f"Tags: {[tag.name for tag in tags]}")

# Get the name of the most recent tag
last_tag = get_last_tag_name()
print(f"Last tag: {last_tag}")

# Get the name of the most recent version tag (e.g. "v1.2.3")
last_version_tag = get_last_version_tag_name()
print(f"Last version tag: {last_version_tag}")

# By default, a RuntimeError is raised if no tag is found.
# Use raise_error=False to return None instead.
last_tag = get_last_tag_name(raise_error=False)
last_version_tag = get_last_version_tag_name(raise_error=False)
```

## Supported Packages

`feu` includes built-in version compatibility information for common packages:

- **Scientific Computing**: numpy, scipy, pandas, polars, xarray, duckdb
- **Machine Learning**: torch, jax, scikit-learn
- **Data Handling**: pyarrow, safetensors, xy
- **Visualization**: matplotlib, bokeh
- **Web**: requests, click
- **Validation**: pydantic

Each package has defined minimum and maximum versions for different Python versions (3.9, 3.10,
3.11, 3.12, 3.13, 3.14, 3.15), and some packages also account for free-threaded builds, OS, and
CPU architecture (see [Discovering Compatibility from PyPI](#discovering-compatibility-from-pypi)
below).

## Discovering Compatibility from PyPI

In addition to the built-in registry, `feu` can query PyPI directly to discover which package
versions are compatible with a given target (Python version, free-threadedness, OS, and
architecture):

```python
from feu.compat import discover_compat_targets, show_compat_targets

# Discover the compatibility matrix for a package by inspecting its wheels on PyPI
compat = discover_compat_targets("numpy")

# Pretty-print the matrix as a table (requires the `rich` extra)
show_compat_targets(compat, pkg_name="numpy")
```

This is useful to keep the built-in registry up to date, or to inspect compatibility for packages
that are not part of the registry.

## Working with GitHub

If you have installed the `requests` extra (`pip install 'feu[requests]'`), you can query GitHub
repository metadata:

```python
from feu.github import fetch_github_metadata, fetch_github_repos, sort_repos_by_key

# Fetch metadata for a single repository. Authentication headers are built automatically
# from the `GITHUB_TOKEN` environment variable, if set, to increase the rate limit.
metadata = fetch_github_metadata(owner="durandtibo", repo="feu")
print(metadata)

# Fetch all repositories of a user or organization
repos = fetch_github_repos(owner="durandtibo")

# Sort repositories by a metadata key, e.g. "stargazers_count"
sorted_repos = sort_repos_by_key(repos, key="stargazers_count", reverse=True)
```

## Testing Utilities

`feu` provides testing utilities for checking package availability in tests:

```python
from feu.testing import (
    click_available,
    git_available,
    requests_available,
)


# Use as pytest marks (skip the test if the dependency is unavailable)
@click_available
def test_click_feature():
    # This test only runs if click is available
    pass


@git_available
def test_git_feature():
    # This test only runs if gitpython is available
    pass


@requests_available
def test_http_feature():
    # This test only runs if requests is available
    pass
```

Each mark has an `..._available` variant (skips the test if the dependency is _not_ available) and
an `..._not_available` variant (skips the test if the dependency _is_ available). Marks are
provided for `click`, `git`, `jax`, `matplotlib`, `numpy`, `pandas`, `pip`, `polars`,
`pyarrow`, `requests`, `rich`, `scipy`, `sklearn`, `torch`, `urllib3`, `uv`, and `xarray`.

## Common Use Cases

### Use Case 1: Multi-Python Version Project

If you're maintaining a project that supports multiple Python versions:

```python
import sys
from feu.compat import Target, find_closest_version

python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

# Find compatible numpy version
numpy_version = find_closest_version(
    pkg_name="numpy", pkg_version="2.0.0", target=Target(python_version=python_version)
)
print(f"Installing numpy {numpy_version} for Python {python_version}")
```

### Use Case 2: Safe Package Installation

Before installing a package, check if the version is compatible:

```python
import sys
from feu.compat import Target, is_valid_version
from feu import install_package
from feu.utils.package import PackageSpec
from feu.utils.installer import InstallerSpec

python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
desired_version = "2.0.2"

if is_valid_version("numpy", desired_version, Target(python_version=python_version)):
    install_package(
        installer=InstallerSpec(name="pip"),
        package=PackageSpec(name="numpy", version=desired_version),
    )
else:
    print(f"Version {desired_version} is not compatible with Python {python_version}")
```

### Use Case 3: Conditional Imports

Use package availability checks for conditional imports:

```python
from feu import is_package_available

if is_package_available("torch"):
    import torch

    USE_PYTORCH = True
else:
    USE_PYTORCH = False
    print("PyTorch not available, using fallback implementation")
```
