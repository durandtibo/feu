from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from feu.benchmark import KINDS, STATS, Run, load_runs, prune_runs
from feu.benchmark.runs import (
    _check_choice,
    _check_days,
    _get_benchmarks,
    _get_date,
    _get_label,
    _get_machine,
    _get_time,
    _get_times,
    _read_json,
)

BENCH_A = {
    "name": "test_a_benchmark",
    "fullname": "t.py::test_a_benchmark",
    "stats": {"median": 0.001},
}
BENCH_B = {
    "name": "test_b_benchmark",
    "fullname": "t.py::test_b_benchmark",
    "stats": {"median": 0.002},
}
IMPORT_A = {"name": "test_import", "param": "a", "extra_info": {"import_seconds_median": 0.001}}
NOW = datetime.now(tz=UTC)


def write_run(path: Path, date: datetime, benchmarks: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"datetime": date.isoformat(), "benchmarks": benchmarks}))


def set_item(mapping: Any, key: str, value: object) -> None:
    mapping[key] = value


def set_attribute(obj: object, name: str, value: object) -> None:
    setattr(obj, name, value)


def ago(days: float) -> datetime:
    return NOW - timedelta(days=days)


#################################
#     Tests for the choices     #
#################################


def test_kinds() -> None:
    assert KINDS == ("benchmark", "import")


def test_stats() -> None:
    assert STATS == ("min", "mean", "median", "max")


def test_check_choice_valid() -> None:
    _check_choice("stat", "min", STATS)


def test_check_choice_invalid() -> None:
    with pytest.raises(ValueError, match=r"Unknown stat 'nope'. The valid values are \['min'"):
        _check_choice("stat", "nope", STATS)


@pytest.mark.parametrize("days", [1, 90])
def test_check_days_valid(days: int) -> None:
    _check_days(days)


@pytest.mark.parametrize("days", [0, -1])
def test_check_days_invalid(days: int) -> None:
    with pytest.raises(ValueError, match=r"days must be greater than or equal to 1"):
        _check_days(days)


########################
#     Tests for Run    #
########################


def test_run_times_are_read_only() -> None:
    run = Run(ago(1), "", {"a": 0.001})
    with pytest.raises(TypeError, match=r"does not support item assignment"):
        set_item(run.times, "b", 1.0)


def test_run_copies_the_times() -> None:
    times = {"a": 0.001}
    run = Run(ago(1), "", times)
    times["b"] = 1.0
    assert dict(run.times) == {"a": 0.001}


def test_run_is_frozen() -> None:
    run = Run(ago(1), "", {"a": 0.001})
    with pytest.raises(AttributeError, match=r"cannot assign to field 'machine'"):
        set_attribute(run, "machine", "x")


def test_run_equal() -> None:
    assert Run(NOW, "m", {"a": 0.001}) == Run(NOW, "m", {"a": 0.001})


def test_run_different_machine() -> None:
    assert Run(NOW, "m", {"a": 0.001}) != Run(NOW, "n", {"a": 0.001})


####################################
#     Tests for _read_json         #
####################################


def test_read_json(tmp_path: Path) -> None:
    path = tmp_path / "0001_a.json"
    path.write_text('{"x": 1}')
    assert _read_json(path) == {"x": 1}


def test_read_json_utf8(tmp_path: Path) -> None:
    path = tmp_path / "0001_a.json"
    path.write_bytes('{"name": "µs"}'.encode())
    assert _read_json(path) == {"name": "µs"}


def test_read_json_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "0001_a.json"
    path.write_text("not json")
    with pytest.raises(ValueError, match=r"0001_a.json: not a pytest-benchmark result \(Expecting"):
        _read_json(path)


def test_read_json_not_an_object(tmp_path: Path) -> None:
    path = tmp_path / "0001_a.json"
    path.write_text("[1]")
    with pytest.raises(ValueError, match=r"0001_a.json: .*not a JSON object"):
        _read_json(path)


##############################
#     Tests for _get_date    #
##############################


def test_get_date(tmp_path: Path) -> None:
    date = _get_date(tmp_path, {"datetime": "2026-01-01T00:00:00+02:00"})
    assert date == datetime(2025, 12, 31, 22, 0, tzinfo=UTC)


def test_get_date_naive_is_utc(tmp_path: Path) -> None:
    assert _get_date(tmp_path, {"datetime": "2026-01-01T00:00:00"}) == datetime(
        2026, 1, 1, tzinfo=UTC
    )


def test_get_date_missing(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=r"missing key 'datetime'"):
        _get_date(tmp_path, {})


