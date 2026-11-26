from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from feu.benchmark import (
    BENCHMARK_KIND,
    IMPORT_KIND,
    Regression,
    Run,
    TrendKind,
    build_trend_report,
    find_regressions,
    make_annotations,
    make_regression_report,
    make_table,
    sparkline,
    with_unit,
)
from feu.benchmark.trend import _make_trend_report

if TYPE_CHECKING:
    from pathlib import Path

DATE = datetime(2026, 1, 1, tzinfo=UTC)
BENCH_A = {"name": "test_a_benchmark", "stats": {"median": 0.001}}
BENCH_B = {"name": "test_b_benchmark", "stats": {"median": 0.002}}
IMPORT_A = {"name": "test_import", "param": "a", "extra_info": {"import_seconds_median": 0.001}}


def make_runs(*values: dict) -> list[Run]:
    return [Run(DATE, "", times) for times in values]


def write_run(path: Path, date: datetime, benchmarks: list[dict]) -> None:
    path.write_text(json.dumps({"datetime": date.isoformat(), "benchmarks": benchmarks}))


def build_report(
    path: Path,
    *,
    kind: TrendKind = BENCHMARK_KIND,
    days: int = 90,
    baseline_runs: int = 7,
    threshold: float = 50.0,
) -> tuple[str, list[str]]:
    result = build_trend_report(
        path, kind=kind, days=days, baseline_runs=baseline_runs, threshold=threshold
    )
    assert result is not None
    return result


def write_regression(path: Path, benchmark: dict = BENCH_A, slow: dict | None = None) -> None:
    now = datetime.now(tz=UTC)
    slow = slow or {**BENCH_A, "stats": {"median": 0.002}}
    write_run(path / "0001_1.json", now - timedelta(days=2), [benchmark])
    write_run(path / "0001_2.json", now - timedelta(days=1), [slow])


###############################
#     Tests for TrendKind     #
###############################


def test_benchmark_kind_unit() -> None:
    assert (BENCHMARK_KIND.unit, BENCHMARK_KIND.scale) == ("µs", 1e6)


def test_import_kind_unit() -> None:
    assert (IMPORT_KIND.unit, IMPORT_KIND.scale) == ("ms", 1e3)


###############################
#     Tests for sparkline     #
###############################


def test_sparkline_increasing() -> None:
    assert sparkline([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]) == "▁▂▃▄▅▆▇█"


def test_sparkline_constant() -> None:
    assert sparkline([2.0, 2.0, 2.0]) == "▁▁▁"


def test_sparkline_single_value() -> None:
    assert sparkline([5.0]) == "▁"


def test_sparkline_negative_values() -> None:
    assert sparkline([-2.0, 0.0, 2.0]) == "▁▅█"


def test_sparkline_does_not_modify_values() -> None:
    values = [3.0, 1.0, 2.0]
    sparkline(values)
    assert values == [3.0, 1.0, 2.0]


def test_sparkline_empty() -> None:
    with pytest.raises(ValueError, match=r"empty"):
        sparkline([])


def test_sparkline_min_and_max() -> None:
    assert sparkline([3.0, 1.0, 2.0]) == "█▁▅"


################################
#     Tests for make_table     #
################################

HEADER = (
    "| Benchmark | Latest (µs) | First (µs) | Change | Median (µs) | Min (µs) | Max (µs) "
    "| Runs | Trend |\n"
    "|---|---:|---:|---:|---:|---:|---:|---:|---|"
)


def test_make_table_empty() -> None:
    assert make_table([]) == HEADER


def test_make_table_one_benchmark() -> None:
    runs = make_runs({"a": 1.0}, {"a": 2.0}, {"a": 3.0})
    assert make_table(runs) == (
        f"{HEADER}\n"
        "| a | 3000000.0 | 1000000.0 | +200.0% | 2000000.0 | 1000000.0 | 3000000.0 | 3 | `▁▅█` |"
    )


def test_make_table_several_benchmarks() -> None:
    runs = make_runs({"a": 1.0, "b": 4.0}, {"a": 2.0, "b": 3.0})
    assert make_table(runs) == (
        f"{HEADER}\n"
        "| a | 2000000.0 | 1000000.0 | +100.0% | 1500000.0 | 1000000.0 | 2000000.0 | 2 | `▁█` |\n"
        "| b | 3000000.0 | 4000000.0 | -25.0% | 3500000.0 | 3000000.0 | 4000000.0 | 2 | `█▁` |"
    )


