from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_preprocessor.utils import transform_budget_to_report
from database.db_manager import (
    get_budget_ads_summary_by_project,
    get_dim_projects,
    get_finance_budget_plan_by_project,
    get_marketing_ads_ratio,
    get_vw_monitoring_cashflow,
)
from views.style import format_percent, format_rupiah, load_css

project_root = Path.cwd()

st.title("Dashboard Finance")

try:
    project_df = get_dim_projects()
    project_list = project_df["project_name"].unique().tolist()
except Exception as e:
    st.error(f"Gagal memuat daftar proyek dari database: {e}")
    st.stop()

# --- Filter di Halaman Utama ---
st.markdown("#### 🔍 Filter Data")
col1, col2 = st.columns([2, 2])

with col1:
    selected_project = st.selectbox("Pilih Project", options=project_list)

with col2:
    today = date.today()
    start_default = today.replace(day=1)
    date_range = st.date_input(
        "Pilih Periode Analisis:",
        value=(start_default, today),
        key="date_filter",
    )

# --- Validasi Input Date Range ---
if isinstance(date_range, tuple):
    if len(date_range) == 1:
        st.warning(
            "⚠️ Silakan pilih **tanggal akhir** juga untuk menampilkan data dengan benar.",
            icon="⚠️",
        )
        st.stop()
    elif len(date_range) == 2:
        start_date, end_date = date_range
else:
    st.warning("⚠️ Silakan pilih **rentang tanggal** terlebih dahulu.", icon="⚠️")
    st.stop()

if start_date > end_date:
    st.error("🚨 Tanggal akhir harus setelah tanggal mulai.")
    st.stop()

st.markdown("---")

