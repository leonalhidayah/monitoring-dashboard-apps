import streamlit as st

from database.db_connection import get_connection

# Impor "jantung" dari sistem kita
from views.management.generic_editor_renderer import render_generic_editor
from views.management.management_config import REGULAR_TABLE_CONFIGS

# =============================================================================
# ORKESTRATOR UTAMA APLIKASI DATA MANAGEMENT
# =============================================================================


st.title("Regular Data Management System")
st.caption(
    "Sistem terpusat untuk menambah, mengubah, dan menghapus data operasional regular."
)
st.divider()

st.markdown("#### Pilih Data")

table_options = {
    config["display_name"]: key for key, config in REGULAR_TABLE_CONFIGS.items()
}

selected_display_name = st.selectbox(
    "Pilih data yang akan dikelola:",
    options=table_options.keys(),
    key="selected_table",
)

selected_table_key = table_options[selected_display_name]

st.divider()

conn = None
try:
    # conn = st.connection("pipeline_test_db", type="sql")
    conn = get_connection()
    if conn:
        active_config = REGULAR_TABLE_CONFIGS[selected_table_key]

        render_generic_editor(conn=conn, config=active_config)

    else:
        st.error("Gagal terhubung ke database. Periksa koneksi Anda.")

except Exception as e:
    st.error(f"Terjadi kesalahan di aplikasi utama: {e}")
finally:
    if conn:
        conn.close()
