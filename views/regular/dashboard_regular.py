import pandas as pd
import streamlit as st

from data_preprocessor.utils import fetch_data
from database.db_connection import get_connection

st.set_page_config(layout="wide", page_title="Dashboard Regular")
st.title("📊 Dashboard Performa Regular")
st.markdown("Analisis metrik gabungan dari tim Advertiser dan CS.")

conn = get_connection()
full_df = fetch_data(conn)

if full_df.empty:
    st.warning(
        "Belum ada data di tabel `advertiser_cs_regular`. Silakan isi data terlebih dahulu.",
        icon="⚠️",
    )
else:
    all_products = sorted(full_df["product_name"].unique())
    options = ["Semua Produk"] + all_products
    selected_products = st.multiselect(
        "Pilih Produk", options=options, key="select_product", default="Semua Produk"
    )

    if "Semua Produk" in selected_products:
        selected_products = all_products

    col2, col3, col4 = st.columns(3)
    with col2:
        start_date = st.date_input(
            "Dari Tanggal",
            value=full_df["performance_date"].min(),
            min_value=full_df["performance_date"].min(),
            max_value=full_df["performance_date"].max(),
        )
    with col3:
        end_date = st.date_input(
            "Sampai Tanggal",
            value=full_df["performance_date"].max(),
            min_value=full_df["performance_date"].min(),
            max_value=full_df["performance_date"].max(),
        )
    with col4:
        selected_channel = st.selectbox(
            "Pilih Channel", options=["Semua Channel", "CTWA", "Order Online"]
        )

    st.divider()

    if start_date > end_date:
        st.error("Error: Tanggal mulai tidak boleh melebihi tanggal akhir.")
        st.stop()

    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    df_filtered = full_df[
        (full_df["performance_date"] >= start_date)
        & (full_df["performance_date"] <= end_date)
        & (full_df["product_name"].isin(selected_products))
    ]

    if selected_channel != "Semua Channel":
        df_filtered = df_filtered[df_filtered["channel"] == selected_channel]

    if df_filtered.empty:
        st.warning(
            "Tidak ada data yang cocok dengan filter yang Anda pilih.", icon="🕵️‍♂️"
        )
    else:
        st.subheader("Ringkasan Metrik Utama")

        total_spend = df_filtered["spend"].sum()
        total_revenue = df_filtered["gross_revenue"].sum()
        leads_received = df_filtered["leads_received"].sum()
        total_closing = df_filtered["deals_closed"].sum()

        roas = total_revenue / total_spend if total_spend > 0 else 0
        cpl = total_spend / leads_received if leads_received > 0 else 0
        cpa = total_spend / total_closing if total_closing > 0 else 0
        closing_rate = total_closing / leads_received if leads_received > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Total Spend", value=f"Rp {total_spend:,.0f}", border=True)
        with col2:
            st.metric(
                label="Total Omset", value=f"Rp {total_revenue:,.0f}", border=True
            )
        with col3:
            st.metric(
                label="Total Lead Masuk", value=f"{leads_received: .0f}", border=True
            )
        with col4:
            st.metric(label="Total Cloding", value=f"{total_closing: .0f}", border=True)

        m_col5, m_col6, m_col7, m_col8 = st.columns(4)
        with m_col5:
            st.metric(label="CPL", value=f"Rp {cpl:,.0f}", border=True)
        with m_col6:
            st.metric(label="Closing Rate", value=f"{closing_rate:.2%}", border=True)
        with m_col7:
            st.metric(label="CPA", value=f"Rp {cpa:,.0f}", border=True)
        with m_col8:
            st.metric(label="ROAS", value=f"{roas:.2f}", border=True)

        st.divider()

        st.subheader("Tren Metrik Harian")
        df_time_series = (
            df_filtered.groupby("performance_date")
            .agg(
                {
                    "spend": "sum",
                    "gross_revenue": "sum",
                    "leads_generated": "sum",
                    "deals_closed": "sum",
                }
            )
            .reset_index()
        )

        selected_trend_metric = st.selectbox(
            "Pilih metrik untuk melihat tren:",
            options=["gross_revenue", "spend", "leads_generated", "deals_closed"],
        )
        st.line_chart(df_time_series, x="performance_date", y=selected_trend_metric)

        st.subheader("Perbandingan Performa")
        col_viz1, col_viz2 = st.columns(2)

        with col_viz1:
            st.markdown("##### Performa per Produk")
            df_by_product = (
                df_filtered.groupby("product_name")["gross_revenue"]
                .sum()
                .sort_values(ascending=False)
            )
            st.bar_chart(df_by_product)

        with col_viz2:
            st.markdown("##### Performa per Channel")
            df_by_channel = (
                df_filtered.groupby("channel")["gross_revenue"]
                .sum()
                .sort_values(ascending=False)
            )
            st.bar_chart(df_by_channel)

        with st.expander("Lihat Data Mentah Hasil Filter"):
            st.dataframe(df_filtered)
