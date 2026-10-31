import unittest

from src.webhook import parse_target


class WebhookTests(unittest.TestCase):
    def test_rejects_private_network_target(self):
        with self.assertRaises(ValueError):
            parse_target({"callback_url": "http://169.254.169.254/latest/meta-data"})

    def test_accepts_configured_https_host(self):
        self.assertEqual(
            parse_target({"callback_url": "https://hooks.example.com/events"}),
            "https://hooks.example.com/events",
        )
