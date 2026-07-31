# noqa: INP001
r"""Script to discover and update the default package/Python-version
compatibility constraints in ``src/feu/compat/defaults.py``."""

from __future__ import annotations

import logging
import re
import subprocess
from pathlib import Path

from feu.compat.discovery import DEFAULT_PYTHON_VERSIONS, discover_compat

logger: logging.Logger = logging.getLogger(__name__)


# Matches one entry in DEFAULT_COMPAT: optional leading comment lines
# (each starting with ``#``), followed by ``"pkg_name": { ... },``.
_ENTRY_PATTERN = re.compile(
    r"(?P<comments>(?:^ {4}#[^\n]*\n)*)^ {4}\"(?P<name>[^\"]+)\": \{\n(?s:.*?)\n {4}\},\n",
    re.MULTILINE,
)


def parse_packages(source: str) -> list[tuple[str, str]]:
    r"""Extract the ordered list of ``(comments, package_name)``
    currently in ``DEFAULT_COMPAT``.

    Args:
        source: The content of ``defaults.py``.

    Returns:
        A list of ``(comments, package_name)`` tuples, in file order.
    """
    return [(m.group("comments"), m.group("name")) for m in _ENTRY_PATTERN.finditer(source)]


def render_entry(comments: str, name: str, compat: dict[str, dict[str, str | None]]) -> str:
    r"""Render a single ``DEFAULT_COMPAT`` entry as Python source.

    Args:
        comments: The comment lines to keep above the entry.
        name: The package name.
        compat: The mapping of Python version to ``{"min": ..., "max": ...}``.

    Returns:
        The rendered entry, including trailing newline.
    """
    lines = [comments] if comments else []
    lines.append(f'    "{name}": {{\n')
    for python_version in DEFAULT_PYTHON_VERSIONS[::-1]:
        bounds = compat.get(python_version, {"min": None, "max": None})
        lines.append(f'        "{python_version}": {bounds!r},\n')
    lines.append("    },\n")
    return "".join(lines)


def generate_defaults_source(source: str) -> str:
    r"""Regenerate the ``DEFAULT_COMPAT`` dict body from freshly
    discovered data, keeping the rest of the file untouched.

    Args:
        source: The current content of ``defaults.py``.

    Returns:
        The updated file content.
    """
    packages = parse_packages(source)
    if not packages:
        msg = "Could not find any package entry in DEFAULT_COMPAT"
        raise RuntimeError(msg)

    entries = []
    for comments, name in packages:
        logger.info(f"Discovering compatibility for {name}...")
        compat = discover_compat(name)
        entries.append(render_entry(comments, name, compat))

    start = source.index("DEFAULT_COMPAT")
    body_start = source.index("{\n", start) + len("{\n")
    body_end = source.index("\n}\n", body_start) + 1

    return source[:body_start] + "".join(entries) + source[body_end:]


def main() -> None:
    r"""Discover the latest package/Python-version compatibility
    constraints and update ``defaults.py``."""
    path = Path(__file__).parent.parent.joinpath("src/feu/compat/defaults.py")
    source = path.read_text()
    updated = generate_defaults_source(source)
    logger.info(f"Writing updated compatibility defaults to {path}")
    path.write_text(updated)
    subprocess.run(["black", str(path)], check=True)  # noqa: S603, S607


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
