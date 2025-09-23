from __future__ import annotations

from feu.install.pip.command import (
    PipCommandGenerator,
    PipxCommandGenerator,
    UvCommandGenerator,
)

#########################################
#     Tests for PipCommandGenerator     #
#########################################


def test_pip_command_generator_repr() -> None:
    assert repr(PipCommandGenerator()).startswith("PipCommandGenerator(")


def test_pip_command_generator_str() -> None:
    assert str(PipCommandGenerator()).startswith("PipCommandGenerator(")


def test_pip_command_generator_equal_true() -> None:
    assert PipCommandGenerator().equal(PipCommandGenerator())


def test_pip_command_generator_equal_false() -> None:
    assert not PipCommandGenerator().equal(PipxCommandGenerator())


def test_pip_command_generator_generate() -> None:
    assert PipCommandGenerator().generate(["numpy==2.0.0"]) == "pip install numpy==2.0.0"


def test_pip_command_generator_generate_multiple_packages() -> None:
    assert (
        PipCommandGenerator().generate(["numpy==2.0.0", "pandas>=2.0,<3.0"])
        == "pip install numpy==2.0.0 pandas>=2.0,<3.0"
    )


def test_pip_command_generator_generate_with_args() -> None:
    assert (
        PipCommandGenerator().generate(["numpy==2.0.0"], args="-U") == "pip install -U numpy==2.0.0"
    )


##########################################
#     Tests for PipxCommandGenerator     #
##########################################


def test_pipx_command_generator_repr() -> None:
    assert repr(PipxCommandGenerator()).startswith("PipxCommandGenerator(")


def test_pipx_command_generator_str() -> None:
    assert str(PipxCommandGenerator()).startswith("PipxCommandGenerator(")


def test_pipx_command_generator_equal_true() -> None:
    assert PipxCommandGenerator().equal(PipxCommandGenerator())


def test_pipx_command_generator_equal_false() -> None:
    assert not PipxCommandGenerator().equal(PipCommandGenerator())


def test_pipx_command_generator_generate() -> None:
    assert PipxCommandGenerator().generate(["numpy==2.0.0"]) == "pipx install numpy==2.0.0"


def test_pipx_command_generator_generate_multiple_packages() -> None:
    assert (
        PipxCommandGenerator().generate(["numpy==2.0.0", "pandas>=2.0,<3.0"])
        == "pipx install numpy==2.0.0 pandas>=2.0,<3.0"
    )


def test_pipx_command_generator_generate_with_args() -> None:
    assert (
        PipxCommandGenerator().generate(["numpy==2.0.0"], args="-U")
        == "pipx install -U numpy==2.0.0"
    )


########################################
#     Tests for UvCommandGenerator     #
########################################


def test_uv_command_generator_repr() -> None:
    assert repr(UvCommandGenerator()).startswith("UvCommandGenerator(")


def test_uv_command_generator_str() -> None:
    assert str(UvCommandGenerator()).startswith("UvCommandGenerator(")


def test_uv_command_generator_equal_true() -> None:
    assert UvCommandGenerator().equal(UvCommandGenerator())


def test_uv_command_generator_equal_false() -> None:
    assert not UvCommandGenerator().equal(PipCommandGenerator())


def test_uv_command_generator_generate() -> None:
    assert UvCommandGenerator().generate(["numpy==2.0.0"]) == "uv pip install numpy==2.0.0"


def test_uv_command_generator_generate_multiple_packages() -> None:
    assert (
        UvCommandGenerator().generate(["numpy==2.0.0", "pandas>=2.0,<3.0"])
        == "uv pip install numpy==2.0.0 pandas>=2.0,<3.0"
    )


def test_uv_command_generator_generate_with_args() -> None:
    assert (
        UvCommandGenerator().generate(["numpy==2.0.0"], args="-U")
        == "uv pip install -U numpy==2.0.0"
    )
