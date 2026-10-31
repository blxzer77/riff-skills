import unittest

from src.gateway import Actor, Request, get_profile


class GatewayTests(unittest.TestCase):
    def test_owner_can_read_profile(self):
        cache = FakeCache()
        profiles = FakeProfiles({"u-1": {"name": "Ada"}})
        response = get_profile(Request("u-1", Actor("u-1")), cache, profiles)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, {"name": "Ada"})


class FakeCache:
    def __init__(self):
        self.values = {}

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value, ttl):
        self.values[key] = value


class FakeProfiles:
    def __init__(self, values):
        self.values = values

    def fetch(self, user_id):
        return self.values[user_id]
