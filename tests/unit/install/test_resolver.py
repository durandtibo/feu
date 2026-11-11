from __future__ import annotations

import pytest
from packaging.requirements import Requirement
from packaging.version import Version

from feu.install import get_default_resolver_registry, register_resolver
from feu.install.resolver import (
    NUMPY2_MIN_VERSION,
    _is_within,
    default_resolver,
    jax_resolver,
    numpy2_resolver,
    resolve,
)
from feu.utils.package import PackageSpec
from feu.utils.registry import Registry
from feu.version.request import parse_version_request


def _strings(requirements: list[Requirement]) -> list[str]:
    return [str(requirement) for requirement in requirements]


##################################
#     Tests for default_resolver #
##################################


def test_default_resolver() -> None:
    assert _strings(default_resolver(PackageSpec("my_package", "1.2.3"))) == ["my_package==1.2.3"]


def test_default_resolver_no_version() -> None:
    assert _strings(default_resolver(PackageSpec("my_package"))) == ["my_package"]


def test_default_resolver_extras() -> None:
    assert _strings(default_resolver(PackageSpec("my_package", "1.2.3", ["dev"]))) == [
        "my_package[dev]==1.2.3"
    ]


def test_default_resolver_wildcard() -> None:
    assert _strings(default_resolver(PackageSpec("my_package", "1.*"))) == ["my_package==1.*"]


##################################
#     Tests for numpy2_resolver  #
##################################


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        pytest.param("1.2.3", ["my_package==1.2.3"], id="min_version"),
        pytest.param("1.3.0", ["my_package==1.3.0"], id="above"),
        pytest.param("1.2.2", ["my_package==1.2.2", "numpy<2.0.0"], id="below"),
        pytest.param("", ["my_package"], id="latest"),
        pytest.param("1.2.*", ["my_package==1.2.*"], id="wildcard_straddles"),
        pytest.param("1.*", ["my_package==1.*"], id="wildcard_major_straddles"),
        pytest.param("1.1.*", ["my_package==1.1.*", "numpy<2.0.0"], id="wildcard_below"),
        pytest.param("0.*", ["my_package==0.*", "numpy<2.0.0"], id="wildcard_major_below"),
        pytest.param("1.3.*", ["my_package==1.3.*"], id="wildcard_above"),
    ],
)
def test_numpy2_resolver(version: str, expected: list[str]) -> None:
    assert _strings(numpy2_resolver("1.2.3")(PackageSpec("my_package", version))) == expected


def test_numpy2_resolver_none_version() -> None:
    assert _strings(numpy2_resolver("1.2.3")(PackageSpec("my_package", None))) == ["my_package"]


def test_numpy2_resolver_extras() -> None:
    assert _strings(numpy2_resolver("1.2.3")(PackageSpec("my_package", "1.2.2", ["dev"]))) == [
        "my_package[dev]==1.2.2",
        "numpy<2.0.0",
    ]


def test_numpy2_resolver_invalid_min_version() -> None:
    with pytest.raises(ValueError, match="not-a-version"):
        numpy2_resolver("not-a-version")


def test_numpy2_resolver_wildcard_with_a_larger_min_version() -> None:
    assert _strings(numpy2_resolver("2.0.0")(PackageSpec("my_package", "1.*"))) == [
        "my_package==1.*",
        "numpy<2.0.0",
    ]


########################################
#     Tests for NUMPY2_MIN_VERSION     #
########################################


def test_numpy2_min_version() -> None:
    assert dict(NUMPY2_MIN_VERSION) == {
        "matplotlib": "3.8.4",
        "pandas": "2.2.2",
        "pyarrow": "16.0",
        "scikit-learn": "1.4.2",
        "scipy": "1.13.0",
        "torch": "2.3.0",
        "xarray": "2024.6.0",
    }


def test_numpy2_min_version_is_read_only() -> None:
    with pytest.raises(TypeError, match="does not support item assignment"):
        NUMPY2_MIN_VERSION["numpy"] = "1.0"  # ty: ignore[invalid-assignment]


@pytest.mark.parametrize(("package", "min_version"), sorted(NUMPY2_MIN_VERSION.items()))
def test_default_registry_resolver_at_the_min_version(package: str, min_version: str) -> None:
    assert _strings(resolve(PackageSpec(package, min_version))) == [f"{package}=={min_version}"]


@pytest.mark.parametrize(
    ("package", "version"),
    [
        ("matplotlib", "3.8.3"),
        ("pandas", "2.2.1"),
        ("pyarrow", "15.0.2"),
        ("scikit-learn", "1.4.1"),
        ("scipy", "1.12.0"),
        ("torch", "2.2.2"),
        ("xarray", "2024.5.0"),
    ],
)
def test_default_registry_resolver_below_the_min_version(package: str, version: str) -> None:
    assert _strings(resolve(PackageSpec(package, version))) == [
        f"{package}=={version}",
        "numpy<2.0.0",
    ]


