import httpx

RATES_URL = "https://rates.example/v1/latest"


def exchange_rate(client: httpx.Client, base: str, quote: str) -> float:
    resp = client.get(RATES_URL, params={"base": base, "symbols": quote}, timeout=10)
    resp.raise_for_status()
    return float(resp.json()["rates"][quote])


def default_client() -> httpx.Client:
    return httpx.Client(headers={"user-agent": "pricing/1.0"})