def test_make_table_sorted_by_latest_time() -> None:
    runs = make_runs({"a": 2.0, "b": 1.0})
    assert make_table(runs).splitlines()[2:] == [
        "| b | 1000000.0 | 1000000.0 | +0.0% | 1000000.0 | 1000000.0 | 1000000.0 | 1 | `▁` |",
        "| a | 2000000.0 | 2000000.0 | +0.0% | 2000000.0 | 2000000.0 | 2000000.0 | 1 | `▁` |",
    ]


def test_make_table_benchmark_missing_in_some_runs() -> None:
    runs = make_runs({"a": 1.0}, {"a": 1.0, "b": 2.0})
    assert make_table(runs).splitlines()[-1] == (
        "| b | 2000000.0 | 2000000.0 | +0.0% | 2000000.0 | 2000000.0 | 2000000.0 | 1 | `▁` |"
    )


def test_make_table_unit() -> None:
    assert make_table(make_runs({"a": 1.0}), kind=with_unit(BENCHMARK_KIND, "s")) == (
        "| Benchmark | Latest (s) | First (s) | Change | Median (s) | Min (s) | Max (s) "
        "| Runs | Trend |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---|\n"
        "| a | 1.0 | 1.0 | +0.0% | 1.0 | 1.0 | 1.0 | 1 | `▁` |"
    )


def test_make_table_import_kind() -> None:
    assert make_table(make_runs({"a": 1.0}), kind=IMPORT_KIND) == (
        "| Import | Latest (ms) | First (ms) | Change | Median (ms) | Min (ms) | Max (ms) "
        "| Runs | Trend |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---|\n"
        "| a | 1000.0 | 1000.0 | +0.0% | 1000.0 | 1000.0 | 1000.0 | 1 | `▁` |"
    )


######################################
#     Tests for find_regressions     #
######################################


def reg(label: str, latest: float, baseline: float, change: float, machine: str = "") -> Regression:
    return Regression(machine, label, latest, baseline, change)


def make_machine_runs(machine: str, *values: dict) -> list[Run]:
    return [Run(DATE, machine, times) for times in values]


def test_find_regressions_slower_than_threshold() -> None:
    runs = make_runs({"a": 1.0}, {"a": 1.0}, {"a": 1.0}, {"a": 2.0})
    assert find_regressions(runs) == [reg("a", 2.0, 1.0, 100.0)]


def test_find_regressions_at_threshold_is_not_a_regression() -> None:
    assert find_regressions(make_runs({"a": 1.0}, {"a": 1.5})) == []


def test_find_regressions_faster_is_not_a_regression() -> None:
    assert find_regressions(make_runs({"a": 2.0}, {"a": 1.0})) == []


def test_find_regressions_custom_threshold() -> None:
    runs = make_runs({"a": 1.0}, {"a": 1.5})
    assert find_regressions(runs, threshold=10.0) == [reg("a", 1.5, 1.0, 50.0)]


def test_find_regressions_uses_median_of_previous_runs() -> None:
    # The median of [1, 1, 10] is 1, so one slow run in the history does not hide a regression.
    runs = make_runs({"a": 1.0}, {"a": 1.0}, {"a": 10.0}, {"a": 2.0})
    assert find_regressions(runs) == [reg("a", 2.0, 1.0, 100.0)]


def test_find_regressions_uses_only_baseline_runs() -> None:
    runs = make_runs({"a": 100.0}, {"a": 1.0}, {"a": 1.0}, {"a": 2.0})
    assert find_regressions(runs, baseline_runs=2) == [reg("a", 2.0, 1.0, 100.0)]


def test_find_regressions_one_baseline_run_is_the_last_previous_run() -> None:
    runs = make_runs({"a": 1.0}, {"a": 1.0}, {"a": 4.0}, {"a": 5.0})
    assert find_regressions(runs, baseline_runs=1) == []


def test_find_regressions_two_baseline_runs() -> None:
    runs = make_runs({"a": 1.0}, {"a": 1.0}, {"a": 4.0}, {"a": 5.0})
    assert find_regressions(runs, baseline_runs=2) == [reg("a", 5.0, 2.5, 100.0)]


