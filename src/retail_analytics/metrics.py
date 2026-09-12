from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


TRANSACTION_COLUMNS = {
    "transaction_id",
    "date",
    "location_id",
    "customer_segment",
    "product_category",
    "quantity",
    "net_revenue",
    "status",
}
INVENTORY_COLUMNS = {
    "date",
    "location_id",
    "product_category",
    "received_qty",
    "sold_qty",
    "waste_qty",
}


def _require_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{name} is missing required columns: {', '.join(missing)}")


def prepare_transactions(frame: pd.DataFrame) -> pd.DataFrame:
    _require_columns(frame, TRANSACTION_COLUMNS, "transactions")
    data = frame.copy()
    data["date"] = pd.to_datetime(data["date"], errors="raise").dt.normalize()
    for column in ("quantity", "net_revenue"):
        data[column] = pd.to_numeric(data[column], errors="raise")
    data = data.loc[data["status"].eq("completed")].copy()
    if (data["quantity"] <= 0).any() or (data["net_revenue"] < 0).any():
        raise ValueError("completed transactions require positive quantity and non-negative revenue")
    return data


def prepare_inventory(frame: pd.DataFrame) -> pd.DataFrame:
    _require_columns(frame, INVENTORY_COLUMNS, "inventory")
    data = frame.copy()
    data["date"] = pd.to_datetime(data["date"], errors="raise").dt.normalize()
    for column in ("received_qty", "sold_qty", "waste_qty"):
        data[column] = pd.to_numeric(data[column], errors="raise")
        if (data[column] < 0).any():
            raise ValueError(f"{column} cannot be negative")
    return data


def daily_sales(frame: pd.DataFrame, dimensions: Sequence[str] = ()) -> pd.DataFrame:
    data = prepare_transactions(frame)
    group_columns = ["date", *dimensions]
    result = (
        data.groupby(group_columns, dropna=False)
        .agg(
            order_count=("transaction_id", "nunique"),
            units=("quantity", "sum"),
            net_revenue=("net_revenue", "sum"),
        )
        .reset_index()
    )
    result["average_order_size"] = result["units"] / result["order_count"]
    return result


def daily_inventory(frame: pd.DataFrame, dimensions: Sequence[str] = ()) -> pd.DataFrame:
    data = prepare_inventory(frame)
    group_columns = ["date", *dimensions]
    result = (
        data.groupby(group_columns, dropna=False)
        .agg(
            received_qty=("received_qty", "sum"),
            sold_qty=("sold_qty", "sum"),
            waste_qty=("waste_qty", "sum"),
        )
        .reset_index()
    )
    result["waste_rate_pct"] = np.where(
        result["received_qty"] > 0,
        result["waste_qty"] / result["received_qty"] * 100,
        np.nan,
    )
    return result


def snapshot_with_comparisons(
    daily: pd.DataFrame,
    report_date: str | pd.Timestamp,
    dimensions: Sequence[str] = (),
) -> pd.DataFrame:
    report_day = pd.Timestamp(report_date).normalize()
    metrics = [column for column in daily.columns if column not in {"date", *dimensions}]
    current = daily.loc[daily["date"].eq(report_day)].copy()
    if current.empty:
        raise ValueError(f"no data is available for report date {report_day.date()}")

    previous = daily.loc[daily["date"].eq(report_day - pd.Timedelta(days=1))].copy()
    history = daily.loc[
        daily["date"].between(report_day - pd.Timedelta(days=7), report_day - pd.Timedelta(days=1))
    ].copy()

    key_columns = list(dimensions)
    if key_columns:
        previous = previous[key_columns + metrics].rename(columns={m: f"{m}_previous" for m in metrics})
        history = history.groupby(key_columns, dropna=False)[metrics].mean().reset_index()
        history = history.rename(columns={m: f"{m}_avg7" for m in metrics})
        result = current.merge(previous, on=key_columns, how="left").merge(history, on=key_columns, how="left")
    else:
        result = current.copy()
        for metric in metrics:
            result[f"{metric}_previous"] = previous[metric].iloc[0] if not previous.empty else np.nan
            result[f"{metric}_avg7"] = history[metric].mean() if not history.empty else np.nan

    for metric in metrics:
        for suffix in ("previous", "avg7"):
            baseline = result[f"{metric}_{suffix}"]
            result[f"{metric}_change_vs_{suffix}_pct"] = np.where(
                baseline.notna() & baseline.ne(0),
                (result[metric] - baseline) / baseline * 100,
                np.nan,
            )
    return result

