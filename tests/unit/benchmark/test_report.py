from __future__ import annotations

from datetime import UTC, datetime

import pytest

from feu.benchmark import UNITS, Regression, Run, TrendReport, make_report
from feu.benchmark.report import (
    _escape_annotation,
    _escape_cell,
    _format_time,
    _make_annotation,
    _make_regression_table,
    _make_section,
    _make_table,
    _sparkline,
    _unit_name,
)

DATE = datetime(2026, 1, 1, tzinfo=UTC)
HEADER = (
    "| Benchmark | Latest ({u}) | First ({u}) | Change | Median ({u}) | Min ({u}) | Max ({u}) "
    "| Runs | Trend |\n|---|---:|---:|---:|---:|---:|---:|---:|---|"
)


ANNOTATION = (
    "::warning title=Regression::a is 200.0%25 slower than the median of the previous "
    "runs (1.50 s instead of 0.500 s)"
)


def make_runs(*values: dict, machine: str = "") -> list[Run]:
    return [Run(DATE, machine, times) for times in values]


def reg(label: str, latest: float, baseline: float, change: float, machine: str = "") -> Regression:
    return Regression(machine, label, latest, baseline, change)


###############################
#     Tests for sparkline     #
###############################


def test_sparkline_increasing() -> None:
    assert _sparkline([1.0, 2.0, 3.0]) == "▁▅█"


def test_sparkline_constant() -> None:
    assert _sparkline([2.0, 2.0]) == "▁▁"


def test_sparkline_single_value() -> None:
    assert _sparkline([5.0]) == "▁"


def test_sparkline_negative_values() -> None:
    assert _sparkline([-1.0, 0.0, 1.0]) == "▁▅█"


def test_sparkline_does_not_modify_values() -> None:
    values = [3.0, 1.0, 2.0]
    _sparkline(values)
    assert values == [3.0, 1.0, 2.0]


def test_sparkline_empty() -> None:
    with pytest.raises(ValueError, match=r"min\(\) .*empty"):
        _sparkline([])


###############################
#     Tests for UNITS         #
###############################


def test_units() -> None:
    assert UNITS == {"s": 1.0, "ms": 1e3, "us": 1e6, "ns": 1e9}


def test_unit_name_us_is_shown_with_the_micro_sign() -> None:
    assert _unit_name("us") == "µs"


@pytest.mark.parametrize("unit", ["s", "ms", "ns"])
def test_unit_name_other_units(unit: str) -> None:
    assert _unit_name(unit) == unit


###################################
#     Tests for _format_time      #
###################################


@pytest.mark.parametrize(
    ("seconds", "unit", "expected"),
    [
        (0.1234, "s", "0.123"),
        (12.34, "s", "12.3"),
        (123.4, "s", "123"),
        (1234567.8, "s", "1234568"),
        (1e-9, "ns", "1.00"),
        (1.2e-6, "us", "1.20"),
        (1.2e-6, "s", "0.00000120"),
        (0.0015, "ms", "1.50"),
        (9.996e-6, "us", "10.0"),
        (0.9996, "s", "1.00"),
        (99.96, "s", "100"),
        (2e-7, "ns", "200"),
    ],
)
def test_format_time(seconds: float, unit: str, expected: str) -> None:
    assert _format_time(seconds, unit) == expected


@pytest.mark.parametrize("seconds", [0.0, -1.0])
def test_format_time_not_positive(seconds: float) -> None:
    with pytest.raises(ValueError, match=r"seconds must be greater than 0"):
        _format_time(seconds, "s")


###################################
#     Tests for the escaping      #
###################################


def test_escape_cell_pipe() -> None:
    assert _escape_cell("a|b") == "a\\|b"


def test_escape_cell_line_breaks() -> None:
    assert _escape_cell("a\r\nb\nc") == "a  b c"


def test_escape_cell_plain_text() -> None:
    assert _escape_cell("sort[10]") == "sort[10]"


def test_escape_annotation() -> None:
    assert _escape_annotation("a%b\r\nc") == "a%25b%0D%0Ac"


def test_escape_annotation_plain_text() -> None:
    assert _escape_annotation("sort") == "sort"


###################################
#     Tests for _make_table       #
###################################


def test_make_table_header() -> None:
    table = _make_table(make_runs({"a": 1e-6}), kind="benchmark", unit="us")
    assert table.splitlines()[:2] == HEADER.format(u="µs").splitlines()


def test_make_table_import_header() -> None:
    table = _make_table(make_runs({"a": 1e-3}), kind="import", unit="ms")
    assert table.splitlines()[0].startswith("| Import | Latest (ms) |")