@pytest.mark.parametrize("value", ["yesterday", None, 3])
def test_get_date_invalid(tmp_path: Path, value: object) -> None:
    with pytest.raises(ValueError, match=r"invalid date"):
        _get_date(tmp_path, {"datetime": value})


##################################
#     Tests for _get_benchmarks  #
##################################


def test_get_benchmarks(tmp_path: Path) -> None:
    assert _get_benchmarks(tmp_path, {"benchmarks": [BENCH_A]}) == [BENCH_A]


@pytest.mark.parametrize("data", [{}, {"benchmarks": None}, {"benchmarks": {}}])
def test_get_benchmarks_invalid(tmp_path: Path, data: dict) -> None:
    with pytest.raises(ValueError, match=r"missing key 'benchmarks'"):
        _get_benchmarks(tmp_path, data)


################################
#     Tests for _get_label     #
################################


@pytest.mark.parametrize(
    ("name", "label"),
    [
        ("test_sort_benchmark", "sort"),
        ("test_sort_benchmark[10]", "sort[10]"),
        ("test_sort", "sort"),
        ("sort_benchmark", "sort"),
        ("sort", "sort"),
        ("test_benchmark", "benchmark"),
        ("test_a_b_benchmark[x_benchmark]", "a_b[x_benchmark]"),
        ("test_test_benchmark_benchmark", "test_benchmark"),
        ("test_sort[a|b]", "sort[a|b]"),
    ],
)
def test_get_label_name(name: str, label: str) -> None:
    assert _get_label({"name": name}, "benchmark", "name") == label


def test_get_label_name_with_a_newline() -> None:
    assert _get_label({"name": "test_a[x\ny]"}, "benchmark", "name") == "a[x\ny]"


def test_get_label_fullname() -> None:
    assert _get_label(BENCH_A, "benchmark", "fullname") == "t.py::test_a_benchmark"


def test_get_label_fullname_import_kind() -> None:
    bench = {**IMPORT_A, "fullname": "t.py::test_import[a]"}
    assert _get_label(bench, "import", "fullname") == "t.py::test_import[a]"


def test_get_label_import_uses_param() -> None:
    assert _get_label({"name": "test_import[x]", "param": "x"}, "import", "name") == "x"


@pytest.mark.parametrize("param", [None, ""])
def test_get_label_import_without_param_uses_name(param: str | None) -> None:
    assert _get_label({"name": "test_foo_benchmark", "param": param}, "import", "name") == "foo"


def test_get_label_benchmark_kind_ignores_param() -> None:
    assert _get_label({"name": "test_foo", "param": "x"}, "benchmark", "name") == "foo"


###############################
#     Tests for _get_time     #
###############################


def test_get_time_benchmark() -> None:
    assert _get_time(BENCH_A, "benchmark", "median") == 0.001


def test_get_time_benchmark_integer() -> None:
    assert _get_time({"name": "t", "stats": {"max": 2}}, "benchmark", "max") == 2.0


def test_get_time_import() -> None:
    assert _get_time(IMPORT_A, "import", "median") == 0.001


def test_get_time_import_other_stat_is_none() -> None:
    assert _get_time(IMPORT_A, "import", "min") is None


def test_get_time_import_without_extra_info_is_none() -> None:
    assert _get_time({"name": "t"}, "import", "median") is None


def test_get_time_missing_stat() -> None:
    with pytest.raises(KeyError, match=r"mean"):
        _get_time(BENCH_A, "benchmark", "mean")


def test_get_time_missing_stats() -> None:
    with pytest.raises(KeyError, match=r"stats"):
        _get_time({"name": "t"}, "benchmark", "median")


@pytest.mark.parametrize("value", [0, 0.0, -1.0, float("nan"), float("inf"), True, "1.0", None])
def test_get_time_invalid_benchmark(value: object) -> None:
    bench = {"name": "test_a", "stats": {"median": value}}
    with pytest.raises(ValueError, match=r"the time .* of 'test_a' is not a finite number > 0"):
        _get_time(bench, "benchmark", "median")


@pytest.mark.parametrize("value", [0.0, -1.0, float("nan"), float("inf")])
def test_get_time_invalid_import(value: float) -> None:
    bench = {"name": "test_a", "extra_info": {"import_seconds_median": value}}
    with pytest.raises(ValueError, match=r"of 'test_a' is not a finite number > 0"):
        _get_time(bench, "import", "median")


#################################
#     Tests for _get_times      #
#################################


def get_times(data: dict, **kwargs: str) -> dict:
    options = {"kind": "benchmark", "stat": "median", "label": "name"} | kwargs
    return _get_times(PATH, data, **options)