def test_find_regressions_baseline_runs_longer_than_the_history() -> None:
    runs = make_runs({"a": 1.0}, {"a": 2.0})
    assert find_regressions(runs, baseline_runs=100) == [reg("a", 2.0, 1.0, 100.0)]


def test_find_regressions_baseline_skips_runs_without_the_benchmark() -> None:
    runs = make_runs({"a": 1.0}, {"b": 9.0}, {"a": 3.0})
    assert find_regressions(runs, baseline_runs=1) == [reg("a", 3.0, 1.0, 200.0)]


def test_find_regressions_one_run() -> None:
    assert find_regressions(make_runs({"a": 1.0})) == []


def test_find_regressions_no_run() -> None:
    assert find_regressions([]) == []


def test_find_regressions_new_benchmark_is_ignored() -> None:
    assert find_regressions(make_runs({"a": 1.0}, {"a": 1.0, "b": 5.0})) == []


def test_find_regressions_benchmark_missing_in_latest_run_is_ignored() -> None:
    assert find_regressions(make_runs({"a": 1.0, "b": 1.0}, {"a": 1.0})) == []


def test_find_regressions_sorted_by_decreasing_change() -> None:
    runs = make_runs({"a": 1.0, "b": 1.0}, {"a": 2.0, "b": 3.0})
    assert find_regressions(runs) == [reg("b", 3.0, 1.0, 200.0), reg("a", 2.0, 1.0, 100.0)]


def test_find_regressions_ties_are_sorted_by_label() -> None:
    runs = make_runs({"b": 1.0, "a": 1.0}, {"b": 3.0, "a": 3.0})
    assert [item.label for item in find_regressions(runs)] == ["a", "b"]


def test_find_regressions_ties_are_sorted_by_machine() -> None:
    runs = make_machine_runs("y", {"a": 1.0}, {"a": 3.0}) + make_machine_runs(
        "x", {"a": 1.0}, {"a": 3.0}
    )
    assert [item.machine for item in find_regressions(runs)] == ["x", "y"]


def test_find_regressions_several_benchmarks_only_slow_ones() -> None:
    runs = make_runs({"a": 1.0, "b": 1.0}, {"a": 1.0, "b": 3.0})
    assert find_regressions(runs) == [reg("b", 3.0, 1.0, 200.0)]


def test_find_regressions_machines_are_compared_separately() -> None:
    # A run of another machine is neither the baseline nor the latest run.
    runs = make_machine_runs("linux", {"a": 0.001}, {"a": 0.001}) + make_machine_runs(
        "mac", {"a": 0.005}, {"a": 0.005}
    )
    assert find_regressions(runs) == []


def test_find_regressions_regression_of_one_machine() -> None:
    runs = make_machine_runs("linux", {"a": 1.0}, {"a": 3.0}) + make_machine_runs(
        "mac", {"a": 5.0}, {"a": 5.0}
    )
    assert find_regressions(runs) == [reg("a", 3.0, 1.0, 200.0, machine="linux")]


def test_find_regressions_machine_with_one_run_has_no_regression() -> None:
    runs = make_machine_runs("linux", {"a": 1.0}, {"a": 3.0}) + make_machine_runs("mac", {"a": 9.0})
    assert [item.machine for item in find_regressions(runs)] == ["linux"]


@pytest.mark.parametrize("baseline_runs", [0, -1])
def test_find_regressions_invalid_baseline_runs(baseline_runs: int) -> None:
    with pytest.raises(ValueError, match=r"baseline_runs must be greater than or equal to 1"):
        find_regressions(make_runs({"a": 1.0}), baseline_runs=baseline_runs)


@pytest.mark.parametrize("threshold", [0.0, -1.0])
def test_find_regressions_invalid_threshold(threshold: float) -> None:
    with pytest.raises(ValueError, match=r"threshold must be greater than 0"):
        find_regressions(make_runs({"a": 1.0}), threshold=threshold)


def test_find_regressions_does_not_modify_runs() -> None:
    runs = make_runs({"a": 1.0}, {"a": 2.0})
    find_regressions(runs)
    assert runs == make_runs({"a": 1.0}, {"a": 2.0})


def test_find_regressions_is_deterministic() -> None:
    runs = make_runs({"a": 1.0, "b": 1.0}, {"a": 2.0, "b": 3.0})
    assert find_regressions(runs) == find_regressions(runs)


