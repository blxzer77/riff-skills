import unittest


class PaymentTests(unittest.TestCase):
    def test_settling_invoice_marks_order_paid(self):
        from shop import billing, orders

        orders.place_order("P1", 1200)
        self.assertEqual(billing.invoice_for("P1").amount_cents, 1200)
        billing.settle_invoice("P1")
        self.assertTrue(orders.get_order("P1").paid)
