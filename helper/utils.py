import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "olist_ecommerce.db")


def run_query(title, sql, export_csv=False, filename=None, preview_rows=10):
    conn = sqlite3.connect(DB_PATH)

    print(f"\n{'='*55}")
    print(title)
    print(f"{'='*55}")

    df = pd.read_sql_query(sql, conn)

    if export_csv:
        if filename is None:
            raise ValueError("Please provide a filename when export_csv=True.")

        df.to_csv(f"exports/{filename}", index=False)

        print(f"Successfully exported {len(df):,} rows to exports/{filename}\n")
        print(f"Preview (First {preview_rows} rows):")
        print(df.head(preview_rows).to_string(index=False))
    else:
        print(df.to_string(index=False))

    conn.close()


def load_table(table_name: str) -> pd.DataFrame:
    """
    Load a SQLite table into a pandas DataFrame.

    Parameters
    ----------
    table_name : str
        Name of the table in the SQLite database.

    Returns
    -------
    pd.DataFrame
        DataFrame containing all rows from the specified table.
    """
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql_query(query, conn)


def convert_datetime_columns(df, columns):
    """
    Convert specified columns in a DataFrame to datetime.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the datetime columns.

    columns : list
        List of column names to convert.

    Returns
    -------
    pandas.DataFrame
        DataFrame with converted datetime columns.
    """

    df = df.copy()

    for column in columns:
        df[column] = pd.to_datetime(df[column])

    return df


def flag_outliers(df, column, mild_k=1.5, extreme_k=3.0):
    """
    Flags outliers in a numeric column using the IQR method,
    with two severity tiers.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the column.
    column : str
        Name of the numeric column.
    mild_k : float, default 1.5
        IQR multiplier for the "mild" outlier boundary (standard convention).
    extreme_k : float, default 3.0
        IQR multiplier for the "extreme" outlier boundary (standard convention
        for far outliers).

    Returns
    -------
    pandas.DataFrame
        A copy of the DataFrame with an additional column
        '<column>_outlier_severity' containing one of:
        'normal', 'mild', or 'extreme'.
    """
    new_df = df.copy()
    Q1 = new_df[column].quantile(0.25)
    Q3 = new_df[column].quantile(0.75)
    IQR = Q3 - Q1

    mild_lower, mild_upper = Q1 - mild_k * IQR, Q3 + mild_k * IQR
    extreme_lower, extreme_upper = Q1 - extreme_k * IQR, Q3 + extreme_k * IQR

    def classify(x):
        if x < extreme_lower or x > extreme_upper:
            return "extreme"
        elif x < mild_lower or x > mild_upper:
            return "mild"
        return "normal"

    severity_col = f"{column}_outlier_severity"
    new_df[severity_col] = new_df[column].apply(classify)

    counts = new_df[severity_col].value_counts()
    print("=" * 80)
    print(f"OUTLIERS INVESTIGATION OF:\n{column}")
    print("=" * 80)
    print(f"Mild bounds    : [{mild_lower:.2f}, {mild_upper:.2f}]")
    print(f"Extreme bounds : [{extreme_lower:.2f}, {extreme_upper:.2f}]")
    print(f"Mild outliers  : {counts.get('mild', 0)}")
    print(f"Extreme outliers: {counts.get('extreme', 0)}")
    print("=" * 80)
    print(f"OUTLIERS INVESTIGATION OF:\n{column} COMPLETED.")
    print("=" * 80)

    return new_df


def validate_order_timestamps(orders_df):
    """
    Validate timestamp consistency against order status.

    Checks performed:
        1. Delivered orders with missing critical timestamps.
        2. Canceled orders that have a customer delivery date.
        3. Order status distribution for each missing timestamp column.

    Parameters
    ----------
    orders_df : pandas.DataFrame
        Orders DataFrame with datetime columns already converted.

    Returns
    -------
    None
        Prints a validation summary to the console.
    """

    timestamp_cols = [
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
    ]

    print("=" * 80)
    print("ORDER TIMESTAMP VALIDATION")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # Check 1: Delivered orders with missing timestamps
    # -------------------------------------------------------------------------
    print("\n[1] Delivered Orders with Missing Timestamps")

    for col in timestamp_cols:
        suspicious = orders_df.loc[
            (orders_df["order_status"] == "delivered") & (orders_df[col].isna()),
            ["order_id", "order_status", col],
        ]

        print(f"\n• {col}")
        print(f"Suspicious rows: {len(suspicious)}")

        if not suspicious.empty:
            print(suspicious)

    # -------------------------------------------------------------------------
    # Check 2: Canceled orders with customer delivery dates
    # -------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[2] Canceled Orders with Customer Delivery Dates")

    unexpected = orders_df.loc[
        (orders_df["order_status"] == "canceled")
        & (orders_df["order_delivered_customer_date"].notna()),
        ["order_id", "order_status", "order_delivered_customer_date"],
    ]

    print(f"Unexpected rows: {len(unexpected)}")

    if not unexpected.empty:
        print(unexpected)

    # -------------------------------------------------------------------------
    # Check 3: Status distribution for missing timestamps
    # -------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[3] Order Status Distribution for Missing Timestamp Values")

    for col in timestamp_cols:
        print(f"\nMissing '{col}' by order status:")

        status_counts = (
            orders_df.loc[orders_df[col].isna(), "order_status"]
            .value_counts()
            .sort_index()
        )

        print(status_counts)

    print("\n" + "=" * 80)
    print("Timestamp validation completed.")
    print("=" * 80)
