from datetime import date, datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_preprocessor.utils import (
    create_visual_report,
    expand_sku,
    get_cpas_column_config,
    get_marketplace_column_config,
    initialize_cpas_data_session,
    initialize_marketplace_data_session,
    parse_bundle_pcs,
)
from database.db_manager import (
    get_advertiser_cpas_data,
    get_advertiser_marketplace_data,
    get_dim_projects,
    get_dim_stores,
    get_financial_summary,
    get_map_project_stores,
    get_target_ads_ratio,
    get_total_sales_target,
    get_vw_admin_shipments_delivery,
    get_vw_ads_performance_summary,
    insert_advertiser_cpas_data,
    insert_advertiser_marketplace_data,
)
from views.style import load_css


def render_marketplace_page(project_name: str, project_config: dict):
    mp_list = project_config["Marketplace"]
    toko_list = project_config["Nama Toko"]

    st.header(f"Advertiser Marketplace {project_name}")

    df_key = f"df_{project_name.lower().replace(' ', '_')}_marketplace"
    preview_key = f"show_preview_{project_name.lower().replace(' ', '_')}_marketplace"

    # Inisialisasi DataFrame
    initialize_marketplace_data_session(
        project_name.lower().replace(" ", "_"),
        mp_list,
        toko_list,
    )

    # Form input
    with st.form(f"form_{project_name.lower().replace(' ', '_')}_marketplace"):
        st.session_state[df_key] = st.data_editor(
            st.session_state[df_key],
            num_rows="dynamic",
            width="stretch",
            column_config=get_marketplace_column_config(toko_list),
        )
        submitted = st.form_submit_button("Simpan & Pratinjau")
        if submitted:
            st.session_state[preview_key] = True

    # Preview
    if st.session_state.get(preview_key, False):
        cleaned_df = st.session_state[df_key].dropna(how="all")
        if not cleaned_df.empty:
            st.markdown("---")
            st.subheader(
                f"Pratinjau Data untuk {project_name}_{datetime.today().strftime('%d-%m-%Y %H:%M:%S')}"
            )
            st.dataframe(
                cleaned_df,
                width="stretch",
                column_config=get_marketplace_column_config(toko_list),
            )

            button_cols = st.columns([8, 3, 1.9])
            with button_cols[0]:
                if st.button(
                    "Ya, Simpan ke Database",
                    key=f"save_button_{project_name.lower().replace(' ', '_')}_marketplace",
                ):
                    result = insert_advertiser_marketplace_data(cleaned_df)
                    if result["status"] == "success":
                        st.success(result["message"])
                        st.session_state[preview_key] = False
                    else:
                        st.error(
                            f"Gagal menyimpan data omset {project_name}: {result['message']}"
                        )
            with button_cols[2]:
                if st.button(
                    "OMG, Ada yg slhhhh",
                    key=f"update_button_{project_name.lower().replace(' ', '_')}_marketplace",
                ):
                    st.session_state[preview_key] = False
                    st.rerun()
        else:
            st.warning("Tidak ada data valid untuk disimpan.")


def render_cpas_page(project_name: str, project_config: dict):
    nama_toko_list = project_config["Nama Toko"]
    akun_list = project_config["Akun"]

    st.header(f"Advertiser CPAS {project_name}")

    df_key = f"df_{project_name.lower().replace(' ', '_')}_cpas"
    preview_key = f"show_preview_{project_name.lower().replace(' ', '_')}_cpas"

    # Inisialisasi DataFrame
    initialize_cpas_data_session(
        project_name.lower().replace(" ", "_"),
        nama_toko_list,
        akun_list,
    )

    # Form input
    with st.form(f"form_{project_name.lower().replace(' ', '_')}_cpas"):
        st.session_state[df_key] = st.data_editor(
            st.session_state[df_key],
            num_rows="dynamic",
            width="stretch",
            column_config=get_cpas_column_config(nama_toko_list, akun_list),
        )
        submitted = st.form_submit_button("Simpan & Pratinjau")
        if submitted:
            st.session_state[preview_key] = True

    # Preview
    if st.session_state.get(preview_key, False):
        cleaned_df = st.session_state[df_key].dropna(how="all")
        if not cleaned_df.empty:
            st.markdown("---")
            st.subheader(
                f"Pratinjau Data untuk {project_name}_{datetime.today().strftime('%d-%m-%Y %H:%M:%S')}"
            )
            st.write("Silakan cek kembali data Anda sebelum disimpan permanen.")

            st.dataframe(
                cleaned_df,
                width="stretch",
                column_config=get_cpas_column_config(nama_toko_list, akun_list),
            )

            button_cols = st.columns([8, 3, 1.9])
            with button_cols[0]:
                if st.button(
                    "Ya, Simpan ke Database",
                    key=f"save_button_{project_name.lower().replace(' ', '_')}_cpas",
                ):
                    result = insert_advertiser_cpas_data(cleaned_df)
                    if result["status"] == "success":
                        st.success(result["message"])
                        st.session_state[preview_key] = False
                    else:
                        st.error(
                            f"Gagal menyimpan data CPAS {project_name}: {result['message']}"
                        )
            with button_cols[2]:
                if st.button(
                    "OMG, Ada yg slhhhh",
                    key=f"update_button_{project_name.lower().replace(' ', '_')}_cpas",
                ):
                    st.session_state[preview_key] = False
                    st.rerun()
        else:
            st.warning("Tidak ada data valid untuk disimpan.")


