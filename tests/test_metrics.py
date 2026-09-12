import unittest

import pandas as pd

from retail_analytics.metrics import daily_inventory, daily_sales, snapshot_with_comparisons


class MetricTests(unittest.TestCase):
    def test_average_order_size_uses_distinct_orders(self) -> None:
        frame = pd.DataFrame(
            [
                ["T1", "2026-01-01", "L01", "consumer", "A", 2, 20, "completed"],
                ["T1", "2026-01-01", "L01", "consumer", "B", 3, 30, "completed"],
                ["T2", "2026-01-01", "L01", "business", "A", 1, 10, "completed"],
                ["T3", "2026-01-01", "L01", "consumer", "A", 9, 90, "cancelled"],
            ],
            columns=[
                "transaction_id", "date", "location_id", "customer_segment",
                "product_category", "quantity", "net_revenue", "status",
            ],
        )
        result = daily_sales(frame).iloc[0]
        self.assertEqual(result["units"], 6)
        self.assertEqual(result["order_count"], 2)
        self.assertEqual(result["average_order_size"], 3)

    def test_waste_rate_uses_aggregated_quantities(self) -> None:
        frame = pd.DataFrame(
            [
                ["2026-01-01", "L01", "A", 100, 80, 5],
                ["2026-01-01", "L02", "A", 50, 40, 5],
            ],
            columns=["date", "location_id", "product_category", "received_qty", "sold_qty", "waste_qty"],
        )
        result = daily_inventory(frame).iloc[0]
        self.assertAlmostEqual(result["waste_rate_pct"], 10 / 150 * 100)

    def test_snapshot_calculates_previous_change(self) -> None:
        daily = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
                "units": [100, 120],
            }
        )
        result = snapshot_with_comparisons(daily, "2026-01-02").iloc[0]
        self.assertEqual(result["units_previous"], 100)
        self.assertAlmostEqual(result["units_change_vs_previous_pct"], 20)


if __name__ == "__main__":
    unittest.main()
