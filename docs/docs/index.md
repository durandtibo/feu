# Home

<p align="center">
    <a href="https://github.com/durandtibo/feu/actions/workflows/ci.yaml">
        <img alt="CI" src="https://img.shields.io/github/actions/workflow/status/durandtibo/feu/ci.yaml?branch=main&label=CI&logo=github"></a>
    <a href="https://github.com/durandtibo/feu/actions/workflows/nightly-package.yaml">
        <img alt="Nightly Package Tests" src="https://img.shields.io/github/actions/workflow/status/durandtibo/feu/nightly-package.yaml?label=nightly&logo=github"></a>
    <a href="https://codecov.io/gh/durandtibo/feu">
        <img alt="Codecov" src="https://img.shields.io/codecov/c/github/durandtibo/feu?logo=codecov"></a>
    <a href="https://durandtibo.github.io/feu/">
        <img alt="Documentation (stable)" src="https://img.shields.io/badge/docs-stable-blue?logo=readthedocs&logoColor=white"></a>
    <br/>
    <a href="https://pypi.org/project/feu/">
        <img alt="PyPI version" src="https://img.shields.io/pypi/v/feu?logo=pypi&logoColor=white"></a>
    <a href="https://pypi.org/project/feu/">
        <img alt="Python" src="https://img.shields.io/pypi/pyversions/feu?logo=python&logoColor=white"></a>
    <a href="https://opensource.org/licenses/BSD-3-Clause">
        <img alt="BSD-3-Clause" src="https://img.shields.io/pypi/l/feu"></a>
    <br/>
    <a href="https://github.com/astral-sh/ruff">
        <img alt="Ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"></a>
    <a href="https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings">
        <img alt="Doc style: google" src="https://img.shields.io/badge/docstyle-google-3666d6"></a>
    <a href="https://scorecard.dev/viewer/?uri=github.com/durandtibo/feu">
        <img alt="OpenSSF Scorecard" src="https://img.shields.io/ossf-scorecard/github.com/durandtibo/feu?label=openssf%20scorecard"></a>
    <br/>
    <a href="https://pepy.tech/project/feu">
        <img alt="Downloads" src="https://img.shields.io/pepy/dt/feu"></a>
    <a href="https://pepy.tech/project/feu">
        <img alt="Monthly downloads" src="https://img.shields.io/pepy/dm/feu"></a>
    <a href="https://github.com/durandtibo/feu/stargazers">
        <img alt="GitHub stars" src="https://img.shields.io/github/stars/durandtibo/feu?logo=github"></a>
</p>

## Overview

`feu` (French word for "fire" 🔥) is a lightweight Python library designed to help manage Python
packages and their versions across different Python environments. It provides utilities to:

- **Check package availability**: Verify if packages and modules are available in your environment
- **Install packages intelligently**: Install packages with version compatibility checks for your
  target environment
- **Version management**: Find the closest valid package version for your target environment
- **Package configuration**: A registry of known package version compatibility, shipped as data
  generated from the wheels published on PyPI, which you can extend with your own constraints
- **Version requests**: Every version argument is an exact version (`2.4.0`), a wildcard
  (`2.4.*`) or an empty string for the latest version
- **Version utilities**: Compare, filter and sort versions, fetch the versions published on PyPI,
  and read dependency bounds from `pyproject.toml`
- **Git and GitHub utilities**: Get the tags of a local git repository, and fetch and sort
  repository metadata from the GitHub API

The library is particularly useful for projects that need to support multiple Python versions,
free-threaded builds, OSes, and CPU architectures, and want to ensure they install compatible
package versions.

## Key Features

- **Target-aware**: Automatically selects compatible package versions based on the Python version,
  free-threadedness, OS, and CPU architecture
- **CLI interface**: Command-line tools to install a package, find the closest valid version,
  check a version, list the versions to test and follow the trend of benchmarks
- **Lightweight**: Minimal dependencies (only `packaging` required for core functionality)
- **Extensible**: Registry of common packages (numpy, pandas, polars, torch, etc.) with known
  version constraints, PyPI-backed discovery for anything not in the registry, and registries of
  installers (`pip`, `uv`) and dependency resolvers that you can add to

## Quick Example

```pycon
>>> from feu import is_package_available
>>> from feu.compat import Target, find_closest_version
>>> is_package_available("packaging")
True
>>> target = Target(python_version="3.9", os="linux", arch="x86_64")
>>> find_closest_version("numpy", "2.3.0", target)
'2.0.2'
>>> find_closest_version("numpy", "1.*", target)
'1.26.4'

```

## Documentation

- 🚀 [Get Started Guide](get_started.md)
- 📖 [Usage Guide](usage.md)
- 🖥️ [CLI Reference](cli.md)
- 🧭 [Design](design.md): the properties of `feu`, the design choices and their trade-offs
- 🧱 [Architecture](dev/architecture.md): layers, how to add a package, an installer or a resolver
- 📚 [API Reference](refs/root.md)

## Installation

```shell
pip install feu            # only the required dependency, packaging
pip install 'feu[all]'     # every optional dependency
pip install 'feu[cli]'     # the feu command (click)
```

The other extras are `feu[git]` (`feu.local_git`), `feu[requests]` (PyPI and GitHub calls, which
wildcard version requests need) and `feu[rich]` (`show_compat_targets`). See
[Get Started](get_started.md).

## API stability

:warning: While `feu` is in development stage, no API is guaranteed to be stable from one
release to the next. In fact, it is very likely that the API will change multiple times before a
stable 1.0.0 release. In practice, this means that upgrading `feu` to a new version will
possibly break any code that was using the old version of `feu`.

## License

`feu` is licensed under BSD 3-Clause "New" or "Revised" license available
in [LICENSE](https://github.com/durandtibo/feu/blob/main/LICENSE) file.