############################################
#     Tests for make_regression_report     #
############################################


def test_make_regression_report_empty() -> None:
    assert make_regression_report([]) == ""


def test_make_regression_report() -> None:
    assert make_regression_report([reg("a", 2e-06, 1e-06, 100.0)]) == (
        "### Regressions\n"
        "\n"
        "| Benchmark | Latest (µs) | Previous median (µs) | Change |\n"
        "|---|---:|---:|---:|\n"
        "| a | 2.0 | 1.0 | +100.0% |"
    )


def test_make_regression_report_several_regressions() -> None:
    assert make_regression_report(
        [reg("b", 3e-06, 1e-06, 200.0), reg("a", 2e-06, 1e-06, 100.0)]
    ) == (
        "### Regressions\n"
        "\n"
        "| Benchmark | Latest (µs) | Previous median (µs) | Change |\n"
        "|---|---:|---:|---:|\n"
        "| b | 3.0 | 1.0 | +200.0% |\n"
        "| a | 2.0 | 1.0 | +100.0% |"
    )


def test_make_regression_report_import_kind() -> None:
    assert make_regression_report([reg("a", 0.002, 0.001, 100.0)], kind=IMPORT_KIND) == (
        "### Regressions\n"
        "\n"
        "| Import | Latest (ms) | Previous median (ms) | Change |\n"
        "|---|---:|---:|---:|\n"
        "| a | 2.0 | 1.0 | +100.0% |"
    )


######################################
#     Tests for make_annotations     #
######################################


def test_make_annotations_empty() -> None:
    assert make_annotations([]) == []


def test_make_annotations() -> None:
    assert make_annotations([reg("a", 2e-06, 1e-06, 100.0)]) == [
        (
            "::warning title=Regression::a is 100.0% slower than the median of the previous runs "
            "(2.0 µs instead of 1.0 µs)"
        )
    ]


def test_make_annotations_one_per_regression() -> None:
    regressions = [reg("b", 3e-06, 1e-06, 200.0), reg("a", 2e-06, 1e-06, 100.0)]
    assert len(make_annotations(regressions)) == 2


def test_make_annotations_import_kind() -> None:
    assert make_annotations([reg("a", 0.002, 0.001, 100.0)], kind=IMPORT_KIND) == [
        (
            "::warning title=Regression::a is 100.0% slower than the median of the previous runs "
            "(2.0 ms instead of 1.0 ms)"
        )
    ]


########################################
#     Tests for build_trend_report     #
########################################


def test_build_trend_report_no_results(tmp_path: Path) -> None:
    assert build_trend_report(tmp_path) is None


def test_build_trend_report_without_regression(tmp_path: Path) -> None:
    date = datetime.now(tz=UTC) - timedelta(days=1)
    write_run(tmp_path / "0001_a.json", date, [BENCH_A])
    assert build_trend_report(tmp_path, days=5) == (
        f"## Benchmarks over the last 5 days (1 runs)\n\n{make_table([Run(date, '', {'a': 0.001})])}\n",
        [],
    )


def test_build_trend_report_with_regression(tmp_path: Path) -> None:
    write_regression(tmp_path)
    report, _ = build_report(tmp_path)
    assert report.endswith(
        "\n### Regressions\n\n"
        "| Benchmark | Latest (µs) | Previous median (µs) | Change |\n"
        "|---|---:|---:|---:|\n"
        "| a | 2000.0 | 1000.0 | +100.0% |\n"
    )


def test_build_trend_report_with_regression_annotations(tmp_path: Path) -> None:
    write_regression(tmp_path)
    _, annotations = build_report(tmp_path)
    assert annotations == [
        (
            "::warning title=Regression::a is 100.0% slower than the median of the previous runs "
            "(2000.0 µs instead of 1000.0 µs)"
        )
    ]


def test_build_trend_report_with_regression_full_report(tmp_path: Path) -> None:
    write_regression(tmp_path)
    report, _ = build_report(tmp_path, days=5)
    assert report == (
        "## Benchmarks over the last 5 days (2 runs)\n"
        "\n"
        f"{HEADER}\n"
        "| a | 2000.0 | 1000.0 | +100.0% | 1500.0 | 1000.0 | 2000.0 | 2 | `▁█` |\n"
        "\n"
        "### Regressions\n"
        "\n"
        "| Benchmark | Latest (µs) | Previous median (µs) | Change |\n"
        "|---|---:|---:|---:|\n"
        "| a | 2000.0 | 1000.0 | +100.0% |\n"
    )