# --- Memuat dan Menampilkan Data ---
if selected_project:
    # st.header("Monitoring Plan, Aktualisasi, Realisasi")
    df_plan = get_finance_budget_plan_by_project(
        project_name=selected_project, start_date=start_date, end_date=end_date
    )
    df_plan_transform = transform_budget_to_report(df_plan)
    formatter_dict = {"Target Kuartal": format_rupiah, "Target Rasio": "{:.2f}%"}

    all_months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    existing_month_columns = [
        month for month in all_months if month in df_plan_transform.columns
    ]

    for month in existing_month_columns:
        formatter_dict[month] = format_rupiah

    styled_df_plan = df_plan_transform.style.format(formatter_dict)

    df_cashflow_monitoring = get_vw_monitoring_cashflow(
        project_name=selected_project, start_date=start_date, end_date=end_date
    )
    df_cashflow_monitoring = df_cashflow_monitoring.query(
        "`Parameter Budget` != 'Target Omset'"
    )

    def highlight_status_cashflow(val):
        color = "tomato" if val == "Over Budget" else "lightgreen"
        return f"background-color: {color}; color: black; font-weight: bold; text-align: center;"

    # Terapkan styling ke DataFrame
    styled_df_cashflow = (
        df_cashflow_monitoring.style.format(
            {
                "Maksimal Budget (Plan)": format_rupiah,
                "Total Realisasi (Actual)": format_rupiah,
                "Sisa Budget": format_rupiah,
                "Persentase Terpakai": format_percent,
            }
        )
        .applymap(highlight_status_cashflow, subset=["Status"])
        .set_properties(
            **{
                "text-align": "center",
                "border": "1px solid #ccc",
                "border-radius": "4px",
                "padding": "6px",
            }
        )
    )

    # st.header("Budget Ads Summary Dashboard")

    df = get_budget_ads_summary_by_project(
        project_name=selected_project,
        start_date=start_date,
        end_date=end_date,
    )

    st.header(f"Ringkasan Data: {selected_project}")
    st.markdown("  ")

    if df is not None and not df.empty:
        total_akrual = df["akrual_basis"].sum()
        total_cash = df["cash_basis"].sum()
        total_topup = df["aktual_topup"].sum()
        total_cashout = df_cashflow_monitoring["Total Realisasi (Actual)"].sum()
        estimasi_profit = total_akrual - total_cashout

        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        kpi_col1.metric("Total Akrual Basis", f"Rp {total_akrual:,.0f}", border=True)
        kpi_col2.metric("Total Cash Basis", f"Rp {total_cash:,.0f}", border=True)
        kpi_col3.metric("Total Cashout", f"Rp {total_cashout:,.0f}", border=True)
        kpi_col4.metric("Total Aktual Topup", f"Rp {total_topup:,.0f}", border=True)

        st.metric("Estimasi Profit", f"Rp {estimasi_profit:,.0f}", border=True)

        st.divider()

        st.subheader("Budget Plan")
        st.dataframe(styled_df_plan)

        st.divider()

        st.subheader("Aktualisasi vs Realisasi")
        st.dataframe(styled_df_cashflow)

        st.divider()

        st.subheader("Total Omset Daily")

        try:
            df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.date
        except Exception as e:
            st.error(f"Gagal mengubah kolom 'tanggal' menjadi datetime. Error: {e}")
            st.info(
                "Pastikan format tanggal di data Anda konsisten, contoh: 'YYYY-MM-DD'."
            )
            st.stop()

        df_akrual_daily = df.groupby(["tanggal"])["akrual_basis"].sum().reset_index()
        df_cash_daily = df.groupby(["tanggal"])["cash_basis"].sum().reset_index()

        load_css()

        akrual_tab, cash_tab = st.tabs(["Akrual", "Cash"])

        # --- TAB AKRUAL ---
        with akrual_tab:
            # Membuat grafik dengan Plotly Express
            fig_akrual = px.line(
                df_akrual_daily,
                x="tanggal",
                y="akrual_basis",
                markers=True,
                title="Perkembangan Pendapatan Akrual",
            )

            # Kustomisasi format tooltip dan sumbu
            fig_akrual.update_traces(
                hovertemplate="<b>Tanggal:</b> %{x|%d %B %Y}<br><b>Jumlah:</b> Rp %{y:,.0f}<extra></extra>"
            )
            fig_akrual.update_layout(
                xaxis_title="Tanggal",
                yaxis_title="Pendapatan (Rp)",
                yaxis_tickformat=".2s",
            )

            st.plotly_chart(fig_akrual, use_container_width=True)

            with st.expander("Lihat Data Mentah (Akrual)"):
                styled_akrual_df = df_akrual_daily.style.format(
                    {
                        "tanggal": lambda x: x.strftime("%d %B %Y"),
                        "akrual_basis": lambda x: f"Rp {x:,.0f}",
                    }
                )

                st.dataframe(styled_akrual_df)

        # --- TAB CASH ---
        with cash_tab:
            fig_cash = px.line(
                df_cash_daily,
                x="tanggal",
                y="cash_basis",
                markers=True,
                title="Perkembangan Pendapatan Cash",
            )

            fig_cash.update_traces(
                hovertemplate="<b>Tanggal:</b> %{x|%d %B %Y}<br><b>Jumlah:</b> Rp %{y:,.0f}<extra></extra>"
            )
            fig_cash.update_layout(
                xaxis_title="Tanggal",
                yaxis_title="Pendapatan (Rp)",
                yaxis_tickformat=".2s",
            )

            st.plotly_chart(fig_cash, use_container_width=True)

            with st.expander("Lihat Data Mentah (Cash)"):
                styled_cash_df = df_cash_daily.style.format(
                    {
                        "tanggal": lambda x: x.strftime("%d %B %Y"),
                        "cash_basis": lambda x: f"Rp {x:,.0f}",
                    }
                )

                st.dataframe(styled_cash_df)

        st.divider()

        target_rasio_ads = (
            get_marketing_ads_ratio(selected_project, start_date, end_date)[
                "target_rasio_persen"
            ].values
            / 100
        )

        df["budget_ads"] = df["akrual_basis"] * target_rasio_ads
        df["status"] = np.where(df["aktual_topup"] > df["budget_ads"], "Over", "Normal")

        st.subheader("Detail Data Monitoring Budget Ads")

        # Misal data agregat
        total_budget = df["budget_ads"].sum()
        monitoring = total_topup / total_budget * 100

        status = "Over Budget" if monitoring > 100 else "Normal"
        bar_color = "tomato" if monitoring > 100 else "green"

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=monitoring,
                number={"suffix": "%", "font": {"size": 40}},
                gauge={
                    "axis": {"range": [0, monitoring * 1.5]},
                    "bar": {"color": bar_color},
                    "steps": [
                        {
                            "range": [0, 100],
                            "color": "lightgreen",
                        },
                    ],
                    "threshold": {
                        "line": {"color": "black", "width": 4},
                        "value": monitoring,
                    },
                    "borderwidth": 2,
                    "bordercolor": "gray",
                },
                domain={"x": [0, 1], "y": [0, 1]},
            )
        )

        fig.update_layout(height=250, margin=dict(l=20, r=20, t=60, b=20))

        st.plotly_chart(fig, use_container_width=True)

        st.metric("Total Budget", f"Rp {total_budget:,.0f}")
        st.metric("Total Top Up", f"Rp {total_topup:,.0f}")

        if status == "Over Budget":
            st.error(f"🚨 **{status}!** Aktual melebihi batas rencana.")
        else:
            st.success(f"✅ **{status}** — pengeluaran masih aman.")

        # Styling warna untuk kolom status
        def highlight_status(val):
            color = "tomato" if val == "Over" else "lightgreen"
            return f"background-color: {color}; color: black; font-weight: bold; text-align: center;"

        # Terapkan styling ke DataFrame
        styled_df = (
            df[["tanggal", "nama_toko", "budget_ads", "aktual_topup", "status"]]
            .style.format(
                {
                    "budget_ads": format_rupiah,
                    "aktual_topup": format_rupiah,
                }
            )
            .applymap(highlight_status, subset=["status"])
            .set_properties(
                **{
                    "text-align": "center",
                    "border": "1px solid #ccc",
                    "border-radius": "4px",
                    "padding": "6px",
                }
            )
        )

        st.dataframe(styled_df, width="stretch")

    else:
        st.warning("Tidak ada data yang ditemukan untuk filter yang dipilih.")
