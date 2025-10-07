from datetime import datetime

import streamlit as st

from data_preprocessor.utils import (
    get_omset_column_config,
    get_omset_reg_column_config,
    initialize_omset_data_session,
    initialize_omset_reg_data_session,
)
from database.db_manager import insert_omset_data, insert_omset_reg_data
from views.config import DATA_MAP_FINANCE
from views.style import load_css

load_css()

st.header("Omset")

mp_tab, reg_tab = st.tabs(["Marketplace", "Regular"])

with mp_tab:
    # Membuat tab secara dinamis
    tab_names = list(DATA_MAP_FINANCE.keys())
    tabs = st.tabs(tab_names)

    for i, project_name in enumerate(tab_names):
        with tabs[i]:
            df_key = f"df_{project_name.lower().replace(' ', '_')}_omset"
            preview_key = f"show_preview_{project_name.lower().replace(' ', '_')}_omset"

            # Inisialisasi DataFrame
            initialize_omset_data_session(
                project_name.lower().replace(" ", "_"),
                DATA_MAP_FINANCE[project_name]["Marketplace"],
                DATA_MAP_FINANCE[project_name]["Nama Toko"],
            )

            # Form untuk input & pratinjau
            with st.form(f"form_{project_name.lower().replace(' ', '_')}_omset"):
                # Data editor → hasilnya langsung overwrite ke session_state
                st.session_state[df_key] = st.data_editor(
                    st.session_state[df_key],
                    num_rows="dynamic",
                    width="stretch",
                    column_config=get_omset_column_config(
                        DATA_MAP_FINANCE[project_name]["Nama Toko"]
                    ),
                )

                st.write("Tekan tombol di bawah untuk pratinjau dan menyimpan data.")
                submitted = st.form_submit_button("Simpan & Pratinjau")

                if submitted:
                    st.session_state[preview_key] = True

            # Tampilkan pratinjau setelah submit
            if st.session_state.get(preview_key, False):
                cleaned_df = st.session_state[df_key].dropna(how="all")
                if not cleaned_df.empty:
                    st.markdown("---")
                    st.subheader(
                        f"Pratinjau Data untuk {project_name}_{datetime.today().strftime('%d-%M-%Y %H:%M:%S')}"
                    )
                    st.write("Silakan cek kembali data Anda sebelum disimpan permanen.")

                    st.dataframe(
                        cleaned_df,
                        width="stretch",
                        column_config=get_omset_column_config(
                            DATA_MAP_FINANCE[project_name]["Nama Toko"]
                        ),
                    )

                    button_cols = st.columns([8, 10, 3])
                    with button_cols[0]:
                        if st.button(
                            "Ya, Simpan ke Database",
                            key=f"save_button_{project_name.lower().replace(' ', '_')}_omset",
                        ):
                            result = insert_omset_data(cleaned_df)
                            if result["status"] == "success":
                                st.success(result["message"])
                                st.session_state[preview_key] = False
                            else:
                                st.error(
                                    f"Gagal menyimpan data omset {project_name}: {result['message']}"
                                )
                    with button_cols[2]:
                        if st.button(
                            "OMG, Ada yg slh",
                            key=f"update_button_{project_name.lower().replace(' ', '_')}_omset",
                        ):
                            st.session_state[preview_key] = False
                            st.rerun()

                else:
                    st.warning("Tidak ada data valid untuk disimpan.")

with reg_tab:
    project_name = "SosCom"

    df_key = f"df_{project_name.lower().replace(' ', '_')}_omset_reg"
    preview_key = f"show_preview_{project_name.lower().replace(' ', '_')}_omset_reg"

    # Inisialisasi DataFrame
    initialize_omset_reg_data_session(
        project_name.lower().replace(" ", "_"),
    )

    # Form untuk input & pratinjau
    with st.form(f"form_{project_name.lower().replace(' ', '_')}_omset_reg"):
        # Data editor → hasilnya langsung overwrite ke session_state
        st.session_state[df_key] = st.data_editor(
            st.session_state[df_key],
            num_rows="dynamic",
            width="stretch",
            column_config=get_omset_reg_column_config(),
        )

        st.write("Tekan tombol di bawah untuk pratinjau dan menyimpan data.")
        submitted = st.form_submit_button("Simpan & Pratinjau")

        if submitted:
            st.session_state[preview_key] = True

    # Tampilkan pratinjau setelah submit
    if st.session_state.get(preview_key, False):
        cleaned_df = st.session_state[df_key].dropna(how="all")
        if not cleaned_df.empty:
            st.markdown("---")
            st.subheader(
                f"Pratinjau Data untuk {project_name}_{datetime.today().strftime('%d-%M-%Y %H:%M:%S')}"
            )
            st.write("Silakan cek kembali data Anda sebelum disimpan permanen.")

            st.dataframe(
                cleaned_df,
                width="stretch",
                column_config=get_omset_reg_column_config(),
            )

            button_cols = st.columns([8, 10, 3])
            with button_cols[0]:
                if st.button(
                    "Ya, Simpan ke Database",
                    key=f"save_button_{project_name.lower().replace(' ', '_')}_omset_reg",
                ):
                    result = insert_omset_reg_data(cleaned_df)
                    if result["status"] == "success":
                        st.success(result["message"])
                        st.session_state[preview_key] = False
                    else:
                        st.error(
                            f"Gagal menyimpan data omset {project_name}: {result['message']}"
                        )
            with button_cols[2]:
                if st.button(
                    "OMG, Ada yg slh",
                    key=f"update_button_{project_name.lower().replace(' ', '_')}_omset_reg",
                ):
                    st.session_state[preview_key] = False
                    st.rerun()

        else:
            st.warning("Tidak ada data valid untuk disimpan.")