def format_number(num):
    """Fungsi helper untuk memformat angka menjadi B/M/K."""
    if pd.isna(num):
        return "Rp0"
    num = float(num)
    if num >= 1_000_000_000:
        return f"Rp{num / 1_000_000_000:.2f}B"
    if num >= 1_000_000:
        return f"Rp{num / 1_000_000:.2f}M"
    if num >= 1_000:
        return f"Rp{num / 1_000:.2f}K"
    return f"Rp{num:,.0f}"


def display_advertiser_dashboard(project_name: str):
    """
    Template untuk menampilkan dashboard advertiser untuk satu project spesifik,
    dengan filter tanggal di bagian atas.
    """
    try:
        df_adv = get_advertiser_marketplace_data()

        df_stores = get_dim_stores()
        df_map = get_map_project_stores()
        df_projects = get_dim_projects()

        df_mapping = pd.merge(df_map, df_stores, on="store_id")
        df_mapping = pd.merge(df_mapping, df_projects, on="project_id")
        store_to_project_map = pd.Series(
            df_mapping.project_name.values, index=df_mapping.nama_toko
        ).to_dict()

        df_adv["project"] = df_adv["nama_toko"].map(store_to_project_map)
        df_adv["tanggal"] = pd.to_datetime(df_adv["tanggal"]).dt.date
        df_adv.dropna(subset=["project"], inplace=True)

        df_project = df_adv[df_adv["project"] == project_name].copy()

    except Exception as e:
        st.error(f"Gagal memuat atau memproses data advertiser: {e}")
        st.stop()

    if df_project.empty:
        st.warning(
            f"Tidak ada data advertiser yang ditemukan untuk project {project_name}."
        )
        st.stop()

    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(" ")

    with col2:
        min_date = df_project["tanggal"].min()
        max_date = df_project["tanggal"].max()
        date_range = st.date_input(
            "Pilih Periode",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key=f"date_filter_{project_name}",
        )

    if len(date_range) != 2:
        st.warning("👈 Harap pilih rentang tanggal (tanggal mulai dan akhir).")
        st.stop()

    start_date, end_date = date_range
    df_filtered = df_project[
        (df_project["tanggal"] >= start_date) & (df_project["tanggal"] <= end_date)
    ]

    if df_filtered.empty:
        st.warning("Tidak ada data yang ditemukan untuk filter yang dipilih.")
        st.stop()

    total_spend = df_filtered["spend"].sum()
    total_revenue = df_filtered["gross_revenue"].sum()
    total_konversi = df_filtered["konversi"].sum()
    total_produk_terjual = df_filtered["produk_terjual"].sum()
    overall_roas = total_revenue / total_spend if total_spend > 0 else 0
    overall_cpa = total_spend / total_konversi if total_konversi > 0 else 0

    st.subheader("Ringkasan Performa Iklan")
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    kpi1.metric("Total Spend", value=format_number(total_spend))
    kpi2.metric("Total Gross Revenue", value=format_number(total_revenue))
    kpi3.metric("Total Konversi", value=f"{total_konversi:,.0f}")
    kpi4.metric("Total Produk Terjual", value=f"{int(total_produk_terjual):,.0f}")
    kpi5.metric("ROAS", value=f"{overall_roas:.2f}")
    kpi6.metric("CPA", value=format_number(overall_cpa))

    st.divider()
    st.subheader("Detail Performa per Toko")
    store_performance = (
        df_filtered.groupby("nama_toko")
        .agg(
            spend=("spend", "sum"),
            gross_revenue=("gross_revenue", "sum"),
            konversi=("konversi", "sum"),
            produk_terjual=("produk_terjual", "sum"),
        )
        .reset_index()
    )
    store_performance["ROAS"] = (
        store_performance["gross_revenue"] / store_performance["spend"]
    )
    store_performance["CPA"] = (
        store_performance["spend"] / store_performance["konversi"]
    )

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

    st.divider()
    st.subheader("Tren Harian: Gross Revenue vs Spend")
    time_series_data = df_filtered.groupby("tanggal")[["gross_revenue", "spend"]].sum()
    st.line_chart(time_series_data)


