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

Compare package versions to determine compatibility:

```python
from feu import compare_version

# Compare versions
result = compare_version("2.0.0", "1.5.0")
print(result)  # Returns 1 (first version is greater)

result = compare_version("1.0.0", "2.0.0")
print(result)  # Returns -1 (first version is less)

result = compare_version("1.5.0", "1.5.0")
print(result)  # Returns 0 (versions are equal)
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
from feu.package import find_closest_version, is_valid_version

# Check if a specific version is valid for your Python version
is_valid = is_valid_version(
    pkg_name="numpy", pkg_version="2.0.2", python_version="3.10"
)
print(f"NumPy 2.0.2 is valid for Python 3.10: {is_valid}")

# Find the closest valid version
closest = find_closest_version(
    pkg_name="numpy",
    pkg_version="1.0.0",  # This is too old for Python 3.11
    python_version="3.11",
)
print(f"Closest valid version: {closest}")  # Will return "1.23.2"
```

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

# Install the closest valid version for your Python environment
install_package_closest_version(
    installer=InstallerSpec(name="pip"),
    package=PackageSpec(name="numpy", version="2.0.2"),
)
```

## Managing Package Configurations

Add custom package configurations to the registry:

```python
from feu.package import PackageConfig

# Add a custom package configuration
PackageConfig.add_config(
    pkg_name="my_package",
    python_version="3.11",
    pkg_version_min="1.2.0",
    pkg_version_max="2.0.0",
    exist_ok=True,
)

# Get the configuration for a package
config = PackageConfig.get_config(pkg_name="my_package", python_version="3.11")
print(config)  # {'min': '1.2.0', 'max': '2.0.0'}

# Get min and max versions
min_version, max_version = PackageConfig.get_min_and_max_versions(
    pkg_name="numpy", python_version="3.11"
)
print(f"Min: {min_version}, Max: {max_version}")
```

## Working with Git Repositories

If you have installed the `git` extra (`pip install 'feu[git]'`), you can work with git repositories:

```python
from feu.git import get_git_branch, get_git_last_commit_hash

# Get the current git branch
branch = get_git_branch()
print(f"Current branch: {branch}")

# Get the last commit hash
commit_hash = get_git_last_commit_hash()
print(f"Last commit: {commit_hash}")
```

## Supported Packages

`feu` includes built-in version compatibility information for common packages:

- **Scientific Computing**: numpy, scipy, pandas, xarray
- **Machine Learning**: torch, jax, scikit-learn
- **Data Handling**: pyarrow
- **Visualization**: matplotlib
- **Web**: requests, click

Each package has defined minimum and maximum versions for different Python versions (3.9, 3.10, 3.11, 3.12, 3.13, 3.14).

## Testing Utilities

`feu` provides testing utilities for checking package availability in tests:

```python
from feu.testing import (
    click_available,
    gitpython_available,
    requests_available,
)


# Use as decorators in pytest
@click_available
def test_click_feature():
    # This test only runs if click is available
    pass


@gitpython_available
def test_git_feature():
    # This test only runs if gitpython is available
    pass


@requests_available
def test_http_feature():
    # This test only runs if requests is available
    pass
```

## Common Use Cases

### Use Case 1: Multi-Python Version Project

If you're maintaining a project that supports multiple Python versions:

```python
import sys
from feu.package import find_closest_version

python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

# Find compatible numpy version
numpy_version = find_closest_version(
    pkg_name="numpy", pkg_version="2.0.0", python_version=python_version
)
print(f"Installing numpy {numpy_version} for Python {python_version}")
```

### Use Case 2: Safe Package Installation

Before installing a package, check if the version is compatible:

```python
import sys
from feu.package import is_valid_version
from feu import install_package
from feu.utils.package import PackageSpec
from feu.utils.installer import InstallerSpec

python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
desired_version = "2.0.2"

if is_valid_version("numpy", desired_version, python_version):
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
