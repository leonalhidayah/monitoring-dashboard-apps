from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from database.db_connection import get_engine
from database.queries.dimmension_query import get_nama_project
from database.queries.finance_query import (
    get_mart_budget_ads_summary,
    get_mart_budget_plan,
    get_mart_marketing_ads_ratio,
    get_mart_monitoring_cashflow,
)
from views.style import format_percent, format_rupiah, load_css

st.title("Dashboard Finance")

engine = get_engine()
if engine is None:
    st.error("Koneksi database gagal. Aplikasi tidak dapat dimuat.")
    st.stop()

try:
    project_list = get_nama_project()
except Exception as e:
    st.error(f"Gagal memuat daftar proyek dari database: {e}")
    st.stop()

st.markdown("#### 🔍 Filter Data")
col1, col2 = st.columns([2, 2])

with col1:
    all_project = sorted(project_list)
    options = ["Semua Project"] + all_project
    selected_in_widget = st.multiselect(
        "Pilih Project", options=options, key="select_product", default="Zhi Yang Yao"
    )

    if "Semua Project" in selected_in_widget:
        selected_projects = all_project
    else:
        selected_projects = selected_in_widget

    if "Semua Project" in selected_in_widget or len(selected_projects) == len(
        all_project
    ):
        display_title = "Semua Project"
    elif len(selected_projects) > 2:
        display_title = f"{len(selected_projects)} Project Terpilih"
    elif selected_projects:
        display_title = ", ".join(selected_projects)
    else:
        display_title = "Tidak Ada Project Terpilih"

with col2:
    today = date.today()
    start_default = today.replace(day=1)
    date_range = st.date_input(
        "Pilih Periode Analisis:",
        value=(start_default, today),
        key="date_filter",
    )

if isinstance(date_range, tuple):
    if len(date_range) == 1:
        st.warning("⚠️ Silakan pilih **tanggal akhir** juga.", icon="⚠️")
        st.stop()
    elif len(date_range) == 2:
        start_date, end_date = date_range
else:
    st.warning("⚠️ Silakan pilih **rentang tanggal**.", icon="⚠️")
    st.stop()

if start_date > end_date:
    st.error("🚨 Tanggal akhir harus setelah tanggal mulai.")
    st.stop()

st.markdown("---")

