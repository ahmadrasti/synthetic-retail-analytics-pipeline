from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20260825
DAYS = 45
LOCATIONS = ["L01", "L02", "L03"]
CATEGORIES = ["Category A", "Category B", "Category C", "Category D"]
SEGMENTS = ["consumer", "business"]


def main() -> None:
    rng = np.random.default_rng(SEED)
    output_dir = Path(__file__).resolve().parents[1] / "data" / "synthetic"
    output_dir.mkdir(parents=True, exist_ok=True)
    dates = pd.date_range(end="2026-08-25", periods=DAYS, freq="D")

    transactions: list[dict[str, object]] = []
    transaction_number = 1
    for date in dates:
        for location in LOCATIONS:
            for _ in range(int(rng.integers(12, 22))):
                category = rng.choice(CATEGORIES)
                quantity = int(rng.integers(1, 7))
                unit_price = float(rng.integers(8, 26))
                transactions.append(
                    {
                        "transaction_id": f"T{transaction_number:06d}",
                        "date": date.date().isoformat(),
                        "location_id": location,
                        "customer_segment": rng.choice(SEGMENTS, p=[0.82, 0.18]),
                        "product_category": category,
                        "quantity": quantity,
                        "net_revenue": round(quantity * unit_price, 2),
                        "status": rng.choice(["completed", "cancelled"], p=[0.97, 0.03]),
                    }
                )
                transaction_number += 1

    inventory: list[dict[str, object]] = []
    for date in dates:
        for location in LOCATIONS:
            for category in CATEGORIES:
                received = int(rng.integers(45, 96))
                waste = int(rng.integers(0, 7))
                sold = int(rng.integers(max(1, received // 2), received - waste + 1))
                inventory.append(
                    {
                        "date": date.date().isoformat(),
                        "location_id": location,
                        "product_category": category,
                        "received_qty": received,
                        "sold_qty": sold,
                        "waste_qty": waste,
                    }
                )

    calendar = pd.DataFrame({"date": dates.date})
    calendar["date"] = calendar["date"].astype(str)
    calendar["weekday"] = dates.day_name()
    calendar["is_weekend"] = (dates.weekday >= 5).astype(int)
    calendar["is_holiday"] = 0

    pd.DataFrame(transactions).to_csv(output_dir / "transactions.csv", index=False)
    pd.DataFrame(inventory).to_csv(output_dir / "inventory.csv", index=False)
    calendar.to_csv(output_dir / "calendar.csv", index=False)
    print(f"Synthetic data written to {output_dir}")


if __name__ == "__main__":
    main()

