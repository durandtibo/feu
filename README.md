# feu :fire:

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
packages and their versions across different Python environments.

### Key Features

- ✅ **Check package availability**: Verify if packages and modules are installed
- 🔄 **Version-aware installation**: Install packages with automatic version compatibility checks
- 🎯 **Smart version resolution**: Find the closest valid package version for your target
  environment (Python version, free-threadedness, OS, and CPU architecture). A version can be an
  exact version (`2.4.0`), a wildcard (`2.4.*`) or empty (the latest)
- 📋 **Package registry**: Built-in compatibility information for popular packages (numpy, pandas,
  polars, torch, pydantic, etc.), which can be extended with your own constraints
- 🔍 **PyPI-backed discovery**: Discover version compatibility from the wheels published on PyPI,
  including for packages that aren't in the built-in registry
- 🔖 **Version utilities**: Compare, filter and sort versions, fetch the versions published on PyPI,
  and read dependency bounds from `pyproject.toml`
- 🌿 **Git and GitHub utilities**: Get the tags of a local repository, and fetch and sort
  repository metadata from the GitHub API
- 🖥️ **CLI tools**: Command-line interface (`feu`) to install a package, find the closest valid
  version, check if a version is valid, list the versions to test and follow the trend of
  `pytest-benchmark` results (`pip install 'feu[cli]'`)
- 🧩 **Extensible**: Register your own installers (`pip` and `uv` are built in), dependency
  resolvers and compatibility constraints
- 🪶 **Lightweight**: Minimal dependencies (only `packaging` required for core functionality)

### Quick Example

The examples are doctests: they are run by the test suite, so they cannot drift from the code.

```pycon
>>> from feu import is_package_available
>>> from feu.compat import Target, find_closest_version
>>> is_package_available("packaging")
True
>>> # The closest valid version for a target (Python 3.9 on Linux x86_64)
>>> target = Target(python_version="3.9", os="linux", arch="x86_64")
>>> find_closest_version("numpy", "2.3.0", target)
'2.0.2'
>>> # A version is a request: an exact version, a wildcard or "" for the latest
>>> find_closest_version("numpy", "1.*", target)
'1.26.4'
>>> # A target without a platform means "any platform"
>>> find_closest_version("numpy", "2.3.0", Target(python_version="3.9"))
'2.0.2'

```

The same checks are available from the command line (`pip install 'feu[cli]'`). The standard
output holds only the answer and the exit status carries the result (`0` ok, `1` negative answer,
`2` usage error):

```shell
feu find-closest-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10
feu check-valid-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10
feu install --pkg-name=numpy --pkg-version=2.0.2
```

`python -m feu ...` is equivalent. The commands are `install`, `find-closest-version`,
`check-valid-version`, `package-versions` and `benchmark-trend`.

### Main API

| Name                                                 | What it does                                                                 |
| ---------------------------------------------------- | ---------------------------------------------------------------------------- |
| `is_package_available`, `is_module_available`        | Check if a package is installed, or a module can be imported (cached)        |
| `get_package_version`, `compare_version`             | Read the installed version of a package, and compare it to a version         |
| `Target`, `resolve_target`                           | The environment (Python version, free-threaded flag, OS, architecture)       |
| `is_valid_version`, `find_closest_version`           | Validate a version request for a target, or find the closest valid version   |
| `install_package`, `install_package_closest_version` | Install a package as written, or at the closest valid version for the target |
| `PackageSpec`, `InstallerSpec`                       | Describe the package (name, version request, extras) and the installer       |

All of them can be imported from `feu`. The other modules are `feu.compat` (registry, discovery from
PyPI), `feu.install` (installers, dependency resolvers), `feu.version` (version utilities, PyPI and
`pyproject.toml`), `feu.imports` (optional dependencies), `feu.testing` (`pytest` marks),
`feu.benchmark`, `feu.github` and `feu.local_git`.

### Version requests