##############################
#     Tests for jax_resolver #
##############################


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        pytest.param("0.4.26", ["jax==0.4.26", "jaxlib==0.4.26"], id="numpy2_support"),
        pytest.param("0.5.0", ["jax==0.5.0", "jaxlib==0.5.0"], id="above"),
        pytest.param("0.4.25", ["jax==0.4.25", "jaxlib==0.4.25", "numpy<2.0.0"], id="below_numpy2"),
        pytest.param(
            "0.4.9",
            ["jax==0.4.9", "jaxlib==0.4.9", "numpy<2.0.0", "ml_dtypes<=0.2.0"],
            id="ml_dtypes_lower",
        ),
        pytest.param(
            "0.4.11",
            ["jax==0.4.11", "jaxlib==0.4.11", "numpy<2.0.0", "ml_dtypes<=0.2.0"],
            id="ml_dtypes_upper",
        ),
        pytest.param(
            "0.4.12", ["jax==0.4.12", "jaxlib==0.4.12", "numpy<2.0.0"], id="after_ml_dtypes"
        ),
        pytest.param(
            "0.4.8", ["jax==0.4.8", "jaxlib==0.4.8", "numpy<2.0.0"], id="before_ml_dtypes"
        ),
        pytest.param("", ["jax"], id="latest"),
        pytest.param("0.4.*", ["jax==0.4.*", "jaxlib==0.4.*"], id="wildcard_straddles"),
        pytest.param("0.3.*", ["jax==0.3.*", "jaxlib==0.3.*", "numpy<2.0.0"], id="wildcard_below"),
        pytest.param(
            "0.4.10.*",
            ["jax==0.4.10.*", "jaxlib==0.4.10.*", "numpy<2.0.0", "ml_dtypes<=0.2.0"],
            id="wildcard_in_ml_dtypes_range",
        ),
    ],
)
def test_jax_resolver(version: str, expected: list[str]) -> None:
    assert _strings(jax_resolver(PackageSpec("jax", version))) == expected


def test_jax_resolver_extras() -> None:
    assert _strings(jax_resolver(PackageSpec("jax", "0.4.26", ["cpu"]))) == [
        "jax[cpu]==0.4.26",
        "jaxlib==0.4.26",
    ]


def test_jax_resolver_none_version() -> None:
    assert _strings(jax_resolver(PackageSpec("jax", None))) == ["jax"]


#############################
#     Tests for _is_within  #
#############################


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("2.5.0", True, id="exact_inside"),
        pytest.param("2.0.0", True, id="exact_lower_bound"),
        pytest.param("3.0.0", False, id="exact_upper_bound"),
        pytest.param("1.9.0", False, id="exact_below"),
        pytest.param("2.5.*", True, id="wildcard_inside"),
        pytest.param("2.*", True, id="wildcard_major_inside"),
        pytest.param("1.*", False, id="wildcard_below"),
        pytest.param("3.*", False, id="wildcard_above"),
        pytest.param("", False, id="latest"),
    ],
)
def test_is_within(text: str, expected: bool) -> None:
    assert (
        _is_within(parse_version_request(text), lower=Version("2.0.0"), upper=Version("3.0.0"))
        == expected
    )


########################################
#     Tests for the resolver registry  #
########################################


def test_get_default_resolver_registry_keys() -> None:
    assert get_default_resolver_registry().keys() == [
        "jax",
        "matplotlib",
        "pandas",
        "pyarrow",
        "scikit-learn",
        "scipy",
        "torch",
        "xarray",
    ]


def test_get_default_resolver_registry_is_a_registry() -> None:
    assert isinstance(get_default_resolver_registry(), Registry)


def test_get_default_resolver_registry_is_a_singleton() -> None:
    assert get_default_resolver_registry() is get_default_resolver_registry()


@pytest.mark.parametrize("name", ["Scikit-Learn", "scikit_learn", "SCIKIT.LEARN"])
def test_get_default_resolver_registry_canonical_names(name: str) -> None:
    assert name in get_default_resolver_registry()


def test_get_default_resolver_registry_does_not_know_sklearn() -> None:
    assert "sklearn" not in get_default_resolver_registry()


def test_register_resolver() -> None:
    register_resolver("My_Package", default_resolver)
    assert get_default_resolver_registry().find("my-package") is default_resolver


def test_register_resolver_exist_ok_false() -> None:
    with pytest.raises(RuntimeError, match="already registered for the key 'torch'"):
        register_resolver("torch", default_resolver)


def test_register_resolver_exist_ok_true() -> None:
    register_resolver("torch", default_resolver, exist_ok=True)
    assert get_default_resolver_registry().find("torch") is default_resolver


def test_register_resolver_is_used_by_resolve() -> None:
    register_resolver("my_package", lambda package: [Requirement(f"{package.name}>=1")])
    assert _strings(resolve(PackageSpec("My-Package", "2"))) == ["My-Package>=1"]


####################################
#     Tests for resolve            #
####################################


def test_resolve_unknown_package_uses_the_default_resolver() -> None:
    assert _strings(resolve(PackageSpec("my_package", "1.2.3"))) == ["my_package==1.2.3"]


@pytest.mark.parametrize("name", ["Scikit-Learn", "scikit_learn"])
def test_resolve_canonical_package_name(name: str) -> None:
    assert _strings(resolve(PackageSpec(name, "1.4.1"))) == [f"{name}==1.4.1", "numpy<2.0.0"]


def test_resolve_sklearn_is_not_scikit_learn() -> None:
    assert _strings(resolve(PackageSpec("sklearn", "1.4.1"))) == ["sklearn==1.4.1"]


def test_resolve_custom_registry() -> None:
    registry = Registry("dependency resolver")
    registry.register("pandas", lambda _: [Requirement("custom")])
    assert _strings(resolve(PackageSpec("pandas", "2.0.0"), registry)) == ["custom"]


def test_resolve_custom_registry_has_no_default_resolvers() -> None:
    assert _strings(resolve(PackageSpec("pandas", "2.0.0"), Registry("dependency resolver"))) == [
        "pandas==2.0.0"
    ]


def test_resolve_wildcard_straddling_the_min_version_has_no_pin() -> None:
    assert _strings(resolve(PackageSpec("pandas", "2.*"))) == ["pandas==2.*"]


def test_resolve_wildcard_below_the_min_version_has_a_pin() -> None:
    assert _strings(resolve(PackageSpec("pandas", "2.1.*"))) == ["pandas==2.1.*", "numpy<2.0.0"]
