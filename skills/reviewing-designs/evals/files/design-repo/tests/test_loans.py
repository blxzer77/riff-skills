import sqlite3
import unittest
from datetime import date

from app.loans import lend


class LoanTest(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript("""
            CREATE TABLE books (id INTEGER PRIMARY KEY, on_loan INTEGER DEFAULT 0);
            CREATE TABLE loans (book_id INTEGER, member_id INTEGER, due TEXT);
            INSERT INTO books (id) VALUES (1);
        """)

    def test_due_in_three_weeks(self):
        self.assertEqual(lend(self.db, 1, 7, date(2026, 3, 1))["dueDate"], "2026-03-22")

    def test_integration_double_lend(self):
        lend(self.db, 1, 7, date(2026, 3, 1))
        with self.assertRaises(LookupError):
            lend(self.db, 1, 8, date(2026, 3, 2))
