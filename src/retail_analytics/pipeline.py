from __future__ import annotations

from pathlib import Path

import pandas as pd

from .insights import deterministic_summary, llm_summary
from .metrics import daily_inventory, daily_sales, snapshot_with_comparisons


def run_pipeline(data_dir: Path, output_dir: Path, report_date: str | None, use_llm: bool = False) -> dict[str, Path]:
    transactions = pd.read_csv(data_dir / "transactions.csv")
    inventory = pd.read_csv(data_dir / "inventory.csv")
    calendar = pd.read_csv(data_dir / "calendar.csv")

    calendar_columns = {"date", "weekday", "is_weekend", "is_holiday"}
    missing_calendar_columns = sorted(calendar_columns.difference(calendar.columns))
    if missing_calendar_columns:
        raise ValueError(f"calendar is missing required columns: {', '.join(missing_calendar_columns)}")
    calendar["date"] = pd.to_datetime(calendar["date"], errors="raise").dt.normalize()

    parsed_dates = pd.to_datetime(transactions["date"], errors="raise")
    selected_date = report_date or parsed_dates.max().date().isoformat()
    selected_day = pd.Timestamp(selected_date).normalize()
    calendar_row = calendar.loc[calendar["date"].eq(selected_day)].copy()
    if calendar_row.empty:
        raise ValueError(f"report date {selected_day.date()} is missing from calendar.csv")

    sales_overall = snapshot_with_comparisons(daily_sales(transactions), selected_date)
    inventory_overall = snapshot_with_comparisons(daily_inventory(inventory), selected_date)
    overall = sales_overall.merge(inventory_overall, on="date", how="outer")
    overall = overall.merge(calendar_row[["date", "weekday", "is_weekend", "is_holiday"]], on="date", how="left")

    reports = {
        "daily_overall": overall,
        "sales_by_location_customer": snapshot_with_comparisons(
            daily_sales(transactions, ["location_id", "customer_segment"]),
            selected_date,
            ["location_id", "customer_segment"],
        ),
        "sales_by_location_product": snapshot_with_comparisons(
            daily_sales(transactions, ["location_id", "product_category"]),
            selected_date,
            ["location_id", "product_category"],
        ),
        "inventory_by_location_product": snapshot_with_comparisons(
            daily_inventory(inventory, ["location_id", "product_category"]),
            selected_date,
            ["location_id", "product_category"],
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for name, report in reports.items():
        path = output_dir / f"{name}.csv"
        report.to_csv(path, index=False)
        paths[name] = path

    kpis = overall.iloc[0].where(pd.notna(overall.iloc[0]), None).to_dict()
    summary = llm_summary(kpis) if use_llm else deterministic_summary(kpis)
    summary_path = output_dir / "management_summary.txt"
    summary_path.write_text(summary, encoding="utf-8")
    paths["management_summary"] = summary_path
    return paths