Wherever a function takes the version of a package to install or to validate, it accepts a
_version request_: an exact version (`2.4.0`), a wildcard (`2.4.*`, `2.*`) or an empty string (the
latest version). A wildcard is matched against the versions published on PyPI when it is resolved,
so it needs network access and the `requests` extra.

### Why feu?

Managing Python package versions across different Python versions can be challenging. Different
Python versions support different package versions, and manually tracking compatibility can be
error-prone. `feu` solves this by:

1. **Automating version selection**: Automatically finds compatible package versions for your Python
   environment
2. **Preventing installation failures**: Validates versions before installation to avoid runtime
   errors
3. **Simplifying multi-version support**: Makes it easy to support multiple Python versions in your
   projects
4. **Providing graceful fallbacks**: Check package availability and provide alternatives when
   packages aren't installed

### Documentation

- 📚 [Full Documentation](https://durandtibo.github.io/feu/)
- 🚀 [Get Started Guide](https://durandtibo.github.io/feu/get_started)
- 📖 [Usage Examples](https://durandtibo.github.io/feu/usage)
- 🧭 [Design](https://durandtibo.github.io/feu/design): the properties of `feu`, the design choices
  and their trade-offs
- 🧱 [Architecture](https://durandtibo.github.io/feu/dev/architecture): layers, how to add a package,
  an installer or a resolver
- 🖥️ [CLI Reference](https://durandtibo.github.io/feu/cli)
- 📚 [API Reference](https://durandtibo.github.io/feu/refs/root)

### Quick Links

- [Installation](#installation)
- [Contributing](#contributing)
- [API stability](#api-stability)
- [License](#license)

## Installation

We highly recommend installing a
[virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).
`feu` can be installed from pip using the following command:

```shell
pip install feu
```

To make the package as slim as possible, only the minimal packages required to use `feu` are
installed. To include all the dependencies, you can use the following command:

```shell
pip install feu[all]
```

Please check the [get started page](https://durandtibo.github.io/feu/get_started) to see how to
install only some specific dependencies (`feu[cli]`, `feu[git]`, `feu[requests]`, `feu[rich]`) or
other alternatives to install the library. The following
is the corresponding `feu` versions and supported dependencies.

| `feu`   | `packaging`    | `python`       | `click`<sup>*</sup> | `gitpython`<sup>*</sup> | `requests`<sup>*</sup> | `rich`<sup>*</sup> |
| ------- | -------------- | -------------- | ------------------- | ----------------------- | ---------------------- | ------------------ |
| `main`  | `>=22.0,<27.0` | `>=3.11`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          | `>=14.0.0,<16.0`   |
| `0.8.4` | `>=21.0,<27.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          | `>=14.0.0,<16.0`   |
| `0.8.3` | `>=21.0,<27.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          | `>=14.0.0,<16.0`   |
| `0.8.2` | `>=21.0,<27.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          | `>=14.0.0,<16.0`   |
| `0.8.1` | `>=21.0,<27.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          | `>=14.0.0,<16.0`   |
| `0.8.0` | `>=21.0,<27.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          | `>=14.0.0,<16.0`   |
| `0.7.3` | `>=21.0,<27.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |                    |
| `0.7.2` | `>=21.0,<27.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |                    |
| `0.7.1` | `>=21.0,<27.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |                    |
| `0.7.0` | `>=21.0,<27.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |                    |
| `0.6.2` | `>=21.0,<27.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |                    |
| `0.6.1` | `>=21.0,<26.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |                    |
| `0.6.0` | `>=21.0,<26.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |                    |
| `0.5.0` | `>=21.0,<26.0` | `>=3.10,<3.15` | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |                    |

<sup>*</sup> indicates an optional dependency

<details>
    <summary>older versions</summary>

| `feu`   | `packaging`    | `python`       | `click`<sup>*</sup> | `gitpython`<sup>*</sup> | `fire`<sup>*</sup> | `requests`<sup>*</sup> |
| ------- | -------------- | -------------- | ------------------- | ----------------------- | ------------------ | ---------------------- |
| `0.4.2` | `>=21.0,<26.0` | `>=3.10,<3.15` | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         |                    | `>=2.30,<3.0`          |
| `0.4.1` | `>=21.0,<26.0` | `>=3.10,<3.15` | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         |                    | `>=2.30,<3.0`          |
| `0.4.0` | `>=21.0,<26.0` | `>=3.9,<3.14`  | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         |                    | `>=2.30,<3.0`          |
| `0.3.5` | `>=21.0,<26.0` | `>=3.9,<3.14`  | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         |                    |                        |
| `0.3.4` | `>=21.0,<26.0` | `>=3.9,<3.14`  | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         |                    |                        |
| `0.3.3` | `>=21.0,<26.0` | `>=3.9,<3.14`  | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         |                    |                        |
| `0.3.2` | `>=21.0,<25.0` | `>=3.9,<3.14`  | `>=8.1,<9.0`        |                         |                    |                        |
| `0.3.1` | `>=21.0,<25.0` | `>=3.9,<3.14`  | `>=8.1,<9.0`        |                         |                    |                        |
| `0.3.0` | `>=21.0,<25.0` | `>=3.9,<3.14`  | `>=8.1,<9.0`        |                         |                    |                        |
| `0.2.4` | `>=21.0,<25.0` | `>=3.9,<3.13`  | `>=8.1,<9.0`        |                         |                    |                        |
| `0.2.3` | `>=21.0,<25.0` | `>=3.9,<3.13`  | `>=8.1,<9.0`        |                         |                    |                        |
| `0.2.2` | `>=21.0,<25.0` | `>=3.9,<3.13`  | `>=8.1,<9.0`        |                         |                    |                        |
| `0.2.1` | `>=21.0,<25.0` | `>=3.9,<3.13`  | `>=8.1,<9.0`        |                         |                    |                        |
| `0.2.0` | `>=21.0,<25.0` | `>=3.9,<3.13`  | `>=8.1,<9.0`        |                         |                    |                        |
| `0.1.1` | `>=21.0,<25.0` | `>=3.9,<3.13`  |                     |                         | `>=0.6.0,<1.0`     |                        |
| `0.1.0` | `>=21.0,<25.0` | `>=3.9,<3.13`  |                     |                         | `>=0.6.0,<1.0`     |                        |
| `0.0.7` | `>=21.0,<25.0` | `>=3.9,<3.13`  |                     |                         |                    |                        |
| `0.0.6` | `>=21.0,<25.0` | `>=3.9,<3.13`  |                     |                         |                    |                        |
| `0.0.5` | `>=21.0,<25.0` | `>=3.9,<3.13`  |                     |                         |                    |                        |
| `0.0.4` | `>=21.0,<25.0` | `>=3.9,<3.13`  |                     |                         |                    |                        |
| `0.0.3` | `>=21.0,<25.0` | `>=3.9,<3.13`  |                     |                         |                    |                        |
| `0.0.2` | `>=22.0,<24.0` | `>=3.9,<3.13`  |                     |                         |                    |                        |
| `0.0.1` | `>=22.0,<23.3` | `>=3.9,<3.13`  |                     |                         |                    |                        |

</details>

## Contributing

Please check the instructions in [CONTRIBUTING.md](CONTRIBUTING.md).

## Suggestions and Communication

Everyone is welcome to contribute to the community. If you have any questions or suggestions, you
can submit [Github Issues](https://github.com/durandtibo/feu/issues). We will reply to you as soon
as possible. Thank you very much.

## API stability

:warning: While `feu` is in development stage, no API is guaranteed to be stable from one release to
the next. In fact, it is very likely that the API will change multiple times before a stable 1.0.0
release. In practice, this means that upgrading `feu` to a new version will possibly break any code
that was using the old version of `feu`.

## License

`feu` is licensed under BSD 3-Clause "New" or "Revised" license available in [LICENSE](LICENSE)
file.
