import pandas as pd
import requests

def ectract_csv(path: str) -> pd.DataFrame:
    df=pd.read_csv(path)
    print(f"[ectract_csv] loaded with {len(df)} rows from the {path}")
    return df

def extract_api(base_currency: str="USD") -> dict:
    """call the api and get the exchange rates in dictionary"""
    url=f"https://open.er-api.com/v6/latest/{base_currency}"
    response= requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()     
    if data.get("result") != "success":
        raise ValueError("Exchange rate API did not return a success result")

    print(f"[extract_api] Retrieved rates for {len(data['rates'])} currencies")
    return data["rates"]

if __name__ == "__main__":
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent
    csv_path = BASE_DIR / "orders.csv"   # adjust if it's in a subfolder

    orders_df = ectract_csv(csv_path)
    print(orders_df.head())

    rates = extract_api()
    print({k: rates[k] for k in ["INR", "EUR", "GBP", "JPY"]})