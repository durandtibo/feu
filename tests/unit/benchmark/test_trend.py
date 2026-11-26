from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from feu.benchmark import (
    BENCHMARK_KIND,
    IMPORT_KIND,
    KINDS,
    UNITS,
    TrendKind,
    UnknownStatError,
    build_trend_report,
    find_regressions,
    get_benchmark_label,
    get_import_label,
    load_runs,
    make_annotations,
    make_regression_report,
    make_table,
    sparkline,
    with_unit,
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
    path: Path,
    *,
    kind: TrendKind = BENCHMARK_KIND,
    days: int = 90,
    window: int = 7,
    threshold: float = 50.0,
) -> tuple[str, list[str]]:
    result = build_trend_report(path, kind=kind, days=days, window=window, threshold=threshold)
    assert result is not None
    return result


def write_regression(path: Path, benchmark: dict = BENCH_A, slow: dict | None = None) -> None:
    now = datetime.now(tz=UTC)
    slow = slow or {**BENCH_A, "stats": {"median": 0.002}}
    write_run(path / "1.json", now - timedelta(days=2), [benchmark])
    write_run(path / "2.json", now - timedelta(days=1), [slow])


#########################################
#     Tests for the label functions     #
#########################################


@pytest.mark.parametrize(
    ("name", "label"),
    [
        ("test_foo_benchmark", "foo"),
        ("test_foo", "foo"),
        ("foo_benchmark", "foo"),
        ("foo", "foo"),
        ("test_test_benchmark_benchmark", "test_benchmark"),
        ("test__benchmark", ""),
    ],
)
def test_get_benchmark_label(name: str, label: str) -> None:
    assert get_benchmark_label({"name": name}) == label


def test_get_benchmark_label_ignores_param() -> None:
    assert get_benchmark_label({"name": "test_foo", "param": "x"}) == "foo"


def test_get_benchmark_label_missing_name() -> None:
    with pytest.raises(KeyError, match=r"name"):
        get_benchmark_label({})


def test_get_import_label_uses_param() -> None:
    assert get_import_label({"name": "test_import[x]", "param": "x"}) == "x"


def test_get_import_label_without_param_uses_name() -> None:
    assert get_import_label({"name": "test_foo_benchmark"}) == "foo"


def test_get_import_label_none_param_uses_name() -> None:
    assert get_import_label({"name": "test_foo", "param": None}) == "foo"


def test_get_import_label_empty_param_uses_name() -> None:
    assert get_import_label({"name": "test_foo", "param": ""}) == "foo"


###############################
#     Tests for TrendKind     #
###############################


STATS = {"name": "test_a", "stats": {"median": 0.5, "mean": 2.0}}


def test_benchmark_kind_get_time() -> None:
    assert BENCHMARK_KIND.get_time(STATS, "median") == 0.5


def test_benchmark_kind_get_time_other_stat() -> None:
    assert BENCHMARK_KIND.get_time(STATS, "mean") == 2.0


def test_benchmark_kind_get_time_unknown_stat() -> None:
    with pytest.raises(UnknownStatError, match=r"'max' is not in the stats of 'test_a'"):
        BENCHMARK_KIND.get_time(STATS, "max")


def test_benchmark_kind_get_time_missing_stats() -> None:
    with pytest.raises(KeyError, match=r"stats"):
        BENCHMARK_KIND.get_time({"name": "test_a"}, "median")


IMPORT_STATS = {"extra_info": {"import_seconds_median": 0.5, "import_seconds_min": 0.25}}


def test_import_kind_get_time() -> None:
    assert IMPORT_KIND.get_time(IMPORT_STATS, "median") == 0.5


def test_import_kind_get_time_other_stat() -> None:
    assert IMPORT_KIND.get_time(IMPORT_STATS, "min") == 0.25


def test_import_kind_get_time_unknown_stat() -> None:
    assert IMPORT_KIND.get_time(IMPORT_STATS, "max") is None


def test_import_kind_get_time_without_extra_info() -> None:
    assert IMPORT_KIND.get_time({"name": "test_a"}, "median") is None


@pytest.mark.parametrize(
    ("unit", "shown", "scale"),
    [("s", "s", 1.0), ("ms", "ms", 1e3), ("us", "µs", 1e6), ("µs", "µs", 1e6), ("ns", "ns", 1e9)],
)
def test_with_unit(unit: str, shown: str, scale: float) -> None:
    kind = with_unit(BENCHMARK_KIND, unit)
    assert (kind.unit, kind.scale) == (shown, scale)


def test_with_unit_keeps_the_other_fields() -> None:
    assert with_unit(IMPORT_KIND, "s").get_time is IMPORT_KIND.get_time


def test_with_unit_does_not_modify_the_kind() -> None:
    with_unit(BENCHMARK_KIND, "s")
    assert (BENCHMARK_KIND.unit, BENCHMARK_KIND.scale) == ("µs", 1e6)


def test_with_unit_unknown_unit() -> None:
    with pytest.raises(ValueError, match=r"Unknown unit 'min'"):
        with_unit(BENCHMARK_KIND, "min")


def test_units() -> None:
    assert UNITS == {"s": 1.0, "ms": 1e3, "us": 1e6, "µs": 1e6, "ns": 1e9}


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


def test_load_runs_invalid_json(tmp_path: Path) -> None:
    tmp_path.joinpath("a.json").write_text("not json")
    with pytest.raises(json.JSONDecodeError, match=r"Expecting value"):
        load_runs(tmp_path, days=5)


def test_load_runs_missing_datetime(tmp_path: Path) -> None:
    tmp_path.joinpath("a.json").write_text('{"benchmarks": []}')
    with pytest.raises(KeyError, match=r"datetime"):
        load_runs(tmp_path, days=5)


