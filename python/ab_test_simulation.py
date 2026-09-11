"""
A/B test framework for the SLA recovery simulation.

Generalizes the original single-query, First-Class-only A/B test into a
reusable function that runs for any shipping mode and reports statistical
significance (two-proportion z-test) instead of just raw success rates.

Control group: orders kept at the current promised delivery window.
Variant group: orders given a realistic estimate (ceil of the mode's
observed average delivery time).

Usage:
    python python/ab_test_simulation.py --input "data/raw/DataCoSupplyChainDataset.csv"
"""

import argparse
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(__file__))
from prepare_dashboard_data import load_and_clean


def run_ab_test(df: pd.DataFrame, shipping_mode: str, alpha: float = 0.05) -> dict:
    subset = df[df["Shipping Mode"] == shipping_mode].copy()

    control_promise_days = subset["Days for shipment (scheduled)"].mean()
    variant_estimate_days = math.ceil(subset["Days for shipping (real)"].mean())

    subset["group"] = np.where(subset["Order Id"] % 2 == 0, "control", "variant")
    subset["success"] = np.where(
        subset["group"] == "control",
        subset["Days for shipping (real)"] <= subset["Days for shipment (scheduled)"],
        subset["Days for shipping (real)"] <= variant_estimate_days,
    )

    control = subset[subset["group"] == "control"]
    variant = subset[subset["group"] == "variant"]

    x1, n1 = control["success"].sum(), len(control)
    x2, n2 = variant["success"].sum(), len(variant)
    p1, p2 = x1 / n1, x2 / n2

    p_pool = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se if se > 0 else float("nan")
    p_value = 2 * (1 - stats.norm.cdf(abs(z))) if se > 0 else float("nan")

    return {
        "shipping_mode": shipping_mode,
        "control_promise_days": round(control_promise_days, 2),
        "variant_estimate_days": variant_estimate_days,
        "control_n": int(n1),
        "control_success_rate_pct": round(p1 * 100, 2),
        "variant_n": int(n2),
        "variant_success_rate_pct": round(p2 * 100, 2),
        "z_statistic": round(z, 3),
        "p_value": round(p_value, 6) if not math.isnan(p_value) else None,
        "significant_at_0.05": bool(p_value < alpha) if not math.isnan(p_value) else False,
    }


def run_all(df: pd.DataFrame) -> pd.DataFrame:
    modes = sorted(df["Shipping Mode"].unique())
    results = [run_ab_test(df, mode) for mode in modes]
    return pd.DataFrame(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/DataCoSupplyChainDataset.csv")
    parser.add_argument("--output", default="sql/exports/05_ab_test_simulation.csv")
    args = parser.parse_args()

    data = load_and_clean(args.input)
    results_df = run_all(data)
    results_df.to_csv(args.output, index=False)

    print(results_df.to_string(index=False))
    print(f"\nSaved: {args.output}")
