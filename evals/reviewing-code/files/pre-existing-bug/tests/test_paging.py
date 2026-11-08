import unittest

from src.paging import page_count


class PageCountTests(unittest.TestCase):
    def test_exact_multiple(self):
        self.assertEqual(page_count(40, 20), 2)