def test_make_table_one_benchmark() -> None:
    table = _make_table(make_runs({"a": 1e-6}, {"a": 2e-6}), kind="benchmark", unit="us")
    assert table.splitlines()[-1] == "| a | 2.00 | 1.00 | +100.0% | 1.50 | 1.00 | 2.00 | 2 | `▁█` |"


def test_make_table_no_run() -> None:
    assert _make_table([], kind="benchmark", unit="us") == HEADER.format(u="µs")


def test_make_table_sorted_by_latest_time() -> None:
    table = _make_table(make_runs({"a": 3e-6, "b": 1e-6}), kind="benchmark", unit="us")
    assert [line.split("|")[1].strip() for line in table.splitlines()[2:]] == ["b", "a"]


def test_make_table_ties_are_sorted_by_label() -> None:
    table = _make_table(make_runs({"b": 1e-6, "a": 1e-6}), kind="benchmark", unit="us")
    assert [line.split("|")[1].strip() for line in table.splitlines()[2:]] == ["a", "b"]


def test_make_table_benchmark_missing_in_some_runs() -> None:
    table = _make_table(make_runs({"a": 1e-6}, {"a": 2e-6, "b": 5e-6}), kind="benchmark", unit="us")
    assert table.splitlines()[-1] == "| b | 5.00 | 5.00 | +0.0% | 5.00 | 5.00 | 5.00 | 1 | `▁` |"


def test_make_table_unit() -> None:
    table = _make_table(make_runs({"a": 1.5e-3}), kind="benchmark", unit="ms")
    assert table.splitlines()[-1].startswith("| a | 1.50 |")


def test_make_table_small_time_keeps_its_digits() -> None:
    table = _make_table(make_runs({"a": 1.2e-6}), kind="benchmark", unit="s")
    assert table.splitlines()[-1].startswith("| a | 0.00000120 |")


def test_make_table_escapes_the_label() -> None:
    table = _make_table(make_runs({"a|b": 1e-6}), kind="benchmark", unit="us")
    assert table.splitlines()[-1].startswith("| a\\|b | 1.00 |")


def test_make_table_does_not_modify_runs() -> None:
    runs = make_runs({"a": 1e-6}, {"a": 2e-6})
    _make_table(runs, kind="benchmark", unit="us")
    assert runs == make_runs({"a": 1e-6}, {"a": 2e-6})


###########################################
#     Tests for _make_regression_table    #
###########################################


def test_make_regression_table() -> None:
    table = _make_regression_table([reg("a", 2e-6, 1e-6, 100.0)], kind="benchmark", unit="us")
    assert table == (
        "| Benchmark | Latest (µs) | Previous median (µs) | Change |\n"
        "|---|---:|---:|---:|\n"
        "| a | 2.00 | 1.00 | +100.0% |"
    )


def test_make_regression_table_import() -> None:
    table = _make_regression_table([reg("a", 2e-3, 1e-3, 100.0)], kind="import", unit="ms")
    assert table.splitlines()[0] == "| Import | Latest (ms) | Previous median (ms) | Change |"


def test_make_regression_table_several_regressions_keep_the_order() -> None:
    items = [reg("b", 3e-6, 1e-6, 200.0), reg("a", 2e-6, 1e-6, 100.0)]
    table = _make_regression_table(items, kind="benchmark", unit="us")
    assert [line.split("|")[1].strip() for line in table.splitlines()[2:]] == ["b", "a"]


def test_make_regression_table_escapes_the_label() -> None:
    table = _make_regression_table([reg("a|b", 2e-6, 1e-6, 100.0)], kind="benchmark", unit="us")
    assert table.splitlines()[-1].startswith("| a\\|b |")


##################################
#     Tests for _make_annotation #
##################################


def test_make_annotation() -> None:
    assert _make_annotation(reg("a", 2e-6, 1e-6, 100.0), unit="us", show_machine=False) == (
        "::warning title=Regression::a is 100.0%25 slower than the median of the previous runs "
        "(2.00 µs instead of 1.00 µs)"
    )


def test_make_annotation_with_the_machine() -> None:
    annotation = _make_annotation(
        reg("a", 2e-6, 1e-6, 100.0, machine="linux"), unit="us", show_machine=True
    )
    assert annotation.startswith("::warning title=Regression::a on linux is 100.0%25")


def test_make_annotation_with_the_root_machine() -> None:
    annotation = _make_annotation(reg("a", 2e-6, 1e-6, 100.0), unit="us", show_machine=True)
    assert annotation.startswith("::warning title=Regression::a on (root) is")


def test_make_annotation_escapes_the_label() -> None:
    annotation = _make_annotation(reg("a\nb%c", 2e-6, 1e-6, 100.0), unit="us", show_machine=False)
    assert annotation.startswith("::warning title=Regression::a%0Ab%25c is")


