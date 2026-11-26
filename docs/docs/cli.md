# Command Line Interface

`feu` provides a command-line interface (CLI) for package management tasks. To use the CLI, you need
to install the optional `cli` dependency:

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

## Commands

The reference below is generated from the code (`mkdocs-click`), so it cannot drift. `install`
installs into the interpreter that runs `feu` for the current target, so it has no target option.
The platform (OS and CPU architecture) is always the current one: there is no `--os` or `--arch`
option.

<!-- prettier-ignore -->
::: mkdocs-click
    :module: feu.cli
    :command: cli
    :prog_name: feu
    :depth: 1

## Examples

Find the closest valid NumPy version for Python 3.10 and for an older NumPy on Python 3.11:

```shell
$ feu find-closest-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10
2.0.2
$ feu find-closest-version --pkg-name=numpy --pkg-version=1.0.0 --python-version=3.11
1.23.2
```

A wildcard or an empty version request is resolved like a version. The request itself is printed
when the latest compatible release is in an open-ended range, so that the installer picks the real
latest release:

```shell
$ feu find-closest-version --pkg-name=numpy --pkg-version='1.*' --python-version=3.9
1.26.4
$ feu find-closest-version --pkg-name=numpy --pkg-version='1.24.*' --python-version=3.14
No version of package numpy matches '1.24.*' for target Target(python_version='3.14', ...)
$ echo $?
1
```

Check if a version is valid. The exit status is `0` when the version is valid:

```shell
$ feu check-valid-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10
True
$ feu check-valid-version --pkg-name=numpy --pkg-version=1.0.0 --python-version=3.11
False
```

Install a package, with extras and installer arguments:

```shell
feu install --pkg-name=numpy --pkg-version=2.0.2
feu install --pkg-name=pandas --pkg-version='2.*' --pkg-extras=performance
feu install --installer-name=uv --installer-args='--upgrade' --pkg-name=numpy
```

Write the versions to test of the dependencies of a project, from the bounds of its
`pyproject.toml`:

```shell
feu package-versions --pyproject pyproject.toml --output dev/config/package_versions.json
```

## Use in a shell script or a workflow

The standard output holds only the answer, so it can be captured. An unsupported request makes the
step fail instead of installing `pkg==None`:

```shell
VERSION=$(feu find-closest-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10) \
  && feu install --pkg-name=numpy --pkg-version="$VERSION"
```

Show the trend of the `pytest-benchmark` results saved in a directory over the last 90 days. The
Markdown report goes to the standard output and the `::warning::` annotations of the benchmarks that
are more than 50% slower than the median of the previous runs go to the standard error. Use
`--kind import` for the import time results:

```shell
feu benchmark-trend .benchmarks --days 90 --prune
feu benchmark-trend .benchmarks --kind import --threshold 30
```

Use another statistic of the times with `--stat` (for example `mean` or `min`). The `import` kind
reads `import_seconds_<stat>` of the `extra_info`:

```shell
feu benchmark-trend .benchmarks --stat mean
```

Show the times in another unit with `--unit` (`s`, `ms`, `us` or `ns`). The default is `us` for the
`benchmark` kind and `ms` for the `import` kind:

```shell
feu benchmark-trend .benchmarks --unit ms
```

For another unit, set its name with `--unit` and its conversion from seconds with `--scale`:

```shell
feu benchmark-trend .benchmarks --unit min --scale 0.0166667
```
