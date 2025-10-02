import pandas as pd
import streamlit as st

from database import db_manager  # Pastikan file ini ada

st.set_page_config(layout="wide")


def format_number(num):
    if num >= 1_000_000_000:
        return f"Rp{num / 1_000_000_000:.2f}B"
    if num >= 1_000_000:
        return f"Rp{num / 1_000_000:.2f}M"
    if num >= 1_000:
        return f"Rp{num / 1_000:.2f}K"
    return f"Rp{num}"


# --- MEMUAT DAN MEMPROSES DATA ---
df = db_manager.get_advertiser_marketplace_data()

data_pemetaan_project = {
    "Zhi Yang Yao": {
        "Nama Toko": [
            "SP zhi yang yao official store",
            "SP zhi yang yao official",
            "SP zhi yang yao mart",
            "SP zhi yang yao",
            "SP zhi yang yao (iklan eksternal FB)",
            "TP zhi yang yao official store",
            "TP zhi yang yao",
            "TT zhi yang yao official store",
            "LZ zhi yang yao",
        ]
    },
    "Juwara Herbal": {
        "Nama Toko": [
            "SP juwara herbal official store",
            "TT juwara herbal",
        ],
    },
    "Enzhico": {
        "Nama Toko": [
            "SP enzhico",
            "SP enzhico store",
            "SP enzhico shop",
            "TT enzhico authorized store",
            "LZ enzhico",
            "LZ enzhico store",
        ]
    },
    "Erassgo": {
        "Nama Toko": [
            "SP erassgo official",
            "SP erassgo official store",
            "SP erassgo.co",
            "SP erassgo makassar",
            "TP erassgo",
            "LZ erassgo",
            "LZ erassgo store id",
        ]
    },
    "Kudaku": {
        "Nama Toko": [
            "SP kudaku",
            "SP kudaku store",
            "SP kudaku official store",
            "SP kudaku id",
            "SP kudaku indonesia",
            "TT kudaku milk",
            "LZ kudaku",
        ],
    },
}

store_to_brand_map = {
    store: brand
    for brand, details in data_pemetaan_project.items()
    for store in details["Nama Toko"]
}

df["brand"] = df["nama_toko"].map(store_to_brand_map)
df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.date
df.dropna(subset=["brand"], inplace=True)  # Hapus baris tanpa brand

# --- TAMPILAN UTAMA & FILTER ---
st.title("📊 Report Iklan Marketplace")
st.markdown("---")

filter1, filter2 = st.columns(2)
with filter1:
    unique_brands = df["brand"].unique()
    selected_brands = st.multiselect(
        "Brand", options=unique_brands, default=unique_brands
    )

with filter2:
    min_date = df["tanggal"].min()
    max_date = df["tanggal"].max()
    date_range = st.date_input(
        "Pilih Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM-DD",
    )

if len(date_range) != 2:
    st.warning("Mohon pilih rentang tanggal (mulai dan selesai).")
    st.stop()

start_date, end_date = date_range
df_filtered = df[
    (df["brand"].isin(selected_brands))
    & (df["tanggal"] >= start_date)
    & (df["tanggal"] <= end_date)
]

if df_filtered.empty:
    st.warning("Tidak ada data yang ditemukan untuk filter yang dipilih.")
    st.stop()

# --- HITUNG & TAMPILKAN KPI UTAMA ---
total_spend = df_filtered["spend"].sum()
total_revenue = df_filtered["gross_revenue"].sum()
total_konversi = df_filtered["konversi"].sum()
total_produk_terjual = df_filtered["produk_terjual"].sum()
overall_roas = total_revenue / total_spend if total_spend > 0 else 0
overall_cpa = total_spend / total_konversi if total_konversi > 0 else 0

st.markdown("---")
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
kpi1.metric("Total Spend", value=format_number(total_spend))
kpi2.metric("Total Gross Revenue", value=format_number(total_revenue))
kpi3.metric("Total Konversi", value=f"{total_konversi:,.0f}")
kpi4.metric("Total Produk Terjual", value=f"{int(total_produk_terjual):,.0f}")
kpi5.metric("ROAS", value=f"{overall_roas:.2f}")
kpi6.metric("CPA", value=format_number(overall_cpa))
st.markdown("---")

# --- TABEL & GRAFIK ---
st.subheader("Brand Performance Detail")
brand_performance = (
    df_filtered.groupby("brand")
    .agg(
        {
            "spend": "sum",
            "gross_revenue": "sum",
            "konversi": "sum",
            "produk_terjual": "sum",
        }
    )
    .reset_index()
)

brand_performance["ROAS"] = (
    brand_performance["gross_revenue"] / brand_performance["spend"]
)
brand_performance["CPA"] = brand_performance["spend"] / brand_performance["konversi"]
brand_performance = brand_performance.sort_values(by="gross_revenue", ascending=False)

st.dataframe(
    brand_performance.style.format(
        {
            "spend": "Rp{:,.0f}",
            "gross_revenue": "Rp{:,.0f}",
            "konversi": "{:,.0f}",
            "produk_terjual": "{:,.0f}",
            "ROAS": "{:.2f}",
            "CPA": "Rp{:,.0f}",
        }
    ).bar(subset=["ROAS", "gross_revenue"], color="#649c4f", vmin=0),
    width="stretch",
    hide_index=True,
)

chart1, chart2 = st.columns(2)
with chart1:
    st.subheader("Spend by Brand")
    st.bar_chart(brand_performance.set_index("brand")[["spend"]], horizontal=True)
with chart2:
    st.subheader("Gross Revenue by Brand")
    st.bar_chart(
        brand_performance.set_index("brand")[["gross_revenue"]], horizontal=True
    )


st.markdown("---")
# store performance
st.subheader("Store Performance Detail")
store_performance = (
    df_filtered.groupby("nama_toko")
    .agg(
        {
            "spend": "sum",
            "gross_revenue": "sum",
            "konversi": "sum",
            "produk_terjual": "sum",
        }
    )
    .reset_index()
)

store_performance["ROAS"] = (
    store_performance["gross_revenue"] / store_performance["spend"]
)
store_performance["CPA"] = store_performance["spend"] / store_performance["konversi"]
store_performance = store_performance.sort_values(by="gross_revenue", ascending=False)

st.dataframe(
    store_performance.style.format(
        {
            "spend": "Rp{:,.0f}",
            "gross_revenue": "Rp{:,.0f}",
            "konversi": "{:,.0f}",
            "produk_terjual": "{:,.0f}",
            "ROAS": "{:.2f}",
            "CPA": "Rp{:,.0f}",
        }
    ).bar(subset=["ROAS", "gross_revenue"], color="#649c4f", vmin=0),
    width="stretch",
    hide_index=True,
)

st.subheader("Gross Revenue vs Spend Over Time")
time_series_data = df_filtered.groupby("tanggal")[["gross_revenue", "spend"]].sum()
st.line_chart(time_series_data)
