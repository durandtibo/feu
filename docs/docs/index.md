# Home

<p align="center">
    <a href="https://github.com/durandtibo/feu/actions">
        <img alt="CI" src="https://github.com/durandtibo/feu/workflows/CI/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/feu/actions">
        <img alt="Nightly Tests" src="https://github.com/durandtibo/feu/workflows/Nightly%20Tests/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/feu/actions">
        <img alt="Nightly Package Tests" src="https://github.com/durandtibo/feu/workflows/Nightly%20Package%20Tests/badge.svg">
    </a>
    <a href="https://codecov.io/gh/durandtibo/feu">
        <img alt="Codecov" src="https://codecov.io/gh/durandtibo/feu/branch/main/graph/badge.svg">
    </a>
    <br/>
    <a href="https://durandtibo.github.io/feu/">
        <img alt="Documentation" src="https://github.com/durandtibo/feu/workflows/Documentation%20(stable)/badge.svg">
    </a>
    <a href="https://durandtibo.github.io/feu/">
        <img alt="Documentation" src="https://github.com/durandtibo/feu/workflows/Documentation%20(unstable)/badge.svg">
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

`feu` (French word for "fire" 🔥) is a lightweight Python library designed to help manage Python packages and their versions across different Python environments. It provides utilities to:

- **Check package availability**: Verify if packages and modules are available in your environment
- **Install packages intelligently**: Install packages with version compatibility checks for your Python version
- **Version management**: Find the closest valid package version for your Python environment
- **Package configuration**: Maintain a registry of known package version compatibility with different Python versions

The library is particularly useful for projects that need to support multiple Python versions and want to ensure they install compatible package versions.

## Key Features

- **Python version-aware**: Automatically selects compatible package versions based on your Python version
- **CLI interface**: Command-line tools for package management tasks
- **Lightweight**: Minimal dependencies (only `packaging` required for core functionality)
- **Extensible**: Registry of common packages (numpy, pandas, torch, etc.) with known version constraints

## Quick Example

```python
from feu import is_package_available, install_package_closest_version
from feu.package import find_closest_version

# Check if a package is available
if is_package_available("numpy"):
    print("NumPy is installed!")

# Find the closest valid version for your Python version
version = find_closest_version(
    pkg_name="numpy",
    pkg_version="2.0.2",
    python_version="3.10"
)
print(f"Closest valid version: {version}")
```

## API stability

:warning: While `feu` is in development stage, no API is guaranteed to be stable from one
release to the next. In fact, it is very likely that the API will change multiple times before a
stable 1.0.0 release. In practice, this means that upgrading `feu` to a new version will
possibly break any code that was using the old version of `feu`.

## License

`feu` is licensed under BSD 3-Clause "New" or "Revised" license available
in [LICENSE](https://github.com/durandtibo/feu/blob/main/LICENSE) file.
