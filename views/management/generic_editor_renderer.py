import copy
import logging
import time
from datetime import date, timedelta

import streamlit as st

from database.db_generic_crud import (
    fetch_distinct_options,
    fetch_filtered_data,
    process_generic_changes,
)


def render_generic_editor(engine, config: dict, project_context: str = None):
    """
    Merender UI data editor yang dinamis, stabil, dan responsif.
    """
    source_name = config.get("source_view", config.get("table_name"))
    table_key = config.get("target_table", config.get("table_name"))
    display_name = config["display_name"]

    # --- HEADER SECTION ---
    st.header(f"⚙️ Manajemen Data: {display_name}")

    st.divider()
    # --- 1. FILTER SECTION ---
    with st.container():
        st.subheader("🔎 Filter Data")

        filter_values = {}
        filter_configs = config.get("filters", [])

        base_filter = {}
        ui_filter_configs = []

        if project_context:
            base_filter["project_name"] = project_context
            for f in filter_configs:
                if f["column_name"] != "project_name":
                    ui_filter_configs.append(f)
        else:
            base_filter = {}
            ui_filter_configs = filter_configs
        if ui_filter_configs:
            cols = st.columns(len(ui_filter_configs))
            for i, f_config in enumerate(ui_filter_configs):
                with cols[i]:
                    col_name = f_config["column_name"]
                    label = f_config["label"]
                    f_type = f_config["filter_type"]
                    widget_key = f"filter_{table_key}_{col_name}"

                    # Type: Date Range
                    if f_type == "date_range":
                        range_type = f_config.get("date_range_type", "last_30_days")
                        if range_type == "today":
                            defaults = (date.today(), date.today())
                        elif range_type == "yesterday":
                            yesterday = date.today() - timedelta(days=1)
                            defaults = (yesterday, yesterday)
                        else:
                            defaults = (date.today() - timedelta(days=30), date.today())

                        date_val = st.date_input(label, value=defaults, key=widget_key)
                        if isinstance(date_val, tuple) and len(date_val) == 2:
                            filter_values[col_name] = date_val
                        else:
                            st.warning("Set tanggal akhir.", icon="⚠️")

                    # Type: Selectbox
                    elif f_type == "selectbox":
                        options = ["Semua Kategori"]
                        if "options_source" in f_config:
                            src = f_config["options_source"]
                            context_to_pass = None
                            if src.get("needs_project_context") and project_context:
                                context_to_pass = project_context
                            db_opts = fetch_distinct_options(
                                engine,
                                src["table"],
                                src["column"],
                                project_context=context_to_pass,  # <-- MODIFIKASI
                            )
                            options += db_opts

                        elif "options" in f_config:
                            options += f_config["options"]

                        selected = st.selectbox(label, options=options, key=widget_key)
                        if selected != "Semua Kategori":
                            filter_values[col_name] = selected
        else:
            st.info("Tidak ada konfigurasi filter untuk tabel ini.")

    # --- 2. DATA FETCHING ---
    with st.spinner("⏳ Sedang memuat data..."):
        filtered_df = fetch_filtered_data(
            _engine=engine,
            table_name=source_name,
            active_filters=filter_values,
            base_filter=base_filter,
        )

    active_date = next(
        (v for v in filter_values.values() if isinstance(v, tuple)), None
    )
    if active_date:
        s_str, e_str = (
            active_date[0].strftime("%d/%m/%Y"),
            active_date[1].strftime("%d/%m/%Y"),
        )
        period_str = (
            f"tanggal **{s_str}**"
            if s_str == e_str
            else f"periode **{s_str} - {e_str}**"
        )
    else:
        period_str = "**semua periode**"

    st.caption(f"Menampilkan **{len(filtered_df):,}** baris data untuk {period_str}.")

    # --- 4. EDITOR SECTION ---
    col_header, col_reset = st.columns([0.80, 0.2])
    with col_header:
        st.subheader("✏️ Editor Data")
    with col_reset:
        if st.button(
            "Refresh",
            key=f"refresh_{table_key}",
            help="Ambil data terbaru dari database",
            width="stretch",
        ):
            st.cache_data.clear()
            st.rerun()

    df_to_edit = filtered_df.reset_index(drop=True)
    editor_key = f"editor_{table_key}"

    dynamic_column_config = copy.deepcopy(config.get("column_config", {}))

    if project_context and "nama_toko" in dynamic_column_config:
        try:
            toko_list_for_project = fetch_distinct_options(
                _engine=engine,
                table_name="dim_stores",
                column_name="nama_toko",
                project_context=project_context,
            )

            # 4. Ganti placeholder 'options=[]' dengan daftar yang sudah difilter
            dynamic_column_config["nama_toko"] = st.column_config.SelectboxColumn(
                "Nama Toko",
                options=toko_list_for_project,
                required=True,
            )
        except Exception as e:
            logging.warning(f"Gagal memuat opsi dinamis 'nama_toko': {e}")
            pass

    if project_context and "akun" in dynamic_column_config:
        try:
            list_for_project = fetch_distinct_options(
                _engine=engine,
                table_name="dim_cpas_accounts",
                column_name="nama_akun_cpas",
                project_context=project_context,
            )

            # 4. Ganti placeholder 'options=[]' dengan daftar yang sudah difilter
            dynamic_column_config["akun"] = st.column_config.SelectboxColumn(
                "Pilih Akun",
                options=list_for_project,
                required=True,
            )
        except Exception as e:
            logging.warning(f"Gagal memuat opsi dinamis 'nama_toko': {e}")
            pass

    edited_df = st.data_editor(
        df_to_edit,
        num_rows="dynamic",
        key=editor_key,
        hide_index=True,
        column_order=config.get("column_order"),
        column_config=dynamic_column_config,
        width="stretch",
    )

    btn_col1, btn_col2 = st.columns([0.8, 0.2])
    with btn_col2:
        save_clicked = st.button(
            "Simpan",
            key=f"save_{table_key}",
            type="primary",
            width="stretch",
        )

    # --- 5. SAVE LOGIC HANDLER ---
    if save_clicked:
        with st.status("Memproses perubahan...", expanded=True) as status:
            try:
                changes = st.session_state[editor_key]
                added = len(changes.get("added_rows", []))
                edited = len(changes.get("edited_rows", {}))
                deleted = len(changes.get("deleted_rows", []))

                if not any([added, edited, deleted]):
                    status.update(
                        label="🤷 Tidak ada perubahan yang terdeteksi.",
                        state="complete",
                        expanded=False,
                    )
                    time.sleep(1)  # Beri waktu user membaca status sebelum menutup
                else:
                    st.write("Menyimpan ke database...")
                    # Panggil fungsi proses generic (pastikan fungsi ini sudah optimized)
                    process_generic_changes(engine, config, df_to_edit, changes)

                    # Pesan sukses detail
                    msg_parts = []
                    if added:
                        msg_parts.append(f"{added} ditambah")
                    if edited:
                        msg_parts.append(f"{edited} diubah")
                    if deleted:
                        msg_parts.append(f"{deleted} dihapus")

                    status.update(
                        label=f"✅ Berhasil! ({', '.join(msg_parts)})",
                        state="complete",
                        expanded=False,
                    )

                    st.cache_data.clear()
                    time.sleep(3)
                    st.rerun()

            except Exception as e:
                status.update(label="❌ Gagal menyimpan!", state="error", expanded=True)
                st.error(f"Terjadi kesalahan: {e}")


