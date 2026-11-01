import unittest

from shop import orders, support


class RefundTests(unittest.TestCase):
    def test_partial_refunds_accumulate(self):
        orders.place_order("A1", 1000)
        self.assertEqual(support.issue_goodwill_refund("A1", 300), 300)
        self.assertEqual(support.issue_goodwill_refund("A1", 200), 500)

    def test_refund_cannot_exceed_total(self):
        orders.place_order("A2", 500)
        with self.assertRaises(ValueError):
            support.issue_goodwill_refund("A2", 600)
