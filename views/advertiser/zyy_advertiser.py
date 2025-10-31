import streamlit as st

from database.db_connection import get_connection
from views.config import ADV_CPAS_MAP_PROJECT, ADV_MP_MAP_PROJECT
from views.management.generic_editor_renderer import render_generic_editor
from views.management.management_config import ADVERTISER_TABLE_CONFIGS
from views.render_pages import render_cpas_page, render_marketplace_page
from views.style import load_css

load_css()

project_name = "Zhi Yang Yao"

tab1, tab2, tab3 = st.tabs(["Marketplace", "CPAS", "Management"])

with tab1:
    render_marketplace_page(project_name, ADV_MP_MAP_PROJECT[project_name])

with tab2:
    render_cpas_page(project_name, ADV_CPAS_MAP_PROJECT[project_name])

with tab3:
    # =============================================================================
    # ORKESTRATOR UTAMA APLIKASI DATA MANAGEMENT
    # =============================================================================

    # --- Konfigurasi Halaman ---
    st.set_page_config(
        page_title="Data Management System", page_icon="⚙️", layout="wide"
    )

    st.title("Data Management System")
    st.caption(
        "Sistem terpusat untuk menambah, mengubah, dan menghapus data operasional."
    )
    st.divider()

    # --- PEMILIHAN TABEL DI HALAMAN UTAMA (MENGGANTIKAN SIDEBAR) ---
    st.markdown("#### 📖 Pilih Modul Data")

    # Membuat pilihan dropdown secara dinamis dari semua "blueprint" yang ada
    table_options = {
        config["display_name"]: key for key, config in ADVERTISER_TABLE_CONFIGS.items()
    }

    selected_display_name = st.selectbox(
        "Pilih data yang akan dikelola:",
        options=table_options.keys(),  # Tampilkan nama yang ramah
        key="selected_table",
    )

    # Dapatkan kunci internal (misal: "finance_omset") dari nama yang dipilih
    selected_table_key = table_options[selected_display_name]

    st.divider()

    # --- Halaman Utama ---
    conn = None
    try:
        conn = get_connection()
        if conn:
            # Ambil "blueprint" (konfigurasi) untuk tabel yang dipilih
            active_config = ADVERTISER_TABLE_CONFIGS[selected_table_key]

            # Panggil "Mesin UI Generik" kita, ia akan melakukan sisanya!
            render_generic_editor(conn=conn, config=active_config)

        else:
            st.error("Gagal terhubung ke database. Periksa koneksi Anda.")

    except Exception as e:
        st.error(f"Terjadi kesalahan di aplikasi utama: {e}")

    finally:
        if conn:
            conn.close()
