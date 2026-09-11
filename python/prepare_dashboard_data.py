"""
Prepare Tableau-ready data extracts from the raw DataCo Supply Chain dataset.

Runs the same 5-stage audit logic used in notebooks/supply-chain-audit.ipynb,
but instead of printing results, writes each stage's output to sql/exports/
as a CSV, plus a PII-stripped order-level extract to data/processed/ that
Tableau connects to directly for the interactive dashboard.

Usage:
    python python/prepare_dashboard_data.py --input "data/raw/DataCoSupplyChainDataset.csv"
"""

import argparse
import pandas as pd
import numpy as np

PII_COLUMNS = [
    "Customer Email", "Customer Password", "Customer Fname", "Customer Lname",
    "Customer Street", "Customer Zipcode", "Order Zipcode", "Product Description",
    "Product Image",
]


def load_and_clean(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="ISO-8859-1")
    df = df.dropna(subset=[
        "Days for shipping (real)", "Days for shipment (scheduled)", "Customer Id",
    ])
    df = df[df["Order Item Total"] > 0]
    df = df.drop_duplicates(subset=["Order Id", "Order Item Id"])

    df["latency_gap_days"] = df["Days for shipping (real)"] - df["Days for shipment (scheduled)"]
    df["strict_success"] = (df["Days for shipping (real)"] <= df["Days for shipment (scheduled)"]).astype(int)
    df["buffered_success"] = (df["Days for shipping (real)"] <= df["Days for shipment (scheduled)"] + 1).astype(int)
    df["order_month"] = pd.to_datetime(df["order date (DateOrders)"], errors="coerce").dt.to_period("M").astype(str)
    return df


def customer_segment(spend: float) -> str:
    if spend > 500:
        return "Priority (High Spend)"
    if spend >= 200:
        return "Standard (Mid Spend)"
    return "Casual (Low Spend)"


def build_exports(df: pd.DataFrame, sql_exports_dir: str, processed_dir: str) -> None:
    # 1. Data integrity audit
    integrity = pd.DataFrame([{
        "total_rows": len(df),
        "unique_orders": df["Order Id"].nunique(),
        "price_errors": int((df["Order Item Total"] <= 0).sum()),
        "extreme_delays": int((df["Days for shipping (real)"] > 10).sum()),
    }])
    integrity.to_csv(f"{sql_exports_dir}/01_data_integrity_audit.csv", index=False)

    # 2. SLA performance (strict vs buffered) by shipping mode
    sla = df.groupby("Shipping Mode").agg(
        order_volume=("Order Id", "count"),
        strict_success_rate=("strict_success", lambda s: round(s.mean() * 100, 2)),
        buffered_success_rate=("buffered_success", lambda s: round(s.mean() * 100, 2)),
    ).reset_index().sort_values("order_volume", ascending=False)
    sla.to_csv(f"{sql_exports_dir}/02_sla_performance_by_shipping_mode.csv", index=False)

    # 3. Fulfillment funnel / latency gap
    funnel = df.groupby("Shipping Mode").agg(
        promised_days=("Days for shipment (scheduled)", "mean"),
        actual_days=("Days for shipping (real)", "mean"),
        avg_latency_gap=("latency_gap_days", "mean"),
    ).round(2).reset_index().sort_values("avg_latency_gap", ascending=False)
    funnel.to_csv(f"{sql_exports_dir}/03_latency_gap_by_shipping_mode.csv", index=False)

    # 4. Customer segmentation (value at risk)
    user_value = df.groupby("Customer Id").agg(
        total_spent=("Order Item Total", "sum"),
        delay_rate=("Late_delivery_risk", "mean"),
    ).reset_index()
    user_value["customer_segment"] = user_value["total_spent"].apply(customer_segment)
    segmentation = user_value.groupby("customer_segment").agg(
        user_count=("Customer Id", "count"),
        avg_failure_pct=("delay_rate", lambda s: round(s.mean() * 100, 2)),
    ).reset_index().sort_values("avg_failure_pct", ascending=False)
    segmentation.to_csv(f"{sql_exports_dir}/04_customer_segmentation.csv", index=False)

    # 5. A/B test simulation (First Class only)
    fc = df[df["Shipping Mode"] == "First Class"].copy()
    fc["test_group"] = np.where(fc["Order Id"] % 2 == 0, "Control (1-Day Promise)", "Variant (4-Day Estimate)")
    fc["success"] = np.where(
        (fc["Order Id"] % 2 != 0) & (fc["Days for shipping (real)"] <= 4), 1.0,
        np.where(
            (fc["Order Id"] % 2 == 0) & (fc["Days for shipping (real)"] <= fc["Days for shipment (scheduled)"]),
            1.0, 0.0,
        ),
    )
    ab_test = fc.groupby("test_group")["success"].mean().mul(100).round(2).reset_index()
    ab_test.columns = ["test_group", "fulfillment_success_rate_pct"]
    ab_test.to_csv(f"{sql_exports_dir}/05_ab_test_simulation.csv", index=False)

    # 6. Regional breakdown (bonus, for dashboard map)
    regional = df.groupby(["Market", "Order Region", "Order Country"]).agg(
        order_volume=("Order Id", "count"),
        avg_latency_gap=("latency_gap_days", "mean"),
        sla_breach_rate=("Late_delivery_risk", lambda s: round(s.mean() * 100, 2)),
        total_sales=("Sales", "sum"),
    ).round(2).reset_index().sort_values("order_volume", ascending=False)
    regional.to_csv(f"{sql_exports_dir}/06_regional_summary.csv", index=False)

    # 7. Monthly trend (bonus, for dashboard trend line)
    trend = df.groupby(["order_month", "Shipping Mode"]).agg(
        order_volume=("Order Id", "count"),
        avg_latency_gap=("latency_gap_days", "mean"),
        sla_breach_rate=("Late_delivery_risk", lambda s: round(s.mean() * 100, 2)),
    ).round(2).reset_index().sort_values(["order_month", "Shipping Mode"])
    trend.to_csv(f"{sql_exports_dir}/07_monthly_trend.csv", index=False)

    # 8. PII-stripped order-level extract for the interactive Tableau dashboard
    keep_cols = [c for c in df.columns if c not in PII_COLUMNS]
    order_level = df[keep_cols].copy()
    order_level.to_csv(f"{processed_dir}/orders_clean.csv", index=False)

    print("Exports written:")
    print(f"  {sql_exports_dir}/01_data_integrity_audit.csv")
    print(f"  {sql_exports_dir}/02_sla_performance_by_shipping_mode.csv")
    print(f"  {sql_exports_dir}/03_latency_gap_by_shipping_mode.csv")
    print(f"  {sql_exports_dir}/04_customer_segmentation.csv")
    print(f"  {sql_exports_dir}/05_ab_test_simulation.csv")
    print(f"  {sql_exports_dir}/06_regional_summary.csv")
    print(f"  {sql_exports_dir}/07_monthly_trend.csv")
    print(f"  {processed_dir}/orders_clean.csv  ({len(order_level):,} rows, {len(keep_cols)} cols)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/DataCoSupplyChainDataset.csv")
    parser.add_argument("--sql-exports-dir", default="sql/exports")
    parser.add_argument("--processed-dir", default="data/processed")
    args = parser.parse_args()

    data = load_and_clean(args.input)
    build_exports(data, args.sql_exports_dir, args.processed_dir)
