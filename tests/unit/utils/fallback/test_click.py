from __future__ import annotations

from feu.utils.fallback.click import click


def test_click_group() -> None:
    @click.group()
    def my_function() -> None: ...


def test_click_command() -> None:
    @click.command()
    def my_function() -> None: ...


def test_click_command_and_option() -> None:
    @click.command()
    @click.option("-n", "--pkg-name", "pkg_name")
    @click.option("-v", "--pkg-version", "pkg_version")
    def my_function() -> None: ...
