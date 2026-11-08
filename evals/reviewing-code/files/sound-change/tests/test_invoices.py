import unittest
from decimal import Decimal

from src.invoices import invoice_total


class InvoiceTotalTests(unittest.TestCase):
    def test_sums_lines(self):
        lines = [(Decimal("2.50"), 2), (Decimal("1.25"), 4)]
        self.assertEqual(invoice_total(lines), Decimal("10.00"))
