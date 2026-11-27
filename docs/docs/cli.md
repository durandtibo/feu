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

An unexpected error, such as a network failure, a missing extra or a failed installation, is not
caught: Python prints the traceback on the standard error and the status is `1`. So a script that
must tell a negative answer from a failure has to check that the standard output holds the answer
(`check-valid-version` prints `False`).

`feu --version` prints the version. `feu` is a console script; `python -m feu` is equivalent.
`--verbose` is an option of `feu` itself, so it goes before the command:
`feu --verbose install --pkg-name=numpy`.

A wildcard version request (`2.*`) and `package-versions` download the releases from PyPI, so they
need network access and the `requests` extra (`pip install 'feu[cli,requests]'`).

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

Every option has a short form (`-n`, `-v`, and `-p` / `-f` for the target; see the reference
above). A free-threaded target is chosen with a `t` suffix or with `--free-threaded`, and a
contradiction between the two is a usage error:

```shell
$ feu find-closest-version -n numpy -v 1.26.4 -p 3.14t
2.3.2
$ feu find-closest-version -n numpy -v 1.26.4 -p 3.14 --free-threaded
2.3.2
$ feu find-closest-version -n numpy -p 3.14t --no-free-threaded
Usage: feu find-closest-version [OPTIONS]
...
$ echo $?
2
```

Without `--pkg-version`, the request is the latest version. For a package whose latest release is
compatible, the request itself is printed, which is an empty line.

Check if a version is valid. The exit status is `0` when the version is valid:

```shell
$ feu check-valid-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10
True
$ feu check-valid-version --pkg-name=numpy --pkg-version=1.0.0 --python-version=3.11
False
```

An exact version of a package without data is valid, but a wildcard of such a package is not:

```shell
$ feu check-valid-version -n my-package -v 1.0
True
$ feu check-valid-version -n my-package -v '1.*'
False
```

Install a package, with extras and installer arguments:

```shell
feu install --pkg-name=numpy --pkg-version=2.0.2
feu install --pkg-name=pandas --pkg-version='2.*' --pkg-extras=performance
feu install --installer-name=uv --installer-args='--upgrade' --pkg-name=numpy
feu install -i uv -a '--upgrade --pre' -n pandas -v '2.*' -e performance,excel
feu --verbose install -n numpy -v 2.0.2  # logs the pip command on the standard error
python -m feu install -n numpy           # the same CLI, for a given interpreter
```

Write the versions to test of the dependencies of a project, from the bounds of its
`pyproject.toml`. For each dependency of `[project.dependencies]` and
`[project.optional-dependencies]`, the output holds the latest stable version of each minor version
at or above the lower bound (of each major version for the packages given with `--major-only`, which
defaults to `packaging`), and the first stable version at or above the lower bound. The upper bound
is not applied. The result is a JSON object, written to the standard output unless `--output` is
given:

```shell
feu package-versions --pyproject pyproject.toml --output dev/config/package_versions.json
feu package-versions --major-only packaging --major-only click
```

## Use in a shell script or a workflow

The standard output holds only the answer, so it can be captured. An unsupported request makes the
step fail instead of installing `pkg==None`:

```shell
VERSION=$(feu find-closest-version --pkg-name=numpy --pkg-version=2.0.2 --python-version=3.10) \
  && feu install --pkg-name=numpy --pkg-version="$VERSION"
```

In a GitHub Actions matrix, give the Python version of the job to the command (`3.14t` selects the
free-threaded build):

```yaml
- name: Install the closest valid NumPy
  run: |
    VERSION=$(feu find-closest-version -n numpy -v 2.0.2 -p "${PYTHON_VERSION}")
    feu install -n numpy -v "${VERSION}"
  env:
    PYTHON_VERSION: ${{ matrix.python-version }}
```

## benchmark-trend

Show the trend of the `pytest-benchmark` results saved in a directory (for example by a scheduled
workflow with `pytest --benchmark-save=run --benchmark-storage=.benchmarks`). The latest run is
compared with the median of the previous runs, which is stable on noisy runners.

```shell
feu benchmark-trend .benchmarks
feu benchmark-trend .benchmarks --days 30 --baseline-runs 5 --threshold 30 --prune
feu benchmark-trend .benchmarks --kind import --stat min --unit ms
```