# def render_generic_editor(engine, config: dict):
#     """
#     Merender antarmuka pengguna (UI) data editor yang sepenuhnya dinamis
#     berdasarkan konfigurasi yang diberikan.

#     Args:
#         engine: Koneksi database yang aktif.
#         config (dict): Blueprint/konfigurasi untuk tabel yang akan dirender.
#     """

#     source_name = config.get("source_view", config.get("table_name"))
#     table_key = config.get("target_table", config.get("table_name"))
#     display_name = config["display_name"]
#     # session_key = f"df_{table_key}"

#     st.header(f"⚙️ Manajemen Data: {display_name}")
#     st.divider()

#     st.markdown("### 🔎 Filter Data")

#     filter_values = {}
#     filter_configs = config.get("filters", [])
#     filter_cols = (
#         st.columns(len(filter_configs)) if filter_configs else [st.container()]
#     )

#     for i, f_config in enumerate(filter_configs):
#         with filter_cols[i]:
#             col_name = f_config["column_name"]
#             label = f_config["label"]
#             f_type = f_config["filter_type"]
#             widget_key = f"filter_{table_key}_{col_name}"

#             if f_type == "date_range":
#                 range_type = f_config.get("date_range_type", "last_30_days")

#                 if range_type == "today":
#                     defaults = (date.today(), date.today())
#                 elif range_type == "yesterday":
#                     yesterday = date.today() - timedelta(days=1)
#                     defaults = (yesterday, yesterday)
#                 else:
#                     defaults = (date.today() - timedelta(days=30), date.today())

#                 date_range_val = st.date_input(label, value=defaults, key=widget_key)

#                 if isinstance(date_range_val, tuple) and len(date_range_val) == 2:
#                     filter_values[col_name] = date_range_val
#                 else:
#                     st.warning("Pilih tanggal akhir.", icon="⚠️")

#             elif f_type == "selectbox":
#                 options = ["Semua Kategori"]

