# `feu.benchmark`: target state and the changes to reach it

This document describes the design `feu.benchmark` should have, then the changes to make to the
current implementation (`main`, `2e57596`) to get there. The aim is a small sub-package that is easy
to maintain: **one loader that validates, one pure analysis, one pure renderer, one thin command**.
It follows the properties of `feu` (`docs/docs/design.md`) and of `CLAUDE.md`. Breaking changes are
accepted (`feu` is `0.x`, and `review/target_state.md` plans `0.9.0` as the next release), and the
future state is more important than the past one.

`feu.benchmark` is four commits old (#1095 to #1098: the `benchmark-trend` command, then its
`--stat`, `--unit` and `--scale` options). It grew by adding options to one module, and it was never
checked against a real `pytest-benchmark` result: every input of its 96 unit tests is a hand-written
dictionary. That is where most findings of section 2 come from.

The documentation of `feu` has no properties for this sub-package (`docs/docs/design.md` lists 15
properties for the whole package; `docs/docs/dev/architecture.md` only says that `feu.benchmark` is
outside the chain and uses the standard library). The properties of section 1 are therefore
**derived**: each one says which property of `design.md` or which rule of `CLAUDE.md` it applies,
and which finding of section 2 breaks it.

Evidence comes from probes run on `main` (Python 3.14, `.venv`) and from reading the code. Items are
marked **[verified]** (reproduced by running code or a command), **[reading]** (from the code only)
or **[downstream]** (from a search of the other repositories of the owner). Nothing in `src`,
`tests` or `docs` was changed by this document.

## 1. Properties of the sub-package

These are the rules `feu.benchmark` must satisfy. Every design choice of section 3 exists to make
one of them true **by construction** (in one place) instead of by the discipline of each function.

| #   | Property                           | Statement                                                                                                                                                                                                                                                                                                                             | Applies                |
| --- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| B1  | **Lightweight**                    | `feu.benchmark` uses only the standard library. Importing it imports no optional library, reads no file and does no network call. The command needs `click` like every command.                                                                                                                                                       | design 1, 2            |
| B2  | **Read-only unless asked**         | Loading and reporting never change the storage. Files are deleted only by `prune_runs`, which the command calls only when `--prune` is given, and only after the report was built.                                                                                                                                                    | design 4 (new)         |
| B3  | **Strict input, loud failure**     | A file of the storage that looks like a `pytest-benchmark` result is validated. A malformed file, a time that is not a finite number greater than zero, or an invalid argument raises `ValueError` with an explicit message that names the file or the argument. An empty result is reported with a message, never as an empty table. | design 4, 12           |
| B4  | **One stable label per benchmark** | The label of a benchmark is a function of its entry, so it is the same in every run. Two entries of a run never get the same label: the load fails instead of keeping one of them.                                                                                                                                                    | design 4, 10 (new)     |
| B5  | **Comparable runs only**           | A run is compared only with runs of the same machine, the same kind and the same statistic. `pytest-benchmark` already stores the runs of a machine in one directory; `feu` uses it.                                                                                                                                                  | design 3 (new)         |
| B6  | **Honest numbers**                 | A time is shown with three significant digits in a unit chosen from a closed set (`s`, `ms`, `us`, `ns`). A change is never computed from a zero (B3 forbids it), so no change is hidden as `+0.0%`.                                                                                                                                  | design 4 (new)         |
| B7  | **Deterministic output**           | The same storage gives the same bytes. Rows are sorted by `(value, label)`, regressions by `(-change, label)`, files by path, runs by `(date, path)`.                                                                                                                                                                                 | design 10              |
| B8  | **Safe, portable output**          | A label cannot break a Markdown table or a GitHub workflow command (both are escaped). Files are read and the report is written as UTF-8 on every platform.                                                                                                                                                                           | design 14 (new)        |
| B9  | **A thin command**                 | The standard output holds only the Markdown report, the annotations and messages go to the standard error, and the exit status carries the result: `0` ok, `1` a regression with `--fail-on-regression`, `2` a usage error. The command parses, calls the API and prints; it holds no logic.                                          | design 11              |
| B10 | **Pure core, I/O at the edge**     | One module reads and deletes files. Analysis and rendering are pure functions of values. Results are frozen dataclasses with named fields, not positional tuples.                                                                                                                                                                     | design 9, 13           |
| B11 | **Strict, typed, documented**      | Options are keyword-only. Every public function has a doctest. The input format is tested against a result written by the real `pytest-benchmark`, not only against hand-written dictionaries.                                                                                                                                        | design 12, `CLAUDE.md` |

