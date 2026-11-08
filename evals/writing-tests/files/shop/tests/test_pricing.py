import unittest

from shop.pricing import Coupon, subtotal, total

MUG = {"sku": "mug", "price": 12.0, "qty": 1}
POSTER = {"sku": "poster", "price": 20.0, "qty": 1}


class PricingTest(unittest.TestCase):
    def test_subtotal_sums_price_times_quantity(self):
        self.assertEqual(subtotal([MUG, {**POSTER, "qty": 2}]), 52.0)

    def test_small_order_pays_flat_shipping(self):
        self.assertEqual(total([MUG]), 16.99)

    def test_free_shipping_coupon_removes_shipping(self):
        self.assertEqual(total([MUG], [Coupon("FREESHIP", "free_shipping")]), 12.0)

    def test_percent_coupon_discounts_items(self):
        self.assertEqual(total([POSTER], [Coupon("SAVE10", "percent", 10)]), 22.99)


if __name__ == "__main__":
    unittest.main()