PATH = Path("0001_run.json")


def test_get_times() -> None:
    assert get_times({"benchmarks": [BENCH_A, BENCH_B]}) == {"a": 0.001, "b": 0.002}


def test_get_times_empty() -> None:
    assert get_times({"benchmarks": []}) == {}


def test_get_times_import_skips_entries_without_time() -> None:
    assert get_times({"benchmarks": [IMPORT_A, {"name": "other"}]}, kind="import") == {"a": 0.001}


def test_get_times_duplicate_label() -> None:
    data = {"benchmarks": [BENCH_A, {**BENCH_A, "fullname": "t.py::TestA::test_a_benchmark"}]}
    with pytest.raises(ValueError, match=r"0001_run.json: the label 'a' is used by two"):
        get_times(data)


def test_get_times_duplicate_label_message_names_the_fix() -> None:
    with pytest.raises(ValueError, match=r"use label='fullname'"):
        get_times({"benchmarks": [BENCH_A, BENCH_A]})


def test_get_times_fullname_avoids_the_duplicate() -> None:
    other = {**BENCH_A, "fullname": "t.py::TestA::test_a_benchmark"}
    assert get_times({"benchmarks": [BENCH_A, other]}, label="fullname") == {
        "t.py::test_a_benchmark": 0.001,
        "t.py::TestA::test_a_benchmark": 0.001,
    }


def test_get_times_missing_stats() -> None:
    with pytest.raises(ValueError, match=r"0001_run.json: .*missing key 'stats'"):
        get_times({"benchmarks": [{"name": "test_a"}]})


def test_get_times_missing_name() -> None:
    with pytest.raises(ValueError, match=r"missing key 'name'"):
        get_times({"benchmarks": [{"stats": {"median": 1.0}}]})


def test_get_times_missing_fullname() -> None:
    with pytest.raises(ValueError, match=r"missing key 'fullname'"):
        get_times({"benchmarks": [{"name": "a", "stats": {"median": 1.0}}]}, label="fullname")


@pytest.mark.parametrize("entry", [None, 1, "a", [1]])
def test_get_times_invalid_entry(entry: object) -> None:
    with pytest.raises(ValueError, match=r"invalid benchmark entry"):
        get_times({"benchmarks": [entry]})


def test_get_times_invalid_time_names_the_path() -> None:
    bench = {"name": "test_a", "stats": {"median": 0.0}}
    with pytest.raises(ValueError, match=r"0001_run.json: the time 0.0 of 'test_a'"):
        get_times({"benchmarks": [bench]})


###############################
#     Tests for _get_machine  #
###############################


def test_get_machine_in_the_storage(tmp_path: Path) -> None:
    assert _get_machine(tmp_path, tmp_path / "0001_a.json") == ""


def test_get_machine_in_a_directory(tmp_path: Path) -> None:
    assert _get_machine(tmp_path, tmp_path / "Linux-A" / "0001_a.json") == "Linux-A"


def test_get_machine_nested(tmp_path: Path) -> None:
    assert _get_machine(tmp_path, tmp_path / "a" / "b" / "0001_a.json") == "a/b"


###############################
#     Tests for load_runs     #
###############################


def test_load_runs_empty_storage(tmp_path: Path) -> None:
    assert load_runs(tmp_path) == []


def test_load_runs_one_run(tmp_path: Path) -> None:
    date = ago(1)
    write_run(tmp_path / "0001_a.json", date, [BENCH_A])
    assert load_runs(tmp_path) == [Run(date, "", {"a": 0.001})]


