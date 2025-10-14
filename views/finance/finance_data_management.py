import streamlit as st

# Impor "jantung" dari sistem kita
from database.db_connection import get_connection
from views.management.generic_editor_renderer import render_generic_editor
from views.management.management_config import FINANCE_TABLE_CONFIGS

# =============================================================================
# ORKESTRATOR UTAMA APLIKASI DATA MANAGEMENT
# =============================================================================

# --- Konfigurasi Halaman ---
# st.set_page_config(page_title="Data Management System", page_icon="⚙️", layout="wide")

st.title("Finance Data Management System")
st.caption(
    "Sistem terpusat untuk menambah, mengubah, dan menghapus data operasional finance."
)
st.divider()

# --- PEMILIHAN TABEL DI HALAMAN UTAMA (MENGGANTIKAN SIDEBAR) ---
st.markdown("#### Pilih Data")

# Membuat pilihan dropdown secara dinamis dari semua "blueprint" yang ada
table_options = {
    config["display_name"]: key for key, config in FINANCE_TABLE_CONFIGS.items()
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
        active_config = FINANCE_TABLE_CONFIGS[selected_table_key]

        # Panggil "Mesin UI Generik" kita, ia akan melakukan sisanya!
        render_generic_editor(conn=conn, config=active_config)

    else:
        st.error("Gagal terhubung ke database. Periksa koneksi Anda.")

except Exception as e:
    st.error(f"Terjadi kesalahan di aplikasi utama: {e}")

finally:
    if conn:
        conn.close()
