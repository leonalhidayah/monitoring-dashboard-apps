from datetime import datetime

import streamlit as st

from data_preprocessor import utils
from database import db_manager

st.set_page_config(layout="wide")
st.title("Data Entry Harian Advertiser")

# CSS untuk tab
st.markdown(
    """
        <style>
        button[data-baseweb="tab"] {
            font-size: 18px;
            width: 100%;
            justify-content: center !important;
            text-align: center !important;
        }
        </style>
    """,
    unsafe_allow_html=True,
)

marketplace_tab, cpas_tab, regular_tab = st.tabs(["Marketplace", "CPAS", "Regular"])

with marketplace_tab:
    # Definisikan data toko untuk setiap project
    data = {
        "Zhi Yang Yao": {
            "Marketplace": [
                "Shopee",
                "Shopee",
                "Shopee",
                "Shopee",
                "Shopee",
                "Tokopedia",
                "Tokopedia",
                "TikTok",
                "Lazada",
            ],
            "Nama Toko": [
                "SP zhi yang yao official store",
                "SP zhi yang yao official",
                "SP zhi yang yao mart",
                "SP zhi yang yao",
                "SP zhi yang yao (iklan eksternal FB)",
                "TP zhi yang yao official store",
                "TP zhi yang yao",
                "TT zhi yang yao",
                "LZ zhi yang yao",
            ],
        },
        "Juwara Herbal": {
            "Marketplace": [
                "Shopee",
                "TikTok",
            ],
            "Nama Toko": [
                "SP juwara herbal official store",
                "TT juwaraherbal",
            ],
        },
        "Enzhico": {
            "Marketplace": ["Shopee", "Shopee", "Shopee", "TikTok", "Lazada", "Lazada"],
            "Nama Toko": [
                "SP enzhico",
                "SP enzhico store",
                "SP enzhico shop",
                "TT enzhico authorized store",
                "LZ enzhico",
                "LZ enzhico store",
            ],
        },
        "Erassgo": {
            "Marketplace": [
                "Shopee",
                "Shopee",
                "Shopee",
                "Shopee",
                "Shopee",
                "Tokopedia",
                "Lazada",
                "Lazada",
            ],
            "Nama Toko": [
                "SP erassgo official",
                "SP erassgo official store",
                "SP erassgo.co",
                "SP erassgo",
                "SP erassgo makassar",
                "TP erassgo",
                "LZ erassgo",
                "LZ erassgo store id",
            ],
        },
        "Kudaku": {
            "Marketplace": [
                "Shopee",
                "Shopee",
                "Shopee",
                "Shopee",
                "Shopee",
                "TikTok",
                "Lazada",
            ],
            "Nama Toko": [
                "SP kudaku",
                "SP kudaku store",
                "SP kudaku official store",
                "SP kudaku id",
                "SP kudaku indonesia",
                "TT kudaku milk",
                "LZ kudaku",
            ],
        },
    }

    # Membuat tab secara dinamis
    tab_names = list(data.keys())
    tabs = st.tabs(tab_names)

    for i, project_name in enumerate(tab_names):
        with tabs[i]:
            df_key = f"df_{project_name.lower().replace(' ', '_')}_marketplace"
            preview_key = (
                f"show_preview_{project_name.lower().replace(' ', '_')}_marketplace"
            )

            # Inisialisasi DataFrame
            utils.initialize_marketplace_data_session(
                project_name.lower().replace(" ", "_"),
                data[project_name]["Marketplace"],
                data[project_name]["Nama Toko"],
            )

            # Form untuk input & pratinjau
            with st.form(f"form_{project_name.lower().replace(' ', '_')}"):
                # Data editor → hasilnya langsung overwrite ke session_state
                st.session_state[df_key] = st.data_editor(
                    st.session_state[df_key],
                    num_rows="dynamic",
                    width="stretch",
                    column_config=utils.get_marketplace_column_config(
                        data[project_name]["Nama Toko"]
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
                        column_config=utils.get_marketplace_column_config(
                            data[project_name]["Nama Toko"]
                        ),
                    )

                    button_cols = st.columns([8, 3, 1.9])
                    with button_cols[0]:
                        if st.button(
                            "Ya, Simpan ke Database",
                            key=f"save_button_{project_name.lower().replace(' ', '_')}_marketplace",
                        ):
                            result = db_manager.insert_advertiser_marketplace_data(
                                cleaned_df
                            )
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

with cpas_tab:
    data = {
        "Porject ZYY x JUW": {
            "Nama Toko": [
                "SP zhi yang yao official store",
                "SP zhi yang yao",
                "SP zhi yang yao",
                "TT zhi yang yao",
            ],
            "Akun": [
                "Zhi yang yao mall 1",
                "Zhi yang yao CPAS 03",
                "Zhi yang yao CPAS",
                "Zhi yang yao CPAS Tokopedia",
            ],
        },
        "Porject ENZ x KDK x ERA": {
            "Nama Toko": [
                "SP erassgo",
                "SP erassgo official store",
                "SP enzhico",
                "SP kudaku official store",
                "TT kudaku milk",
            ],
            "Akun": [
                "Erassgo CPAS 1",
                "Erassgo mall 1",
                "Enzhico CPAS 1",
                "Kudaku mall CPAS Shopee",
                "Kudaku milk CPAS Tokopedia",
            ],
        },
    }

    # Membuat tab secara dinamis
    tab_names = list(data.keys())
    tabs = st.tabs(tab_names)

    for i, project_name in enumerate(tab_names):
        with tabs[i]:
            df_key = f"df_{project_name.lower().replace(' ', '_')}_cpas"
            preview_key = f"show_preview_{project_name.lower().replace(' ', '_')}_cpas"

            # Inisialisasi DataFrame
            utils.initialize_cpas_data_session(
                project_name.lower().replace(" ", "_"),
                data[project_name]["Nama Toko"],
                data[project_name]["Akun"],
            )

            # Form untuk input & pratinjau
            with st.form(f"form_{project_name.lower().replace(' ', '_')}"):
                # Data editor → hasilnya langsung overwrite ke session_state
                st.session_state[df_key] = st.data_editor(
                    st.session_state[df_key],
                    num_rows="dynamic",
                    width="stretch",
                    column_config=utils.get_cpas_column_config(
                        data[project_name]["Nama Toko"],
                        data[project_name]["Akun"],
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
                        column_config=utils.get_cpas_column_config(
                            data[project_name]["Nama Toko"],
                            data[project_name]["Akun"],
                        ),
                    )

                    button_cols = st.columns([8, 3, 1.9])
                    with button_cols[0]:
                        if st.button(
                            "Ya, Simpan ke Database",
                            key=f"save_button_{project_name.lower().replace(' ', '_')}_cpas",
                        ):
                            result = db_manager.insert_advertiser_cpas_data(cleaned_df)
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
                            key=f"update_button_{project_name.lower().replace(' ', '_')}_cpas",
                        ):
                            st.session_state[preview_key] = False
                            st.rerun()

                else:
                    st.warning("Tidak ada data valid untuk disimpan.")
