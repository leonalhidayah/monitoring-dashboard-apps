from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from data_preprocessor.utils import get_quarter_months
from database.db_connection import get_connection
from database.db_manager import (
    get_financial_summary,
    get_payments,
    get_vw_budget_ads_monitoring,
)

project_root = Path.cwd()


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

df_monitoring_budget_ads = get_vw_budget_ads_monitoring()
df_monitoring_budget_ads["nominal_aktual_ads"].fillna(0, inplace=True)
df_monitoring_budget_ads["status"] = np.where(
    df_monitoring_budget_ads["nominal_aktual_ads"]
    <= df_monitoring_budget_ads["nominal_budget_ads"],
    "Normal",
    "Over",
)
df_project = pd.read_csv(project_root / "data_preprocessor" / "project_mapping.csv")
df_monitoring_budget_ads = df_monitoring_budget_ads.merge(
    df_project, how="inner", on="nama_toko"
)
st.dataframe(df_monitoring_budget_ads)

df_payments = get_payments()
st.dataframe(df_payments)

st.metric(
    label="Estimasi Omset dari Total Pesanan", value=df_payments["total_pesanan"].sum()
)

df_finance_summary = get_financial_summary(1, "01-10-2025", "05-10-2025")
st.dataframe(df_finance_summary)
