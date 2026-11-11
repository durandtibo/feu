from __future__ import annotations

import pytest
from packaging.version import InvalidVersion, Version

from feu.version.request import VersionRequest, _padded_release, parse_version_request

#######################################
#     Tests for parse_version_request #
#######################################


@pytest.mark.parametrize("text", [None, "", " ", "   "])
def test_parse_version_request_latest(text: str | None) -> None:
    assert parse_version_request(text) == VersionRequest(text="")


def test_parse_version_request_exact() -> None:
    assert parse_version_request("2.4.0") == VersionRequest(text="2.4.0", exact=Version("2.4.0"))


def test_parse_version_request_exact_prerelease() -> None:
    assert parse_version_request("2.4.0rc1") == VersionRequest(
        text="2.4.0rc1", exact=Version("2.4.0rc1")
    )


def test_parse_version_request_exact_epoch() -> None:
    assert parse_version_request("1!2.0") == VersionRequest(text="1!2.0", exact=Version("1!2.0"))


def test_parse_version_request_exact_is_stripped() -> None:
    assert parse_version_request(" 2.4.0 ").text == "2.4.0"


def test_parse_version_request_wildcard_minor() -> None:
    assert parse_version_request("2.4.*") == VersionRequest(text="2.4.*", prefix=(2, 4))


def test_parse_version_request_wildcard_major() -> None:
    assert parse_version_request("2.*") == VersionRequest(text="2.*", prefix=(2,))


def test_parse_version_request_wildcard_patch() -> None:
    assert parse_version_request("2.4.1.*") == VersionRequest(text="2.4.1.*", prefix=(2, 4, 1))


@pytest.mark.parametrize("text", ["*", "2.*.1", "2.4.*.dev", "2.4*", ".*", "2.4.0rc1.*", "1!2.*"])
def test_parse_version_request_invalid_wildcard(text: str) -> None:
    with pytest.raises(ValueError, match="a wildcard is digits and dots followed by one trailing"):
        parse_version_request(text)


@pytest.mark.parametrize("text", ["*", "2.*.1", "2.4*"])
def test_parse_version_request_invalid_wildcard_is_not_invalid_version(text: str) -> None:
    with pytest.raises(ValueError, match="invalid version wildcard") as exc_info:
        parse_version_request(text)
    assert not isinstance(exc_info.value, InvalidVersion)


def test_parse_version_request_invalid_version() -> None:
    with pytest.raises(InvalidVersion, match="not-a-version"):
        parse_version_request("not-a-version")


###################################
#     Tests for VersionRequest    #
###################################


def test_version_request_str() -> None:
    assert str(parse_version_request("2.4.*")) == "2.4.*"


def test_version_request_is_latest_true() -> None:
    assert parse_version_request("").is_latest


@pytest.mark.parametrize("text", ["2.4.0", "2.*"])
def test_version_request_is_latest_false(text: str) -> None:
    assert not parse_version_request(text).is_latest


@pytest.mark.parametrize("version", ["2.4", "2.4.0", "2.4.17", "2.4.0.post1"])
def test_version_request_matches_wildcard_true(version: str) -> None:
    assert parse_version_request("2.4.*").matches(Version(version))


@pytest.mark.parametrize("version", ["2.40", "2.5", "2.3.9", "3.4.0", "1.4"])
def test_version_request_matches_wildcard_false(version: str) -> None:
    assert not parse_version_request("2.4.*").matches(Version(version))


def test_version_request_matches_wildcard_zero_padding() -> None:
    assert parse_version_request("2.*").matches(Version("2"))


def test_version_request_matches_wildcard_prefix_longer_than_release() -> None:
    assert parse_version_request("2.0.0.*").matches(Version("2"))


def test_version_request_matches_wildcard_prefix_longer_than_release_false() -> None:
    assert not parse_version_request("2.0.1.*").matches(Version("2"))


@pytest.mark.parametrize("version", ["2.4.0rc1", "2.4.0a1", "2.4.0.dev1"])
def test_version_request_matches_wildcard_prerelease_false(version: str) -> None:
    assert not parse_version_request("2.4.*").matches(Version(version))


def test_version_request_matches_exact_true() -> None:
    assert parse_version_request("2.4.0").matches(Version("2.4"))


def test_version_request_matches_exact_false() -> None:
    assert not parse_version_request("2.4.0").matches(Version("2.4.1"))


@pytest.mark.parametrize("version", ["0.1", "2.4.0", "99.0rc1"])
def test_version_request_matches_latest(version: str) -> None:
    assert parse_version_request("").matches(Version(version))


@pytest.mark.parametrize(
    ("text", "version", "expected"),
    [
        pytest.param("2.1.*", "2.2.2", True, id="wildcard_below"),
        pytest.param("2.*", "2.2.2", False, id="wildcard_straddles"),
        pytest.param("2.2.*", "2.2.2", False, id="wildcard_same_minor"),
        pytest.param("2.3.*", "2.2.2", False, id="wildcard_above"),
        pytest.param("1.*", "2.2.2", True, id="wildcard_major_below"),
        pytest.param("2.2.1.*", "2.2.2", True, id="wildcard_longer_prefix_below"),
        pytest.param("2.2.2.1.*", "2.2.2", False, id="wildcard_longer_than_release"),
        pytest.param("2.1.0", "2.2.2", True, id="exact_below"),
        pytest.param("2.2.2", "2.2.2", False, id="exact_equal"),
        pytest.param("2.3.0", "2.2.2", False, id="exact_above"),
        pytest.param("", "2.2.2", False, id="latest"),
    ],
)
def test_version_request_entirely_below(text: str, version: str, expected: bool) -> None:
    assert parse_version_request(text).entirely_below(Version(version)) == expected


##################################
#     Tests for _padded_release  #
##################################


def test_padded_release_pads_with_zeros() -> None:
    assert _padded_release(Version("2.4"), 4) == (2, 4, 0, 0)


def test_padded_release_does_not_truncate() -> None:
    assert _padded_release(Version("2.4.1"), 2) == (2, 4, 1)