| Option                 | Default     | Meaning                                                                                                                                                                                       |
| ---------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--kind`               | `benchmark` | `benchmark` reads the times of the benchmarks, `import` reads the import times (see below).                                                                                                   |
| `--stat`               | `median`    | The statistic of the times: `min`, `mean`, `median` or `max`.                                                                                                                                 |
| `--unit`               | by kind     | The unit of the report: `s`, `ms`, `us` or `ns`. The default is `us` (`benchmark`) or `ms` (`import`).                                                                                        |
| `--label`              | `name`      | `name` is the name without the `test_` prefix and the `_benchmark` suffix (`test_sort_benchmark[10]` is `sort[10]`). `fullname` is the full name, for two benchmarks that have the same name. |
| `--days`               | `90`        | The size of the window in days (at least 1).                                                                                                                                                  |
| `--baseline-runs`      | `7`         | The number of previous runs of the baseline (at least 1).                                                                                                                                     |
| `--threshold`          | `50`        | The slowdown in percent above which a benchmark is a regression (greater than 0).                                                                                                             |
| `--prune`              | off         | Delete the results older than the window, after the report was made.                                                                                                                          |
| `--fail-on-regression` | off         | Exit with the status `1` if there is a regression.                                                                                                                                            |

The standard output holds only the Markdown report. The `::warning::` annotations of the
regressions and the messages go to the standard error. Both are written as UTF-8, so a redirect
(`feu benchmark-trend .benchmarks > report.md`) works under any locale. The report shows the times
with three significant digits, and has one section per machine if the storage has the results of
several machines.

The exit status is `0`, `1` with `--fail-on-regression` and a regression, and `2` for a usage error
or an invalid result file. If there is no result in the window, a message goes to the standard
error, the standard output is empty and the status is `0`: the first run of a new workflow has no
history.

### In a scheduled workflow

Keep the storage between the runs (here with the cache of GitHub Actions), add the results of the
run, then write the report in the summary of the job. The annotations of the regressions go to the
standard error, so they are still read by GitHub when the standard output is redirected:

```yaml
- uses: actions/cache@v4
  with:
    path: .benchmarks
    key: benchmarks-${{ github.run_id }}
    restore-keys: benchmarks-
- run: pytest tests/benchmarks --benchmark-only --benchmark-save=run --benchmark-storage=.benchmarks
- run: feu benchmark-trend .benchmarks --prune >> "$GITHUB_STEP_SUMMARY"
```

### What is read

- Only the files named `NNNN_*.json`, the names that `pytest-benchmark` writes
  (`<storage>/<machine>/0001_run.json`). Other JSON files are ignored.
- A file that has this name and is not a valid result (invalid JSON, a missing `datetime` or
  `stats`, a time that is not a finite number greater than zero) is an error that names the file.
  Nothing is skipped silently, because a trend computed on a different history without notice is
  misleading, and nothing is deleted when the load fails.
- The runs of different machines (the directories of the storage) are never compared with each
  other.
- Two benchmarks of a run with the same label are an error; use `--label fullname`.

### The `import` kind

The `import` kind reads the import times that a test records in `extra_info`, so a storage can hold
both kinds. The key is `import_seconds_<stat>` (for example `import_seconds_median`), the value is
in seconds, and the label is the parameter of the test. A producer is a test such as:

```python
import subprocess
import sys
import time

import pytest


@pytest.mark.parametrize("package", ["feu", "feu.utils"])
def test_import(benchmark, package):
    def import_package():
        start = time.perf_counter()
        subprocess.run([sys.executable, "-c", f"import {package}"], check=True)
        return time.perf_counter() - start

    benchmark(import_package)
    benchmark.extra_info["import_seconds_median"] = benchmark.stats["median"]
```

A test that has no `import_seconds_<stat>` is ignored by this kind.

### Python API

The command is a thin layer over `feu.benchmark`: `load_runs` reads and validates the files,
`find_regressions` and `make_report` are pure functions of the runs, and `prune_runs` deletes the
old files. See [Benchmark trend](usage.md#benchmark-trend) for an example and the
[API reference](refs/benchmark.md) for the signatures.
