import time
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from database.db_generic_crud import fetch_table_data, process_generic_changes
from pipeline.config.variables import get_now_in_jakarta, get_yesterday_in_jakarta


def render_generic_editor(conn, config: dict):
    """
    Merender antarmuka pengguna (UI) data editor yang sepenuhnya dinamis
    berdasarkan konfigurasi yang diberikan.

    Args:
        conn: Koneksi database yang aktif.
        config (dict): Blueprint/konfigurasi untuk tabel yang akan dirender.
    """

    source_name = config.get("source_view", config.get("table_name"))
    table_key = config.get("target_table", config.get("table_name"))
    display_name = config["display_name"]
    session_key = f"df_{table_key}"

    if session_key not in st.session_state:
        st.session_state[session_key] = fetch_table_data(conn, source_name)

    full_df = st.session_state[session_key]

    st.header(f"⚙️ Manajemen Data: {display_name}")
    st.divider()

    st.markdown("### 🔎 Filter Data")

    filter_values = {}
    filter_configs = config.get("filters", [])
    filter_cols = st.columns(len(filter_configs) if filter_configs else 1)

    if not filter_configs:
        filter_cols = [st.container()]

    for i, f_config in enumerate(filter_configs):
        with filter_cols[i]:
            col_name = f_config["column_name"]

            label = f_config["label"]

            if f_config["filter_type"] == "date_range":
                range_type = f_config.get("date_range_type", "full_range")

                if range_type == "today":
                    default_start = get_now_in_jakarta().date()

                    default_end = get_now_in_jakarta().date()

                elif range_type == "yesterday":
                    default_start = get_yesterday_in_jakarta()

                    default_end = get_yesterday_in_jakarta()

                else:
                    default_start = (
                        full_df[col_name].min()
                        if not full_df.empty and col_name in full_df
                        else date.today() - timedelta(days=30)
                    )

                    default_end = (
                        full_df[col_name].max()
                        if not full_df.empty and col_name in full_df
                        else date.today()
                    )

                date_range_val = st.date_input(
                    label,
                    value=(default_start, default_end),
                    key=f"daterange_{table_key}_{col_name}",
                )

                if len(date_range_val) == 1:
                    st.warning(
                        "☝️ Harap pilih tanggal akhir untuk menyelesaikan rentang.",
                        icon="⚠️",
                    )

                    st.stop()

                filter_values[col_name] = date_range_val

            elif f_config["filter_type"] == "selectbox":
                options = []

                if "options_source" in f_config:
                    src = f_config["options_source"]

                    try:
                        options_df = pd.read_sql(
                            f'SELECT DISTINCT "{src["column"]}" FROM {src["table"]} ORDER BY 1',
                            conn,
                        )

                        options = ["Semua Kategori"] + options_df[
                            src["column"]
                        ].tolist()

                    except Exception as e:
                        st.warning(f"Gagal memuat filter: {e}")

                        options = ["Semua Kategori"]

                elif "options" in f_config:
                    options = f_config["options"]

                selected_val = st.selectbox(
                    label, options, key=f"select_{table_key}_{col_name}"
                )

                if selected_val == "Semua Kategori":
                    filter_values[col_name] = None

                else:
                    filter_values[col_name] = selected_val

    filtered_df = full_df.copy()
    active_date_range = None

    for col_name, value in filter_values.items():
        if value is None:
            continue

        if isinstance(value, tuple):
            active_date_range = value

            filtered_df[col_name] = pd.to_datetime(filtered_df[col_name]).dt.date
            filtered_df = filtered_df[
                (filtered_df[col_name] >= value[0])
                & (filtered_df[col_name] <= value[1])
            ]
        else:
            filtered_df = filtered_df[filtered_df[col_name] == value]

    date_period_str = ""
    if active_date_range:
        start_date, end_date = active_date_range

        start_str = start_date.strftime("%d/%m/%Y")
        end_str = end_date.strftime("%d/%m/%Y")

        if start_date == end_date:
            date_period_str = f"periode {start_str}"
        else:
            date_period_str = f"periode {start_str} - {end_str}"

    st.info(
        f"Menampilkan **{len(filtered_df)}** dari **{len(full_df)}** total data dari **{date_period_str}**."
    )
    st.divider()

    st.markdown("### ✏️ Editor Data")

    df_to_edit = filtered_df.reset_index(drop=True)

    editor_key = f"editor_{table_key}"
    edited_df = st.data_editor(
        df_to_edit,
        num_rows="dynamic",
        key=editor_key,
        hide_index=True,
        column_order=config.get("column_order"),
        column_config=config["column_config"],
        width="stretch",
    )

    if st.button(
        "Simpan Perubahan",
        key=f"save_{table_key}",
        type="primary",
        width="stretch",
    ):
        with st.spinner("Menyimpan perubahan..."):
            try:
                changes = st.session_state[editor_key]

                added_count = len(changes.get("added_rows", []))
                edited_count = len(changes.get("edited_rows", {}))
                deleted_count = len(changes.get("deleted_rows", []))

                if not any([added_count, edited_count, deleted_count]):
                    st.toast("Tidak ada perubahan untuk disimpan.", icon="🤷")
                else:
                    process_generic_changes(conn, config, df_to_edit, changes)

                    messages = []
                    if added_count > 0:
                        messages.append(f"**{added_count}** data ditambahkan")
                    if edited_count > 0:
                        messages.append(f"**{edited_count}** data diupdate")
                    if deleted_count > 0:
                        messages.append(f"**{deleted_count}** data dihapus")

                    final_message = ", ".join(messages)

                    st.toast(f"✅ Berhasil! {final_message}.", icon="🎉")

                    time.sleep(3)
                    del st.session_state[session_key]
                    st.rerun()

            except Exception as e:
                st.error(f"Terjadi kesalahan saat menyimpan: {e}")
