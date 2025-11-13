from urllib.parse import urlparse


def extract_host(origin: str) -> str:
    parsed = urlparse(origin)
    return parsed.hostname or ""


def is_domain_allowed(host: str, allowed_domains: list[str]) -> bool:
    host = host.lower()
    for domain in allowed_domains:
        domain_lower = domain.lower()
        if host == domain_lower or host.endswith(f".{domain_lower}"):
            return True
    return False