def test_make_annotation_has_no_line_break() -> None:
    annotation = _make_annotation(reg("a\r\nb", 2e-6, 1e-6, 100.0), unit="us", show_machine=False)
    assert "\n" not in annotation
    assert "\r" not in annotation


#################################
#     Tests for _make_section   #
#################################


def test_make_section_without_regression() -> None:
    runs = make_runs({"a": 1e-6})
    assert _make_section(runs, [], kind="benchmark", unit="us", level=3) == (
        f"{_make_table(runs, kind='benchmark', unit='us')}\n"
    )


@pytest.mark.parametrize("level", [3, 4])
def test_make_section_regression_heading_level(level: int) -> None:
    section = _make_section(
        make_runs({"a": 1e-6}),
        [reg("a", 2e-6, 1e-6, 100.0)],
        kind="benchmark",
        unit="us",
        level=level,
    )
    assert f"\n\n{'#' * level} Regressions\n\n| Benchmark |" in section


#################################
#     Tests for make_report     #
#################################


def test_make_report_whole_report() -> None:
    runs = make_runs({"a": 0.5, "b|c": 2.0}, {"a": 0.5, "b|c": 2.0}, {"a": 1.5, "b|c": 2.0})
    assert make_report(runs, unit="s") == TrendReport(
        markdown=(
            "## Benchmarks (median) over the last 90 days (3 runs)\n"
            "\n"
            "| Benchmark | Latest (s) | First (s) | Change | Median (s) | Min (s) "
            "| Max (s) | Runs | Trend |\n"
            "|---|---:|---:|---:|---:|---:|---:|---:|---|\n"
            "| a | 1.50 | 0.500 | +200.0% | 0.500 | 0.500 | 1.50 | 3 | `▁▁█` |\n"
            "| b\\|c | 2.00 | 2.00 | +0.0% | 2.00 | 2.00 | 2.00 | 3 | `▁▁▁` |\n"
            "\n"
            "### Regressions\n"
            "\n"
            "| Benchmark | Latest (s) | Previous median (s) | Change |\n"
            "|---|---:|---:|---:|\n"
            "| a | 1.50 | 0.500 | +200.0% |\n"
        ),
        annotations=(ANNOTATION,),
        regressions=(Regression("", "a", 1.5, 0.5, 200.0),),
    )


def test_make_report_two_machines() -> None:
    runs = make_runs({"a": 1e-3}, {"a": 4e-3}, machine="linux") + make_runs(
        {"a": 1e-3}, machine="mac"
    )
    assert make_report(runs, unit="ms").markdown == (
        "## Benchmarks (median) over the last 90 days (3 runs)\n"
        "\n"
        "### linux\n"
        "\n"
        "| Benchmark | Latest (ms) | First (ms) | Change | Median (ms) | Min (ms) "
        "| Max (ms) | Runs | Trend |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---|\n"
        "| a | 4.00 | 1.00 | +300.0% | 2.50 | 1.00 | 4.00 | 2 | `▁█` |\n"
        "\n"
        "#### Regressions\n"
        "\n"
        "| Benchmark | Latest (ms) | Previous median (ms) | Change |\n"
        "|---|---:|---:|---:|\n"
        "| a | 4.00 | 1.00 | +300.0% |\n"
        "\n"
        "### mac\n"
        "\n"
        "| Benchmark | Latest (ms) | First (ms) | Change | Median (ms) | Min (ms) "
        "| Max (ms) | Runs | Trend |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---|\n"
        "| a | 1.00 | 1.00 | +0.0% | 1.00 | 1.00 | 1.00 | 1 | `▁` |\n"
    )


def test_make_report_two_machines_annotation_has_the_machine() -> None:
    runs = make_runs({"a": 1e-3}, {"a": 4e-3}, machine="linux") + make_runs(
        {"a": 1e-3}, machine="mac"
    )
    assert make_report(runs).annotations[0].startswith("::warning title=Regression::a on linux is")


def test_make_report_root_machine_among_others() -> None:
    runs = make_runs({"a": 1e-3}) + make_runs({"a": 1e-3}, machine="mac")
    assert "### (root)\n" in make_report(runs).markdown


def test_make_report_machines_are_sorted() -> None:
    runs = make_runs({"a": 1e-3}, machine="b") + make_runs({"a": 1e-3}, machine="a")
    markdown = make_report(runs).markdown
    assert markdown.index("### a\n") < markdown.index("### b\n")


def test_make_report_one_machine_has_no_machine_section() -> None:
    assert "### linux" not in make_report(make_runs({"a": 1e-3}, machine="linux")).markdown


