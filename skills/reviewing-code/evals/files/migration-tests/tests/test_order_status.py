import sqlite3
import unittest


class OrderStatusMigrationTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE orders (id INTEGER, paid_at TEXT)")

    def apply_migration(self):
        self.db.execute(
            "ALTER TABLE orders ADD COLUMN status TEXT NOT NULL DEFAULT 'pending'"
        )
        self.db.execute(
            "UPDATE orders SET status = 'paid' WHERE paid_at IS NOT NULL"
        )

    def test_new_orders_have_pending_status(self):
        self.db.execute("INSERT INTO orders (id, paid_at) VALUES (1, NULL)")
        self.apply_migration()
        row = self.db.execute("SELECT status FROM orders WHERE id = 1").fetchone()
        self.assertEqual(row[0], "pending")

    def test_paid_orders_are_marked_paid(self):
        self.db.execute("INSERT INTO orders (id, paid_at) VALUES (2, '2026-01-02')")
        self.apply_migration()
        row = self.db.execute("SELECT status FROM orders WHERE id = 2").fetchone()
        self.assertEqual(row[0], "paid")
