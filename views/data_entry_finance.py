from datetime import datetime

import pandas as pd
import streamlit as st

from data_preprocessor import utils
from database import db_manager

st.set_page_config(layout="wide")
st.title("Data Entry Harian Finance")

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


def get_quarter_months(month: int):
    """Helper: menentukan bulan dalam kuartal"""
    if month in [1, 2, 3]:
        return ["January", "February", "March"], 1
    elif month in [4, 5, 6]:
        return ["April", "May", "June"], 2
    elif month in [7, 8, 9]:
        return ["July", "August", "September"], 3
    else:
        return ["October", "November", "December"], 4


plan_tab, aktual_tab, omset_tab, budget_ads_tab, budget_non_ads_tab, cashflow_tab = (
    st.tabs(
        [
            "Budget Plan",
            "Aktualisasi",
            "Omset",
            "Budegt Ads",
            "Budget Non Ads",
            "Cashflow",
        ]
    )
)

with plan_tab:
    st.header("Budget Plan (Per Kuartal)")

    # Tentukan kuartal berjalan
    now = datetime.now()
    months, q = get_quarter_months(now.month)
    tahun = now.year

    st.write(f"Saat ini berada di **Kuartal {q} {tahun}** ({', '.join(months)})")

    with st.form("budget_plan_form"):
        target_quarter = st.number_input(
            "Masukkan Target Kuartalan (Rp)", value=7_000_000_000, step=1_000_000
        )
        st.markdown(f"**Target Kuartalan:** Rp {target_quarter:,.0f}")
        st.markdown(f"**Target Bulanan (per bulan):** Rp {(target_quarter / 3):,.0f}")

        st.subheader("Input Rasio (%)")
        col1, col2, col3 = st.columns(3)
        with col1:
            hpp = st.number_input("HPP (%)", value=20, step=1)
            biaya_admin = st.number_input("Biaya Admin (%)", value=20, step=1)
            biaya_ads = st.number_input("Biaya Marketing (Ads) (%)", value=25, step=1)
        with col2:
            biaya_non_ads = st.number_input(
                "Biaya Marketing (Non Ads) (%)", value=5, step=1
            )
            personal_expense = st.number_input("Personal Expense (%)", value=10, step=1)
            administrasi_umum = st.number_input(
                "Administrasi dan Umum (%)", value=5, step=1
            )
        with col3:
            ebit = st.number_input("Estimasi Ebit/Net Profit (%)", value=15, step=1)

        submitted = st.form_submit_button("🚀 Generate Budget Plan")

    if submitted:
        ratios = {
            "HPP": hpp,
            "Biaya Admin": biaya_admin,
            "Biaya Marketing (Ads)": biaya_ads,
            "Biaya Marketing (Non Ads)": biaya_non_ads,
            "Personal Expense": personal_expense,
            "Administrasi dan Umum": administrasi_umum,
            "Estimasi Ebit/Net Profit": ebit,
        }
        total_ratio = sum(ratios.values())

        if total_ratio != 100:
            st.error(f"Total rasio harus 100%. Saat ini: {total_ratio}%")
            if "df_budget_plan" in st.session_state:
                del st.session_state["df_budget_plan"]
            if "df_long_budget_plan" in st.session_state:
                del st.session_state["df_long_budget_plan"]
        else:
            target_monthly = target_quarter / 3
            data = []
            for param, ratio in ratios.items():
                row = [param, ratio, target_quarter * (ratio / 100)] + [
                    target_monthly * (ratio / 100)
                ] * 3
                data.append(row)

            df = pd.DataFrame(
                data, columns=["Parameter", "Target Rasio", "Target Kuartal"] + months
            )
            df["Tahun"] = tahun
            df["Kuartal"] = q

            df_long = (
                df.melt(
                    id_vars=[
                        "Parameter",
                        "Target Rasio",
                        "Target Kuartal",
                        "Tahun",
                        "Kuartal",
                    ],
                    var_name="Bulan",
                    value_name="Target Bulanan",
                )
                .sort_values(by=["Parameter", "Bulan"])
                .reset_index(drop=True)
            )

            st.session_state["df_budget_plan"] = df
            st.session_state["df_long_budget_plan"] = df_long

    # Tampilkan hasil HANYA jika data sudah digenerate dan ada di session state
    if (
        "df_budget_plan" in st.session_state
        and "df_long_budget_plan" in st.session_state
    ):
        df_to_show = st.session_state["df_budget_plan"]
        df_long_to_save = st.session_state["df_long_budget_plan"]

        # Tampilan untuk tim Finance
        st.subheader("Alokasi Budget Plan (Finance View)")
        st.dataframe(df_to_show, width="stretch", hide_index=True)

        if st.button("Simpan ke Database"):
            try:
                db_manager.insert_budget_plan_long(df_long_to_save)
                st.success("✅ Budget Plan berhasil disimpan ke database!")
            except Exception as e:
                st.error(f"Gagal menyimpan ke database: {e}")


# with aktual_tab:


