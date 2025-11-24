import calendar
from datetime import date, datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from database.db_manager import (
    get_budget_ads_summary_by_project,
    get_target_ads_ratio,
    get_total_sales_target,
    get_vw_ads_performance_summary,
)
from views.config import get_yesterday_in_jakarta


def highlight_status(val):
    """Memberi warna pada sel status berdasarkan nilainya."""
    color = "lightgreen" if val == "Normal" else "tomato"
    return f"background-color: {color}; color: black; font-weight: bold; text-align: center;"


def calculate_ads_status(df, target_rasio, safe_zone_start):
    """
    Menambahkan kolom 'status' ke DataFrame berdasarkan target rasio.
    Menggunakan kolom 'ads_spend_percentage' yang sudah ada di df.
    """
    conditions = [
        df["ads_spend_percentage"] < safe_zone_start,  # Under
        (df["ads_spend_percentage"] >= safe_zone_start)
        & (df["ads_spend_percentage"] <= target_rasio),  # Normal
    ]
    choices = ["Under", "Normal"]
    df["status"] = np.select(conditions, choices, default="Over")
    df["target_rasio"] = target_rasio
    return df


def style_ads_dataframe(df):
    """
    Menerapkan styling standar ke DataFrame performa iklan.
    Memastikan 'status' adalah kolom terakhir.
    """

    cols = list(df.columns)

    if "status" in cols:
        cols.remove("status")
        cols.append("status")

    return (
        df[cols]
        .style.format(
            {
                "total_omset": format_rupiah,
                "total_spending": format_rupiah,
                "ads_spend_percentage": "{:.2f}%",
                "target_rasio": "{:.2f}%",
            }
        )
        .applymap(highlight_status, subset=["status"])
        .set_properties(
            **{
                "text-align": "center",
                "border": "1px solid #ccc",
                "padding": "6px",
            }
        )
    )


def format_rupiah(value):
    return f"Rp {value:,.0f}"


# ==============================================================================
# 1. BAGIAN OMSET (STRATEGIC - MTD)
# ==============================================================================
def display_omset_summary(project_id, project_name, tgl_awal, tgl_akhir):
    """
    Menampilkan ringkasan performa omset (Selalu MTD: Awal Bulan s/d Hari Ini).
    """
    st.subheader("Ringkasan Pencapaian Omset")
    st.caption(
        f"Periode Data: **{tgl_awal.strftime('%d %b')}** s/d **{tgl_akhir.strftime('%d %b %Y')}**"
    )

    # --- Setup Konteks Bulan ---
    tahun_konteks, bulan_konteks = tgl_akhir.year, tgl_akhir.month
    tgl_awal_bulan = tgl_akhir.replace(day=1)
    _, akhir_hari = calendar.monthrange(tahun_konteks, bulan_konteks)
    tgl_akhir_bulan = tgl_akhir.replace(day=akhir_hari)

    # --- Ambil Data ---
    total_target_omset = get_total_sales_target(
        project_id, tgl_awal_bulan, tgl_akhir_bulan
    )
    df_raw = get_budget_ads_summary_by_project(project_name, tgl_awal, tgl_akhir)

    total_omset_aktual = df_raw["akrual_basis"].sum() if not df_raw.empty else 0

    pencapaian_persen = (
        (float(total_omset_aktual) / float(total_target_omset) * 100)
        if total_target_omset > 0
        else 0
    )

    # --- Hitung Pace Linear ---
    if isinstance(tgl_akhir, datetime):
        tgl_akhir = tgl_akhir.date()

    _, total_hari_di_bulan = calendar.monthrange(tgl_akhir.year, tgl_akhir.month)
    ideal_daily_omset = (
        total_target_omset / total_hari_di_bulan if total_hari_di_bulan > 0 else 0
    )

    # Logic Pace: Hari berjalan adalah tanggal dari tgl_akhir (biasanya hari ini)
    hari_berjalan = max(0, min(tgl_akhir.day, total_hari_di_bulan))
    ideal_omset_until_today = ideal_daily_omset * hari_berjalan

    persentase_ideal = (
        (hari_berjalan / total_hari_di_bulan * 100) if total_hari_di_bulan > 0 else 0
    )
    gap_pace = pencapaian_persen - persentase_ideal

    # --- Display Metrics ---
    col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 1, 1, 1])

    col1.metric(
        "Omset Aktual (Akrual)",
        format_rupiah(total_omset_aktual),
        border=True,
        help="""Pendapatan omset aktual dari penarikan data omset  
        pada setiap dashboard toko oleh Tim Finance""",
    )
    col2.metric(
        "Target Omset (Bulanan)",
        format_rupiah(round(total_target_omset, -1)),
        border=True,
        help="Target omset yang ditetapkan oleh management",
    )

    col3.metric(
        "Pencapaian Aktual",
        f"{pencapaian_persen:.2f} %",
        border=True,
        help="""Pencapaian aktual target yang didapatkan oleh tim.  
        Persentase ini digunakan sebagai acuan bonus kuartal tim""",
    )

    help_pace = (
        f"**Pencapaian Ideal Periode Ini**\n\n"
        f"- Menggunakan progres *linear* selama 1 bulan.\n"
        f"- Hari ke-**{hari_berjalan}** dari total **{total_hari_di_bulan}** hari.\n"
        f"- Idealnya, hingga tanggal **{tgl_akhir.day}**, omset seharusnya mencapai:\n"
        f"  **{format_rupiah(ideal_omset_until_today)}**.\n\n"
        f"Gunakan angka ini untuk membandingkan omset aktual terhadap target progres bulan berjalan."
    )

    col4.metric(
        "Pencapaian Ideal", f"{persentase_ideal:.2f} %", help=help_pace, border=True
    )

    col5.metric("Gap Pace", f"{gap_pace:.2f} %", border=True, delta_color="normal")


