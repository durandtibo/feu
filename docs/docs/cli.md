# Command Line Interface

`feu` provides a command-line interface (CLI) for package management tasks. To use the CLI, you need to install the optional `cli` dependency:

```shell
pip install 'feu[cli]'
```

## Available Commands

The CLI provides three main commands:

1. `install` - Install a package with version compatibility checks
2. `find-closest-version` - Find the closest valid version for a package
3. `check-valid-version` - Check if a package version is valid for a Python version

## Install Command

Install a package with automatic version compatibility handling for your Python environment.

### Syntax

```shell
python -m feu install [OPTIONS]
```

### Options

- `-n, --pkg-name TEXT` - Package name (required)
- `-v, --pkg-version TEXT` - Package version (required)
- `-e, --pkg-extras TEXT` - Package extra dependencies (optional, comma-separated)
- `-i, --installer-name TEXT` - Installer name (default: "pip")
- `-a, --installer-args TEXT` - Installer arguments (optional)

### Examples

Install NumPy version 2.0.2:

```shell
python -m feu install --pkg-name=numpy --pkg-version=2.0.2
```

Install NumPy with specific extras:

```shell
python -m feu install --pkg-name=numpy --pkg-version=2.0.2 --pkg-extras=dev,doc
```

Install with custom installer arguments:

```shell
python -m feu install \
  --pkg-name=numpy \
  --pkg-version=2.0.2 \
  --installer-name=pip \
  --installer-args="--upgrade --no-cache-dir"
```

## Find Closest Version Command

Find the closest valid version of a package for a specific Python version.

### Syntax

```shell
python -m feu find-closest-version [OPTIONS]
```

### Options

- `-n, --pkg-name TEXT` - Package name (required)
- `-v, --pkg-version TEXT` - Package version to check (required)
- `-p, --python-version TEXT` - Python version (required, e.g., "3.10", "3.11")

### Examples

Find the closest valid NumPy version for Python 3.10:

```shell
python -m feu find-closest-version \
  --pkg-name=numpy \
  --pkg-version=2.0.2 \
  --python-version=3.10
```

Output:
```
2.0.2
```

Check what version would be used for an older NumPy version on Python 3.11:

```shell
python -m feu find-closest-version \
  --pkg-name=numpy \
  --pkg-version=1.0.0 \
  --python-version=3.11
```

Output:
```
1.23.2
```

This shows that NumPy 1.0.0 is too old for Python 3.11, so the minimum supported version (1.23.2) would be used instead.

## Check Valid Version Command

Check if a specific package version is valid for a given Python version.

### Syntax

```shell
python -m feu check-valid-version [OPTIONS]
```

### Options

- `-n, --pkg-name TEXT` - Package name (required)
- `-v, --pkg-version TEXT` - Package version to check (required)
- `-p, --python-version TEXT` - Python version (required, e.g., "3.10", "3.11")

### Examples

Check if NumPy 2.0.2 is valid for Python 3.10:

```shell
python -m feu check-valid-version \
  --pkg-name=numpy \
  --pkg-version=2.0.2 \
  --python-version=3.10
```

Output:
```
True
```

Check if NumPy 1.0.0 is valid for Python 3.11:

```shell
python -m feu check-valid-version \
  --pkg-name=numpy \
  --pkg-version=1.0.0 \
  --python-version=3.11
```

Output:
```
False
```

## Practical Workflows

### Workflow 1: Verify Before Install

Before installing a package, check if the version is compatible:

```shell
# Check compatibility
VALID=$(python -m feu check-valid-version \
  --pkg-name=numpy \
  --pkg-version=2.0.2 \
  --python-version=3.10)

if [ "$VALID" = "True" ]; then
  echo "Version is compatible, proceeding with installation..."
  python -m feu install --pkg-name=numpy --pkg-version=2.0.2
else
  echo "Version is not compatible, finding closest version..."
  VERSION=$(python -m feu find-closest-version \
    --pkg-name=numpy \
    --pkg-version=2.0.2 \
    --python-version=3.10)
  echo "Installing version $VERSION instead"
  python -m feu install --pkg-name=numpy --pkg-version=$VERSION
fi
```

### Workflow 2: Batch Installation

Install multiple packages with compatibility checks:

```shell
#!/bin/bash

PACKAGES=(
  "numpy:2.0.2"
  "pandas:2.0.0"
  "scipy:1.10.0"
)

PYTHON_VERSION="3.10"

for pkg in "${PACKAGES[@]}"; do
  IFS=':' read -r name version <<< "$pkg"
  
  echo "Processing $name $version..."
  
  closest=$(python -m feu find-closest-version \
    --pkg-name=$name \
    --pkg-version=$version \
    --python-version=$PYTHON_VERSION)
  
  echo "Installing $name $closest"
  python -m feu install --pkg-name=$name --pkg-version=$closest
done
```

### Workflow 3: CI/CD Integration

Use in continuous integration to ensure compatible versions:

```yaml
# .github/workflows/install-deps.yml
name: Install Dependencies

on: [push, pull_request]

jobs:
  install:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12', '3.13']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install feu
        run: pip install 'feu[cli]'
      
      - name: Install numpy with version check
        run: |
          python -m feu install \
            --pkg-name=numpy \
            --pkg-version=2.0.2
```

## Tips and Best Practices

1. **Always specify Python version**: When using `find-closest-version` or `check-valid-version`, make sure to specify the correct Python version you're targeting.

2. **Use extras for optional dependencies**: When installing packages with optional features, use the `--pkg-extras` flag to include them.

3. **Combine with pip options**: Use `--installer-args` to pass additional pip options like `--upgrade`, `--no-deps`, or `--no-cache-dir`.

4. **Script automation**: The CLI commands are designed to be easily integrated into shell scripts and CI/CD pipelines.

5. **Version checking**: Always use `check-valid-version` before attempting installation in production environments to avoid runtime errors.
