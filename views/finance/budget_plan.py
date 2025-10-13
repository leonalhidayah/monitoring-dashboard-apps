from datetime import datetime

import pandas as pd
import streamlit as st

from data_preprocessor.utils import get_quarter_months
from database import db_manager
from views.style import load_css

# --- PAGE CONFIG ---
st.set_page_config(layout="wide")
load_css()

st.header("🎯 Generator Budget Plan Kuartalan (Per Project)")

# --- 1. PILIH PERIODE ---
now = datetime.now()
months, q = get_quarter_months(now.month)
tahun = now.year
st.info(
    f"Anda sedang membuat budget plan untuk **Kuartal {q} {tahun}** ({', '.join(months)})."
)

# --- 2. AMBIL DAFTAR PROJECT ---
try:
    projects_df = db_manager.get_dim_projects()
    project_list = projects_df["project_name"].tolist()
except Exception as e:
    st.error(f"Gagal memuat daftar project dari database: {e}")
    st.stop()

if not project_list:
    st.warning(
        "Tidak ada data project yang ditemukan. Mohon tambahkan project terlebih dahulu."
    )
    st.stop()

# --- 3. PILIH PROJECT ---
selected_project = st.selectbox("Pilih Project", options=project_list)
st.divider()

st.subheader(f"⚙️ Konfigurasi Budget: {selected_project}")
config = {"ratios": {}}

# --- 4. INPUT TARGET OMSET ---
target_val = st.number_input(
    "Target Omset Kuartalan (Rp)",
    min_value=0,
    step=1_000_000,
    format="%d",
    key=f"target_{selected_project}",
)
config["target_quarter"] = target_val
if target_val > 0:
    st.caption(f"↳ Pratinjau: **Rp {target_val:,.0f}**")

st.markdown("---")
st.markdown("**Alokasi Rasio Budget (%)**")

# --- 5. INPUT RASIO ---
col1, col2 = st.columns(2)
with col1:
    config["ratios"]["HPP"] = st.number_input("HPP (%)", value=20.0, step=1.0)
    config["ratios"]["Biaya Admin"] = st.number_input(
        "Biaya Admin (%)", value=20.0, step=1.0
    )
    config["ratios"]["Biaya Marketing (Ads)"] = st.number_input(
        "Biaya Marketing (Ads) (%)", value=25.0, step=1.0
    )
    config["ratios"]["Biaya Marketing (Non Ads)"] = st.number_input(
        "Biaya Marketing (Non Ads) (%)", value=5.0, step=1.0
    )
with col2:
    config["ratios"]["Personal Expense"] = st.number_input(
        "Personal Expense (%)", value=10.0, step=1.0
    )
    config["ratios"]["Administrasi dan Umum"] = st.number_input(
        "Administrasi dan Umum (%)", value=5.0, step=1.0
    )
    config["ratios"]["Estimasi Ebit/Net Profit"] = st.number_input(
        "Estimasi Ebit/Net Profit (%)", value=15.0, step=1.0
    )

# --- 6. VALIDASI ---
total_ratio = sum(config["ratios"].values())
if total_ratio != 100:
    st.error(f"❌ Total Rasio harus 100% (saat ini: {total_ratio:.2f}%)")
else:
    st.success(f"✅ Total Rasio: {total_ratio:.2f}%")

st.divider()

# --- 7. GENERATE & SIMPAN ---
if st.button(
    "🚀 Generate & Simpan Budget Plan", use_container_width=True, type="primary"
):
    if total_ratio != 100:
        st.error("Gagal menyimpan: total rasio belum 100%.")
        st.stop()

    if target_val <= 0:
        st.warning("Isi target omset kuartalan terlebih dahulu.")
        st.stop()

    # Hitung target per bulan
    target_monthly = target_val / 3

    data_rows = [
        [selected_project, "Target Omset", 0, target_val] + [target_monthly] * 3
    ]
    for param, ratio in config["ratios"].items():
        row = [selected_project, param, ratio, target_val * (ratio / 100)] + [
            target_monthly * (ratio / 100)
        ] * 3
        data_rows.append(row)

    df = pd.DataFrame(
        data_rows,
        columns=["Project", "Parameter", "Target Rasio", "Target Kuartal"] + months,
    )
    df["Tahun"] = tahun
    df["Kuartal"] = q

    # Bentuk long format
    df_long = df.melt(
        id_vars=[
            "Project",
            "Parameter",
            "Target Rasio",
            "Target Kuartal",
            "Tahun",
            "Kuartal",
        ],
        var_name="Bulan",
        value_name="Target Bulanan",
    )

    st.subheader("📊 Pratinjau Budget Plan")
    formatters = {"Target Rasio": "{:.2f}%", "Target Kuartal": "Rp {:,.0f}"}
    for m in months:
        formatters[m] = "Rp {:,.0f}"

    st.dataframe(df.style.format(formatters, na_rep="-"), use_container_width=True)

    # Simpan ke database
    result = db_manager.insert_budget_plan(df_long)
    if result["status"] == "success":
        st.success("✅ Budget plan berhasil disimpan ke database!")
        st.balloons()
    else:
        st.error(f"Gagal menyimpan: {result['message']}")
