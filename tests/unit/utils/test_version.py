import pytest

from feu.utils.version import get_python_major_minor


@pytest.fixture(autouse=True)
def _reset() -> None:
    get_python_major_minor.cache_clear()


############################################
#     Tests for get_python_major_minor     #
############################################


def test_get_python_major_minor() -> None:
    isinstance(get_python_major_minor(), str)
