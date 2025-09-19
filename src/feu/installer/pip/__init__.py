r"""Contain functionalities to install packages with pip or compatible
package installers."""

from __future__ import annotations

__all__ = ["BaseDependencyResolver", "DependencyResolver"]

from feu.installer.pip.resolver import BaseDependencyResolver, DependencyResolver
