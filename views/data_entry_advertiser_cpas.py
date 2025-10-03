from datetime import datetime

import streamlit as st

from data_preprocessor import utils
from database import db_manager

st.set_page_config(layout="wide")
st.title("Data Entry Harian Advertiser CPAS")

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


data = {
    "Sadewa": {
        "Brand": [
            "Zhi Yang Yao",
            "Zhi Yang Yao",
            "Zhi Yang Yao",
            "Zhi Yang Yao",
            "Erassgo",
            "Erassgo",
            "Enzhico",
        ],
        "Akun": [
            "Zhi yang yao mall 1",
            "Zhi yang yao CPAS 03",
            "Zhi yang yao CPAS",
            "Zhi yang yao CPAS Tokopedia",
            "Erassgo CPAS 1",
            "Erassgo mall 1",
            "Enzhico CPAS 1",
        ],
    },
}

# Membuat tab secara dinamis
tab_names = list(data.keys())
tabs = st.tabs(tab_names)

for i, branch_name in enumerate(tab_names):
    with tabs[i]:
        df_key = f"df_{branch_name.lower().replace(' ', '_')}_cpas"
        preview_key = f"show_preview_{branch_name.lower().replace(' ', '_')}_cpas"

        # Inisialisasi DataFrame
        utils.initialize_cpas_data_session(
            branch_name.lower().replace(" ", "_"),
            data[branch_name]["Brand"],
            data[branch_name]["Akun"],
        )

        # Form untuk input & pratinjau
        with st.form(f"form_{branch_name.lower().replace(' ', '_')}"):
            # Data editor → hasilnya langsung overwrite ke session_state
            st.session_state[df_key] = st.data_editor(
                st.session_state[df_key],
                num_rows="dynamic",
                width="stretch",
                column_config=utils.get_cpas_column_config(),
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
                    f"Pratinjau Data untuk {branch_name}_{datetime.today().strftime('%d-%M-%Y %H:%M:%S')}"
                )
                st.write("Silakan cek kembali data Anda sebelum disimpan permanen.")

                st.dataframe(
                    cleaned_df,
                    width="stretch",
                    column_config=utils.get_cpas_column_config(),
                )

                button_cols = st.columns([8, 3, 1.9])
                with button_cols[0]:
                    if st.button(
                        "Ya, Simpan ke Database",
                        key=f"save_button_{branch_name.lower().replace(' ', '_')}_cpas",
                    ):
                        result = db_manager.insert_advertiser_cpas_data(cleaned_df)
                        if result["status"] == "success":
                            st.success(result["message"])
                            st.session_state[preview_key] = False
                        else:
                            st.error(
                                f"Gagal menyimpan data omset {branch_name}: {result['message']}"
                            )
                with button_cols[2]:
                    if st.button(
                        "OMG, Ada yg slhhhh",
                        key=f"update_button_{branch_name.lower().replace(' ', '_')}_cpas",
                    ):
                        st.session_state[preview_key] = False
                        st.rerun()

            else:
                st.warning("Tidak ada data valid untuk disimpan.")
