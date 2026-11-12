# Command Line Interface

`feu` provides a command-line interface (CLI) for package management tasks. To use the CLI, you need to install the optional `cli` dependency:

```shell
pip install 'feu[cli]'
```

## Exit Status

The standard output holds only the answer of a command, the logs and the error messages go to the
standard error (`--verbose` logs the executed commands), and the exit status carries the result:

- `0`: success, or a valid version;
- `1`: a negative answer (no compatible version, or `check-valid-version` printed `False`);
- `2`: a usage error (unknown option, missing option, invalid version request).

`feu --version` prints the version. `feu` is a console script; `python -m feu` is equivalent.

## Available Commands

The CLI provides four commands:

1. `install` - Install a package with version compatibility checks
2. `find-closest-version` - Find the closest valid version for a package
3. `check-valid-version` - Check if a package version is valid for a Python version
4. `package-versions` - Write the versions to test of the dependencies of a project

`install` installs into the interpreter that runs `feu` for the current target, so it has no target
option.

## Install Command

Install a package with automatic version compatibility handling for your Python environment.

### Syntax

```shell
feu install [OPTIONS]
```

### Options

- `-n, --pkg-name TEXT` - Package name (required)
- `-v, --pkg-version TEXT` - Package version request: an exact version (`2.0.2`), a wildcard (`2.*`) or an empty string for the latest version (optional, default: latest)
- `-e, --pkg-extras TEXT` - Package extra dependencies (required, comma-separated; pass an empty string for none)
- `-i, --installer-name TEXT` - Installer name (default: "pip")
- `-a, --installer-args TEXT` - Installer arguments (default: "", i.e. none)

### Examples

Install NumPy version 2.0.2:

```shell
feu install --pkg-name=numpy --pkg-version=2.0.2
```

Install NumPy with specific extras:

```shell
feu install --pkg-name=numpy --pkg-version=2.0.2 --pkg-extras=dev,doc
```

Install with custom installer arguments:

```shell
feu install \
  --pkg-name=numpy \
  --pkg-version=2.0.2 \
  --installer-name=pip \
  --installer-args="--upgrade --no-cache-dir"
```

## Find Closest Version Command

Find the closest valid version of a package for a specific target environment.

### Syntax

```shell
feu find-closest-version [OPTIONS]
```

### Options

- `-n, --pkg-name TEXT` - Package name (required)
- `-v, --pkg-version TEXT` - Package version request to check: an exact version (`2.0.2`), a wildcard (`2.*`) or an empty string for the latest version (optional, default: latest)
- `-p, --python-version TEXT` - Python version, e.g. "3.10", "3.11" (optional; defaults to the
  current Python version)
- `-f, --free-threaded / --no-free-threaded` - Whether the target is a free-threaded build
  (optional; defaults to the current interpreter's free-threaded status)

The platform (OS and CPU architecture) is always the current one: there is no `--os` or `--arch`
option.

### Examples

Find the closest valid NumPy version for Python 3.10:

```shell
feu find-closest-version \
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
feu find-closest-version \
  --pkg-name=numpy \
  --pkg-version=1.0.0 \
  --python-version=3.11
```

Output:

```
1.23.2
```

This shows that NumPy 1.0.0 is too old for Python 3.11, so the minimum supported version (1.23.2) would be used instead.

If the options are omitted, the command falls back to the properties of the Python interpreter
running the CLI. The standard output holds only the version, so it can be used in `$(...)`. If no
valid version exists for the target, the message is printed on the standard error, the standard
output is empty and the exit status is `1`.

## Check Valid Version Command

Check if a specific package version is valid for a given target environment.

### Syntax

```shell
feu check-valid-version [OPTIONS]
```

### Options

- `-n, --pkg-name TEXT` - Package name (required)
- `-v, --pkg-version TEXT` - Package version request to check: an exact version (`2.0.2`), a wildcard (`2.*`) or an empty string for the latest version (optional, default: latest)
- `-p, --python-version TEXT` - Python version, e.g. "3.10", "3.11" (optional; defaults to the
  current Python version)
- `-f, --free-threaded / --no-free-threaded` - Whether the target is a free-threaded build
  (optional; defaults to the current interpreter's free-threaded status)

The platform (OS and CPU architecture) is always the current one: there is no `--os` or `--arch`
option.

### Examples

Check if NumPy 2.0.2 is valid for Python 3.10:

```shell
feu check-valid-version \
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
feu check-valid-version \
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
VALID=$(feu check-valid-version \
  --pkg-name=numpy \
  --pkg-version=2.0.2 \
  --python-version=3.10)

if [ "$VALID" = "True" ]; then
  echo "Version is compatible, proceeding with installation..."
  feu install --pkg-name=numpy --pkg-version=2.0.2
else
  echo "Version is not compatible, finding closest version..."
  VERSION=$(feu find-closest-version \
    --pkg-name=numpy \
    --pkg-version=2.0.2 \
    --python-version=3.10)
  echo "Installing version $VERSION instead"
  feu install --pkg-name=numpy --pkg-version=$VERSION
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

  closest=$(feu find-closest-version \
    --pkg-name=$name \
    --pkg-version=$version \
    --python-version=$PYTHON_VERSION)

  echo "Installing $name $closest"
  feu install --pkg-name=$name --pkg-version=$closest
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
        python-version: ["3.10", "3.11", "3.12", "3.13"]

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
          feu install \
            --pkg-name=numpy \
            --pkg-version=2.0.2
```

## Tips and Best Practices

1. **Always specify Python version**: When using `find-closest-version` or `check-valid-version`, make sure to specify the correct Python version you're targeting.

2. **Use extras for optional dependencies**: The `--pkg-extras` flag is required; pass an empty string (`--pkg-extras=""`) when there are none, or a comma-separated list to include optional features.

3. **Combine with pip options**: Use `--installer-args` to pass additional pip options like `--upgrade`, `--no-deps`, or `--no-cache-dir`.

4. **Script automation**: The CLI commands are designed to be easily integrated into shell scripts and CI/CD pipelines.

5. **Version checking**: Always use `check-valid-version` before attempting installation in production environments to avoid runtime errors.

## Package Versions Command

Write the versions to test of the dependencies of a `pyproject.toml` (the latest version of each
minor version at or above the lower bound, or of each major version for the packages of
`--major-only`). It replaces the `dev/generate_versions.py` script that is copied in several
repositories.

### Syntax

```shell
feu package-versions [OPTIONS]
```

### Options

- `--pyproject PATH` - The `pyproject.toml` file (default: `pyproject.toml`)
- `--output PATH` - The JSON file to write (default: the standard output)
- `--major-only TEXT` - A package for which only the major versions are kept; repeat the option
  for several packages (default: `packaging`)

### Example

```shell
feu package-versions --pyproject pyproject.toml --output dev/config/package_versions.json
```
