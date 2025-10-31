import pandas as pd
import plotly.express as px
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
            st.metric(label="Total Closing", value=f"{total_closing: .0f}", border=True)

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

        fig_line = px.line(
            df_time_series,
            x="performance_date",
            y=selected_trend_metric,
            markers=True,
        )
        fig_line.update_traces(
            hovertemplate="<b>%{x|%d %B %Y}</b><br><b>Amount:</b> Rp %{y:,.0f}<extra></extra>"
        )
        fig_line.update_layout(
            xaxis_title="Tanggal",
            yaxis_title="Jumlah (Rp)",
            yaxis_tickformat=".2s",
            legend_title_text="",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
            ),
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # TODO: add option select product from df_filtered
        st.subheader("Tren Metrik Harian per Brand")

        col_metric, col_product = st.columns(2)

        all_trend_metric = ["gross_revenue", "spend", "leads_generated", "deals_closed"]
        options = ["Semua Metrik"] + all_trend_metric
        with col_metric:
            selected_trend_metric = st.multiselect(
                "Pilih Metrik",
                options=options,
                key="select_trend_metric",
                default=["gross_revenue", "spend"],
            )

        if "Semua Metrik" in selected_trend_metric:
            selected_trend_metric = all_trend_metric

        all_products_2 = sorted(df_filtered["product_name"].unique())
        options_2 = ["Semua Produk"] + all_products_2
        with col_product:
            selected_products_2 = st.multiselect(
                "Pilih Produk",
                options=options_2,
                key="select_product_2",
                default="Semua Produk",
            )

        if "Semua Produk" in selected_products_2:
            selected_products_2 = all_products_2

        df_filtered_2 = df_filtered[
            (df_filtered["product_name"].isin(selected_products_2))
        ]

        df_time_series_product = (
            df_filtered_2.groupby(["performance_date", "product_name"])
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

        # selected_trend_metric = st.selectbox(
        #     "Pilih metrik untuk melihat tren:",
        #     options=["gross_revenue", "spend", "leads_generated", "deals_closed"],
        # )

        fig_line = px.line(
            df_time_series_product,
            x="performance_date",
            y=selected_trend_metric,
            color="product_name",
            custom_data=["product_name", "variable"],
            markers=True,
        )
        fig_line.update_traces(
            hovertemplate=(
                "<b>product_name:</b> %{customdata[0]}<br>"
                "<b>variable:</b> %{customdata[1]}<br>"
                "<b>performance_date:</b> %{x|%b %d, %Y}<br>"
                "<b>value:</b> Rp %{y:,.0f}<extra></extra>"
            )
        )
        fig_line.update_layout(
            xaxis_title="Tanggal",
            yaxis_title="Jumlah (Rp)",
            yaxis_tickformat=".2s",
            legend_title_text="",
            # legend=dict(
            #     orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
            # ),
        )
        st.plotly_chart(fig_line, use_container_width=True)

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
