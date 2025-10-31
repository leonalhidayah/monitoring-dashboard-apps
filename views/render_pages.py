import time
from datetime import date, datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_preprocessor.utils import (
    create_daily_template,
    create_visual_report,
    expand_sku,
    get_cpas_column_config,
    get_marketplace_column_config,
    initialize_cpas_data_session,
    initialize_marketplace_data_session,
    parse_bundle_pcs,
    process_changes,
)
from database.db_manager import (
    get_advertiser_cpas_data,
    get_advertiser_marketplace_data,
    get_budget_ads_summary_by_project,
    get_budget_regular_summary_by_project,
    get_dim_projects,
    get_dim_stores,
    get_map_project_stores,
    get_target_ads_ratio,
    get_total_sales_target,
    get_vw_admin_shipments,
    get_vw_ads_performance_summary,
    get_vw_ragular_performance_summary,
    insert_advertiser_cpas_data,
    insert_advertiser_marketplace_data,
)
from views.config import REG_MAP_PROJECT, get_yesterday_in_jakarta
from views.style import format_rupiah, load_css


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
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Spend", value=format_number(total_spend), border=True)
    kpi2.metric("Total Gross Revenue", value=format_number(total_revenue), border=True)
    kpi3.metric("Total Konversi", value=f"{total_konversi:,.0f}", border=True)

    kpi4, kpi5, kpi6 = st.columns(3)
    kpi4.metric(
        "Total Produk Terjual", value=f"{int(total_produk_terjual):,.0f}", border=True
    )
    kpi5.metric("ROAS", value=f"{overall_roas:.2f}", border=True)
    kpi6.metric("CPA", value=format_number(overall_cpa), border=True)

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

    time_series_data = (
        df_filtered.groupby("tanggal")[["gross_revenue", "spend"]].sum().reset_index()
    )

    fig = px.line(
        time_series_data,
        x="tanggal",
        y=["gross_revenue", "spend"],
        markers=True,
        title="Perkembangan Gross Revenue vs Biaya Iklan",
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Jumlah (Rp)",
        yaxis_tickformat=".2s",
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
    )

    fig.update_traces(
        hovertemplate="<b>Date:</b> %{x|%d %B %Y}<br><b>Amount:</b> Rp %{y:,.0f}<extra></extra>"
    )

    st.plotly_chart(fig, use_container_width=True)


