from app.domain import extract_host, is_domain_allowed


def test_extract_host_parses_origin():
    assert extract_host("https://sub.example.com:3000") == "sub.example.com"


def test_is_domain_allowed_matches_exact_and_subdomains():
    allowed = ["example.com", "foo.bar"]
    assert is_domain_allowed("example.com", allowed)
    assert is_domain_allowed("blog.example.com", allowed)
    assert is_domain_allowed("api.foo.bar", allowed)
    assert not is_domain_allowed("notexample.com", allowed)
