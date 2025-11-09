import streamlit as st

from database.db_connection import get_engine

# Impor "jantung" dari sistem kita
from views.management.generic_editor_renderer import render_generic_editor
from views.management.management_config import ADVERTISER_TABLE_CONFIGS

project_name = "Zhi Yang Yao"

st.title("Advertiser Data Management System")
st.caption(
    "Sistem terpusat untuk menambah, mengubah, dan menghapus data operasional advertiser."
)
st.divider()

st.markdown("#### Pilih Data")

table_options = {
    config["display_name"]: key for key, config in ADVERTISER_TABLE_CONFIGS.items()
}

selected_display_name = st.selectbox(
    "Pilih data yang akan dikelola:",
    options=table_options.keys(),
    key="selected_table",
)

selected_table_key = table_options[selected_display_name]

st.divider()

engine = None
try:
    engine = get_engine()

    if engine:
        active_config = ADVERTISER_TABLE_CONFIGS[selected_table_key]

        render_generic_editor(
            engine, config=active_config, project_context=project_name
        )

    else:
        st.error("Gagal terhubung ke database. Periksa koneksi Anda.")

except Exception as e:
    st.error(f"Terjadi kesalahan di aplikasi utama: {e}")