def display_budgeting_dashboard(project_id: int, project_name: str):
    """
    Menampilkan dashboard finansial lengkap dengan gauge chart dinamis.
    """
    st.title(f"📊 Dashboard Finansial: {project_name}")

    # --- Filter Periode di ATAS HALAMAN ---
    st.divider()
    col_header, col_filter = st.columns([2, 1])
    with col_header:
        st.header("Ringkasan Performa Omset")
    with col_filter:
        today = date.today()
        start_default = today.replace(day=1)
        date_range = st.date_input(
            "Pilih Periode Analisis:",
            value=(start_default, today),
            key=f"date_filter_{project_name}",
        )

    if not (isinstance(date_range, tuple) and len(date_range) == 2):
        st.warning("Harap pilih rentang tanggal yang valid (mulai dan akhir).")
        st.stop()

    tgl_awal, tgl_akhir = date_range
    st.caption(
        f"Periode: {tgl_awal.strftime('%d %B %Y')} s/d {tgl_akhir.strftime('%d %B %Y')}"
    )

    # --- Bagian 1: Analisis Omset (Tidak Berubah) ---
    total_target_omset = get_total_sales_target(project_id, tgl_awal, tgl_akhir)
    df_raw = get_financial_summary(project_id, tgl_awal, tgl_akhir)
    total_omset_aktual = 0
    if not df_raw.empty:
        df_omset_unik = df_raw[["tanggal", "omset_akrual"]].drop_duplicates()
        total_omset_aktual = df_omset_unik["omset_akrual"].sum()
    pencapaian_persen = (
        (float(total_omset_aktual) / float(total_target_omset) * 100)
        if total_target_omset > 0
        else 0
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Omset Aktual (Akrual)", f"Rp {total_omset_aktual:,.0f}")
    col2.metric("🎯 Target Omset", f"Rp {round(total_target_omset, -1):,.0f}")
    col3.metric("🏆 Pencapaian Target", f"{pencapaian_persen:.2f} %")

    st.divider()

    # --- Bagian 2: Analisis Performa Iklan (DIMODIFIKASI TOTAL) ---
    st.header("Analisis Performa Iklan")

    # Ambil data iklan sesuai filter tanggal
    df_ads = get_vw_ads_performance_summary(project_name, tgl_awal, tgl_akhir)

    if df_ads.empty:
        st.info("Tidak ada data performa iklan yang ditemukan untuk periode ini.")
    else:
        # Kalkulasi metrik keseluruhan untuk periode yang dipilih
        total_spending_ads = df_ads["total_spending"].sum()
        total_omset_ads = df_ads["total_omset"].sum()
        rasio_ads_overall = (
            (total_spending_ads / total_omset_ads * 100) if total_omset_ads > 0 else 0
        )

        year = tgl_akhir.year
        quarter = (tgl_akhir.month - 1) // 3 + 1
        target_rasio = get_target_ads_ratio(project_id, year, quarter)

        if target_rasio is None:
            st.warning(f"Target rasio untuk Q{quarter} {year} belum diatur.")
        else:
            safe_zone_start = target_rasio - 5

            if rasio_ads_overall < safe_zone_start:
                status_text = "Under"
                bar_color = "red"
            elif safe_zone_start <= rasio_ads_overall <= target_rasio:
                status_text = "Normal"
                bar_color = "green"
            else:
                status_text = "Over"
                bar_color = "red"

            df_ads["target_rasio"] = target_rasio
            conditions = [
                df_ads["ads_spend_percentage"] < safe_zone_start,
                (df_ads["ads_spend_percentage"] >= safe_zone_start)
                & (df_ads["ads_spend_percentage"] <= target_rasio),
            ]

            # Definisikan pilihan status sesuai kondisi
            choices = ["Under", "Normal"]

            # Tambahkan kolom 'target_rasio' dan 'status'
            df_ads["target_rasio"] = target_rasio
            df_ads["status"] = np.select(conditions, choices, default="Over")

            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=rasio_ads_overall,
                    number={"suffix": "%", "font": {"size": 40}},
                    title={
                        "text": f"Target: {target_rasio:.2f}%, Status: {status_text}",
                        "font": {"size": 20},
                    },
                    gauge={
                        "axis": {"range": [0, target_rasio * 2]},
                        "bar": {"color": bar_color},
                        "steps": [
                            {
                                "range": [safe_zone_start, target_rasio],
                                "color": "lightgreen",
                            },
                        ],
                        "threshold": {
                            "line": {"color": "black", "width": 4},
                            "value": target_rasio,
                        },
                    },
                )
            )
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig, width="stretch")

        st.divider()
        # --- Sub-Bagian Metrik Ringkasan ---
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric(
                label="💸 Total Ad Spend (MP + CPAS)",
                value=f"Rp {total_spending_ads:,.0f}",
            )
        with col2:
            st.metric(
                label="💰 Omset Berjalan (Total Pesanan)",
                value=f"Rp {total_omset_ads:,.0f}",
            )
        with col3:
            st.metric(
                label="📊 Rasio Ads/Omset",
                value=f"{rasio_ads_overall:.2f} %",
            )

        st.divider()

        # Tampilkan tabel detail performa iklan
        st.subheader("Detail Performa Iklan per Toko")
        st.dataframe(
            df_ads.style.format(
                {
                    "total_omset": "Rp {:,.0f}",
                    "total_spending": "Rp {:,.0f}",
                    "ads_spend_percentage": "{:.2f}%",
                    "target_rasio": "{:.2f}%",
                }
            ),
            width="stretch",
        )


