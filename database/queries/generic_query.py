import pandas as pd
from sqlalchemy import text

from database.db_connection import get_engine


def get_table_data(
    table_name: str, columns: list = None, order_by: str = None
) -> pd.DataFrame:
    engine = get_engine()
    cols = ", ".join(columns) if columns else "*"
    query = f"SELECT {cols} FROM {table_name}"
    if order_by:
        query += f" ORDER BY {order_by}"

    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)
