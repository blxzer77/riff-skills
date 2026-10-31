from urllib.parse import urlparse

ALLOWED_HOSTS = {"hooks.example.com"}


def parse_target(payload):
    url = payload.get("callback_url")
    if not isinstance(url, str):
        raise ValueError("callback_url is required")
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("callback host is not allowed")
    return url


def send_webhook(payload, http_client):
    target = parse_target(payload)
    return http_client.post(target, json=payload, timeout=5)