def test_load_runs_sorted_by_date(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_a.json", ago(1), [BENCH_B])
    write_run(tmp_path / "0002_a.json", ago(2), [BENCH_A])
    assert load_runs(tmp_path) == [
        Run(ago(2), "", {"a": 0.001}),
        Run(ago(1), "", {"b": 0.002}),
    ]


def test_load_runs_same_date_sorted_by_machine(tmp_path: Path) -> None:
    write_run(tmp_path / "b" / "0001_a.json", NOW, [BENCH_A])
    write_run(tmp_path / "a" / "0001_a.json", NOW, [BENCH_B])
    assert [run.machine for run in load_runs(tmp_path)] == ["a", "b"]


def test_load_runs_machine_is_the_directory(tmp_path: Path) -> None:
    write_run(tmp_path / "Linux-A" / "0001_a.json", ago(1), [BENCH_A])
    assert load_runs(tmp_path)[0].machine == "Linux-A"


def test_load_runs_skips_old_runs(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_old.json", ago(10), [BENCH_A])
    write_run(tmp_path / "0002_new.json", ago(1), [BENCH_B])
    assert load_runs(tmp_path, days=5) == [Run(ago(1), "", {"b": 0.002})]


def test_load_runs_does_not_read_the_entries_of_an_old_run(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_old.json", ago(10), [{"name": "broken"}])
    assert load_runs(tmp_path, days=5) == []


def test_load_runs_keeps_old_files(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_old.json", ago(10), [BENCH_A])
    load_runs(tmp_path, days=5)
    assert (tmp_path / "0001_old.json").exists()


def test_load_runs_ignores_files_that_are_not_results(tmp_path: Path) -> None:
    tmp_path.joinpath("other.json").write_text('{"x": 1}')
    tmp_path.joinpath("notes.txt").write_text("not json")
    assert load_runs(tmp_path) == []


def test_load_runs_ignores_a_foreign_json_next_to_a_result(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_a.json", ago(1), [BENCH_A])
    tmp_path.joinpath("config.json").write_text("[1, 2")
    assert [run.times for run in load_runs(tmp_path)] == [{"a": 0.001}]


def test_load_runs_invalid_json_names_the_file(tmp_path: Path) -> None:
    tmp_path.joinpath("0001_a.json").write_text("not json")
    with pytest.raises(ValueError, match=r"0001_a.json: not a pytest-benchmark result"):
        load_runs(tmp_path)


def test_load_runs_missing_datetime_names_the_file(tmp_path: Path) -> None:
    tmp_path.joinpath("0001_a.json").write_text('{"benchmarks": []}')
    with pytest.raises(ValueError, match=r"0001_a.json: .*missing key 'datetime'"):
        load_runs(tmp_path)


def test_load_runs_missing_stats_names_the_file(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_a.json", ago(1), [{"name": "test_a"}])
    with pytest.raises(ValueError, match=r"0001_a.json: .*missing key 'stats'"):
        load_runs(tmp_path)


@pytest.mark.parametrize("value", [0, -1.0, float("nan"), float("inf")])
def test_load_runs_invalid_time_names_the_file(tmp_path: Path, value: float) -> None:
    write_run(tmp_path / "0001_a.json", ago(1), [{"name": "test_a", "stats": {"median": value}}])
    with pytest.raises(ValueError, match=r"0001_a.json: the time"):
        load_runs(tmp_path)


def test_load_runs_duplicate_label_raises(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_a.json", ago(1), [BENCH_A, {**BENCH_A, "fullname": "t.py::C::x"}])
    with pytest.raises(ValueError, match=r"the label 'a' is used by two benchmarks"):
        load_runs(tmp_path)


def test_load_runs_fullname_label(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_a.json", ago(1), [BENCH_A, {**BENCH_A, "fullname": "t.py::C::x"}])
    assert [sorted(run.times) for run in load_runs(tmp_path, label="fullname")] == [
        ["t.py::C::x", "t.py::test_a_benchmark"]
    ]


def test_load_runs_parametrized_label_is_stable(tmp_path: Path) -> None:
    bench = {"name": "test_sort_benchmark[10]", "fullname": "t::x", "stats": {"median": 0.1}}
    write_run(tmp_path / "0001_a.json", ago(1), [bench])
    assert [run.times for run in load_runs(tmp_path)] == [{"sort[10]": 0.1}]


@pytest.mark.parametrize(
    ("stat", "expected"), [("median", 0.001), ("mean", 0.003), ("min", 0.0005)]
)
def test_load_runs_stat(tmp_path: Path, stat: str, expected: float) -> None:
    bench = {"name": "test_a", "stats": {"median": 0.001, "mean": 0.003, "min": 0.0005}}
    write_run(tmp_path / "0001_a.json", ago(1), [bench])
    assert load_runs(tmp_path, stat=stat)[0].times == {"a": expected}


def test_load_runs_stat_missing_from_the_result(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_a.json", ago(1), [BENCH_A])
    with pytest.raises(ValueError, match=r"0001_a.json: .*missing key 'mean'"):
        load_runs(tmp_path, stat="mean")


def test_load_runs_unknown_stat_fails_even_without_results(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=r"Unknown stat 'nope'"):
        load_runs(tmp_path, stat="nope")


def test_load_runs_unknown_kind(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=r"Unknown kind 'nope'"):
        load_runs(tmp_path, kind="nope")


def test_load_runs_unknown_label(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=r"Unknown label 'nope'"):
        load_runs(tmp_path, label="nope")


@pytest.mark.parametrize("days", [0, -3])
def test_load_runs_days_must_be_positive(tmp_path: Path, days: int) -> None:
    with pytest.raises(ValueError, match=r"days must be greater than or equal to 1"):
        load_runs(tmp_path, days=days)


def test_load_runs_import_kind(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_a.json", ago(1), [IMPORT_A])
    assert [run.times for run in load_runs(tmp_path, kind="import")] == [{"a": 0.001}]


def test_load_runs_import_kind_stat(tmp_path: Path) -> None:
    bench = {"name": "t", "param": "a", "extra_info": {"import_seconds_min": 0.0005}}
    write_run(tmp_path / "0001_a.json", ago(1), [bench])
    assert [run.times for run in load_runs(tmp_path, kind="import", stat="min")] == [{"a": 0.0005}]


def test_load_runs_import_kind_skips_benchmarks_without_import_time(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_a.json", ago(1), [IMPORT_A, {"name": "test_other"}])
    assert [run.times for run in load_runs(tmp_path, kind="import")] == [{"a": 0.001}]


def test_load_runs_import_kind_ignores_the_benchmark_entries(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_a.json", ago(1), [BENCH_A])
    assert load_runs(tmp_path, kind="import") == []


def test_load_runs_drops_a_run_without_time(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_a.json", ago(2), [BENCH_A])
    write_run(tmp_path / "0002_a.json", ago(1), [])
    assert [run.times for run in load_runs(tmp_path)] == [{"a": 0.001}]


def test_load_runs_naive_datetime_is_utc(tmp_path: Path) -> None:
    date = NOW.replace(tzinfo=None) - timedelta(days=1)
    write_run(tmp_path / "0001_a.json", date, [BENCH_A])
    assert load_runs(tmp_path)[0].date == date.replace(tzinfo=UTC)


def test_read_json_passes_the_utf8_encoding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    encodings = []

    def read_text(_path: Path, encoding: str | None = None) -> str:
        encodings.append(encoding)
        return "{}"

    monkeypatch.setattr(Path, "read_text", read_text)
    _read_json(tmp_path / "0001_a.json")
    assert encodings == ["utf-8"]


def test_load_runs_is_deterministic(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_a.json", ago(2), [BENCH_A])
    write_run(tmp_path / "0002_a.json", ago(1), [BENCH_B])
    assert load_runs(tmp_path) == load_runs(tmp_path)


###############################
#     Tests for prune_runs    #
###############################


def test_prune_runs_deletes_old_files(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_old.json", ago(10), [BENCH_A])
    prune_runs(tmp_path, days=5)
    assert not (tmp_path / "0001_old.json").exists()


def test_prune_runs_returns_the_deleted_files(tmp_path: Path) -> None:
    write_run(tmp_path / "0002_old.json", ago(10), [BENCH_A])
    write_run(tmp_path / "0001_old.json", ago(11), [BENCH_A])
    assert prune_runs(tmp_path, days=5) == [tmp_path / "0001_old.json", tmp_path / "0002_old.json"]


def test_prune_runs_keeps_recent_files(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_new.json", ago(1), [BENCH_A])
    assert prune_runs(tmp_path, days=5) == []
    assert (tmp_path / "0001_new.json").exists()


def test_prune_runs_deletes_in_subdirectories(tmp_path: Path) -> None:
    write_run(tmp_path / "Linux-A" / "0001_old.json", ago(10), [BENCH_A])
    prune_runs(tmp_path, days=5)
    assert not (tmp_path / "Linux-A" / "0001_old.json").exists()


def test_prune_runs_keeps_files_that_are_not_results(tmp_path: Path) -> None:
    tmp_path.joinpath("other.json").write_text('{"datetime": "2000-01-01T00:00:00+00:00"}')
    assert prune_runs(tmp_path, days=5) == []
    assert (tmp_path / "other.json").exists()


def test_prune_runs_does_not_read_the_entries(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_old.json", ago(10), [{"name": "broken"}])
    assert prune_runs(tmp_path, days=5) == [tmp_path / "0001_old.json"]


def test_prune_runs_invalid_file_deletes_nothing(tmp_path: Path) -> None:
    write_run(tmp_path / "0001_old.json", ago(10), [BENCH_A])
    tmp_path.joinpath("0002_bad.json").write_text("not json")
    with pytest.raises(ValueError, match=r"0002_bad.json: not a pytest-benchmark result"):
        prune_runs(tmp_path, days=5)
    assert (tmp_path / "0001_old.json").exists()


def test_prune_runs_days_must_be_positive(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=r"days must be greater than or equal to 1"):
        prune_runs(tmp_path, days=0)
