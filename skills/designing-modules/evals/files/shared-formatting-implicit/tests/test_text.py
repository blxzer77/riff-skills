import unittest

from shop import billing, orders


class TextTests(unittest.TestCase):
    def test_invoice_text(self):
        self.assertEqual(billing.invoice_text("X9", 123456), "Invoice for X9: EUR 1,234.56")

    def test_confirmation_mentions_items(self):
        self.assertIn("2 item(s)", orders.confirmation_text("X9", 2, 5000))
