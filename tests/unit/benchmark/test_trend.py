from __future__ import annotations

from datetime import UTC, datetime

import pytest

from feu.benchmark import Regression, Run, find_regressions

DATE = datetime(2026, 1, 1, tzinfo=UTC)


def make_runs(*values: dict) -> list[Run]:
    return [Run(DATE, "", times) for times in values]


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