def test_load_runs_invalid_datetime(tmp_path: Path) -> None:
    tmp_path.joinpath("a.json").write_text('{"datetime": "yesterday", "benchmarks": []}')
    with pytest.raises(ValueError, match=r"Invalid isoformat string"):
        load_runs(tmp_path, days=5)


def test_load_runs_stat(tmp_path: Path) -> None:
    date = datetime.now(tz=UTC) - timedelta(days=1)
    bench = {"name": "test_a", "stats": {"median": 0.001, "mean": 0.003}}
    write_run(tmp_path / "a.json", date, [bench])
    assert load_runs(tmp_path, days=5, stat="mean") == [(date, {"a": 0.003})]


def test_load_runs_unknown_stat(tmp_path: Path) -> None:
    write_run(tmp_path / "a.json", datetime.now(tz=UTC) - timedelta(days=1), [BENCH_A])
    with pytest.raises(UnknownStatError, match=r"'mean' is not in the stats of 'test_a_benchmark'"):
        load_runs(tmp_path, days=5, stat="mean")


def test_load_runs_import_kind_stat(tmp_path: Path) -> None:
    date = datetime.now(tz=UTC) - timedelta(days=1)
    bench = {"name": "t", "param": "a", "extra_info": {"import_seconds_min": 0.0005}}
    write_run(tmp_path / "a.json", date, [bench])
    assert load_runs(tmp_path, days=5, kind=IMPORT_KIND, stat="min") == [(date, {"a": 0.0005})]


def test_load_runs_run_without_benchmarks(tmp_path: Path) -> None:
    date = datetime.now(tz=UTC) - timedelta(days=1)
    write_run(tmp_path / "a.json", date, [])
    assert load_runs(tmp_path, days=5) == [(date, {})]


def test_load_runs_several_benchmarks_in_one_run(tmp_path: Path) -> None:
    date = datetime.now(tz=UTC) - timedelta(days=1)
    write_run(tmp_path / "a.json", date, [BENCH_A, BENCH_B])
    assert load_runs(tmp_path, days=5) == [(date, {"a": 0.001, "b": 0.002})]


def test_load_runs_zero_days_skips_every_run(tmp_path: Path) -> None:
    write_run(tmp_path / "a.json", datetime.now(tz=UTC) - timedelta(seconds=1), [BENCH_A])
    assert load_runs(tmp_path, days=0) == []


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


def test_make_table_zero_first_value_has_zero_change() -> None:
    runs = make_runs({"a": 0.0}, {"a": 1.0})
    assert make_table(runs).splitlines()[-1] == (
        "| a | 1000000.0 | 0.0 | +0.0% | 500000.0 | 0.0 | 1000000.0 | 2 | `▁█` |"
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


def test_find_regressions_several_benchmarks_only_slow_ones() -> None:
    runs = make_runs({"a": 1.0, "b": 1.0}, {"a": 1.0, "b": 3.0})
    assert find_regressions(runs) == [("b", 3.0, 1.0, 200.0)]


def test_find_regressions_negative_threshold_reports_any_slowdown() -> None:
    runs = make_runs({"a": 1.0}, {"a": 1.01})
    assert find_regressions(runs, threshold=-1.0) == [("a", 1.01, 1.0, pytest.approx(1.0))]


def test_find_regressions_window_zero_uses_every_previous_run() -> None:
    # previous[-0:] is the whole list, so a window of 0 does not disable the detection.
    runs = make_runs({"a": 1.0}, {"a": 1.0}, {"a": 2.0})
    assert find_regressions(runs, window=0) == [("a", 2.0, 1.0, 100.0)]


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


def test_make_regression_report_several_regressions() -> None:
    assert make_regression_report([("b", 3e-06, 1e-06, 200.0), ("a", 2e-06, 1e-06, 100.0)]) == (
        "### Regressions\n"
        "\n"
        "| Benchmark | Latest (µs) | Previous median (µs) | Change |\n"
        "|---|---:|---:|---:|\n"
        "| b | 3.0 | 1.0 | +200.0% |\n"
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


def test_make_annotations_one_per_regression() -> None:
    regressions = [("b", 3e-06, 1e-06, 200.0), ("a", 2e-06, 1e-06, 100.0)]
    assert len(make_annotations(regressions)) == 2


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
    write_run(tmp_path / "0.json", now - timedelta(days=4), [BENCH_A])
    write_run(tmp_path / "1.json", now - timedelta(days=3), [BENCH_A])
    write_run(tmp_path / "2.json", now - timedelta(days=2), [slow])
    write_run(tmp_path / "3.json", now - timedelta(days=1), [slow])
    _, annotations = build_report(tmp_path, window=1)
    assert annotations == []


def test_build_trend_report_stat_in_title(tmp_path: Path) -> None:
    bench = {"name": "test_a", "stats": {"median": 0.001, "mean": 0.003}}
    write_run(tmp_path / "a.json", datetime.now(tz=UTC) - timedelta(days=1), [bench])
    result = build_trend_report(tmp_path, stat="mean", days=5)
    assert result is not None
    assert result[0].startswith("## Benchmarks (mean) over the last 5 days (1 runs)\n")


def test_build_trend_report_median_is_not_in_title(tmp_path: Path) -> None:
    write_run(tmp_path / "a.json", datetime.now(tz=UTC) - timedelta(days=1), [BENCH_A])
    result = build_trend_report(tmp_path, stat="median", days=5)
    assert result is not None
    assert result[0].startswith("## Benchmarks over the last 5 days (1 runs)\n")


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
