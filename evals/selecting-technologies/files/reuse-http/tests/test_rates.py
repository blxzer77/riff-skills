import unittest

import httpx

from pricing import exchange_rate


def handler(request: httpx.Request) -> httpx.Response:
    assert request.url.params["base"] == "EUR"
    return httpx.Response(200, json={"rates": {"USD": 1.08}})


class RatesTest(unittest.TestCase):
    def test_exchange_rate(self):
        client = httpx.Client(transport=httpx.MockTransport(handler))
        self.assertEqual(exchange_rate(client, "EUR", "USD"), 1.08)


if __name__ == "__main__":
    unittest.main()
