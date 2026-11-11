r"""Contain functionalities to install packages with pip or compatible
package installers."""

from __future__ import annotations

__all__ = ["PipInstaller", "UvInstaller"]


from feu.install.pip.installer import PipInstaller, UvInstaller
