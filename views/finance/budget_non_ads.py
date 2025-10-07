from datetime import datetime

import streamlit as st

from data_preprocessor.utils import (
    get_non_ads_column_config,
    get_non_ads_lainnya_column_config,
    initialize_non_ads_data_session,
    initialize_non_ads_lainnya_data_session,
)
from database.db_manager import (
    insert_budget_non_ads_fo_data,
    insert_budget_non_ads_lainnya_data,
)
from views.config import ADV_MP_MAP_PROJECT
from views.style import load_css

load_css()

st.header("Budgeting Non Ads")

fo_tab, lainnya_tab = st.tabs(["FO", "Lainnya"])

with fo_tab:
    # Membuat tab secara dinamis
    tab_names = list(ADV_MP_MAP_PROJECT.keys())
    tabs = st.tabs(tab_names)

    for i, project_name in enumerate(tab_names):
        with tabs[i]:
            df_key = f"df_{project_name.lower().replace(' ', '_')}_ads"
            preview_key = f"show_preview_{project_name.lower().replace(' ', '_')}_ads"

            # Inisialisasi DataFrame
            initialize_non_ads_data_session(
                project_name.lower().replace(" ", "_"),
                ADV_MP_MAP_PROJECT[project_name]["Marketplace"],
                ADV_MP_MAP_PROJECT[project_name]["Nama Toko"],
            )

            # Form untuk input & pratinjau
            with st.form(f"form_{project_name.lower().replace(' ', '_')}_ads"):
                # Data editor → hasilnya langsung overwrite ke session_state
                st.session_state[df_key] = st.data_editor(
                    st.session_state[df_key],
                    num_rows="dynamic",
                    width="stretch",
                    column_config=get_non_ads_column_config(
                        ADV_MP_MAP_PROJECT[project_name]["Nama Toko"]
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
                        column_config=get_non_ads_column_config(
                            ADV_MP_MAP_PROJECT[project_name]["Nama Toko"]
                        ),
                    )

                    button_cols = st.columns([8, 10, 3])
                    with button_cols[0]:
                        if st.button(
                            "Ya, Simpan ke Database",
                            key=f"save_button_{project_name.lower().replace(' ', '_')}_ads",
                        ):
                            result = insert_budget_non_ads_fo_data(cleaned_df)
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
                            key=f"update_button_{project_name.lower().replace(' ', '_')}_ads",
                        ):
                            st.session_state[preview_key] = False
                            st.rerun()

                else:
                    st.warning("Tidak ada data valid untuk disimpan.")


with lainnya_tab:
    df_key = "df_non_ads_lainnya"
    preview_key = "show_preview_non_ads_lainnya"

    # Inisialisasi DataFrame
    initialize_non_ads_lainnya_data_session()

    # Form untuk input & pratinjau
    with st.form("form_non_ads_lainnya"):
        # Data editor → hasilnya langsung overwrite ke session_state
        st.session_state[df_key] = st.data_editor(
            st.session_state[df_key],
            num_rows="dynamic",
            width="stretch",
            column_config=get_non_ads_lainnya_column_config(),
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
                f"Pratinjau Data untuk Non Ads Lainnya_{datetime.today().strftime('%d-%M-%Y %H:%M:%S')}"
            )
            st.write("Silakan cek kembali data Anda sebelum disimpan permanen.")

            st.dataframe(
                cleaned_df,
                width="stretch",
                column_config=get_non_ads_lainnya_column_config(),
            )

            button_cols = st.columns([8, 10, 3])
            with button_cols[0]:
                if st.button(
                    "Ya, Simpan ke Database",
                    key="save_button_non_ads_lainnya",
                ):
                    result = insert_budget_non_ads_lainnya_data(cleaned_df)
                    if result["status"] == "success":
                        st.success(result["message"])
                        st.session_state[preview_key] = False
                    else:
                        st.error(f"Gagal menyimpan data: {result['message']}")
            with button_cols[2]:
                if st.button(
                    "OMG, Ada yg slh",
                    key="update_button_non_ads_lainnya",
                ):
                    st.session_state[preview_key] = False
                    st.rerun()

        else:
            st.warning("Tidak ada data valid untuk disimpan.")