#                 if "options_source" in f_config:
#                     src = f_config["options_source"]
#                     # Panggil fungsi fetch_distinct_options yang sudah dicache
#                     db_opts = fetch_distinct_options(
#                         engine, src["table"], src["column"]
#                     )
#                     options += db_opts

#                 # Opsi 2: Ambil dari config (statis)
#                 elif "options" in f_config:
#                     options += f_config["options"]

#                 selected_val = st.selectbox(label, options, key=widget_key)

#                 if selected_val != "Semua Kategori":
#                     filter_values[col_name] = selected_val

#     # --- 2. FETCH DATA (Server-side Filtering) ---
#     # Data baru ditarik SETELAH semua filter terkumpul.
#     # Fungsi ini harus sudah menggunakan @st.cache_data agar cepat saat interaksi ulang.
#     with st.spinner("Memuat data..."):
#         filtered_df = fetch_filtered_data(engine, source_name, filter_values)

#     # --- 3. INFO & RENDER HASIL ---
#     # Logika membuat string periode untuk info
#     active_date_range = None
#     for val in filter_values.values():
#         if isinstance(val, tuple) and len(val) == 2:
#             active_date_range = val
#             break

#     date_period_str = ""
#     if active_date_range:
#         start_str = active_date_range[0].strftime("%d/%m/%Y")
#         end_str = active_date_range[1].strftime("%d/%m/%Y")
#         date_period_str = (
#             f"periode {start_str}"
#             if start_str == end_str
#             else f"periode {start_str} - {end_str}"
#         )
#     else:
#         date_period_str = "semua periode"

#     st.info(f"Menampilkan **{len(filtered_df):,}** data untuk **{date_period_str}**.")
#     st.divider()

#     # Render dataframe (opsional, jika dilakukan di luar snippet ini, bisa dihapus)
#     # st.dataframe(filtered_df, use_container_width=True, hide_index=True)

#     col1, col2 = st.columns([0.85, 0.15])

#     with col1:
#         st.markdown("### ✏️ Editor Data")

#     with col2:
#         # Tombol refresh manual untuk user
#         if st.button("🔄 Refresh Data", use_container_width=True):
#             st.cache_data.clear()
#             st.rerun()

#     # Persiapkan data untuk editor. PENTING: reset_index agar sinkron dengan editor.
#     df_to_edit = filtered_df.reset_index(drop=True)

#     editor_key = f"editor_{table_key}"

#     # Render Data Editor
#     edited_df = st.data_editor(
#         df_to_edit,
#         num_rows="dynamic",
#         key=editor_key,
#         hide_index=True,
#         # Gunakan config untuk kustomisasi kolom jika ada
#         column_order=config.get("column_order"),
#         column_config=config.get("column_config", {}),
#         use_container_width=True,  # Ganti width="stretch" dengan parameter native terbaru
#     )

#     # --- Bagian Tombol Simpan ---
#     if st.button(
#         "💾 Simpan Perubahan",
#         key=f"save_{table_key}",
#         type="primary",
#         use_container_width=True,
#     ):
#         with st.spinner("Menyimpan perubahan ke database..."):
#             try:
#                 # Ambil state perubahan dari data_editor
#                 changes = st.session_state[editor_key]

#                 added_count = len(changes.get("added_rows", []))
#                 edited_count = len(changes.get("edited_rows", {}))
#                 deleted_count = len(changes.get("deleted_rows", []))

#                 if not any([added_count, edited_count, deleted_count]):
#                     st.toast("Tidak ada perubahan untuk disimpan.", icon="🤷")
#                 else:
#                     # Panggil fungsi proses perubahan (versi SQLAlchemy yang baru)
#                     process_generic_changes(engine, config, df_to_edit, changes)

#                     # Buat pesan sukses yang informatif
#                     messages = []
#                     if added_count > 0:
#                         messages.append(f"**{added_count}** data ditambahkan")
#                     if edited_count > 0:
#                         messages.append(f"**{edited_count}** data diupdate")
#                     if deleted_count > 0:
#                         messages.append(f"**{deleted_count}** data dihapus")

#                     st.toast(f"✅ Berhasil! {', '.join(messages)}.", icon="🎉")

#                     # HAPUS CACHE AGAR DATA UPDATE MUNCUL
#                     st.cache_data.clear()

#                     # Tunggu sebentar agar toast terbaca user, lalu refresh halaman
#                     time.sleep(2)
#                     st.rerun()

#             except Exception as e:
#                 st.error(f"❌ Terjadi kesalahan saat menyimpan: {e}")
#                 # Opsional: log error lengkap ke console/file untuk debugging
#                 # logging.exception("Error saving changes:")