Properties B1, B9 (partly), B10 (partly) and B11 (partly) are promises that exist today. B2 to B8 are
new rules. Today the sub-package breaks B2 to B11 in at least one place (section 2).

## 2. What differs today

Each finding says which property it breaks. The probe commands are in the appendix.

| #   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                             | Evidence         | Breaks   |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| F1  | `load_runs` reads **every** `*.json` below the storage. A JSON file that is not a result (`{"x": 1}`) raises a bare `KeyError: 'datetime'`; invalid JSON raises `JSONDecodeError`. Neither names the file.                                                                                                                                                                                                                          | **[verified]**   | B3       |
| F2  | With `prune=True` the old files are deleted **while loading**. If a later file fails to load (F1), the old file is already gone and no report was made.                                                                                                                                                                                                                                                                             | **[verified]**   | B2       |
| F3  | The label rule is inconsistent. On a real `pytest-benchmark` 5.3.1 run, `test_sort_benchmark` becomes `sort` but `test_sort_benchmark[10]` becomes `sort_benchmark[10]`, because `removesuffix("_benchmark")` does not see the suffix before `[10]`. The same test shows two different spellings in one table.                                                                                                                      | **[verified]**   | B4       |
| F4  | Two entries with the same label in one run (the same test name in two classes or two modules) silently overwrite each other: the table shows the slower one (`{'sort': 0.009}` for 0.001 and 0.009).                                                                                                                                                                                                                                | **[verified]**   | B4       |
| F5  | Runs of different machines are merged. `pytest-benchmark` writes `<storage>/<machine-id>/NNNN_*.json` (`Darwin-CPython-3.15-64bit/0001_run.json`), and `rglob` mixes the directories: a Linux run and a macOS run of the same benchmark give `[0.001, 0.005]`, a false regression of 400%.                                                                                                                                          | **[verified]**   | B5       |
| F6  | A zero baseline hides a regression: `find_regressions` returns `[]` for `0.0` then `1.0`, and the table shows `+0.0%`.                                                                                                                                                                                                                                                                                                              | **[verified]**   | B3, B6   |
| F7  | `.1f` loses the information. A real fast benchmark shows `0.1` and `0.2` (µs); with `--unit s` every cell of a micro-benchmark is `0.0`.                                                                                                                                                                                                                                                                                            | **[verified]**   | B6       |
| F8  | `window`, `days` and `threshold` are not validated. `window=0` is `previous[-0:]`, the **whole** list, not "no run". `feu benchmark-trend DIR --days 0` prints `No results.` and exits `0`.                                                                                                                                                                                                                                         | **[verified]**   | B3       |
| F9  | An unknown statistic is handled in two ways. The `benchmark` kind raises `UnknownStatError(KeyError)`, whose `str()` is quoted (the CLI works around it with `exc.args[0]`). The `import` kind returns runs with no times, and the command prints a report with an **empty table** and exits `0`.                                                                                                                                   | **[verified]**   | B3       |
| F10 | A run with no usable entry still counts: three files, one without entries, give `(3 runs)`. The title also says `(1 runs)`.                                                                                                                                                                                                                                                                                                         | **[verified]**   | B3, B6   |
| F11 | Labels are not escaped. A `\|` in a label (a parameter) breaks the table. A `%` or a newline in a label gives an invalid `::warning::` command (the newline ends the command; GitHub expects `%25` and `%0A`).                                                                                                                                                                                                                      | **[verified]**   | B8       |
| F12 | Encoding depends on the locale. `path.read_text()` has no `encoding`: with `LC_ALL=C` a result with `µ` raises `UnicodeDecodeError`. Redirecting the output under a `cp1252` console (`feu benchmark-trend DIR > report.md`) raises `UnicodeEncodeError` on the sparkline character `▁`.                                                                                                                                            | **[verified]**   | B8       |
| F13 | The order of equal rows depends on the insertion order: two benchmarks with the same latest time are listed `b`, `a`.                                                                                                                                                                                                                                                                                                               | **[verified]**   | B7       |
| F14 | The public API is 17 names for one command. Results are positional tuples (`Run = (date, dict)`, `Regression = (label, latest, baseline, change)`); `with_unit` special-cases `"us"` to `"µs"`; `TrendKind` carries two callables and is used only through two constants; `window` (runs) and `days` (time) are both windows.                                                                                                       | **[reading]**    | B10, B11 |
| F15 | The command holds logic: unit and scale resolution, the "scale requires unit" rule, the translation of two exceptions, the choice of what goes to the standard error. A regression can only be a warning: there is no way to fail a job.                                                                                                                                                                                            | **[reading]**    | B9       |
| F16 | The tests are 96 unit tests with 100% coverage of `feu.benchmark` **[verified]**, but no input is a result written by `pytest-benchmark` and there is no integration test. `pytest-benchmark` is not installed in `.venv` **[verified]**, so a change of its format is not detected. The `import` kind reads `extra_info["import_seconds_<stat>"]`, a contract written by another repository; it is documented only in a docstring. | **[verified]**   | B11      |
| F17 | Nothing in this repository calls `benchmark-trend` (`.github/` has no use), and `gh search code "benchmark-trend" --owner durandtibo` returned no result. The command is used by scheduled workflows of other repositories or not at all; the search may not index every repository.                                                                                                                                                | **[downstream]** | none     |

