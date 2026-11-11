from __future__ import annotations

import logging
from unittest.mock import Mock, patch

import pytest

from feu.imports import (
    MissingPackageError,
    availability_cache,
    check_package,
    clear_availability_caches,
    is_module_available,
    is_package_available,
    module_available,
    package_available,
    raise_package_missing_error,
)


@pytest.fixture(autouse=True)
def _reset() -> None:
    clear_availability_caches()


#####################################
#     Tests for availability_cache  #
#####################################


def test_availability_cache_caches_the_result() -> None:
    mock = Mock(return_value=True)

    @availability_cache
    def check() -> bool:
        return mock()

    check()
    check()
    mock.assert_called_once_with()


def test_availability_cache_has_cache_clear() -> None:
    @availability_cache
    def check() -> bool:
        return True

    assert callable(check.cache_clear)


def test_clear_availability_caches_resets_a_registered_function() -> None:
    mock = Mock(return_value=True)

    @availability_cache
    def check() -> bool:
        return mock()

    check()
    clear_availability_caches()
    check()
    assert mock.call_count == 2


def test_clear_availability_caches_resets_package_available() -> None:
    with patch("feu.imports.package.find_spec", Mock(return_value=None)):
        assert not package_available("my_package")
    clear_availability_caches()
    with patch("feu.imports.package.find_spec", Mock(return_value=object())):
        assert package_available("my_package")


def test_package_available_is_stale_without_clear() -> None:
    with patch("feu.imports.package.find_spec", Mock(return_value=None)):
        assert not package_available("my_package")
    with patch("feu.imports.package.find_spec", Mock(return_value=object())):
        assert not package_available("my_package")


def test_clear_availability_caches_resets_module_available() -> None:
    with patch("feu.imports.package.importlib.import_module", Mock(side_effect=ImportError("x"))):
        assert not module_available("my_module")
    clear_availability_caches()
    with patch("feu.imports.package.importlib.import_module", Mock()):
        assert module_available("my_module")


##################################
#     Tests for MissingPackageError #
##################################


def test_missing_package_error_is_a_module_not_found_error() -> None:
    assert issubclass(MissingPackageError, ModuleNotFoundError)


def test_missing_package_error_is_a_runtime_error() -> None:
    assert issubclass(MissingPackageError, RuntimeError)


def test_missing_package_error_name() -> None:
    assert MissingPackageError("message", name="my_package").name == "my_package"


###################################
#     Tests for package_available #
###################################


def test_package_available_true() -> None:
    assert package_available("os")


def test_package_available_false() -> None:
    assert not package_available("missing_package")


def test_package_available_submodule_of_missing_package() -> None:
    assert not package_available("missing_package.submodule")


@pytest.mark.parametrize("error", [ImportError("x"), ValueError("x")])
def test_package_available_find_spec_error(error: Exception) -> None:
    with patch("feu.imports.package.find_spec", Mock(side_effect=error)):
        assert not package_available("my_package")


def test_package_available_does_not_import_the_package() -> None:
    with patch("feu.imports.package.importlib.import_module") as import_mock:
        package_available("os")
        import_mock.assert_not_called()


def test_is_package_available_is_an_alias() -> None:
    assert is_package_available is package_available


###################################
#     Tests for module_available  #
###################################


def test_module_available_true() -> None:
    assert module_available("os")


def test_module_available_missing_module() -> None:
    assert not module_available("missing.module")


def test_module_available_missing_submodule() -> None:
    assert not module_available("os.missing")


def test_module_available_import_error_is_not_logged(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger="feu.imports.package"):
        module_available("missing.module")
    assert caplog.messages == []


def test_module_available_broken_install_is_false() -> None:
    with patch(
        "feu.imports.package.importlib.import_module", Mock(side_effect=OSError("libfoo.so"))
    ):
        assert not module_available("my_module")


def test_module_available_broken_install_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    with (
        patch(
            "feu.imports.package.importlib.import_module", Mock(side_effect=OSError("libfoo.so"))
        ),
        caplog.at_level(logging.WARNING, logger="feu.imports.package"),
    ):
        module_available("my_module")
    assert caplog.messages == ["The module 'my_module' is installed but cannot be imported"]


def test_is_module_available_is_an_alias() -> None:
    assert is_module_available is module_available


##############################
#     Tests for check_package #
##############################


def test_check_package_with_package() -> None:
    check_package("os")


def test_check_package_without_package() -> None:
    with pytest.raises(
        MissingPackageError, match="'missing' package is required but not installed"
    ):
        check_package("missing")


def test_check_package_without_package_is_an_import_error() -> None:
    with pytest.raises(ImportError, match="'missing' package is required"):
        check_package("missing")


def test_check_package_without_package_is_a_runtime_error() -> None:
    with pytest.raises(RuntimeError, match="'missing' package is required"):
        check_package("missing")


def test_check_package_install_name() -> None:
    with pytest.raises(MissingPackageError, match=r"pip install my-distribution"):
        check_package("missing", install="my-distribution")


def test_check_package_broken_package_raises() -> None:
    with (
        patch(
            "feu.imports.package.importlib.import_module", Mock(side_effect=OSError("libfoo.so"))
        ),
        pytest.raises(MissingPackageError, match="'my_module' package is required"),
    ):
        check_package("my_module")


#########################################
#     Tests for raise_package_missing_error #
#########################################


def test_raise_package_missing_error_message() -> None:
    with pytest.raises(MissingPackageError) as exc_info:
        raise_package_missing_error("numpy")
    assert str(exc_info.value) == (
        "'numpy' package is required but not installed. "
        "You can install 'numpy' package with the command:\n\n"
        "pip install numpy\n\nor\n\nuv pip install numpy\n"
    )


def test_raise_package_missing_error_install_name() -> None:
    with pytest.raises(MissingPackageError) as exc_info:
        raise_package_missing_error("git", install="gitpython")
    assert "pip install gitpython\n" in str(exc_info.value)


def test_raise_package_missing_error_name() -> None:
    with pytest.raises(MissingPackageError) as exc_info:
        raise_package_missing_error("git", install="gitpython")
    assert exc_info.value.name == "git"
