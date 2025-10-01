import numpy as np
import pandas as pd
import streamlit as st

from database import db_manager

st.set_page_config(page_title="Dashboard Admin AMS", layout="wide")


@st.cache_data
def load_data():
    """
    Fungsi ini memuat data dari view v_shipment_details.
    Untuk sekarang, kita akan membuat data sampel yang realistis.
    """
    data = {
        "no_resi": [f"AMS{100 + i}" for i in range(100)]
        + [f"AMS{100 + i}" for i in range(20)],
        "nama_brand": np.random.choice(
            ["Brand A", "Brand B", "Brand C", "Brand D"], 120
        ),
        "timestamp_input_data": pd.to_datetime(
            pd.date_range(start="2025-09-01", periods=120, freq="4H")
        ),
        "Sesi": np.random.choice(["SESI 1", "SESI 2", "SESI 3", "SESI 4"], 120),
    }
    df = pd.DataFrame(data)
    df["timestamp_input_data"] = pd.to_datetime(df["timestamp_input_data"])
    return df


df = db_manager.get_admin_shipments()

st.title("📊 Report Admin Marketplace")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    list_brand = ["Semua Brand"] + sorted(df["nama_brand"].unique().tolist())
    selected_brand = st.selectbox("Pilih Brand", list_brand)

with col2:
    min_date = df["timestamp_input_data"].min().date()
    max_date = df["timestamp_input_data"].max().date()
    selected_date = st.date_input(
        "Pilih Rentang Waktu",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

with col3:
    list_sesi = ["Semua Sesi"] + sorted(df["sesi"].unique().tolist())
    selected_sesi = st.selectbox("Pilih Sesi", list_sesi)

with col4:
    list_order_status = ["Semua Order Status"] + sorted(
        df["order_status"].unique().tolist()
    )
    selected_order_status = st.selectbox("Pilih Order Status", list_order_status)

st.markdown("---")


start_date, end_date = selected_date
df_filtered = df[
    (df["timestamp_input_data"].dt.date >= start_date)
    & (df["timestamp_input_data"].dt.date <= end_date)
]

if selected_brand != "Semua Brand":
    df_filtered = df_filtered[df_filtered["nama_brand"] == selected_brand]

if selected_sesi != "Semua Sesi":
    df_filtered = df_filtered[df_filtered["sesi"] == selected_sesi]

if selected_order_status != "Semua Order Status":
    df_filtered = df_filtered[df_filtered["order_status"] == selected_order_status]


st.header("Ringkasan Data")
m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    total_resi_unik = df_filtered["no_resi"].nunique()
    st.metric(label="🚚 **Total Resi Unik**", value=f"{total_resi_unik}")

with m_col2:
    total_brand_aktif = df_filtered["nama_brand"].nunique()
    st.metric(label="🏢 **Brand Aktif**", value=f"{total_brand_aktif}")

# Kolom 3 dikosongkan untuk metrik lain
# with m_col3:
#     pass

st.markdown("---")

st.header("Visualisasi Detail")

st.subheader("Tren Jumlah Resi Unik per Hari")
if not df_filtered.empty:
    daily_unique_resi = df_filtered.groupby(
        df_filtered["timestamp_input_data"].dt.date
    )["no_resi"].nunique()
    st.line_chart(daily_unique_resi)
else:
    st.warning("Tidak ada data untuk ditampilkan dengan filter yang dipilih.")

# Visualisasi 2: Jumlah Resi Unik per Brand (Bar Chart)
st.subheader("Perbandingan Jumlah Resi Unik per Brand")
if not df_filtered.empty:
    brand_unique_resi = (
        df_filtered.groupby("nama_brand")["no_resi"]
        .nunique()
        .sort_values(ascending=False)
    )
    st.bar_chart(brand_unique_resi)
else:
    st.warning("Tidak ada data untuk ditampilkan dengan filter yang dipilih.")

# Menampilkan data mentah (opsional)
if st.checkbox("Tampilkan Data Mentah Hasil Filter"):
    if not df_filtered.empty:
        st.write(df_filtered.reset_index(drop=True))
    else:
        st.info("Tidak ada data mentah untuk ditampilkan.")
