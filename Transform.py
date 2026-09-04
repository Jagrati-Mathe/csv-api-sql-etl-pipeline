"""
transform.py
------------
Job: Take the RAW DataFrame + RAW rates dict from extract.py,
and turn them into ONE clean, unified DataFrame ready for SQL Server.
"""

import pandas as pd


def clean_customer_names(df: pd.DataFrame) -> pd.DataFrame:
    missing_count = df["customer_name"].isna().sum()
    df["customer_name"] = df["customer_name"].fillna("Unknown")
    print(f"[clean_customer_names] Filled {missing_count} missing name(s) with 'Unknown'")
    return df


def fix_dates(df: pd.DataFrame) -> pd.DataFrame:
    df["order_date"] = pd.to_datetime(df["order_date"])
    print("[fix_dates] Converted order_date to datetime")
    return df


def attach_exchange_rates(df: pd.DataFrame, rates: dict) -> pd.DataFrame:
    df["exchange_rate"] = df["currency_code"].map(rates)
    missing = df["exchange_rate"].isna().sum()
    if missing > 0:
        print(f"[attach_exchange_rates] WARNING: {missing} row(s) had no matching rate")
    print("[attach_exchange_rates] Attached exchange rates")
    return df


def calculate_local_total(df: pd.DataFrame) -> pd.DataFrame:
    df["total_local_price"] = (
        df["quantity"] * df["unit_price_usd"] * df["exchange_rate"]
    ).round(2)
    print("[calculate_local_total] Calculated total_local_price")
    return df


def transform(df: pd.DataFrame, rates: dict) -> pd.DataFrame:
    df = clean_customer_names(df)
    df = fix_dates(df)
    df = attach_exchange_rates(df, rates)
    df = calculate_local_total(df)
    return df


if __name__ == "__main__":
    from pathlib import Path
    from Extract import ectract_csv, extract_api

    BASE_DIR = Path(__file__).resolve().parent
    csv_path = BASE_DIR / "orders.csv"   # adjust if your CSV is elsewhere

    raw_df = ectract_csv(csv_path)
    rates = extract_api()

    clean_df = transform(raw_df, rates)
    print(clean_df.head(10))
    print(clean_df.dtypes)