def display_admin_dashboard(project_name: str):
    """
    Template dashboard Admin Marketplace untuk project spesifik.
    Mengikuti struktur logika dashboard general agar hasil (jumlah pcs, SKU, dsb) identik.
    """
    st.title(f"📦 Dashboard Admin: {project_name}")

    # --- MEMUAT DAN MEMPROSES DATA ---
    try:
        df_admin = get_vw_admin_shipments()

        df_admin["timestamp_input_data"] = pd.to_datetime(
            df_admin["timestamp_input_data"]
        )

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
        label="🚚 **Total Resi Unik**",
        value=f"{df_filtered['no_resi'].nunique():,.0f}",
        border=True,
    )
    m_col2.metric(
        label="🏢 **Brand Aktif**",
        value=f"{df_filtered['nama_brand'].nunique()}",
        border=True,
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
    kpi1.metric("Total Spend", value=format_number(total_spend), border=True)
    kpi2.metric("Total Gross Revenue", value=format_number(total_revenue), border=True)
    kpi3.metric("Total Konversi", value=f"{total_konversi:,.0f}", border=True)
    kpi4.metric("ROAS", value=f"{overall_roas:.2f}", border=True)
    kpi5.metric("CPA", value=format_number(overall_cpa), border=True)

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
    time_series_data = (
        df_filtered.groupby("tanggal")[["gross_revenue", "spend"]].sum().reset_index()
    )

    fig = px.line(
        time_series_data,
        x="tanggal",
        y=["gross_revenue", "spend"],
        markers=True,
        title="Perkembangan Gross Revenue vs Biaya Iklan",
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Jumlah (Rp)",
        yaxis_tickformat=".2s",
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
    )

    fig.update_traces(
        hovertemplate="<b>Date:</b> %{x|%d %B %Y}<br><b>Amount:</b> Rp %{y:,.0f}<extra></extra>"
    )

    st.plotly_chart(fig, use_container_width=True)


def render_team_regular_tab(team_name, full_df, conn):
    """Merender seluruh UI dan logika untuk satu tab tim."""
    team_products_channels = REG_MAP_PROJECT[team_name]
    team_products = sorted(list(set([p[0] for p in team_products_channels])))

    with st.container(border=True):
        st.markdown("#### Generate Template Harian")
        template_date = st.date_input(
            "Pilih Tanggal", value=get_yesterday_in_jakarta(), key=f"date_{team_name}"
        )
        if st.button(
            "Buat Template Harian",
            type="primary",
            width="stretch",
            key=f"btn_{team_name}",
        ):
            with st.spinner(f"Membuat template untuk {team_name}..."):
                create_daily_template(conn, template_date, team_products_channels)
                st.toast(f"✅ Template untuk {team_name} siap!", icon="🎉")
                st.session_state[f"auto_filter_date_{team_name}"] = template_date
                st.cache_data.clear()
                if "full_df" in st.session_state:
                    del st.session_state.full_df
                time.sleep(2)
                st.rerun()
    st.divider()

    # 2. Filter & Tampilkan Data
    team_df = full_df[full_df["product_name"].isin(team_products)]
    default_start_date = st.session_state.get(
        f"auto_filter_date_{team_name}",
        team_df["performance_date"].min() if not team_df.empty else date.today(),
    )
    default_end_date = st.session_state.get(
        f"auto_filter_date_{team_name}",
        team_df["performance_date"].max() if not team_df.empty else date.today(),
    )

    st.markdown("### 🔎 Filter Data")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        start_date = st.date_input(
            "Dari Tanggal", default_start_date, key=f"start_date_{team_name}"
        )
    with f_col2:
        end_date = st.date_input(
            "Sampai Tanggal", default_end_date, key=f"end_date_{team_name}"
        )
    with f_col3:
        selected_product = st.selectbox(
            "Pilih Produk",
            options=["Semua Produk"] + team_products,
            key=f"product_{team_name}",
        )
    with f_col4:
        selected_channel = st.selectbox(
            "Pilih Channel",
            options=["Semua Channel", "CTWA", "Order Online"],
            key=f"channel_{team_name}",
        )

    if f"auto_filter_date_{team_name}" in st.session_state:
        del st.session_state[f"auto_filter_date_{team_name}"]

    start_date_pd = pd.to_datetime(start_date).date()
    end_date_pd = pd.to_datetime(end_date).date()
    filtered_df = team_df[
        (team_df["performance_date"] >= start_date_pd)
        & (team_df["performance_date"] <= end_date_pd)
    ]
    if selected_product != "Semua Produk":
        filtered_df = filtered_df[filtered_df["product_name"] == selected_product]
    if selected_channel != "Semua Channel":
        filtered_df = filtered_df[filtered_df["channel"] == selected_channel]

    st.info(f"Menampilkan {len(filtered_df)} dari {len(team_df)} total data tim.")

    # 3. Data Editor (dengan kolom Channel)
    edited_df = st.data_editor(
        filtered_df.reset_index(drop=True),
        num_rows="dynamic",
        key=f"editor_{team_name}",
        hide_index=True,
        column_order=(
            "performance_date",
            "product_name",
            "channel",
            "spend",
            "reach",
            "leads_generated",
            "leads_received",
            "deals_closed",
            "gross_revenue",
        ),
        column_config={
            "performance_date": st.column_config.DateColumn(
                "Tanggal", required=True, default=get_yesterday_in_jakarta()
            ),
            "product_name": st.column_config.SelectboxColumn(
                "Nama Produk", required=True, options=team_products
            ),
            "channel": st.column_config.SelectboxColumn(
                "Channel", options=["CTWA", "Order Online"], required=True
            ),
            "spend": st.column_config.NumberColumn(
                "Spend", format="accounting", required=True
            ),
            "reach": st.column_config.NumberColumn(
                "Reach", format="accounting", required=True
            ),
            "leads_generated": st.column_config.NumberColumn(
                "Leads (dari Iklan)", required=True
            ),
            "leads_received": st.column_config.NumberColumn("Leads Diterima (CS)"),
            "deals_closed": st.column_config.NumberColumn("Closing"),
            "gross_revenue": st.column_config.NumberColumn(
                "Gross Revenue", format="accounting"
            ),
        },
    )

    # 4. Tombol Simpan
    if st.button("Simpan Perubahan", key=f"save_{team_name}", type="primary"):
        with st.spinner("Menyimpan data..."):
            try:
                changes = st.session_state[f"editor_{team_name}"]
                added = len(changes.get("added_rows", []))
                edited = len(changes.get("edited_rows", {}))
                deleted = len(changes.get("deleted_rows", []))
                if added == 0 and edited == 0 and deleted == 0:
                    st.toast("Tidak ada perubahan untuk disimpan.", icon="🤷")
                else:
                    process_changes(conn, filtered_df, changes)
                    messages = []
                    if added > 0:
                        messages.append(f"{added} data ditambahkan")
                    if edited > 0:
                        messages.append(f"{edited} data diupdate")
                    if deleted > 0:
                        messages.append(f"{deleted} data dihapus")
                    final_message = ", ".join(messages)
                    st.toast(f"✅ Berhasil! {final_message}.", icon="🎉")
                    time.sleep(5)
                    st.cache_data.clear()
                    if "full_df" in st.session_state:
                        del st.session_state.full_df
                    st.rerun()
            except Exception as e:
                st.error(f"Terjadi kesalahan saat menyimpan: {e}")


# def render_order_flag_editor(conn):
#     """
#     Merender UI manajemen data penyesuaian menggunakan st.data_editor.
#     """
#     st.header("Manajemen Nominal Pesanan Dibatalkan")
#     st.caption(
#         "Gunakan editor di bawah untuk menambah, mengedit, atau menghapus data Return & Cancel."
#     )

#     if "flag_df" not in st.session_state:
#         st.session_state.flag_df = fetch_all_flags_reg(conn)

#     full_df = st.session_state.flag_df

#     # 2. Filter Data
#     st.markdown("### 🔎 Filter Data")
#     f_col1, f_col2, f_col3 = st.columns(3)

#     default_start = (
#         full_df["tanggal_input"].min()
#         if not full_df.empty
#         else date.today() - timedelta(days=30)
#     )
#     default_end = full_df["tanggal_input"].max() if not full_df.empty else date.today()

#     with f_col1:
#         start_date = st.date_input("Dari Tanggal", default_start, key="flag_start_date")
#     with f_col2:
#         end_date = st.date_input("Sampai Tanggal", default_end, key="flag_end_date")
#     with f_col3:
#         kategori_filter = st.selectbox(
#             "Kategori", ["Semua Kategori", "RETURN", "CANCEL"], key="flag_kategori"
#         )

#     filtered_df = full_df[
#         (full_df["tanggal_input"] >= start_date)
#         & (full_df["tanggal_input"] <= end_date)
#     ]
#     if kategori_filter != "Semua Kategori":
#         filtered_df = filtered_df[filtered_df["kategori"] == kategori_filter]

#     st.info(f"Menampilkan {len(filtered_df)} dari {len(full_df)} total data.")

#     # 3. Data Editor
#     edited_df = st.data_editor(
#         filtered_df,  # Tidak perlu reset_index() jika kita menyimpan index asli
#         num_rows="dynamic",
#         key="flag_editor",
#         hide_index=True,
#         # PERBAIKAN: Hapus kolom id dan timestamp dari tampilan utama
#         column_order=("tanggal_input", "kategori", "nominal_adjustment", "keterangan"),
#         column_config={
#             # PERBAIKAN: Sembunyikan kolom id dan timestamp dari editor
#             "id_flag": None,
#             "timestamp_created": None,
#             "tanggal_input": st.column_config.DateColumn(
#                 "Tanggal", required=True, default=get_now_in_jakarta()
#             ),
#             "kategori": st.column_config.SelectboxColumn(
#                 "Kategori",
#                 options=["RETURN", "CANCEL"],
#                 required=True,
#                 default="RETURN",
#             ),
#             "nominal_adjustment": st.column_config.NumberColumn(
#                 "Nominal", format="accounting", required=True, min_value=0
#             ),
#             "keterangan": st.column_config.TextColumn("Keterangan"),
#         },
#         width="stretch",
#     )

#     # 4. Tombol Simpan
#     if st.button(
#         "Simpan Perubahan",
#         key="flag_save_button",
#         type="primary",
#         width="stretch",
#     ):
#         with st.spinner("Menyimpan perubahan..."):
#             try:
#                 changes = st.session_state["flag_editor"]

#                 if not any(changes.values()):
#                     st.toast("Tidak ada perubahan untuk disimpan.", icon="🤷")
#                 else:
#                     process_flag_changes_reg(conn, filtered_df, changes)

#                     st.toast("✅ Perubahan berhasil disimpan!", icon="🎉")
#                     time.sleep(2)
#                     del st.session_state.flag_df
#                     st.rerun()

#             except Exception as e:
#                 st.error(f"Terjadi kesalahan saat menyimpan: {e}")


def display_budgeting_regular_dashboard(project_id: int, project_name: str):
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
    df_raw = get_budget_regular_summary_by_project(
        start_date=tgl_awal,
        end_date=tgl_akhir,
    )
    total_omset_aktual = 0
    if not df_raw.empty:
        # total_omset_aktual = df_omset_unik["omset_akrual"].sum()
        total_omset_aktual = df_raw["akrual_basis"].sum()
    pencapaian_persen = (
        (float(total_omset_aktual) / float(total_target_omset) * 100)
        if total_target_omset > 0
        else 0
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("Omset Aktual (Akrual)", f"Rp {total_omset_aktual:,.0f}", border=True)
    col2.metric("Target Omset", f"Rp {round(total_target_omset, -1):,.0f}", border=True)
    col3.metric("Pencapaian Target", f"{pencapaian_persen:.2f} %", border=True)

    st.divider()

    st.header("Analisis Performa Iklan")

    df_ads = get_vw_ragular_performance_summary(tgl_awal, tgl_akhir)

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
                bar_color = "tomato"
            elif safe_zone_start <= rasio_ads_overall <= target_rasio:
                status_text = "Normal"
                bar_color = "green"
            else:
                status_text = "Over"
                bar_color = "tomato"

            df_ads["target_rasio"] = target_rasio
            conditions = [
                df_ads["ads_spend_percentage_net"] < safe_zone_start,
                (df_ads["ads_spend_percentage_net"] >= safe_zone_start)
                & (df_ads["ads_spend_percentage_net"] <= target_rasio),
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
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        # --- Sub-Bagian Metrik Ringkasan ---
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric(
                label="Total Ad Spend Regular",
                value=f"Rp {total_spending_ads:,.0f}",
                border=True,
            )
        with col2:
            st.metric(
                label="Omset Berjalan (Gross Revenue)",
                value=f"Rp {total_omset_ads:,.0f}",
                border=True,
            )
        with col3:
            st.metric(
                label="Rasio Ads/Omset",
                value=f"{rasio_ads_overall:.2f} %",
                border=True,
            )

        st.divider()

        st.subheader("Total Omset Berjalan vs Ads Spend")

        df_omset_daily = (
            df_ads.groupby("tanggal")[["total_omset", "total_spending"]]
            .sum()
            .reset_index()
            .rename(
                columns={
                    "total_omset": "Total Omset Berjalan",
                    "total_spending": "Total Ad Spend",
                }
            )
        )

        fig_line = px.line(
            df_omset_daily,
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
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
            ),
        )
        st.plotly_chart(fig_line, use_container_width=True)

        st.divider()

        # Tampilkan tabel detail performa iklan
        st.subheader("Detail Performa Iklan Regular")
        st.dataframe(
            df_ads.style.format(
                {
                    "total_omset_bruto": "Rp {:,.0f}",
                    "total_penyesuaian": "Rp {:,.0f}",
                    "total_omset": "Rp {:,.0f}",
                    "total_spending": "Rp {:,.0f}",
                    "ads_spend_percentage_net": "{:.2f}%",
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
            ),
            width="stretch",
        )


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


# --- FUNGSI MODULAR (PECAHAN DARI FUNGSI UTAMA) ---


def display_omset_summary(project_id, project_name, tgl_awal, tgl_akhir):
    """Menampilkan bagian ringkasan performa omset."""
    st.header("Ringkasan Performa Omset")

    # Ambil data (akan menggunakan cache jika filter sama)
    total_target_omset = get_total_sales_target(project_id, tgl_awal, tgl_akhir)
    df_raw = get_budget_ads_summary_by_project(
        project_name=project_name,
        start_date=tgl_awal,
        end_date=tgl_akhir,
    )

    total_omset_aktual = 0
    if not df_raw.empty:
        total_omset_aktual = df_raw["akrual_basis"].sum()

    pencapaian_persen = (
        (float(total_omset_aktual) / float(total_target_omset) * 100)
        if total_target_omset > 0
        else 0
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Omset Aktual (Akrual)", format_rupiah(total_omset_aktual), border=True)
    col2.metric(
        "Target Omset", format_rupiah(round(total_target_omset, -1)), border=True
    )
    col3.metric("Pencapaian Target", f"{pencapaian_persen:.2f} %", border=True)


def display_ads_performance(project_id, project_name, tgl_awal, tgl_akhir):
    """Menampilkan seluruh bagian analisis performa iklan."""
    st.header("Analisis Performa Iklan")

    # Ambil data Iklan
    df_ads = get_vw_ads_performance_summary(project_name, tgl_awal, tgl_akhir)
    if df_ads.empty:
        st.info("Tidak ada data performa iklan yang ditemukan untuk periode ini.")
        return  # Keluar dari fungsi jika tidak ada data

    # Ambil Target Rasio
    year = tgl_akhir.year
    quarter = (tgl_akhir.month - 1) // 3 + 1
    target_rasio = get_target_ads_ratio(project_id, year, quarter)

    # --- PERBAIKAN BUG ---
    # Cek jika target_rasio tidak ada, hentikan eksekusi bagian ini
    if target_rasio is None or target_rasio == 0:
        st.warning(
            f"Target rasio untuk Q{quarter} {year} belum diatur. Analisis iklan tidak dapat dilanjutkan."
        )
        return  # Keluar dari fungsi

    # Kalkulasi metrik keseluruhan
    total_spending_ads = df_ads["total_spending"].sum()
    total_omset_ads = df_ads["total_omset"].sum()
    rasio_ads_overall = (
        (total_spending_ads / total_omset_ads * 100) if total_omset_ads > 0 else 0
    )

    # Tentukan zona aman dan status (logika ini hanya perlu sekali)
    safe_zone_start = target_rasio - 5  # Asumsi 5% adalah buffer

    if rasio_ads_overall < safe_zone_start:
        status_text = "Under"
        bar_color = "tomato"
    elif safe_zone_start <= rasio_ads_overall <= target_rasio:
        status_text = "Normal"
        bar_color = "green"
    else:
        status_text = "Over"
        bar_color = "tomato"

    # --- 1. Gauge Chart ---
    fig_gauge = go.Figure(
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
                    {"range": [safe_zone_start, target_rasio], "color": "lightgreen"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 4},
                    "value": target_rasio,
                },
            },
        )
    )
    fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.divider()

    # --- 2. Metrik Iklan ---
    col1, col2, col3 = st.columns([1, 1, 1])
    col1.metric("Total Ad Spend", format_rupiah(total_spending_ads), border=True)
    col2.metric(
        "Omset Berjalan (Total Pesanan)", format_rupiah(total_omset_ads), border=True
    )
    col3.metric("Rasio Ads/Omset", f"{rasio_ads_overall:.2f} %", border=True)

    st.divider()

    # --- 3. Line Chart Harian ---
    st.subheader("Total Omset Berjalan vs Ads Spend Harian")
    try:
        df_ads["tanggal"] = pd.to_datetime(df_ads["tanggal"]).dt.date
    except Exception as e:
        st.error(f"Gagal memproses kolom 'tanggal' di df_ads. Detail: {e}")
        st.stop()

    df_omset_daily = (
        df_ads.groupby("tanggal")[["total_omset", "total_spending"]]
        .sum()
        .reset_index()
        .rename(
            columns={
                "total_omset": "Total Omset Berjalan",
                "total_spending": "Total Ad Spend",
            }
        )
    )

    fig_line = px.line(
        df_omset_daily,
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

    # --- 4. Tabel Detail per Toko ---
    st.subheader("Detail Performa Iklan per Toko")

    df_ads_by_store = (
        df_ads.groupby("nama_toko")
        .agg({"total_omset": "sum", "total_spending": "sum"})
        .reset_index()
    )
    df_ads_by_store["ads_spend_percentage"] = (
        (df_ads_by_store["total_spending"] / df_ads_by_store["total_omset"]) * 100
    ).fillna(0)

    # Gunakan fungsi helper refactoring
    df_ads_by_store = calculate_ads_status(
        df_ads_by_store, target_rasio, safe_zone_start
    )
    styled_df_by_store = style_ads_dataframe(df_ads_by_store)
    st.dataframe(styled_df_by_store, width="stretch")

    # --- 5. Tabel Detail Harian (dalam Expander) ---
    with st.expander("Detail Performa Iklan Toko per Tanggal"):
        # Gunakan fungsi helper refactoring
        df_ads_detailed = calculate_ads_status(df_ads, target_rasio, safe_zone_start)
        styled_df_detailed = style_ads_dataframe(df_ads_detailed)
        st.dataframe(styled_df_detailed, width="stretch")


# --- FUNGSI UTAMA (SEKARANG JAUH LEBIH RAPI) ---


def display_budgeting_dashboard(project_id: int, project_name: str):
    """
    Menampilkan dashboard finansial lengkap dengan gauge chart dinamis.
    (Versi modular dan optimal)
    """
    st.title(f"📊 Dashboard Finansial: {project_name}")

    # --- Filter Periode di ATAS HALAMAN ---
    st.divider()
    col_header, col_filter = st.columns([2, 1])
    with col_header:
        # Pindahkan header Omset ke dalam fungsinya sendiri
        pass
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

    # --- Bagian 1: Analisis Omset (Modular) ---
    display_omset_summary(project_id, project_name, tgl_awal, tgl_akhir)

    st.divider()

    # --- Bagian 2: Analisis Iklan (Modular) ---
    display_ads_performance(project_id, project_name, tgl_awal, tgl_akhir)