if selected_projects:
    df_plan_transform = get_mart_budget_plan(
        engine,
        project_names=selected_projects,
        start_date=start_date,
        end_date=end_date,
    )

    df_cashflow_monitoring = get_mart_monitoring_cashflow(
        engine,
        project_names=selected_projects,
        start_date=start_date,
        end_date=end_date,
    )

    df_ads_summary = get_mart_budget_ads_summary(
        engine,
        project_names=selected_projects,
        start_date=start_date,
        end_date=end_date,
    )

    base_columns = ["Project", "Parameter", "Target Rasio", "Target Kuartal"]
    end_columns = ["Tahun", "Kuartal"]

    month_names_to_show = (
        pd.date_range(
            start_date,
            end_date,
            freq="D",  # 'MS' = Month Start
        )
        .strftime("%B")
        .unique()
        .tolist()
    )

    existing_months_in_range = [
        month for month in month_names_to_show if month in df_plan_transform.columns
    ]

    final_columns_to_display = base_columns + existing_months_in_range + end_columns

    df_plan_display = df_plan_transform[final_columns_to_display]

    formatter_dict = {"Target Kuartal": format_rupiah, "Target Rasio": "{:.2f}%"}
    for month in existing_months_in_range:
        formatter_dict[month] = format_rupiah

    styled_df_plan = df_plan_display.style.format(formatter_dict)

    df_cashflow_monitoring_filtered = df_cashflow_monitoring[
        df_cashflow_monitoring["Parameter Budget"] != "Target Omset"
    ]

    if len(selected_projects) > 1:
        st.info("Menampilkan data agregat untuk project terpilih.")

        group_cols = ["Tahun", "Bulan", "Kuartal", "Parameter Budget"]
        sum_cols = ["Maksimal Budget (Plan)", "Total Realisasi (Actual)", "Sisa Budget"]

        df_cashflow_display = df_cashflow_monitoring_filtered.groupby(
            group_cols, as_index=False
        )[sum_cols].sum()

        df_cashflow_display["Persentase Terpakai"] = (
            df_cashflow_display["Total Realisasi (Actual)"]
            / df_cashflow_display["Maksimal Budget (Plan)"]
        )
        df_cashflow_display["Persentase Terpakai"] = (
            df_cashflow_display["Persentase Terpakai"]
            .fillna(0)
            .replace([np.inf, -np.inf], 0)
        )

        df_cashflow_display["Status"] = np.where(
            df_cashflow_display["Total Realisasi (Actual)"]
            > df_cashflow_display["Maksimal Budget (Plan)"],
            "Over Budget",
            "Normal",
        )

        final_cols = group_cols + sum_cols + ["Persentase Terpakai", "Status"]
        df_cashflow_display = df_cashflow_display[final_cols]

    else:
        df_cashflow_display = df_cashflow_monitoring_filtered

    def highlight_status_cashflow(val):
        color = "tomato" if val == "Over Budget" else "lightgreen"
        return f"background-color: {color}; color: black; font-weight: bold; text-align: center;"

    styled_df_cashflow = (
        df_cashflow_display.style.format(
            {
                "Maksimal Budget (Plan)": format_rupiah,
                "Total Realisasi (Actual)": format_rupiah,
                "Sisa Budget": format_rupiah,
                "Persentase Terpakai": format_percent,
            }
        )
        .map(highlight_status_cashflow, subset=["Status"])
        .set_properties(
            **{"text-align": "center", "border": "1px solid #ccc", "padding": "6px"}
        )
    )

    st.header(f"Ringkasan Data: {display_title}")
    st.markdown(" &nbsp;")

    if df_ads_summary is not None and not df_ads_summary.empty:
        total_pendapatan_kotor = df_ads_summary["pendapatan_kotor"].sum()
        total_biaya_admin = df_ads_summary["biaya_admin"].sum()
        total_akrual = df_ads_summary["akrual_basis"].sum()
        total_cash = df_ads_summary["cash_basis"].sum()
        total_topup = df_ads_summary["aktual_topup"].sum()

        total_cashout = df_cashflow_monitoring_filtered[
            df_cashflow_monitoring_filtered["Parameter Budget"] != "Biaya Admin"
        ]["Total Realisasi (Actual)"].sum()
        estimasi_profit = total_cash - total_cashout

        # (KPI Metrics tetap sama)
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        kpi_col1.metric(
            "Total Pendapatan Kotor", f"Rp {total_pendapatan_kotor:,.0f}", border=True
        )
        kpi_col2.metric(
            "Total Biaya Admin", f"Rp {total_biaya_admin:,.0f}", border=True
        )
        kpi_col3.metric("Total Akrual Basis", f"Rp {total_akrual:,.0f}", border=True)
        kpi_col4.metric("Total Cash Basis", f"Rp {total_cash:,.0f}", border=True)
        kpi_col5, kpi_col6 = st.columns(2)
        kpi_col5.metric("Total Cashout", f"Rp {total_cashout:,.0f}", border=True)
        kpi_col6.metric("Estimasi Profit", f"Rp {estimasi_profit:,.0f}", border=True)

        st.divider()
        st.subheader("Budget Plan")
        st.dataframe(styled_df_plan, width="stretch", hide_index=True)

        st.divider()
        st.subheader("Aktualisasi vs Realisasi")
        st.dataframe(styled_df_cashflow, width="stretch", hide_index=True)

        st.divider()
        st.subheader("Total Omset Daily")

        try:
            df_ads_summary["tanggal"] = pd.to_datetime(
                df_ads_summary["tanggal"]
            ).dt.date
        except Exception as e:
            st.error(f"Gagal mengubah kolom 'tanggal'. Error: {e}")
            st.stop()

        df_akrual_daily = (
            df_ads_summary.groupby(["tanggal"])["akrual_basis"].sum().reset_index()
        )
        df_cash_daily = (
            df_ads_summary.groupby(["tanggal"])["cash_basis"].sum().reset_index()
        )

        load_css()
        akrual_tab, cash_tab = st.tabs(["Akrual", "Cash"])

        with akrual_tab:
            fig_akrual = px.line(
                df_akrual_daily,
                x="tanggal",
                y="akrual_basis",
                markers=True,
                title="Perkembangan Pendapatan Akrual",
            )
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
                st.dataframe(
                    df_akrual_daily.style.format(
                        {
                            "tanggal": lambda x: x.strftime("%d %B %Y"),
                            "akrual_basis": lambda x: f"Rp {x:,.0f}",
                        }
                    ),
                    hide_index=True,
                )

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
                st.dataframe(
                    df_cash_daily.style.format(
                        {
                            "tanggal": lambda x: x.strftime("%d %B %Y"),
                            "cash_basis": lambda x: f"Rp {x:,.0f}",
                        }
                    ),
                    hide_index=True,
                )

        st.divider()

        # --- LOGIKA BARU UNTUK BUDGET ADS (MULTI-PROJECT) ---
        st.subheader("Detail Data Monitoring Budget Ads")

        df_ratios = get_mart_marketing_ads_ratio(
            engine, selected_projects, start_date, end_date
        )

        df_ads_detail = df_ads_summary.copy()

        if not df_ratios.empty:
            df_ratios = df_ratios[
                ["project_name", "target_rasio_persen"]
            ].drop_duplicates()
            df_ratios["target_rasio_persen"] = df_ratios["target_rasio_persen"] / 100.0
            df_ads_detail = pd.merge(
                df_ads_detail, df_ratios, on="project_name", how="left"
            )
            df_ads_detail["target_rasio_persen"] = df_ads_detail[
                "target_rasio_persen"
            ].fillna(0)
        else:
            df_ads_detail["target_rasio_persen"] = 0

        df_ads_detail["budget_ads"] = (
            df_ads_detail["akrual_basis"] * df_ads_detail["target_rasio_persen"]
        )
        df_ads_detail["status"] = np.where(
            df_ads_detail["aktual_topup"] > df_ads_detail["budget_ads"],
            "Over",
            "Normal",
        )

        total_budget = df_ads_detail["budget_ads"].sum()

        if total_budget > 0:
            monitoring = total_topup / total_budget * 100
        else:
            monitoring = 0

        status = "Over Budget" if monitoring > 100 else "Normal"
        bar_color = "tomato" if monitoring > 100 else "green"

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=monitoring,
                number={"suffix": "%", "font": {"size": 40}},
                gauge={
                    "axis": {"range": [0, max(100, monitoring * 1.25)]},
                    "bar": {"color": bar_color},
                    "steps": [{"range": [0, 100], "color": "lightgreen"}],
                    "threshold": {"line": {"color": "black", "width": 4}, "value": 100},
                },
                domain={"x": [0, 1], "y": [0, 1]},
            )
        )
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.metric("Total Budget", f"Rp {total_budget:,.0f}")
        st.metric("Total Top Up", f"Rp {total_topup:,.0f}")

        if status == "Over Budget":
            st.error(f"🚨 **{status}!** Aktual melebihi batas rencana.")
        else:
            st.success(f"✅ **{status}** — pengeluaran masih aman.")

        def highlight_status(val):
            color = "tomato" if val == "Over" else "lightgreen"
            return f"background-color: {color}; color: black; font-weight: bold; text-align: center;"

        df_by_store = (
            df_ads_detail.groupby(["nama_toko"])
            .agg({"budget_ads": "sum", "aktual_topup": "sum"})
            .reset_index()
        )
        df_by_store["status"] = np.where(
            df_by_store["aktual_topup"] > df_by_store["budget_ads"], "Over", "Normal"
        )

        styled_df_by_store = (
            df_by_store[["nama_toko", "budget_ads", "aktual_topup", "status"]]
            .style.format({"budget_ads": format_rupiah, "aktual_topup": format_rupiah})
            .map(highlight_status, subset=["status"])
            .set_properties(
                **{"text-align": "center", "border": "1px solid #ccc", "padding": "6px"}
            )
        )
        st.dataframe(
            styled_df_by_store,
            width="stretch",
            column_config={
                "nama_toko": "Nama Toko",
                "budget_ads": "Budget Ads",
                "aktual_topup": "Aktual Topup",
                "status": "Status",
            },
            hide_index=True,
        )

        styled_df_detail = (
            df_ads_detail[
                ["tanggal", "nama_toko", "budget_ads", "aktual_topup", "status"]
            ]
            .style.format({"budget_ads": format_rupiah, "aktual_topup": format_rupiah})
            .map(highlight_status, subset=["status"])
            .set_properties(
                **{"text-align": "center", "border": "1px solid #ccc", "padding": "6px"}
            )
        )
        with st.expander(label="Data Rinci per Tanggal"):
            st.dataframe(styled_df_detail, width="stretch", hide_index=True)

    else:
        st.warning("Tidak ada data yang ditemukan untuk filter yang dipilih.")
else:
    st.info("Silakan pilih minimal satu project untuk memulai analisis.")
