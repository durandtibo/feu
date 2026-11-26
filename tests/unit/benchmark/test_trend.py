from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from feu.benchmark import (
    BENCHMARK_KIND,
    IMPORT_KIND,
    KINDS,
    TrendKind,
    build_trend_report,
    find_regressions,
    get_benchmark_label,
    get_import_label,
    load_runs,
    make_annotations,
    make_regression_report,
    make_table,
    sparkline,
)

if TYPE_CHECKING:
    from pathlib import Path

DATE = datetime(2026, 1, 1, tzinfo=UTC)
BENCH_A = {"name": "test_a_benchmark", "stats": {"median": 0.001}}
BENCH_B = {"name": "test_b_benchmark", "stats": {"median": 0.002}}
IMPORT_A = {"name": "test_import", "param": "a", "extra_info": {"import_seconds_median": 0.001}}


def make_runs(*values: dict) -> list[tuple[datetime, dict]]:
    return [(DATE, times) for times in values]


def write_run(path: Path, date: datetime, benchmarks: list[dict]) -> None:
    path.write_text(json.dumps({"datetime": date.isoformat(), "benchmarks": benchmarks}))


def build_report(
    path: Path, *, kind: TrendKind = BENCHMARK_KIND, days: int = 90, threshold: float = 50.0
) -> tuple[str, list[str]]:
    result = build_trend_report(path, kind=kind, days=days, threshold=threshold)
    assert result is not None
    return result


def write_regression(path: Path, benchmark: dict = BENCH_A, slow: dict | None = None) -> None:
    now = datetime.now(tz=UTC)
    slow = slow or {**BENCH_A, "stats": {"median": 0.002}}
    write_run(path / "1.json", now - timedelta(days=2), [benchmark])
    write_run(path / "2.json", now - timedelta(days=1), [slow])


###################################
#     Tests for get_*_label       #
###################################


def test_get_benchmark_label_strips_prefix_and_suffix() -> None:
    assert get_benchmark_label({"name": "test_foo_benchmark"}) == "foo"


def test_get_benchmark_label_without_prefix_and_suffix() -> None:
    assert get_benchmark_label({"name": "foo"}) == "foo"


def test_get_benchmark_label_strips_only_one_prefix_and_suffix() -> None:
    assert get_benchmark_label({"name": "test_test_benchmark_benchmark"}) == "test_benchmark"


def test_get_import_label_uses_param() -> None:
    assert get_import_label({"name": "test_import[x]", "param": "x"}) == "x"


def test_get_import_label_without_param_uses_name() -> None:
    assert get_import_label({"name": "test_foo_benchmark"}) == "foo"


def test_get_import_label_empty_param_uses_name() -> None:
    assert get_import_label({"name": "test_foo", "param": ""}) == "foo"


###############################
#     Tests for TrendKind     #
###############################


def test_kinds() -> None:
    assert KINDS == {"benchmark": BENCHMARK_KIND, "import": IMPORT_KIND}


def test_benchmark_kind_unit() -> None:
    assert (BENCHMARK_KIND.unit, BENCHMARK_KIND.scale) == ("µs", 1e6)


def test_import_kind_unit() -> None:
    assert (IMPORT_KIND.unit, IMPORT_KIND.scale) == ("ms", 1e3)


###############################
#     Tests for load_runs     #
###############################


def test_load_runs_empty_storage(tmp_path: Path) -> None:
    assert load_runs(tmp_path, days=90) == []


def test_load_runs_sorted_by_date(tmp_path: Path) -> None:
    now = datetime.now(tz=UTC)
    write_run(tmp_path / "a.json", now - timedelta(days=1), [BENCH_B])
    write_run(tmp_path / "b.json", now - timedelta(days=2), [BENCH_A])
    assert load_runs(tmp_path, days=90) == [
        (now - timedelta(days=2), {"a": 0.001}),
        (now - timedelta(days=1), {"b": 0.002}),
    ]


def test_load_runs_skips_old_runs(tmp_path: Path) -> None:
    now = datetime.now(tz=UTC)
    write_run(tmp_path / "old.json", now - timedelta(days=10), [BENCH_A])
    write_run(tmp_path / "new.json", now - timedelta(days=1), [BENCH_B])
    assert load_runs(tmp_path, days=5) == [(now - timedelta(days=1), {"b": 0.002})]