# Definisikan data toko untuk setiap brand
data = {
    "Zhi Yang Yao": {
        "Marketplace": [
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "TikTok",
            "Lazada",
            "Lazada",
            "Tokopedia",
            "Tokopedia",
            "Tokopedia",
            "Tokopedia",
        ],
        "Nama Toko": [
            "SP zhi yang yao official store",
            "SP zhi yang yao",
            "SP zhi yang yao official",
            "SP zhi yang yao id",
            "SP zhi yang yao shop",
            "SP zhi yang yao indonesia",
            "SP zhi yang yao mart",
            "SP zhi yang yao store",
            "TT zhi yang yao official store",
            "LZ zhi yang yao",
            "LZ zhi yang yao id",
            "TP zhi yang yao official store",
            "TP zhi yang yao",
            "TP zhi yang yao store makassar",
            "TP zhi yang yao official medan",
        ],
    },
    "Juwara Herbal": {
        "Marketplace": [
            "Shopee",
            "TikTok",
        ],
        "Nama Toko": [
            "SP juwara herbal official store",
            "TT juwara herbal",
        ],
    },
    "Enzhico": {
        "Marketplace": [
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "TikTok",
            "Lazada",
            "Lazada",
            "Tokopedia",
        ],
        "Nama Toko": [
            "SP enzhico shop",
            "SP enzhico store",
            "SP enzhico store indonesia",
            "SP enzhico shop indonesia",
            "SP enzhico indonesia",
            "SP enzhico authorize store",
            "SP enzhico",
            "TT enzhico authorized store",
            "LZ enzhico",
            "LZ enzhico store",
            "TP enzhico official store",
        ],
    },
    "Erassgo": {
        "Marketplace": [
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

with omset_tab:
    # Membuat tab secara dinamis
    tab_names = list(data.keys())
    tabs = st.tabs(tab_names)

    for i, project_name in enumerate(tab_names):
        with tabs[i]:
            df_key = f"df_{project_name.lower().replace(' ', '_')}_omset"
            preview_key = f"show_preview_{project_name.lower().replace(' ', '_')}_omset"

            # Inisialisasi DataFrame
            utils.initialize_omset_data_session(
                project_name.lower().replace(" ", "_"),
                data[project_name]["Marketplace"],
                data[project_name]["Nama Toko"],
            )

            # Form untuk input & pratinjau
            with st.form(f"form_{project_name.lower().replace(' ', '_')}_omset"):
                # Data editor → hasilnya langsung overwrite ke session_state
                st.session_state[df_key] = st.data_editor(
                    st.session_state[df_key],
                    num_rows="dynamic",
                    width="stretch",
                    column_config=utils.get_omset_column_config(project_name),
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
                        column_config=utils.get_omset_column_config(project_name),
                    )

                    button_cols = st.columns([8, 10, 3])
                    with button_cols[0]:
                        if st.button(
                            "Ya, Simpan ke Database",
                            key=f"save_button_{project_name.lower().replace(' ', '_')}_omset",
                        ):
                            result = db_manager.insert_omset_data(cleaned_df)
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

with budget_ads_tab:
    # Membuat tab secara dinamis
    tab_names = list(data.keys())
    tabs = st.tabs(tab_names)

    for i, project_name in enumerate(tab_names):
        with tabs[i]:
            df_key = f"df_{project_name.lower().replace(' ', '_')}_ads"
            preview_key = f"show_preview_{project_name.lower().replace(' ', '_')}_ads"

            # Inisialisasi DataFrame
            utils.initialize_ads_data_session(
                project_name.lower().replace(" ", "_"),
                data[project_name]["Marketplace"],
                data[project_name]["Nama Toko"],
            )

            # Form untuk input & pratinjau
            with st.form(f"form_{project_name.lower().replace(' ', '_')}_ads"):
                # Data editor → hasilnya langsung overwrite ke session_state
                st.session_state[df_key] = st.data_editor(
                    st.session_state[df_key],
                    num_rows="dynamic",
                    width="stretch",
                    column_config=utils.get_ads_column_config(project_name),
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
                        column_config=utils.get_ads_column_config(project_name),
                    )

                    button_cols = st.columns([8, 10, 3])
                    with button_cols[0]:
                        if st.button(
                            "Ya, Simpan ke Database",
                            key=f"save_button_{project_name.lower().replace(' ', '_')}_ads",
                        ):
                            result = db_manager.insert_budget_ads_data(cleaned_df)
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

with budget_non_ads_tab:
    # Membuat tab secara dinamis
    tab_names = list(["Sadewa", "Lainnya"])
    tabs = st.tabs(tab_names)

    for i, branch_name in enumerate(tab_names):
        with tabs[i]:
            df_key = f"df_{branch_name.lower().replace(' ', '_')}_non_ads"
            preview_key = (
                f"show_preview_{branch_name.lower().replace(' ', '_')}_non_ads"
            )

            # Inisialisasi DataFrame
            utils.initialize_non_ads_data_session(branch_name.lower().replace(" ", "_"))

            # Form untuk input & pratinjau
            with st.form(f"form_{branch_name.lower().replace(' ', '_')}_non_ads"):
                # Data editor → hasilnya langsung overwrite ke session_state
                st.session_state[df_key] = st.data_editor(
                    st.session_state[df_key],
                    num_rows="dynamic",
                    width="stretch",
                    column_config=utils.get_non_ads_column_config(),
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
                        column_config=utils.get_non_ads_column_config(),
                    )

                    button_cols = st.columns([8, 10, 3])
                    with button_cols[0]:
                        if st.button(
                            "Ya, Simpan ke Database",
                            key=f"save_button_{branch_name.lower().replace(' ', '_')}_non_ads",
                        ):
                            result = db_manager.insert_budget_non_ads_data(cleaned_df)
                            if result["status"] == "success":
                                st.success(result["message"])
                                st.session_state[preview_key] = False
                            else:
                                st.error(
                                    f"Gagal menyimpan data omset {branch_name}: {result['message']}"
                                )
                    with button_cols[2]:
                        if st.button(
                            "OMG, Ada yg slh",
                            key=f"update_button_{branch_name.lower().replace(' ', '_')}_non_ads",
                        ):
                            st.session_state[preview_key] = False
                            st.rerun()

                else:
                    st.warning("Tidak ada data valid untuk disimpan.")
