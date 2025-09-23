r"""Contain functionalities to install packages with pip or compatible
package installers."""

from __future__ import annotations

__all__ = [
    "PipInstaller",
    "PipxInstaller",
    "UvInstaller",
]


from feu.install.pip.installer import PipInstaller, PipxInstaller, UvInstaller