def test_build_trend_report_window_one_compares_with_last_previous_run(tmp_path: Path) -> None:
    now = datetime.now(tz=UTC)
    slow = {**BENCH_A, "stats": {"median": 0.002}}
    write_run(tmp_path / "0001_0.json", now - timedelta(days=4), [BENCH_A])
    write_run(tmp_path / "0001_1.json", now - timedelta(days=3), [BENCH_A])
    write_run(tmp_path / "0001_2.json", now - timedelta(days=2), [slow])
    write_run(tmp_path / "0001_3.json", now - timedelta(days=1), [slow])
    _, annotations = build_report(tmp_path, baseline_runs=1)
    assert annotations == []


def test_build_trend_report_stat_in_title(tmp_path: Path) -> None:
    bench = {"name": "test_a", "stats": {"median": 0.001, "mean": 0.003}}
    write_run(tmp_path / "0001_a.json", datetime.now(tz=UTC) - timedelta(days=1), [bench])
    result = build_trend_report(tmp_path, stat="mean", days=5)
    assert result is not None
    assert result[0].startswith("## Benchmarks (mean) over the last 5 days (1 runs)\n")


def test_build_trend_report_median_is_not_in_title(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_a.json", datetime.now(tz=UTC) - timedelta(days=1), [BENCH_A])
    result = build_trend_report(tmp_path, stat="median", days=5)
    assert result is not None
    assert result[0].startswith("## Benchmarks over the last 5 days (1 runs)\n")


def test_build_trend_report_threshold_hides_regression(tmp_path: Path) -> None:
    write_regression(tmp_path)
    _, annotations = build_report(tmp_path, threshold=150.0)
    assert annotations == []


def test_build_trend_report_import_kind_heading(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_a.json", datetime.now(tz=UTC) - timedelta(days=1), [IMPORT_A])
    report, _ = build_report(tmp_path, kind=IMPORT_KIND, days=5)
    assert report.startswith("## Import time over the last 5 days (1 runs)\n")


def test_build_trend_report_prune_deletes_old_files(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_old.json", datetime.now(tz=UTC) - timedelta(days=10), [BENCH_A])
    build_trend_report(tmp_path, days=5, prune=True)
    assert not (tmp_path / "0001_old.json").exists()


#####################################
#     Tests for _make_trend_report  #
#####################################


def test_make_trend_report_no_runs() -> None:
    assert (
        _make_trend_report(
            [], kind=BENCHMARK_KIND, stat="median", days=5, baseline_runs=7, threshold=50.0
        )
        is None
    )


def test_make_trend_report_with_a_run() -> None:
    runs = make_runs({"a": 0.001})
    report = _make_trend_report(
        runs, kind=BENCHMARK_KIND, stat="median", days=5, baseline_runs=7, threshold=50.0
    )
    assert report == (f"## Benchmarks over the last 5 days (1 runs)\n\n{make_table(runs)}\n", [])


def test_make_trend_report_shows_the_stat() -> None:
    runs = make_runs({"a": 0.001})
    report = _make_trend_report(
        runs, kind=BENCHMARK_KIND, stat="min", days=5, baseline_runs=7, threshold=50.0
    )
    assert report is not None
    assert report[0].startswith("## Benchmarks (min) over the last 5 days")


###########################################
#     Tests for build_trend_report load   #
###########################################


def test_build_trend_report_prunes_when_every_run_is_old(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_old.json", datetime.now(tz=UTC) - timedelta(days=10), [BENCH_A])
    assert build_trend_report(tmp_path, days=5, prune=True) is None
    assert not (tmp_path / "0001_old.json").exists()


def test_build_trend_report_failing_load_deletes_nothing(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_old.json", datetime.now(tz=UTC) - timedelta(days=10), [BENCH_A])
    tmp_path.joinpath("0002_bad.json").write_text("not json")
    with pytest.raises(ValueError, match=r"0002_bad.json: not a pytest-benchmark result"):
        build_trend_report(tmp_path, days=5, prune=True)
    assert (tmp_path / "0001_old.json").exists()


def test_build_trend_report_unknown_stat(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=r"Unknown stat 'nope'"):
        build_trend_report(tmp_path, stat="nope")
