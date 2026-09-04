import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    r"SERVER=NSEZIT1222LPT60\SA;"
    "DATABASE=OrdersETL;"
    "Trusted_Connection=yes;"
    "Encrypt=no;"
    "TrustServerCertificate=yes;"
)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM orders")
print("Total rows in orders table:", cursor.fetchone()[0])

cursor.execute("SELECT TOP 5 * FROM orders")
for row in cursor.fetchall():
    print(row)

conn.close()