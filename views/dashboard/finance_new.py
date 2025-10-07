# pages/4_Financial_Dashboard.py

from datetime import date

import pandas as pd
import streamlit as st

from database import db_manager

st.set_page_config(layout="wide")
st.title("📊 Dashboard Monitoring Keuangan")

# --- SIDEBAR UNTUK FILTER ---
with st.sidebar:
    st.header("⚙️ Filter")
    try:
        projects_df = db_manager.get_dim_projects()
        project_list = projects_df["project_name"].tolist()
        project_map = pd.Series(
            projects_df.project_id.values, index=projects_df.project_name
        ).to_dict()
    except Exception:
        st.error("Gagal memuat data project.")
        project_list = []
        project_map = {}

    project_pilihan = st.selectbox("Pilih Project", project_list)

    today = date.today()
    start_of_quarter = date(today.year, 3 * ((today.month - 1) // 3) + 1, 1)
    end_of_quarter = start_of_quarter + pd.DateOffset(months=3) - pd.DateOffset(days=1)

    tgl_awal, tgl_akhir = st.date_input(
        "Pilih Rentang Tanggal",
        value=(start_of_quarter, end_of_quarter.date()),
        min_value=date(2023, 1, 1),
    )

# --- HALAMAN UTAMA ---
if project_pilihan and tgl_awal and tgl_akhir:
    project_id_pilihan = project_map[project_pilihan]

    # 1. AMBIL DATA DARI DATABASE
    df_raw = db_manager.get_financial_summary(project_id_pilihan, tgl_awal, tgl_akhir)

    if df_raw.empty:
        st.warning("Tidak ada data ditemukan untuk project dan periode yang dipilih.")
    else:
        # 2. LAKUKAN PERHITUNGAN (BUSINESS LOGIC) DI PYTHON
        df = df_raw.copy()
        df["tanggal"] = pd.to_datetime(df["tanggal"])
        df["omset_akrual"] = df["omset_akrual"].fillna(0)
        df["total_cash_out"] = df["total_cash_out"].fillna(0)
        df["budget_harian_rp"] = df["budget_harian_rp"].fillna(0)

        df["aktualisasi_plan_rp"] = df["omset_akrual"] * (
            df["target_rasio_persen"] / 100
        )
        df["varian_rp"] = df["aktualisasi_plan_rp"] - df["total_cash_out"]

        st.header(f"Ringkasan untuk: {project_pilihan}")
        st.caption(
            f"Periode: {tgl_awal.strftime('%d %B %Y')} s/d {tgl_akhir.strftime('%d %B %Y')}"
        )

        # --- MODIFIKASI PERHITUNGAN KPI DI SINI ---
        df_omset_unik = df[["tanggal", "omset_akrual"]].drop_duplicates()
        total_omset = df_omset_unik["omset_akrual"].sum()

        df_pengeluaran_unik = df[
            ["tanggal", "parameter_name", "total_cash_out"]
        ].drop_duplicates()
        total_pengeluaran = df_pengeluaran_unik["total_cash_out"].sum()

        df_budget_unik = df[
            ["tanggal", "parameter_name", "budget_harian_rp"]
        ].drop_duplicates()
        total_budget_plan = df_budget_unik["budget_harian_rp"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Omset (Akrual)", f"Rp {total_omset:,.0f}")
        col2.metric("💸 Total Pengeluaran (Realisasi)", f"Rp {total_pengeluaran:,.0f}")
        col3.metric("📝 Total Budget (Plan)", f"Rp {round(total_budget_plan, -3):,.0f}")
        # --- AKHIR MODIFIKASI ---

        st.divider()

        st.subheader("Ringkasan Perbandingan Bulanan")
        monthly_summary = (
            df.groupby([pd.Grouper(key="tanggal", freq="M"), "parameter_name"])
            .agg(
                budget_plan_rp=("budget_harian_rp", "sum"),
                aktualisasi_plan_rp=("aktualisasi_plan_rp", "sum"),
                realisasi_cash_out_rp=("total_cash_out", "sum"),
                varian_rp=("varian_rp", "sum"),
            )
            .reset_index()
        )
        monthly_summary["bulan"] = monthly_summary["tanggal"].dt.strftime("%B %Y")

        pivot_df = monthly_summary.pivot_table(
            index="parameter_name",
            columns="bulan",
            values=[
                "budget_plan_rp",
                "aktualisasi_plan_rp",
                "realisasi_cash_out_rp",
                "varian_rp",
            ],
        ).fillna(0)

        formatters = {col: "Rp {:,.0f}" for col in pivot_df.columns}
        st.dataframe(
            pivot_df.style.format(formatters).apply(
                lambda s: ["color: red" if v < 0 else "color: green" for v in s],
                subset=pd.IndexSlice[:, pd.IndexSlice["varian_rp", :]],
            ),
            width="stretch",
        )

        with st.expander("Lihat Detail Data Harian"):
            st.dataframe(df, width="stretch")
else:
    st.info("👈 Silakan pilih Project dan rentang tanggal di sidebar untuk memulai.")