def display_admin_dashboard(project_name: str):
    """
    Template dashboard Admin Marketplace untuk project spesifik.
    Mengikuti struktur logika dashboard general agar hasil (jumlah pcs, SKU, dsb) identik.
    """
    st.title(f"📦 Dashboard Admin: {project_name}")

    # --- MEMUAT DAN MEMPROSES DATA ---
    try:
        df_admin = get_vw_admin_shipments_delivery()
        df_stores = get_dim_stores()
        df_map = get_map_project_stores()
        df_projects = get_dim_projects()

        # Mapping antar tabel
        df_mapping = df_map.merge(df_stores, on="store_id").merge(
            df_projects, on="project_id"
        )

        store_to_project_map = pd.Series(
            df_mapping.project_name.values, index=df_mapping.nama_toko
        ).to_dict()

        df_admin["project"] = df_admin["nama_toko"].map(store_to_project_map)
        df_admin["timestamp_input_data"] = pd.to_datetime(
            df_admin["timestamp_input_data"]
        )
        df_admin.dropna(subset=["project"], inplace=True)

        # Filter hanya untuk project ini
        df_project = df_admin[df_admin["project"] == project_name].copy()

    except Exception as e:
        st.error(f"Gagal memuat atau memproses data: {e}")
        st.stop()

    if df_project.empty:
        st.warning(f"Tidak ada data admin ditemukan untuk project {project_name}.")
        st.stop()

    # --- FILTER DI ATAS HALAMAN ---
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        min_date = df_project["timestamp_input_data"].min().date()
        max_date = df_project["timestamp_input_data"].max().date()
        selected_date = st.date_input("Pilih Rentang Waktu", value=(min_date, max_date))
    with col2:
        list_brand = ["Semua Brand"] + sorted(
            df_project["nama_brand"].unique().tolist()
        )
        selected_brand = st.selectbox("Pilih Brand", list_brand)
    with col3:
        list_sesi = ["Semua Sesi"] + sorted(df_project["sesi"].unique().tolist())
        selected_sesi = st.selectbox("Pilih Sesi", list_sesi)
    st.divider()

    if not (isinstance(selected_date, tuple) and len(selected_date) == 2):
        st.warning("Harap pilih rentang tanggal yang valid (tanggal mulai dan akhir).")
        st.stop()

    # Terapkan filter
    start_date, end_date = selected_date
    df_filtered = df_project[
        (df_project["timestamp_input_data"].dt.date >= start_date)
        & (df_project["timestamp_input_data"].dt.date <= end_date)
    ]
    if selected_brand != "Semua Brand":
        df_filtered = df_filtered[df_filtered["nama_brand"] == selected_brand]
    if selected_sesi != "Semua Sesi":
        df_filtered = df_filtered[df_filtered["sesi"] == selected_sesi]

    if df_filtered.empty:
        st.warning("Tidak ada data yang cocok dengan filter yang dipilih.")
        st.stop()

    # --- METRIK RINGKASAN ---
    st.header("Ringkasan Data")
    m_col1, m_col2 = st.columns(2)
    m_col1.metric(
        label="🚚 **Total Resi Unik**", value=f"{df_filtered['no_resi'].nunique():,.0f}"
    )
    m_col2.metric(
        label="🏢 **Brand Aktif**", value=f"{df_filtered['nama_brand'].nunique()}"
    )

    st.divider()

    load_css()

    st.header("Analisis Detail")
    tab1, tab2, tab3 = st.tabs(
        ["📈 Tren Harian", "📊 Perbandingan", "📄 Laporan Excel"]
    )

    # --- TAB 1: Tren Harian ---
    with tab1:
        st.subheader("Tren Jumlah Resi Unik per Hari")
        daily_unique_resi = df_filtered.groupby(
            df_filtered["timestamp_input_data"].dt.date
        )["no_resi"].nunique()
        st.line_chart(daily_unique_resi)

    # --- TAB 2: Perbandingan ---
    with tab2:
        bar_brand, bar_sku = st.columns(2)
        with bar_brand:
            st.subheader("Resi Unik per Brand")
            brand_unique_resi = (
                df_filtered.groupby("nama_brand")["no_resi"]
                .nunique()
                .sort_values(ascending=False)
            )
            st.bar_chart(brand_unique_resi)
        with bar_sku:
            st.subheader("Resi Unik per SKU (Top 15)")
            sku_unique_resi = (
                df_filtered.groupby("sku")["no_resi"]
                .nunique()
                .sort_values(ascending=False)
                .head(15)
            )
            st.bar_chart(sku_unique_resi)

    # --- TAB 3: Laporan Excel ---
    with tab3:
        st.subheader("Buat Laporan Excel")
        if st.button("Buat Laporan", width="stretch", type="primary"):
            with st.spinner("Mohon tunggu, laporan Excel sedang dibuat..."):
                # === Tahapan Persiapan Data (SAMA SEPERTI SEBELUMNYA) ===

                # 1️⃣ Expand SKU untuk produk bundling
                df_expanded = df_filtered.assign(
                    sku=df_filtered["sku"].apply(expand_sku)
                )
                df_expanded = df_expanded.explode("sku").reset_index(drop=True)

                # 2️⃣ Sesuaikan 'jumlah_item' setelah proses explode
                df_expanded["jumlah_item"] = (
                    df_filtered["jumlah_item"]
                    .repeat(df_filtered["sku"].apply(expand_sku).str.len())
                    .reset_index(drop=True)
                )

                # 3️⃣ Proses SKU bundle PCS (misal: SKU-2-PCS)
                df_expanded[["sku", "jumlah_item"]] = df_expanded[
                    ["sku", "jumlah_item"]
                ].apply(parse_bundle_pcs, axis=1)

                # === Panggil Fungsi Laporan ===
                # Tidak perlu lagi melakukan groupby atau merge di sini.
                # Cukup teruskan hasil expand ke dalam fungsi.

                excel_bytes = create_visual_report(
                    report_df=df_expanded, original_df=df_expanded
                )

            st.success("✅ Laporan Excel Siap Diunduh!")
            file_name = f"Report_Admin_{project_name.replace(' ', '_')}_{pd.Timestamp.now():%Y%m%d}.xlsx"
            st.download_button(
                label="**Download Laporan Excel**",
                data=excel_bytes,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
            )


