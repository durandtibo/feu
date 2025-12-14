# feu :fire:

<p align="center">
    <a href="https://github.com/durandtibo/feu/actions/workflows/ci.yaml">
        <img alt="CI" src="https://github.com/durandtibo/feu/actions/workflows/ci.yaml/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/feu/actions/workflows/nightly-tests.yaml">
        <img alt="Nightly Tests" src="https://github.com/durandtibo/feu/actions/workflows/nightly-tests.yaml/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/feu/actions/workflows/nightly-package.yaml">
        <img alt="Nightly Package Tests" src="https://github.com/durandtibo/feu/actions/workflows/nightly-package.yaml/badge.svg">
    </a>
    <a href="https://codecov.io/gh/durandtibo/feu">
        <img alt="Codecov" src="https://codecov.io/gh/durandtibo/feu/branch/main/graph/badge.svg">
    </a>
    <br/>
    <a href="https://durandtibo.github.io/feu/">
        <img alt="Documentation" src="https://github.com/durandtibo/feu/actions/workflows/docs.yaml/badge.svg">
    </a>
    <a href="https://durandtibo.github.io/feu/dev/">
        <img alt="Documentation" src="https://github.com/durandtibo/feu/actions/workflows/docs-dev.yaml/badge.svg">
    </a>
    <br/>
    <a href="https://github.com/psf/black">
        <img  alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
    </a>
    <a href="https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings">
        <img  alt="Doc style: google" src="https://img.shields.io/badge/%20style-google-3666d6.svg">
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;">
    </a>
    <a href="https://github.com/guilatrova/tryceratops">
        <img  alt="Doc style: google" src="https://img.shields.io/badge/try%2Fexcept%20style-tryceratops%20%F0%9F%A6%96%E2%9C%A8-black">
    </a>
    <br/>
    <a href="https://pypi.org/project/feu/">
        <img alt="PYPI version" src="https://img.shields.io/pypi/v/feu">
    </a>
    <a href="https://pypi.org/project/feu/">
        <img alt="Python" src="https://img.shields.io/pypi/pyversions/feu.svg">
    </a>
    <a href="https://opensource.org/licenses/BSD-3-Clause">
        <img alt="BSD-3-Clause" src="https://img.shields.io/pypi/l/feu">
    </a>
    <br/>
    <a href="https://pepy.tech/project/feu">
        <img  alt="Downloads" src="https://static.pepy.tech/badge/feu">
    </a>
    <a href="https://pepy.tech/project/feu">
        <img  alt="Monthly downloads" src="https://static.pepy.tech/badge/feu/month">
    </a>
    <br/>
</p>

## Overview

`feu` (French word for "fire" 🔥) is a lightweight Python library designed to help manage Python
packages and their versions across different Python environments.

### Key Features

- ✅ **Check package availability**: Verify if packages and modules are installed
- 🔄 **Version-aware installation**: Install packages with automatic version compatibility checks
- 🎯 **Smart version resolution**: Find the closest valid package version for your Python environment
- 📋 **Package registry**: Built-in compatibility information for popular packages (numpy, pandas,
  torch, etc.)
- 🖥️ **CLI tools**: Command-line interface for package management tasks
- 🪶 **Lightweight**: Minimal dependencies (only `packaging` required for core functionality)

### Quick Example