def test_load_runs_keeps_old_files_without_prune(tmp_path: Path) -> None:
    write_run(tmp_path / "old.json", datetime.now(tz=UTC) - timedelta(days=10), [BENCH_A])
    load_runs(tmp_path, days=5)
    assert (tmp_path / "old.json").exists()


def test_load_runs_prune_deletes_old_files(tmp_path: Path) -> None:
    write_run(tmp_path / "old.json", datetime.now(tz=UTC) - timedelta(days=10), [BENCH_A])
    load_runs(tmp_path, days=5, prune=True)
    assert not (tmp_path / "old.json").exists()


def test_load_runs_prune_keeps_recent_files(tmp_path: Path) -> None:
    write_run(tmp_path / "new.json", datetime.now(tz=UTC) - timedelta(days=1), [BENCH_A])
    load_runs(tmp_path, days=5, prune=True)
    assert (tmp_path / "new.json").exists()


def test_load_runs_searches_subdirectories(tmp_path: Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    date = datetime.now(tz=UTC) - timedelta(days=1)
    write_run(sub / "a.json", date, [BENCH_A])
    assert load_runs(tmp_path, days=5) == [(date, {"a": 0.001})]


def test_load_runs_ignores_non_json_files(tmp_path: Path) -> None:
    tmp_path.joinpath("notes.txt").write_text("not json")
    assert load_runs(tmp_path, days=5) == []


def test_load_runs_naive_datetime_is_utc(tmp_path: Path) -> None:
    date = datetime.now(tz=UTC).replace(tzinfo=None) - timedelta(days=1)
    write_run(tmp_path / "a.json", date, [BENCH_A])
    assert load_runs(tmp_path, days=5) == [(date.replace(tzinfo=UTC), {"a": 0.001})]


def test_load_runs_import_kind(tmp_path: Path) -> None:
    date = datetime.now(tz=UTC) - timedelta(days=1)
    write_run(tmp_path / "a.json", date, [IMPORT_A])
    assert load_runs(tmp_path, days=5, kind=IMPORT_KIND) == [(date, {"a": 0.001})]


def test_load_runs_import_kind_skips_benchmarks_without_import_time(tmp_path: Path) -> None:
    date = datetime.now(tz=UTC) - timedelta(days=1)
    write_run(tmp_path / "a.json", date, [IMPORT_A, {"name": "test_other"}])
    assert load_runs(tmp_path, days=5, kind=IMPORT_KIND) == [(date, {"a": 0.001})]


###############################
#     Tests for sparkline     #
###############################


def test_sparkline_increasing() -> None:
    assert sparkline([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]) == "▁▂▃▄▅▆▇█"


def test_sparkline_constant() -> None:
    assert sparkline([2.0, 2.0, 2.0]) == "▁▁▁"


def test_sparkline_single_value() -> None:
    assert sparkline([5.0]) == "▁"


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


def test_make_table_zero_first_value_has_zero_change() -> None:
    runs = make_runs({"a": 0.0}, {"a": 1.0})
    assert make_table(runs).splitlines()[-1] == (
        "| a | 1000000.0 | 0.0 | +0.0% | 500000.0 | 0.0 | 1000000.0 | 2 | `▁█` |"
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


def test_find_regressions_slower_than_threshold() -> None:
    runs = make_runs({"a": 1.0}, {"a": 1.0}, {"a": 1.0}, {"a": 2.0})
    assert find_regressions(runs) == [("a", 2.0, 1.0, 100.0)]


def test_find_regressions_at_threshold_is_not_a_regression() -> None:
    assert find_regressions(make_runs({"a": 1.0}, {"a": 1.5})) == []


def test_find_regressions_faster_is_not_a_regression() -> None:
    assert find_regressions(make_runs({"a": 2.0}, {"a": 1.0})) == []


def test_find_regressions_custom_threshold() -> None:
    runs = make_runs({"a": 1.0}, {"a": 1.5})
    assert find_regressions(runs, threshold=10.0) == [("a", 1.5, 1.0, 50.0)]


def test_find_regressions_uses_median_of_previous_runs() -> None:
    # The median of [1, 1, 10] is 1, so one slow run in the history does not hide a regression.
    runs = make_runs({"a": 1.0}, {"a": 1.0}, {"a": 10.0}, {"a": 2.0})
    assert find_regressions(runs) == [("a", 2.0, 1.0, 100.0)]


def test_find_regressions_uses_only_window_runs() -> None:
    runs = make_runs({"a": 100.0}, {"a": 1.0}, {"a": 1.0}, {"a": 2.0})
    assert find_regressions(runs, window=2) == [("a", 2.0, 1.0, 100.0)]


def test_find_regressions_one_run() -> None:
    assert find_regressions(make_runs({"a": 1.0})) == []


def test_find_regressions_no_run() -> None:
    assert find_regressions([]) == []


def test_find_regressions_new_benchmark_is_ignored() -> None:
    assert find_regressions(make_runs({"a": 1.0}, {"a": 1.0, "b": 5.0})) == []


def test_find_regressions_benchmark_missing_in_latest_run_is_ignored() -> None:
    assert find_regressions(make_runs({"a": 1.0, "b": 1.0}, {"a": 1.0})) == []


def test_find_regressions_zero_baseline() -> None:
    assert find_regressions(make_runs({"a": 0.0}, {"a": 1.0})) == []


def test_find_regressions_sorted_by_decreasing_change() -> None:
    runs = make_runs({"a": 1.0, "b": 1.0}, {"a": 2.0, "b": 3.0})
    assert find_regressions(runs) == [("b", 3.0, 1.0, 200.0), ("a", 2.0, 1.0, 100.0)]


def test_find_regressions_does_not_modify_runs() -> None:
    runs = make_runs({"a": 1.0}, {"a": 2.0})
    find_regressions(runs)
    assert runs == make_runs({"a": 1.0}, {"a": 2.0})


############################################
#     Tests for make_regression_report     #
############################################


def test_make_regression_report_empty() -> None:
    assert make_regression_report([]) == ""


def test_make_regression_report() -> None:
    assert make_regression_report([("a", 2e-06, 1e-06, 100.0)]) == (
        "### Regressions\n"
        "\n"
        "| Benchmark | Latest (µs) | Previous median (µs) | Change |\n"
        "|---|---:|---:|---:|\n"
        "| a | 2.0 | 1.0 | +100.0% |"
    )


def test_make_regression_report_import_kind() -> None:
    assert make_regression_report([("a", 0.002, 0.001, 100.0)], kind=IMPORT_KIND) == (
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
    assert make_annotations([("a", 2e-06, 1e-06, 100.0)]) == [
        (
            "::warning title=Regression::a is 100.0% slower than the median of the previous runs "
            "(2.0 µs instead of 1.0 µs)"
        )
    ]


def test_make_annotations_import_kind() -> None:
    assert make_annotations([("a", 0.002, 0.001, 100.0)], kind=IMPORT_KIND) == [
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
    write_run(tmp_path / "a.json", date, [BENCH_A])
    assert build_trend_report(tmp_path, days=5) == (
        f"## Benchmarks over the last 5 days (1 runs)\n\n{make_table([(date, {'a': 0.001})])}\n",
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


def test_build_trend_report_threshold_hides_regression(tmp_path: Path) -> None:
    write_regression(tmp_path)
    _, annotations = build_report(tmp_path, threshold=150.0)
    assert annotations == []


def test_build_trend_report_import_kind_heading(tmp_path: Path) -> None:
    write_run(tmp_path / "a.json", datetime.now(tz=UTC) - timedelta(days=1), [IMPORT_A])
    report, _ = build_report(tmp_path, kind=IMPORT_KIND, days=5)
    assert report.startswith("## Import time over the last 5 days (1 runs)\n")


def test_build_trend_report_prune_deletes_old_files(tmp_path: Path) -> None:
    write_run(tmp_path / "old.json", datetime.now(tz=UTC) - timedelta(days=10), [BENCH_A])
    build_trend_report(tmp_path, days=5, prune=True)
    assert not (tmp_path / "old.json").exists()