What is **good** and stays: the algorithm (the latest run against the median of the previous `N`
runs, which is stable on noisy runners), the Markdown columns, the sparkline, the `::warning::`
annotations on the standard error, the defaults (90 days, 7 runs, 50%), the standard-library-only
imports, and `benchmark` outside the chain (`tests/unit/test_layers.py`).

## 3. Architecture

### 3.1 Layout

Three small modules, one per role, so that B10 can be read from the file list:

```text
feu/benchmark/
  __init__.py   # re-exports the public names (section 4)
  runs.py       # Run, KINDS, STATS, load_runs, prune_runs         <- the only I/O (B10)
  trend.py      # Regression, find_regressions                     <- pure
  report.py     # TrendReport, UNITS, make_report                  <- pure
```

`feu.benchmark` imports nothing from `feu` and nothing outside the standard library (B1). The layer
test keeps `benchmark` outside the chain. The estimated size is the one of today (about 440 lines
with 117 statements): the removed code (`TrendKind` and its callables, `with_unit`, `UnknownStatError`,
the `us` special case) pays for the added code (validation, escaping, machines). This is an estimate,
not a measurement.

### 3.2 The data model (B4, B10)

```python
@dataclass(frozen=True)
class Run:
    date: datetime  # always timezone-aware (a naive date is read as UTC)
    machine: str  # the directory of the file below the storage, "" if there is none
    times: Mapping[str, float]  # label -> seconds, finite and > 0, read-only (MappingProxyType)


@dataclass(frozen=True)
class Regression:
    machine: str
    label: str
    latest: float  # seconds
    baseline: float  # seconds, median of the previous runs
    change: float  # percent, > threshold


@dataclass(frozen=True)
class TrendReport:
    markdown: str  # the report, never empty
    annotations: tuple[str, ...]  # the ::warning:: commands, already escaped
    regressions: tuple[Regression, ...]
```

The three types are frozen, so no caller corrupts a result (design property 9). The times are always
in seconds; the unit exists only in `report.py`.

### 3.3 Loading (`runs.py`, B2 to B5, B8)

One public function reads, one deletes. Both take the storage and the window in days.

```python
KINDS = ("benchmark", "import")
STATS = ("min", "mean", "median", "max")


def load_runs(
    storage: Path,
    *,
    days: int = 90,
    kind: str = "benchmark",
    stat: str = "median",
    label: str = "name",
) -> list[Run]: ...


def prune_runs(storage: Path, *, days: int = 90) -> list[Path]: ...
```

The rules, each one from a finding:

1. **Which files** (F1): only the files that `pytest-benchmark` names itself,
   `storage.rglob("[0-9][0-9][0-9][0-9]_*.json")` (it always prefixes the counter; verified on 5.3.1:
   `0001_run.json`). Other JSON files are not results and are ignored. A matching file that is not
   valid raises `ValueError(f"{path}: not a pytest-benchmark result ({reason})")`, where the
   reason is the missing key or the JSON error. There is no "skip with a warning" mode (D3).
2. **Encoding** (F12): `path.read_text(encoding="utf-8")`, always.
3. **Dates**: `datetime.fromisoformat`, a naive date is read as UTC (older `pytest-benchmark` versions
   wrote a naive date). A file older than `days` is skipped **before** its entries are read.
4. **Times** (F6, B3): the time of an entry is a finite float greater than zero, or the file is
   invalid and its path is in the message. This removes every division by zero downstream and the
   special case of a zero baseline.
5. **Kind** (F9): `benchmark` reads `stats[stat]`. `import` reads `extra_info["import_seconds_<stat>"]`
   and ignores the entries that do not have it, because a storage can hold both kinds. `stat` is one
   of `STATS` (a `ValueError` otherwise), so a typo fails at the call and not as an empty table.