```python
from feu import is_package_available, get_package_version
from feu.package import find_closest_version

# Check if a package is available
if is_package_available("numpy"):
    version = get_package_version("numpy")
    print(f"NumPy {version} is installed!")

# Find the closest valid version for your Python version
version = find_closest_version(
    pkg_name="numpy", pkg_version="2.0.2", python_version="3.10"
)
print(f"Closest valid version: {version}")
```

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
- 🖥️ [CLI Reference](https://durandtibo.github.io/feu/cli)

### Quick Links

- [Installation](#installation)
- [Contributing](#contributing)
- [API stability](#api-stability)
- [License](#license)

## Installation

We highly recommend installing
a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).
`feu` can be installed from pip using the following command:

```shell
pip install feu
```

To make the package as slim as possible, only the minimal packages required to use `feu` are
installed.
To include all the dependencies, you can use the following command:

```shell
pip install feu[all]
```

Please check the [get started page](https://durandtibo.github.io/feu/get_started) to see how to
install only some specific dependencies or other alternatives to install the library.
The following is the corresponding `feu` versions and supported dependencies.

| `feu`   | `packaging`    | `python`       | `click`<sup>*</sup> | `gitpython`<sup>*</sup> | `requests`<sup>*</sup> |
|---------|----------------|----------------|---------------------|-------------------------|------------------------|
| `main`  | `>=21.0,<26.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |
| `0.6.0` | `>=21.0,<26.0` | `>=3.10`       | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |
| `0.5.0` | `>=21.0,<26.0` | `>=3.10,<3.15` | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |
| `0.4.2` | `>=21.0,<26.0` | `>=3.10,<3.15` | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |
| `0.4.1` | `>=21.0,<26.0` | `>=3.10,<3.15` | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |
| `0.4.0` | `>=21.0,<26.0` | `>=3.9,<3.14`  | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         | `>=2.30,<3.0`          |

<sup>*</sup> indicates an optional dependency

<details>
    <summary>older versions</summary>

| `feu`   | `packaging`    | `python`      | `click`<sup>*</sup> | `gitpython`<sup>*</sup> | `fire`<sup>*</sup> | `requests`<sup>*</sup> |
|---------|----------------|---------------|---------------------|-------------------------|--------------------|------------------------|
| `0.3.5` | `>=21.0,<26.0` | `>=3.9,<3.14` | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         |                    |                        |
| `0.3.4` | `>=21.0,<26.0` | `>=3.9,<3.14` | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         |                    |                        |
| `0.3.3` | `>=21.0,<26.0` | `>=3.9,<3.14` | `>=8.1,<9.0`        | `>=3.1.41,<4.0`         |                    |                        |
| `0.3.2` | `>=21.0,<25.0` | `>=3.9,<3.14` | `>=8.1,<9.0`        |                         |                    |                        |
| `0.3.1` | `>=21.0,<25.0` | `>=3.9,<3.14` | `>=8.1,<9.0`        |                         |                    |                        |
| `0.3.0` | `>=21.0,<25.0` | `>=3.9,<3.14` | `>=8.1,<9.0`        |                         |                    |                        |
| `0.2.4` | `>=21.0,<25.0` | `>=3.9,<3.13` | `>=8.1,<9.0`        |                         |                    |                        |
| `0.2.3` | `>=21.0,<25.0` | `>=3.9,<3.13` | `>=8.1,<9.0`        |                         |                    |                        |
| `0.2.2` | `>=21.0,<25.0` | `>=3.9,<3.13` | `>=8.1,<9.0`        |                         |                    |                        |
| `0.2.1` | `>=21.0,<25.0` | `>=3.9,<3.13` | `>=8.1,<9.0`        |                         |                    |                        |
| `0.2.0` | `>=21.0,<25.0` | `>=3.9,<3.13` | `>=8.1,<9.0`        |                         |                    |                        |
| `0.1.1` | `>=21.0,<25.0` | `>=3.9,<3.13` |                     |                         | `>=0.6.0,<1.0`     |                        |
| `0.1.0` | `>=21.0,<25.0` | `>=3.9,<3.13` |                     |                         | `>=0.6.0,<1.0`     |                        |
| `0.0.7` | `>=21.0,<25.0` | `>=3.9,<3.13` |                     |                         |                    |                        |
| `0.0.6` | `>=21.0,<25.0` | `>=3.9,<3.13` |                     |                         |                    |                        |
| `0.0.5` | `>=21.0,<25.0` | `>=3.9,<3.13` |                     |                         |                    |                        |
| `0.0.4` | `>=21.0,<25.0` | `>=3.9,<3.13` |                     |                         |                    |                        |
| `0.0.3` | `>=21.0,<25.0` | `>=3.9,<3.13` |                     |                         |                    |                        |
| `0.0.2` | `>=22.0,<24.0` | `>=3.9,<3.13` |                     |                         |                    |                        |
| `0.0.1` | `>=22.0,<23.3` | `>=3.9,<3.13` |                     |                         |                    |                        |

</details>

## Contributing

Please check the instructions in [CONTRIBUTING.md](CONTRIBUTING.md).

## Suggestions and Communication

Everyone is welcome to contribute to the community.
If you have any questions or suggestions, you can
submit [Github Issues](https://github.com/durandtibo/feu/issues).
We will reply to you as soon as possible. Thank you very much.

## API stability

:warning: While `feu` is in development stage, no API is guaranteed to be stable from one
release to the next.
In fact, it is very likely that the API will change multiple times before a stable 1.0.0 release.
In practice, this means that upgrading `feu` to a new version will possibly break any code that
was using the old version of `feu`.

## License

`feu` is licensed under BSD 3-Clause "New" or "Revised" license available in [LICENSE](LICENSE)
file.
