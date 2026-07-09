import pandas as pd
import sqlite3
from pathlib import Path

conn = sqlite3.connect("olist_ecommerce.db")

csv_folder = Path("data")

for csv_file in csv_folder.glob("*.csv"):
    table_name = csv_file.stem

    df = pd.read_csv(csv_file)

    df.to_sql(table_name, conn, if_exists="replace", index=False)

    print(f"Imported {csv_file.name} -> {table_name}")

conn.close()