6. **Label** (F3, F4): one function maps an entry to its label.
   - `label="name"` (the default): the name of the entry without the `test_` prefix and without the
     `_benchmark` suffix **placed before the parameter id**, so `test_sort_benchmark[10]` is
     `sort[10]` like `test_sort_benchmark` is `sort`. The `import` kind uses the `param` of the entry
     when it has one (`utils` for `test_import[utils]`), as today.
   - `label="fullname"`: the `fullname` of the entry (`tests/a.py::TestA::test_sort_benchmark`).
   - Two entries of one run with the same label raise
     `ValueError(f"{path}: the label {label!r} is used by two benchmarks; use label='fullname'")`.
     The label rule was checked on seven names (`test_sort_benchmark[10]`, `test_import[utils]`,
     `test_a_b_benchmark[x_benchmark]`, ...) with the pattern
     `^(?:test_)?(?P<core>.*?)(?:_benchmark)?(?P<param>\[.*\])?$`.
7. **Empty runs** (F10): a run with no time is dropped, so the number of runs is the number of runs
   that contribute.
8. **Machines** (F5): `Run.machine` is the parent directory of the file relative to the storage.
9. **Order** (B7): files in the order of their path, the result sorted by `(date, machine)`; Python's
   sort is stable, so the path order breaks the ties.
10. **Arguments** (F8): `days` must be `>= 1`, otherwise `ValueError`.

`prune_runs` deletes the files older than `days` that `load_runs` would skip and returns what it
deleted. It reads only the date of each file, and it is called by the command **after** the report
was made (F2): a failing load leaves the storage as it was.

### 3.4 Analysis (`trend.py`, pure)

```python
def find_regressions(
    runs: Sequence[Run], *, baseline_runs: int = 7, threshold: float = 50.0
) -> list[Regression]: ...
```

The algorithm is the one of today and is **not changed**: for each machine, the latest run is
compared with the median of the previous `baseline_runs` runs that contain the label; the change is
`(latest - baseline) / baseline * 100` and a regression is a change above `threshold`.

- The runs are grouped by machine (B5). A machine with fewer than two runs has no regression.
- `baseline_runs` replaces `window` (F14): `days` is the window in time, `baseline_runs` is the number
  of runs of the baseline, so the word "window" has one meaning.
- `baseline_runs >= 1` and `threshold > 0` are validated (F8): `ValueError` otherwise. `previous[-0:]`
  cannot happen.
- No division needs a guard: every time is greater than zero (rule 4 of 3.3).
- The result is sorted by `(-change, label)` then by machine (B7).

### 3.5 Rendering (`report.py`, pure)

```python
UNITS = {"s": 1.0, "ms": 1e3, "us": 1e6, "ns": 1e9}


def make_report(
    runs: Sequence[Run],
    *,
    kind: str = "benchmark",
    stat: str = "median",
    unit: str | None = None,  # None: "us" for benchmark, "ms" for import
    days: int = 90,
    baseline_runs: int = 7,
    threshold: float = 50.0,
) -> TrendReport: ...
```

- `runs` must not be empty (`ValueError`): the command decides what "no result" means (3.6), the
  library does not return `None`.
- The title is `## Benchmarks (median) over the last 90 days (12 runs)`: the statistic is always
  shown (today it is hidden for the default, so a reader cannot tell), and `1 run` is singular (F10).
- The columns, the sorting key and the sparkline are the ones of today. The table is sorted by
  `(latest, label)` (F13). With more than one machine there is one `###` section per machine, named
  after it, with its own table and its own `#### Regressions` block (B5); with one machine the
  output has the shape of today.
- **Numbers** (F7): `format_time(seconds, unit)` shows three significant digits:
  `decimals = max(0, 2 - floor(log10(value)))`. Checked: `0.1234` gives `0.123`, `12.34` gives `12.3`,
  `123.4` gives `123`, `1234567.8` gives `1234568`. The `Change` column keeps `+0.0%`.
- **Escaping** (F11): a label in a table cell has `|` replaced by `\|`. A label in an annotation is
  escaped as GitHub documents: `%` to `%25`, `\r` to `%0D`, `\n` to `%0A`.
- `us` is shown as `µs`; this is the only place where the symbol exists.

### 3.6 The command (B9, F15)

```text
feu benchmark-trend STORAGE
    [--kind {benchmark,import}] [--stat {min,mean,median,max}] [--unit {s,ms,us,ns}]
    [--label {name,fullname}] [--days N] [--baseline-runs N] [--threshold PERCENT]
    [--prune] [--fail-on-regression]
```

The body is the whole logic, about fifteen lines:

```python
runs = load_runs(storage, days=days, kind=kind, stat=stat, label=label)
if not runs:
    click.echo(f"No {kind} results ({stat}) in the last {days} days in {storage}.", err=True)
    return
report = make_report(
    runs,
    kind=kind,
    stat=stat,
    unit=unit,
    days=days,
    baseline_runs=baseline_runs,
    threshold=threshold,
)
for annotation in report.annotations:
    click.echo(annotation, err=True)
click.echo(report.markdown)
if prune:
    prune_runs(storage, days=days)
if fail_on_regression and report.regressions:
    sys.exit(1)
```

- `ValueError` of the API becomes `click.UsageError` in one place (the existing helper of the CLI),
  not one `try` per call. Range checks (`--days`, `--baseline-runs`, `--threshold`) use
  `click.IntRange(min=1)` and `click.FloatRange(min=0, min_open=True)`, so the usage error comes
  from `click` before the API is called; the API checks anyway because it is public.
- `--kind`, `--stat` and `--unit` are `click.Choice` of `KINDS`, `STATS` and `UNITS` (closed sets, D1,
  D2). `--scale` and `--window` are removed.
- `--fail-on-regression` is new (D6). Without it the exit status is `0` as today. With it a
  regression exits `1`, the "negative answer" of design property 11.
- **UTF-8** (F12): the command reconfigures `sys.stdout` and `sys.stderr` to UTF-8, because the
  report is Markdown (GitHub reads UTF-8) and has non-ASCII characters (`µ`, the sparkline). A shell
  redirect then works under any locale.
- "No result" is a message on the standard error naming the kind, the statistic, the window and the
  directory (F8, F9), with exit status `0` (D9). The standard output stays empty.

The `import` kind contract is documented in `docs/docs/cli.md` with the snippet that a producer
needs (F16): a test that records `benchmark.extra_info["import_seconds_median"] = seconds`.

## 4. Public API after the change

```python
# feu.benchmark   (17 names today, 10 after)
KINDS: tuple[str, ...]  # ("benchmark", "import")
STATS: tuple[str, ...]  # ("min", "mean", "median", "max")
UNITS: dict[str, float]  # seconds -> unit
Run, Regression, TrendReport  # frozen dataclasses
load_runs(storage, *, days=90, kind="benchmark", stat="median", label="name") -> list[Run]
prune_runs(storage, *, days=90) -> list[Path]
find_regressions(runs, *, baseline_runs=7, threshold=50.0) -> list[Regression]
make_report(runs, *, kind, stat, unit, days, baseline_runs, threshold) -> TrendReport
```

| Today                                                      | After                                                                      |
| ---------------------------------------------------------- | -------------------------------------------------------------------------- |
| `TrendKind`, `BENCHMARK_KIND`, `IMPORT_KIND`, `with_unit`  | removed; the kind is a string of `KINDS` (D1)                              |
| `UNITS` with `us` and `µs`                                 | `UNITS` has `us` only; `µs` is how it is shown                             |
| `get_benchmark_label`, `get_import_label`                  | private; the rule is in `load_runs` (3.3, rule 6)                          |
| `UnknownStatError`                                         | removed; `ValueError` from the check of `STATS`                            |
| `load_runs(storage, days, *, kind, stat, prune)`           | `load_runs(storage, *, days, kind, stat, label)`; `prune_runs` is separate |
| `Run`, `Regression` as tuples                              | frozen dataclasses                                                         |
| `find_regressions(runs, *, window, threshold)`             | `find_regressions(runs, *, baseline_runs, threshold)`                      |
| `make_table`, `make_regression_report`, `make_annotations` | private; `make_report` returns all of them in a `TrendReport`              |
| `build_trend_report(...) -> tuple[str, list[str]] \| None` | `make_report(...) -> TrendReport`; the command loads then reports          |
| `sparkline`                                                | private                                                                    |
| `--scale`, `--window`                                      | removed; `--baseline-runs` replaces `--window`                             |

Behaviour changes, all deliberate: the labels of parametrized benchmarks (`sort_benchmark[10]` becomes
`sort[10]`); a malformed result file fails instead of crashing with a `KeyError`; foreign JSON files
are ignored; duplicate labels fail; a report has one section per machine; times show three
significant digits; a statistic outside `STATS` is a usage error.

## 5. Dependents

- Inside the repository: `src/feu/cli.py` (the command), `tests/unit/test_cli.py`,
  `tests/unit/test_layers.py` (`benchmark: 1`), `docs/docs/cli.md`, `docs/docs/dev/architecture.md`,
  `docs/docs/refs/benchmark.md` and `docs/mkdocs.yml` **[verified]**. No workflow uses the command.
