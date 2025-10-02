from datetime import datetime

import pandas as pd
import streamlit as st

from database import db_manager
from database.db_connection import get_connection


def get_quarter_months(month: int):
    """Helper: menentukan bulan dalam kuartal"""
    if month in [1, 2, 3]:
        return ["January", "February", "March"], 1
    elif month in [4, 5, 6]:
        return ["April", "May", "June"], 2
    elif month in [7, 8, 9]:
        return ["July", "August", "September"], 3
    else:
        return ["October", "November", "December"], 4


st.header("Aktualisasi Budget Plan (Per Kuartal)")

# Tentukan kuartal berjalan
now = datetime.now()
months, q = get_quarter_months(now.month)
tahun = now.year

st.write(f"Saat ini berada di **Kuartal {q} {tahun}** ({', '.join(months)})")

# --- Query total omset dari DB ---
conn = get_connection()
query = f"""
    SELECT SUM(akrual_basis) AS total_omset
    FROM finance_omset
    WHERE EXTRACT(YEAR FROM tanggal) = {tahun}
      AND EXTRACT(QUARTER FROM tanggal) = {q}
"""
df_omset = pd.read_sql(query, conn)
conn.close()

total_omset = df_omset["total_omset"].iloc[0]


st.markdown(f"**Total Omset Aktualisasi:** Rp {total_omset:,.0f}")
st.markdown(f"**Total Omset Bulanan (per bulan):** Rp {(total_omset / 3):,.0f}")

st.dataframe(db_manager.get_finance_omset())

st.dataframe(db_manager.get_finance_budget_ads())
st.dataframe(db_manager.get_finance_budget_non_ads())
