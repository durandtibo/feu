r"""Contain the parser of a version request.

A version argument of ``feu`` is a *request*, not a version. It has three
forms: an exact version (``"2.4.0"``), a release-prefix wildcard
(``"2.4.*"``, ``"2.*"``) and the latest version (``""`` or ``None``).
"""

from __future__ import annotations

__all__ = ["VersionRequest", "parse_version_request"]

import re
from dataclasses import dataclass

from packaging.version import Version

_WILDCARD_PATTERN = re.compile(r"\d+(?:\.\d+)*\.\*")


@dataclass(frozen=True)
class VersionRequest:
    r"""Represent a version request.

    Use ``parse_version_request`` to create an instance.

    Args:
        text: The request as given, stripped: ``""`` (the latest),
            ``"2.4.*"`` (a wildcard) or ``"2.4.0"`` (an exact
            version).
        exact: The requested version for an exact request, otherwise
            ``None``.
        prefix: The release prefix for a wildcard request, e.g.
            ``(2, 4)`` for ``"2.4.*"``, otherwise ``None``.

    Example:
        ```pycon
        >>> from feu.version import parse_version_request
        >>> parse_version_request("2.4.*")
        VersionRequest(text='2.4.*', exact=None, prefix=(2, 4))

        ```
    """

    text: str
    exact: Version | None = None
    prefix: tuple[int, ...] | None = None

    def __str__(self) -> str:
        return self.text

    @property
    def is_latest(self) -> bool:
        r"""Indicate if the request is for the latest version.

        Returns:
            ``True`` for ``""`` (and ``None``), otherwise ``False``.

        Example:
            ```pycon
            >>> from feu.version import parse_version_request
            >>> parse_version_request("").is_latest
            True
            >>> parse_version_request("2.*").is_latest
            False

            ```
        """
        return self.text == ""

    def matches(self, version: Version) -> bool:
        r"""Indicate if a version satisfies the request.

        An exact request matches the version that is equal to it. A
        wildcard request matches the versions whose release segment,
        padded with zeros, starts with the prefix; pre-releases never
        match a wildcard. The latest request matches every version.

        Args:
            version: The version to check.

        Returns:
            ``True`` if ``version`` satisfies the request, otherwise
                ``False``.

        Example:
            ```pycon
            >>> from packaging.version import Version
            >>> from feu.version import parse_version_request
            >>> request = parse_version_request("2.4.*")
            >>> request.matches(Version("2.4.17"))
            True
            >>> request.matches(Version("2.40"))
            False

            ```
        """
        if self.exact is not None:
            return version == self.exact
        if self.prefix is not None:
            if version.is_prerelease:
                return False
            return _padded_release(version, len(self.prefix))[: len(self.prefix)] == self.prefix
        return True

    def entirely_below(self, version: Version) -> bool:
        r"""Indicate if every version that satisfies the request is
        lower than a version.

        Args:
            version: The version to compare with.

        Returns:
            ``True`` if the whole request lies below ``version``. A
                wildcard that straddles ``version`` (e.g. ``"2.*"``
                and ``2.2.2``) and the latest request are not
                entirely below.

        Example:
            ```pycon
            >>> from packaging.version import Version
            >>> from feu.version import parse_version_request
            >>> parse_version_request("2.1.*").entirely_below(Version("2.2.2"))
            True
            >>> parse_version_request("2.*").entirely_below(Version("2.2.2"))
            False

            ```
        """
        if self.exact is not None:
            return self.exact < version
        if self.prefix is not None:
            return self.prefix < _padded_release(version, len(self.prefix))[: len(self.prefix)]
        return False


def _padded_release(version: Version, length: int) -> tuple[int, ...]:
    r"""Get the release segment of a version, padded with zeros.

    Args:
        version: The version.
        length: The minimum length of the returned tuple.

    Returns:
        The release segment of ``version``, padded with zeros to at
            least ``length`` items.
    """
    release = version.release
    return release + (0,) * (length - len(release))


def parse_version_request(text: str | None) -> VersionRequest:
    r"""Parse a version request.

    Args:
        text: The request. ``None``, ``""`` and a blank string request
            the latest version. A PEP 440 version (e.g. ``"2.4.0"``)
            is an exact request. A wildcard is digits and dots
            followed by one trailing ``".*"`` (e.g. ``"2.4.*"``,
            ``"2.*"``).

    Returns:
        The parsed request.

    Raises:
        ValueError: If ``text`` contains a ``*`` but is not a valid
            wildcard (e.g. ``"*"``, ``"2.*.1"``, ``"2.4*"``,
            ``"2.4.0rc1.*"``, ``"1!2.*"``).
        packaging.version.InvalidVersion: If ``text`` is not a valid
            PEP 440 version (``InvalidVersion`` is a ``ValueError``).

    Example:
        ```pycon
        >>> from feu.version import parse_version_request
        >>> parse_version_request("2.4.0")
        VersionRequest(text='2.4.0', exact=<Version('2.4.0')>, prefix=None)
        >>> parse_version_request("2.*")
        VersionRequest(text='2.*', exact=None, prefix=(2,))
        >>> parse_version_request(None)
        VersionRequest(text='', exact=None, prefix=None)

        ```
    """
    stripped = (text or "").strip()
    if not stripped:
        return VersionRequest(text="")
    if "*" in stripped:
        if _WILDCARD_PATTERN.fullmatch(stripped) is None:
            msg = (
                f"invalid version wildcard {stripped!r}: a wildcard is digits and dots "
                "followed by one trailing '.*', e.g. '2.4.*'"
            )
            raise ValueError(msg)
        return VersionRequest(
            text=stripped, prefix=tuple(int(part) for part in stripped[:-2].split("."))
        )
    return VersionRequest(text=stripped, exact=Version(stripped))
