"""
load.py
-------
Job: Take the CLEAN DataFrame from transform.py and write it into SQL Server.
"""

import pyodbc
import pandas as pd

# ---- Connection settings -----------------------------------------------
SERVER = r"NSEZIT1222LPT60\SA"
DATABASE_NAME = "OrdersETL"
DRIVER = "ODBC Driver 18 for SQL Server"


def get_connection(database: str, autocommit: bool = False) -> pyodbc.Connection:
    """Open a connection to SQL Server using Windows Authentication."""
    conn_str = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
        f"Encrypt=no;"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str, autocommit=autocommit)


def create_database_if_not_exists():
    """Connect to master and create OrdersETL if it doesn't exist yet."""
    conn = get_connection("master", autocommit=True)
    cursor = conn.cursor()

    cursor.execute(f"""
        IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{DATABASE_NAME}')
        CREATE DATABASE {DATABASE_NAME}
    """)

    print(f"[create_database_if_not_exists] Database '{DATABASE_NAME}' is ready")
    cursor.close()
    conn.close()


def create_table_if_not_exists(conn: pyodbc.Connection):
    """Create the orders table if it doesn't already exist."""
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='orders' AND xtype='U')
        CREATE TABLE orders (
            order_id INT PRIMARY KEY,
            customer_name NVARCHAR(100),
            country_code NVARCHAR(5),
            currency_code NVARCHAR(5),
            product NVARCHAR(100),
            quantity INT,
            unit_price_usd DECIMAL(10,2),
            order_date DATE,
            exchange_rate DECIMAL(12,6),
            total_local_price DECIMAL(12,2)
        )
    """)
    conn.commit()
    print("[create_table_if_not_exists] Table 'orders' is ready")
    cursor.close()


def load_orders(df: pd.DataFrame, conn: pyodbc.Connection):
    """Insert all rows from the clean DataFrame into the orders table."""
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO orders (
            order_id, customer_name, country_code, currency_code,
            product, quantity, unit_price_usd, order_date,
            exchange_rate, total_local_price
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    inserted = 0
    skipped = 0

    for _, row in df.iterrows():
        try:
            cursor.execute(insert_sql, (
                int(row["order_id"]),
                row["customer_name"],
                row["country_code"],
                row["currency_code"],
                row["product"],
                int(row["quantity"]),
                float(row["unit_price_usd"]),
                row["order_date"].date(),
                float(row["exchange_rate"]),
                float(row["total_local_price"]),
            ))
            inserted += 1
        except pyodbc.IntegrityError:
            skipped += 1

    conn.commit()
    print(f"[load_orders] Inserted {inserted} row(s), skipped {skipped} duplicate(s)")
    cursor.close()


def load(df: pd.DataFrame):
    """Run the full load process: create DB, create table, insert data."""
    create_database_if_not_exists()

    conn = get_connection(DATABASE_NAME)
    create_table_if_not_exists(conn)
    load_orders(df, conn)
    conn.close()


if __name__ == "__main__":
    from pathlib import Path
    from Extract import ectract_csv, extract_api
    from Transform import transform

    BASE_DIR = Path(__file__).resolve().parent
    csv_path = BASE_DIR / "orders.csv"

    raw_df = ectract_csv(csv_path)
    rates = extract_api()
    clean_df = transform(raw_df, rates)

    load(clean_df)
    print("[main] ETL pipeline complete!")