def display_advertiser_cpas_dashboard(project_name: str):
    """
    Template untuk menampilkan dashboard advertiser CPAS untuk satu project,
    dengan filter tanggal di bagian atas.
    """
    try:
        # 1. Ganti fungsi pengambilan data ke data CPAS
        df_adv = get_advertiser_cpas_data()

        # Bagian mapping project (tetap sama)
        df_stores = get_dim_stores()
        df_map = get_map_project_stores()
        df_projects = get_dim_projects()

        df_mapping = pd.merge(df_map, df_stores, on="store_id")
        df_mapping = pd.merge(df_mapping, df_projects, on="project_id")
        store_to_project_map = pd.Series(
            df_mapping.project_name.values, index=df_mapping.nama_toko
        ).to_dict()

        df_adv["project"] = df_adv["nama_toko"].map(store_to_project_map)
        df_adv["tanggal"] = pd.to_datetime(df_adv["tanggal"]).dt.date
        df_adv.dropna(subset=["project"], inplace=True)

        df_project = df_adv[df_adv["project"] == project_name].copy()

    except Exception as e:
        st.error(f"Gagal memuat atau memproses data advertiser CPAS: {e}")
        st.stop()

    if df_project.empty:
        st.warning(f"Tidak ada data advertiser CPAS untuk project {project_name}.")
        st.stop()

    # Bagian filter tanggal (tetap sama)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(" ")
    with col2:
        min_date = df_project["tanggal"].min()
        max_date = df_project["tanggal"].max()
        date_range = st.date_input(
            "Pilih Periode",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key=f"date_filter_cpas_{project_name}",  # Key diubah agar unik
        )

    if len(date_range) != 2:
        st.warning("👈 Harap pilih rentang tanggal (mulai dan akhir).")
        st.stop()

    start_date, end_date = date_range
    df_filtered = df_project[
        (df_project["tanggal"] >= start_date) & (df_project["tanggal"] <= end_date)
    ]

    if df_filtered.empty:
        st.warning("Tidak ada data yang ditemukan untuk filter yang dipilih.")
        st.stop()

    # 2. Perhitungan metrik disesuaikan (produk_terjual dihapus)
    total_spend = df_filtered["spend"].sum()
    total_revenue = df_filtered["gross_revenue"].sum()
    total_konversi = df_filtered["konversi"].sum()
    overall_roas = total_revenue / total_spend if total_spend > 0 else 0
    overall_cpa = total_spend / total_konversi if total_konversi > 0 else 0

    st.subheader("Ringkasan Performa Iklan")
    # 3. Tampilan KPI disesuaikan (kolom dikurangi menjadi 5)
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Spend", value=format_number(total_spend))
    kpi2.metric("Total Gross Revenue", value=format_number(total_revenue))
    kpi3.metric("Total Konversi", value=f"{total_konversi:,.0f}")
    kpi4.metric("ROAS", value=f"{overall_roas:.2f}")
    kpi5.metric("CPA", value=format_number(overall_cpa))

    st.divider()
    st.subheader("Detail Performa per Toko")
    # 4. Agregasi data per toko disesuaikan
    store_performance = (
        df_filtered.groupby("nama_toko")
        .agg(
            spend=("spend", "sum"),
            gross_revenue=("gross_revenue", "sum"),
            konversi=("konversi", "sum"),
        )
        .reset_index()
    )
    store_performance["ROAS"] = (
        store_performance["gross_revenue"] / store_performance["spend"]
    )
    store_performance["CPA"] = (
        store_performance["spend"] / store_performance["konversi"]
    )

    # 5. Tampilan tabel dan formatnya disesuaikan
    st.dataframe(
        store_performance.style.format(
            {
                "spend": "Rp{:,.0f}",
                "gross_revenue": "Rp{:,.0f}",
                "konversi": "{:,.0f}",
                "ROAS": "{:.2f}",
                "CPA": "Rp{:,.0f}",
            }
        ).bar(subset=["ROAS", "gross_revenue"], color="#649c4f", vmin=0),
        width="stretch",  # Menggunakan parameter baru
        hide_index=True,
    )

    # detail per akun
    st.divider()
    st.subheader("Detail Performa per Akun")
    # 4. Agregasi data per toko disesuaikan
    akun_performance = (
        df_filtered.groupby(["nama_toko", "akun"])
        .agg(
            spend=("spend", "sum"),
            gross_revenue=("gross_revenue", "sum"),
            konversi=("konversi", "sum"),
        )
        .reset_index()
    )
    akun_performance["ROAS"] = (
        akun_performance["gross_revenue"] / akun_performance["spend"]
    )
    akun_performance["CPA"] = akun_performance["spend"] / akun_performance["konversi"]

    # 5. Tampilan tabel dan formatnya disesuaikan
    st.dataframe(
        akun_performance.style.format(
            {
                "spend": "Rp{:,.0f}",
                "gross_revenue": "Rp{:,.0f}",
                "konversi": "{:,.0f}",
                "ROAS": "{:.2f}",
                "CPA": "Rp{:,.0f}",
            }
        ).bar(subset=["ROAS", "gross_revenue"], color="#649c4f", vmin=0),
        width="stretch",  # Menggunakan parameter baru
        hide_index=True,
    )

    st.divider()
    st.subheader("Tren Harian: Gross Revenue vs Spend")
    time_series_data = df_filtered.groupby("tanggal")[["gross_revenue", "spend"]].sum()
    st.line_chart(time_series_data)