- Outside: none found by `gh search code` **[downstream]** (F17). A scheduled workflow that calls
  `feu benchmark-trend` with `--window` or `--scale` fails with a usage error after the change: the
  message of `click` names the option. The step 6 of section 7 lists it in the release notes.

## 6. Evidence

| Claim                                        | Probe                                                                                                                                        |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| F1, F2: foreign JSON, deleted before failing | `load_runs` on a directory with a valid file, `other.json` (`{"x": 1}`) and, with `prune=True`, an old file: `KeyError`, old file deleted    |
| F3: label of a parametrized test             | `uv run --with pytest-benchmark pytest --benchmark-save=run` on a `test_sort_benchmark` with `parametrize`, then `feu benchmark-trend`       |
| F4: duplicates                               | two entries named `test_sort_benchmark` with different `fullname`: `{'sort': 0.009}`                                                         |
| F5: machines                                 | two directories `Linux-A` and `Darwin-B` with the same benchmark: `[{'a': 0.001}, {'a': 0.005}]`                                             |
| F6, F7: zero baseline, precision             | `find_regressions` on `0.0` then `1.0`; `make_table` with `with_unit(..., "s")` on `1.2e-6`                                                  |
| F8: arguments                                | `find_regressions(runs, window=0)`; `feu benchmark-trend DIR --days 0` (exit `0`)                                                            |
| F9, F10: statistic, empty runs               | `load_runs(..., kind=IMPORT_KIND, stat="nope")` returns one run with `{}`; three files with one empty give `(3 runs)`                        |
| F11, F13: escaping, ties                     | `make_table` with the label `a\|b`; `make_annotations` with `a\nb%c`; two equal times listed `b`, `a`                                        |
| F12: encoding                                | `LC_ALL=C PYTHONUTF8=0 .venv/bin/python -c "load_runs(...)"`; `PYTHONIOENCODING=cp1252 feu benchmark-trend DIR > out.md`                     |
| F16: coverage, `pytest-benchmark` missing    | `.venv/bin/pytest tests/unit/benchmark -q --cov=feu.benchmark`: 154 passed with `tests/unit/test_layers.py`, 100%; `import pytest_benchmark` |

The real `pytest-benchmark` file used for F3 and F5 has the keys `machine_info`, `commit_info`,
`benchmarks`, `datetime` (`2026-11-26T21:14:31.219329+00:00`) and `version` (`5.3.1`); each benchmark
has `name`, `fullname`, `group`, `param`, `params` and `stats` with `min`, `max`, `mean`, `median`,
`q1`, `q3`, `iqr`, `stddev`, `ops`, `total`, `rounds` and others. The step 1 of section 7 commits a
small copy as a test fixture.

## 7. Changes to reach the target state

One branch and one pull request per step (`CLAUDE.md`), stacked, because every step edits the same
module. The order puts the safety net first and the correctness fixes next, and every step is
releasable. All the steps ship in the same release.

| Step | Change                                                                                                                                                                                                                                                                                                      | Findings                             |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1    | **Real-format tests.** Commit a result written by `pytest-benchmark` 5.3.1 (two runs, one machine directory, one parametrized test) as a fixture of `tests/unit/benchmark/`, and an integration test that runs the real `pytest-benchmark` (skipped when it is not installed). **No `src` change.**         | F16                                  |
| 2    | **Loader.** Split `runs.py` out of `trend.py`; file pattern, UTF-8, `ValueError` naming the path, times `> 0`, empty runs dropped, `Run` dataclass with `machine`, the label rule and `label=`, duplicates raise, `days >= 1`, `STATS` check, `UnknownStatError` removed.                                   | F1, F3, F4, F5, F6, F8, F9, F10, F12 |
| 3    | **Analysis.** `trend.py` with `Regression`, per-machine comparison, `baseline_runs`, validation, deterministic order.                                                                                                                                                                                       | F5, F8, F13, F14                     |
| 4    | **Rendering.** `report.py`: `make_report` and `TrendReport`, `format_time`, escaping, machine sections, `1 run`, the statistic in the title, closed `UNITS`; remove `TrendKind`, `with_unit`, the public `make_*`.                                                                                          | F7, F10, F11, F13, F14               |
| 5    | **Storage and command.** `prune_runs` out of the loader, the command rewritten as in 3.6 (`Choice`, `IntRange`, UTF-8, `--baseline-runs`, `--fail-on-regression`, no `--scale`, no `--window`).                                                                                                             | F2, F12, F15                         |
| 6    | **Documentation.** `docs/docs/cli.md` (options, exit status, the `import` contract with its snippet), `docs/docs/design.md` (a "Benchmark properties" table from section 1), `docs/docs/dev/architecture.md` (the three modules), `docs/docs/refs/benchmark.md`, the release notes of the breaking changes. | F16                                  |

