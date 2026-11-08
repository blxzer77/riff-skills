import unittest

from src.previews import fetch_status


class FakeResponse:
    def __init__(self, state):
        self._state = state

    def json(self):
        return {"state": self._state}


class FakeHttp:
    def __init__(self):
        self.urls = []

    def get(self, url, timeout):
        self.urls.append(url)
        return FakeResponse("delivered")


class StatusTests(unittest.TestCase):
    def test_status_path_is_escaped(self):
        http = FakeHttp()
        fetch_status(http, {"message_id": "../admin"})
        self.assertEqual(
            http.urls, ["https://status.internal.example.com/messages/..%2Fadmin"]
        )