def test_make_report_one_run_is_singular() -> None:
    title = make_report(make_runs({"a": 1e-3})).markdown.splitlines()[0]
    assert title == "## Benchmarks (median) over the last 90 days (1 run)"


def test_make_report_two_runs_is_plural() -> None:
    title = make_report(make_runs({"a": 1e-3}, {"a": 1e-3})).markdown.splitlines()[0]
    assert title == "## Benchmarks (median) over the last 90 days (2 runs)"


def test_make_report_stat_is_in_the_title() -> None:
    title = make_report(make_runs({"a": 1e-3}), stat="min").markdown.splitlines()[0]
    assert title == "## Benchmarks (min) over the last 90 days (1 run)"


def test_make_report_days_is_in_the_title() -> None:
    title = make_report(make_runs({"a": 1e-3}), days=5).markdown.splitlines()[0]
    assert title == "## Benchmarks (median) over the last 5 days (1 run)"


def test_make_report_import_kind() -> None:
    markdown = make_report(make_runs({"a": 1e-3}), kind="import").markdown
    assert markdown.splitlines()[0] == "## Import time (median) over the last 90 days (1 run)"
    assert "| Import | Latest (ms) |" in markdown


def test_make_report_benchmark_default_unit_is_us() -> None:
    assert "Latest (µs)" in make_report(make_runs({"a": 1e-3})).markdown


@pytest.mark.parametrize(
    ("unit", "header"),
    [("s", "Latest (s)"), ("ms", "Latest (ms)"), ("us", "Latest (µs)"), ("ns", "Latest (ns)")],
)
def test_make_report_unit(unit: str, header: str) -> None:
    assert header in make_report(make_runs({"a": 1e-3}), unit=unit).markdown


def test_make_report_unit_changes_the_numbers() -> None:
    markdown = make_report(make_runs({"a": 1.2e-6}), unit="ns").markdown
    assert markdown.splitlines()[-1].startswith("| a | 1200 |")


def test_make_report_threshold_hides_the_regression() -> None:
    report = make_report(make_runs({"a": 1e-3}, {"a": 2e-3}), threshold=150.0)
    assert (report.regressions, report.annotations) == ((), ())


def test_make_report_no_regression_has_no_regression_block() -> None:
    assert "Regressions" not in make_report(make_runs({"a": 1e-3}, {"a": 1e-3})).markdown


def test_make_report_baseline_runs() -> None:
    runs = make_runs({"a": 1e-3}, {"a": 1e-3}, {"a": 4e-3}, {"a": 5e-3})
    assert make_report(runs, baseline_runs=1).regressions == ()


def test_make_report_markdown_ends_with_one_line_break() -> None:
    assert make_report(make_runs({"a": 1e-3})).markdown.endswith("|\n")


def test_make_report_regressions_are_a_tuple() -> None:
    report = make_report(make_runs({"a": 1e-3}, {"a": 4e-3}))
    assert isinstance(report.regressions, tuple)


def test_make_report_does_not_modify_runs() -> None:
    runs = make_runs({"a": 1e-3}, {"a": 4e-3})
    make_report(runs)
    assert runs == make_runs({"a": 1e-3}, {"a": 4e-3})


def test_make_report_is_deterministic() -> None:
    runs = make_runs({"b": 1e-3, "a": 1e-3}, {"b": 4e-3, "a": 4e-3})
    assert make_report(runs) == make_report(runs)


def test_make_report_no_run() -> None:
    with pytest.raises(ValueError, match=r"runs must not be empty"):
        make_report([])


def test_make_report_unknown_kind() -> None:
    with pytest.raises(ValueError, match=r"Unknown kind 'nope'"):
        make_report(make_runs({"a": 1e-3}), kind="nope")


def test_make_report_unknown_stat() -> None:
    with pytest.raises(ValueError, match=r"Unknown stat 'nope'"):
        make_report(make_runs({"a": 1e-3}), stat="nope")


@pytest.mark.parametrize("unit", ["min", "µs", ""])
def test_make_report_unknown_unit(unit: str) -> None:
    with pytest.raises(ValueError, match=r"Unknown unit"):
        make_report(make_runs({"a": 1e-3}), unit=unit)


def test_make_report_invalid_baseline_runs() -> None:
    with pytest.raises(ValueError, match=r"baseline_runs must be greater than or equal to 1"):
        make_report(make_runs({"a": 1e-3}), baseline_runs=0)


def test_make_report_invalid_threshold() -> None:
    with pytest.raises(ValueError, match=r"threshold must be greater than 0"):
        make_report(make_runs({"a": 1e-3}), threshold=0.0)