Step 1 needs nothing. Steps 2 to 5 each need the previous one. Step 6 is last so the documents
describe what exists; each earlier step updates the docstrings of what it changes.

## 8. Tests and gates

Every function, private ones included, has a docstring and its own tests (`CLAUDE.md`). New tests
per step, one behaviour per test:

- **Step 1.** `test_load_runs_reads_a_real_result` asserts the whole `Run` list against a literal;
  the integration test starts with "Test that ..." and runs `pytest --benchmark-save` in a temporary
  directory, then `load_runs`. A marker `pytest_benchmark_available` is added to `feu.testing`.
- **Step 2.** One test per rule of 3.3: a foreign JSON is ignored; an invalid JSON, a missing
  `datetime`, a missing `stats`, a time of `0`, `-1.0`, `nan` and `inf` each raise `ValueError` with
  the path (`parametrize`); the label of `test_sort_benchmark`, `test_sort_benchmark[10]`, `sort`,
  `test_benchmark`, `test_a_b_benchmark[x_benchmark]`; a duplicate raises and `label="fullname"`
  does not; two machines give two `machine` values; a file older than the window is not read (its
  content is invalid and does not raise); UTF-8 is read under a patched locale; `days=0`.
  Regression tests for F1, F3, F4, F6, F9, F10 must **fail without the fix**
  (`git stash push src`).
- **Step 3.** `window` of one run, of two runs, longer than the history; machines are compared
  separately; ties are ordered by label; `baseline_runs=0` and `threshold=0` raise; the input
  runs are not mutated; the result is the same on a second call.
- **Step 4.** `format_time` on `0.1234`, `12.34`, `123.4`, `1234567.8`, `1e-9` (`parametrize`); a
  `|` is escaped in a cell; `%`, `\r`, `\n` are escaped in an annotation; `1 run` and `2 runs`; one
  machine and two machines; the whole `TrendReport` of a small input against a literal.
- **Step 5.** `prune_runs` deletes only the old files and returns them; a failing load deletes
  nothing (the command test); `--fail-on-regression` exits `1` with a regression and `0` without;
  `--days 0`, `--stat nope`, `--unit min`, `--scale 1` are usage errors (exit `2`); the output is
  UTF-8 under a patched `cp1252` standard output; `No ... results` is on the standard error and the
  standard output is empty.
- **Patched tests need an integration test** (`CLAUDE.md`): the UTF-8 and exit-status tests that
  patch the streams are matched by a test that runs `python -m feu benchmark-trend` in a
  subprocess with `PYTHONIOENCODING=cp1252` on the fixture.

Gates for every step: `.venv/bin/ruff check src tests`, `.venv/bin/ruff format src tests`,
`.venv/bin/ty check`, `.venv/bin/pytest tests/unit/benchmark tests/unit/test_cli.py
tests/unit/test_layers.py -q --cov=feu.benchmark --cov-report=term-missing` with 100% coverage, the
doctests of the touched modules, and `tests/integration/test_import_weight.py` (B1: the import
stays standard-library only).

## 9. Decisions for the maintainers

Each decision has a recommendation, which section 3 applies. They are not yet recorded.

**D1. Are the kinds extensible?** _Recommended: no, a closed set (`KINDS`)._ Today `TrendKind` is a
public dataclass with two callables, but no consumer builds one **[downstream]**, and the `import`
kind is a repository convention (`extra_info`) more than a format. A third kind is one entry of one
private table in `runs.py`. The alternative is a `Registry[Kind]` of `feu.utils` (design property 6),
which costs a type and two functions for a use case that does not exist yet; it can be added later
without breaking `load_runs(kind="benchmark")`.

**D2. Keep arbitrary units (`--unit min --scale 0.0166667`)?** _Recommended: no, `s`, `ms`, `us`,
`ns` only._ The option was added by #1098; the cost is a second option with a cross-rule ("scale
requires unit"), a `replace` of a dataclass, and a number format (B6) that cannot assume a known
magnitude. Times of benchmarks are shown in the four units of the SI prefix. Alternative: keep
`--scale` as the escape hatch.

**D3. Malformed result file: fail or skip?** _Recommended: fail with the path._ Only files named
`NNNN_*.json` are read, so a failing file is a real result that is broken; skipping it (even with a
warning) gives a trend computed on a different history without notice (design property 4). The
price is that a scheduled job fails until the file is removed, which is the signal wanted. Alternative:
`--skip-invalid`, a flag that logs the path and continues.

