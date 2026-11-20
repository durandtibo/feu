from __future__ import annotations

from unittest.mock import patch

import pytest

from tests.package_checks import (
    EXTRA_MODULES,
    check_extras,
    get_required_extras,
    parse_args,
)

ALL_EXTRAS = ["cli", "git", "requests", "rich"]

################################
#     Tests for parse_args     #
################################


def test_parse_args_default() -> None:
    assert parse_args([]).extra == []


def test_parse_args_one_extra() -> None:
    assert parse_args(["--extra", "rich"]).extra == ["rich"]


def test_parse_args_repeated_extra() -> None:
    assert parse_args(["--extra", "rich", "--extra", "cli"]).extra == ["rich", "cli"]


def test_parse_args_empty_extra() -> None:
    assert parse_args(["--extra", ""]).extra == [""]


#########################################
#     Tests for get_required_extras     #
#########################################


def test_get_required_extras_empty() -> None:
    assert get_required_extras([]) == []


def test_get_required_extras_empty_value() -> None:
    assert get_required_extras([""]) == []


def test_get_required_extras_one() -> None:
    assert get_required_extras(["rich"]) == ["rich"]


def test_get_required_extras_comma_separated() -> None:
    assert get_required_extras(["rich, cli"]) == ["cli", "rich"]


def test_get_required_extras_repeated_and_duplicated() -> None:
    assert get_required_extras(["rich", "rich,cli"]) == ["cli", "rich"]


def test_get_required_extras_all() -> None:
    assert get_required_extras(["all"]) == ALL_EXTRAS


def test_get_required_extras_all_with_another_extra() -> None:
    assert get_required_extras(["all", "rich"]) == ALL_EXTRAS


def test_get_required_extras_unknown() -> None:
    with pytest.raises(ValueError, match=r"Unknown extras: \['foo'\]"):
        get_required_extras(["rich", "foo"])


##################################
#     Tests for check_extras     #
##################################


def test_check_extras_no_extra() -> None:
    check_extras([])


def test_check_extras_installed() -> None:
    with patch("tests.package_checks.importlib.util.find_spec", return_value=object()):
        check_extras(ALL_EXTRAS)


def test_check_extras_missing_library() -> None:
    with (
        patch("tests.package_checks.importlib.util.find_spec", return_value=None),
        pytest.raises(
            ModuleNotFoundError,
            match=r"the extra 'rich' was requested but 'rich' is not installed",
        ),
    ):
        check_extras(["rich"])


def test_check_extras_checks_every_module_of_an_extra() -> None:
    with patch("tests.package_checks.importlib.util.find_spec") as find_spec:
        check_extras(["requests"])
    assert [c.args[0] for c in find_spec.call_args_list] == list(EXTRA_MODULES["requests"])
