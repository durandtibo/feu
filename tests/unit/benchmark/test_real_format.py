from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from feu.benchmark import Run, load_runs

# The files of ``data/`` were written by pytest-benchmark 5.3.1 (the layout
# is ``<storage>/<machine-id>/NNNN_<name>.json``), then trimmed to the keys
# that ``feu.benchmark`` reads.
DATA = Path(__file__).parent / "data"
ALL_TIME = 100_000
MACHINE = "Darwin-CPython-3.15-64bit"


###################################
#     Tests for a real result     #
###################################


def test_load_runs_reads_a_real_result() -> None:
    assert load_runs(DATA, days=ALL_TIME) == [
        Run(
            datetime(2026, 11, 1, 10, 0, tzinfo=UTC),
            MACHINE,
            {"sort[10]": 1.5291967429220676e-07, "sort[20]": 1.8457998521625995e-07},
        ),
        Run(
            datetime(2026, 11, 2, 10, 0, tzinfo=UTC),
            MACHINE,
            {"sort[10]": 3.058393485844135e-07, "sort[20]": 3.691599704325199e-07},
        ),
    ]


def test_load_runs_reads_the_requested_stat_of_a_real_result() -> None:
    runs = load_runs(DATA, days=ALL_TIME, stat="min")
    assert runs[0].times["sort[10]"] == 1.4832941815257074e-07


def test_load_runs_reads_the_full_name_of_a_real_result() -> None:
    runs = load_runs(DATA, days=ALL_TIME, label="fullname")
    assert sorted(runs[0].times) == [
        "test_x_benchmark.py::test_sort_benchmark[10]",
        "test_x_benchmark.py::test_sort_benchmark[20]",
    ]