**D4. Group by machine or ignore the machine?** _Recommended: group._ F5 shows a 400% false
regression from two directories of the same storage. The directory is already what `pytest-benchmark`
uses to separate machines, so the rule costs one field. Alternative: keep one history and document
that a storage must hold one machine.

**D5. Duplicate labels: raise or disambiguate?** _Recommended: raise, with `label="fullname"` as the
documented way out._ Disambiguating only the colliding entries makes a label change when a second
test with the same name is added, which breaks the history. Raising is loud and has a one-word fix.

**D6. Add `--fail-on-regression`?** _Recommended: yes, off by default._ It is one `if`, it uses the
exit status as design property 11 says, and without it a regression cannot fail a job. The default
exit status stays `0`, so no workflow changes.

**D7. Force UTF-8 on the standard output, or fall back to ASCII?** _Recommended: force UTF-8._ The
report is Markdown that GitHub reads as UTF-8, `µ` and the sparkline are part of it, and an ASCII
fallback would make two reports for the same input (B7). Alternative: `--ascii`, which replaces
`▁..█` by `_.-=#` and `µs` by `us`.

**D8. One module or three?** _Recommended: three (`runs`, `trend`, `report`)._ B10 becomes visible
in the file list and each module is tested alone. Alternative: keep `trend.py` at about 440 lines;
nothing is wrong with it besides that the pure and I/O code share a file.

**D9. Exit status of "no result".** _Recommended: `0` with a message on the standard error._ The first
run of a new workflow has no history, and a failing first run is noise. A job that must fail when the
benchmarks stop being produced can test the standard output (it is empty). Alternative: exit `1`.

**D10. Rename `--window` to `--baseline-runs`?** _Recommended: yes._ The two "windows" (`--days` and
`--window`) are the most common confusion of the command. The break is one option name, and `click`
names the unknown option in the error.

## 10. Not covered

- **The regression algorithm.** The median of the previous runs and the percent threshold are kept.
  A statistical test (for example a comparison of the `stddev` or of the raw `data`) needs
  `--benchmark-save-data` and is a feature, not a cleanup.
- **Other formats.** `asv`, `pyperf` or `pytest-benchmark --benchmark-json` files that are not in a
  storage directory are not read; `storage` is a directory.
- **Charts.** The sparkline stays the only graphic; an image or an HTML report is out of scope.
- **Running the benchmarks.** `feu.benchmark` only reads results. The `import_seconds` producer
  belongs to the repositories that measure their imports; step 6 documents the contract.
- **A downstream search that is complete.** F17 is a search of the repositories `gh` can index.
  Before the release, check the scheduled workflows of the repositories of the owner for
  `--window` and `--scale`.

## Appendix: reproducing the probes

All commands run from the repository root with `.venv/bin/python` (3.14), on `main` `2e57596`. The
probe script and its fixtures live in a scratchpad outside the repository; nothing writes in it.

```python
import json, tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

from feu.benchmark import load_runs


def write(directory, benchmarks, *, name="r", days_ago=1):
    date = datetime.now(tz=UTC) - timedelta(days=days_ago)
    path = Path(directory) / f"{name}.json"
    path.write_text(json.dumps({"datetime": date.isoformat(), "benchmarks": benchmarks}))


with tempfile.TemporaryDirectory() as d:  # F1: a JSON file that is not a result
    write(d, [{"name": "test_a", "stats": {"median": 1e-3}}])
    (Path(d) / "other.json").write_text('{"x": 1}')
    load_runs(Path(d), 90)  # KeyError: 'datetime'
```

The label (F3) and machine (F5) probes need a real result:

```shell
cd "$SCRATCH" && uv run --no-project --with pytest --with pytest-benchmark \
  pytest -p no:cacheprovider -q --benchmark-save=run --benchmark-storage="$SCRATCH/store" test_x_benchmark.py
.venv/bin/feu benchmark-trend "$SCRATCH/store"   # rows: sort, sort_benchmark[10], sort_benchmark[20]
```

with `test_x_benchmark.py` holding `@pytest.mark.parametrize("n", [10, 20]) def
test_sort_benchmark(benchmark, n)` and a `TestA.test_sort_benchmark`. The encoding probes (F12) are
`LC_ALL=C PYTHONUTF8=0 .venv/bin/python -c "..."` and `PYTHONIOENCODING=cp1252 .venv/bin/feu
benchmark-trend "$SCRATCH/st" > out.md` on a result whose label has `µ`.

The label rule (3.3, rule 6) and the number format (3.5) were checked by a prototype of five lines
each before they were written here: the pattern in 3.3 on seven names and `format_time` on eight
values from `0.0` to `1234567.8`.