# ==============================================================================
# 2. BAGIAN ADS METRICS
# ==============================================================================
def display_ads_metrics_snapshot(project_id, project_name, tgl_akhir):
    """
    Menampilkan Kartu Metrik Iklan Akumulatif (MTD).
    Range: Tgl 1 Bulan Ini s/d H-1 (Kemarin).
    Pembanding: Tgl 1 Bulan Lalu s/d Tanggal yang sama di Bulan Lalu.
    """
    # ==========================================
    # 1. LOGIKA TANGGAL (MTD)
    # ==========================================
    # Cutoff Current (H-1 dari tgl_akhir yang dipilih)
    tgl_cutoff_curr = tgl_akhir

    # Paksa Start Date jadi Tanggal 1 bulan tersebut
    tgl_start_curr = tgl_cutoff_curr.replace(day=1)

    # Periode Pembanding (Bulan Lalu)
    tgl_cutoff_prev = (pd.Timestamp(tgl_cutoff_curr) - pd.DateOffset(months=1)).date()
    tgl_start_prev = tgl_cutoff_prev.replace(day=1)

    st.subheader("Performa Iklan Terkini")
    st.caption(
        f"Menampilkan performa akumulatif **{tgl_start_curr.strftime('%d %b')} - {tgl_cutoff_curr.strftime('%d %b %Y')}** "
        f"dibandingkan dengan periode yang sama bulan lalu (**{tgl_start_prev.strftime('%d %b')} - {tgl_cutoff_prev.strftime('%d %b %Y')}**)."
    )

    # --- Ambil Data Snapshot (MTD Current) ---
    df_curr = get_vw_ads_performance_summary(
        project_name, tgl_start_curr, tgl_cutoff_curr
    )

    # --- Ambil Data Pembanding (MTD Previous) ---
    df_prev = get_vw_ads_performance_summary(
        project_name, tgl_start_prev, tgl_cutoff_prev
    )

    if df_curr.empty:
        st.warning(
            f"Belum ada data iklan akumulatif hingga {tgl_cutoff_curr.strftime('%d %b %Y')}."
        )
        return

    # --- Kalkulasi Current ---
    spend_curr = df_curr["total_spending"].sum()
    omset_curr = df_curr["total_omset"].sum()
    rasio_curr = (spend_curr / omset_curr * 100) if omset_curr > 0 else 0

    # --- Kalkulasi Previous ---
    spend_prev = df_prev["total_spending"].sum() if not df_prev.empty else 0
    omset_prev = df_prev["total_omset"].sum() if not df_prev.empty else 0
    rasio_prev = (spend_prev / omset_prev * 100) if omset_prev > 0 else 0

    # --- Kalkulasi Delta ---
    # Menggunakan logika % growth untuk spend & omset
    delta_spend = (
        ((spend_curr - spend_prev) / spend_prev * 100) if spend_prev > 0 else 0
    )
    delta_omset = (
        ((omset_curr - omset_prev) / omset_prev * 100) if omset_prev > 0 else 0
    )
    delta_rasio = rasio_curr - rasio_prev

    # --- Target & Logic Warna ---
    # Ambil target rasio bulan dari tgl_cutoff_curr
    quarter = (tgl_cutoff_curr.month - 1) // 3 + 1
    target_rasio = get_target_ads_ratio(project_id, tgl_cutoff_curr.year, quarter) or 0

    gap = target_rasio - rasio_curr

    if rasio_curr > target_rasio:
        indicator_color = "#ff2b2b"  # Merah
        status_desc = "Boros (Melebihi Target)"
    elif gap > 5:
        indicator_color = "#ff2b2b"  # Merah
        status_desc = "Terlalu Irit (Gap > 5%)"
    else:
        indicator_color = "#09ab3b"  # Hijau
        status_desc = "Ideal (Gap ≤ 5%)"

    # --- Display 5 Kolom Metrik ---
    col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 1, 1, 1])

    col1.metric(
        "Ad Spend",
        format_rupiah(spend_curr),
        delta=f"{delta_spend:.2f} %",
        delta_color="inverse",
        border=True,
        help="""Total pengeluaran iklan akumulatif dari Tgl 1 sampai H-1.  
        Data bersumber dari input data Tim Advertiser""",
    )
    col2.metric(
        "Omset Berjalan (Total Pesanan)",
        format_rupiah(omset_curr),
        delta=f"{delta_omset:.2f} %",
        delta_color="normal",
        border=True,
        help="""Total omset akumulatif dari Tgl 1 sampai H-1.  
        Data bersumber dari data total pesanan BigSeller""",
    )

    # Tooltip Rumus LaTeX
    tooltip_rumus = r"""
    **Rumus Perhitungan:**
    
    $$
    \text{Rasio} = \frac{\text{Total Biaya Iklan (Ads Spend)}}{\text{Omset Berjalan (Net Order Value)}} \times 100\%
    $$
    
    *Formula ini menghitung efisiensi biaya iklan terhadap pendapatan kotor yang dihasilkan.*
    """
    col3.metric(
        "Rasio Ads/Omset",
        f"{rasio_curr:.2f} %",
        delta=f"{delta_rasio:.2f} %",
        delta_color="inverse",
        border=True,
        help=tooltip_rumus,
    )

    # Tooltip Kriteria Warna
    tooltip_gap = tooltip_gap = """
    **Panduan Indikator Warna Gap:**
    
    Gap dihitung dari selisih `Target - Rasio Aktual`.
    
    🔴 **Merah (Boros / Over Budget)**
    Kondisi: `% Ads/Omset > Target`
    Pengeluaran iklan melebihi batas target yang ditentukan. Perlu efisiensi biaya.
    
    🔴 **Merah (Terlalu Irit / Underspending)**
    Kondisi: `Gap > 5%`
    Pengeluaran iklan terlalu rendah (di bawah target > 5%). Ini bisa berarti potensi omset belum dimaksimalkan ("uang nganggur").
    
    🟢 **Hijau (Ideal / On Track)**
    Kondisi: `Gap ≤ 5%` (dan Rasio < Target)
    Penggunaan anggaran efisien dan optimal (berada di zona aman 0-5% dari target).
    """
    col4.metric(
        "Target",
        f"{target_rasio:.2f} %",
        border=True,
        help=tooltip_gap,
        height=135,
    )

    # Custom Gap Card
    with col5:
        st.markdown(
            f"""
            <div style="border: 1px solid rgba(49, 51, 63, 0.2); border-radius: 0.5rem; padding: 1rem 0.5rem; background-color: {indicator_color}; height: 100%; min-height: 135px; display: flex; flex-direction: column; justify-content: center; padding-left: 15px;">
                <div style="font-size: 14px; color: rgba(255, 255, 255, 0.9);">Gap</div>
                <div style="font-size: 30px; font-weight: 700; color: #FFFFFF;">{gap:.2f} %</div>
                <div style="font-size: 14px; color: rgba(255, 255, 255, 0.9); margin-top: 4px;">{status_desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# 3. BAGIAN ADS TRENDS (ANALYTICAL - CHART & TABLES)
# ==============================================================================
def display_ads_trend_analysis(project_id, project_name, tgl_awal, tgl_akhir):
    """
    Menampilkan Grafik dan Tabel detail.
    Mengikuti filter tanggal yang dipilih user (Global Filter).
    """
    st.subheader("Analisis Tren & Detail")
    st.caption(
        f"Menampilkan data historis dari **{tgl_awal.strftime('%d %b %Y')}** s/d **{tgl_akhir.strftime('%d %b %Y')}**"
    )

    df_ads = get_vw_ads_performance_summary(project_name, tgl_awal, tgl_akhir)
    if df_ads.empty:
        st.info("Tidak ada data untuk rentang tanggal yang dipilih.")
        return

    # --- Line Chart ---
    try:
        df_ads["tanggal"] = pd.to_datetime(df_ads["tanggal"]).dt.date
    except:
        pass

    df_daily = (
        df_ads.groupby("tanggal")[["total_omset", "total_spending"]].sum().reset_index()
    )
    df_daily.rename(
        columns={
            "total_omset": "Total Omset Berjalan",
            "total_spending": "Total Ad Spend",
        },
        inplace=True,
    )

    fig_line = px.line(
        df_daily,
        x="tanggal",
        y=["Total Omset Berjalan", "Total Ad Spend"],
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
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # --- Tables ---
    st.markdown("**Detail Performa per Toko**")

    quarter = (tgl_akhir.month - 1) // 3 + 1
    target_rasio = get_target_ads_ratio(project_id, tgl_akhir.year, quarter) or 0
    safe_zone = max(0, target_rasio - 5)

    df_store = (
        df_ads.groupby("nama_toko")
        .agg({"total_omset": "sum", "total_spending": "sum"})
        .reset_index()
    )
    df_store["ads_spend_percentage"] = (
        df_store["total_spending"] / df_store["total_omset"] * 100
    ).fillna(0)

    # Helper calculate & style (sesuai kode lama Anda)
    df_store = calculate_ads_status(df_store, target_rasio, safe_zone)
    st.dataframe(style_ads_dataframe(df_store), width="stretch")

    with st.expander("Lihat Detail Harian per Toko"):
        df_detail = calculate_ads_status(df_ads, target_rasio, safe_zone)
        st.dataframe(style_ads_dataframe(df_detail), width="stretch")


# ==============================================================================
# 4. MAIN CONTROLLER
# ==============================================================================
def display_marketing_dashboard(project_id: int, project_name: str):
    """
    Fungsi Utama Dashboard Marketing.
    Menggabungkan 3 level pandangan: Strategic (MTD), Tactical (H-1), dan Analytical (Filter).
    """

    # --- SETUP WAKTU DEFAULT ---
    today = date.today()
    start_of_month = today.replace(day=1)

    col_header, col_filter = st.columns(
        [3, 1], gap="medium", vertical_alignment="bottom"
    )

    with col_header:
        st.title(f"📊 Dashboard Marketing: {project_name}")

    with col_filter:
        date_range = st.date_input(
            "Filter Tanggal (Untuk Grafik & Tabel):",
            value=(start_of_month, get_yesterday_in_jakarta()),
            key=f"date_filter_{project_name}",
        )

    # Validasi Range
    if not (isinstance(date_range, tuple) and len(date_range) == 2):
        st.warning("Pilih rentang tanggal lengkap.")
        tgl_awal_filter, tgl_akhir_filter = start_of_month, get_yesterday_in_jakarta()
    else:
        tgl_awal_filter, tgl_akhir_filter = date_range

    st.markdown("---")

    # 1. OMSET SUMMARY (Selalu MTD)
    # Tidak peduli filter user, boss ingin lihat performa bulan ini.
    display_omset_summary(project_id, project_name, start_of_month, tgl_akhir_filter)

    st.markdown("---")

    # 2. ADS METRICS
    display_ads_metrics_snapshot(project_id, project_name, tgl_akhir_filter)

    st.markdown("---")

    # 3. ADS TREND ANALYSIS (Mengikuti Filter User)
    # Untuk analisis mendalam (Deep Dive).
    display_ads_trend_analysis(
        project_id, project_name, tgl_awal_filter, tgl_akhir_filter
    )
