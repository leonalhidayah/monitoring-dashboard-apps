from datetime import date
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from database.db_manager import (
    get_budget_ads_summary_by_project,
    get_dim_projects,
    get_marketing_ads_ratio,
)
from views.style import format_rupiah, load_css

project_root = Path.cwd()

st.title("📊 Budget Ads Summary Dashboard")

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
    df = get_budget_ads_summary_by_project(
        project_name=selected_project,
        start_date=start_date,
        end_date=end_date,
    )

    st.header(f"Menampilkan Data untuk: {selected_project}")
    st.markdown("  ")

    if df is not None and not df.empty:
        total_akrual = df["akrual_basis"].sum()
        total_cash = df["cash_basis"].sum()
        total_topup = df["aktual_topup"].sum()

        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        kpi_col1.metric("Total Akrual Basis", f"Rp {total_akrual:,.0f}")
        kpi_col2.metric("Total Cash Basis", f"Rp {total_cash:,.0f}")
        kpi_col3.metric("Total Aktual Topup", f"Rp {total_topup:,.0f}")

        st.divider()

        st.subheader("Total Omset Daily")

        df_akrual_daily = df.groupby(["tanggal"])["akrual_basis"].sum()
        df_cash_daily = df.groupby(["tanggal"])["cash_basis"].sum()

        load_css()

        akrual_tab, cash_tab = st.tabs(["Akrual", "Cash"])
        with akrual_tab:
            st.line_chart(df_akrual_daily)
        with cash_tab:
            st.line_chart(df_cash_daily)

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
                    "bar": {"color": bar_color},  # warna batang utama
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

        # st.plotly_chart(fig, use_container_width=True)

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
