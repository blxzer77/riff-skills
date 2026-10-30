import unittest
from datetime import date

from invoices.due import due_date


class DueDateTest(unittest.TestCase):
    def test_net30_adds_thirty_days(self):
        self.assertEqual(due_date(date(2026, 3, 2), "net30"), date(2026, 4, 1))

    def test_net15_adds_fifteen_days(self):
        self.assertEqual(due_date(date(2026, 3, 2), "net15"), date(2026, 3, 17))
