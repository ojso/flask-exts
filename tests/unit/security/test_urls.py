import pytest

from flask_exts.security.urls import safe_redirect_target


@pytest.mark.parametrize(
    "target",
    [
        "https://example.com",
        "//example.com",
        "///example.com",
        "/\\example.com",
        "/%2f%2fexample.com",
        "http://[",
    ],
)
def test_safe_redirect_target_rejects_external_or_malformed_urls(target):
    assert safe_redirect_target(target, "/fallback") == "/fallback"


def test_safe_redirect_target_allows_local_path_and_query():
    target = "/user/index/?page=2"
    assert safe_redirect_target(target, "/fallback") == target
