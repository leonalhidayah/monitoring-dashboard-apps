import logging
import re
import warnings
from datetime import datetime

import streamlit as st

from database import db_manager
from pipeline.config.variables import get_now_in_jakarta
from pipeline.transformers.silver_standardizer import standardize_silver_data
from pipeline.transformers.silver_to_gold import process_silver_to_gold
from pipeline.utils.helpers import load_dataframe
from views.style import load_css

warnings.filterwarnings("ignore")

load_css()

st.header("Data Entry Harian Admin Marketplace")

(
    admin_marketplace_tab,
    pesanan_khusus_marketplace_page,
) = st.tabs(["Marketplace", "Pesanan Khusus"])

with admin_marketplace_tab:
    st.subheader("Uploud Data dari Spreadsheet Gudang")

    st.info(
        "Upload file data mentah (`Template Upload ke Dashboard HH-BB-TTTT`) untuk diproses."
    )

    uploaded_file = st.file_uploader(
        "Upload file data (.xlsx atau .csv)", type=["xlsx", "csv"]
    )

    st.markdown("---")
    st.subheader("Parameter Waktu Proses")
    st.caption("Setel tanggal/waktu jika Anda memproses data historis (backfill).")

    if "selected_date" not in st.session_state:
        st.session_state.selected_date = get_now_in_jakarta().date()

    if "selected_time" not in st.session_state:
        st.session_state.selected_time = get_now_in_jakarta().time()

    col1, col2 = st.columns(2)
    with col1:
        input_date = st.date_input(
            "Pilih tanggal input",
            key="selected_date",
        )
    with col2:
        input_time = st.time_input(
            "Pilih waktu input",
            key="selected_time",
        )

    st.markdown("---")

    if st.button("Mulai Proses", type="primary", width="stretch"):
        if uploaded_file is None:
            st.warning("Mohon upload file terlebih dahulu sebelum memproses.")
        else:
            try:
                # Menggabungkan tanggal dan waktu dari widget
                run_timestamp = datetime.combine(input_date, input_time)

                # Ini adalah dictionary yang akan diteruskan ke pipeline
                batch_config = {"run_timestamp": run_timestamp}
                st.write(f"Memproses data untuk timestamp: `{run_timestamp}`")

                # --- Standardisasi (Silver) ---
                df_clean_silver = None
                with st.spinner("Langkah 1/2: Menstandardisasi data (Cleaning)..."):
                    # 1. Load file
                    df_dirty = load_dataframe(uploaded_file)
                    # 2. Panggil Standardizer
                    df_clean_silver = standardize_silver_data(df_dirty)

                st.success("Langkah 1/2: Standardisasi Selesai.")
                st.dataframe(df_clean_silver.head(), width="stretch")
                st.write(f"Total baris bersih: `{len(df_clean_silver)}`")

                # --- C. Langkah 2: Proses ke Gold (Orchestrator) ---
                if df_clean_silver is not None:
                    with st.spinner(
                        "Langkah 2/2: Memproses & memuat data ke Database Gold... (Ini mungkin butuh waktu)"
                    ):
                        # Orchestrator untuk proses Silver ke Gold
                        success = process_silver_to_gold(df_clean_silver, batch_config)

                    if success:
                        st.success("SEMUA PROSES SELESAI! Database telah diperbarui.")
                        st.balloons()
                    else:
                        st.error("Proses Gold gagal tanpa error, silakan cek log.")

            except Exception as e:
                st.error("PROSES GAGAL")
                st.exception(e)
                logging.exception("Error terjadi selama proses ETL di Streamlit:")


with pesanan_khusus_marketplace_page:
    st.subheader("Input Manual Pesanan Khusus")

    with st.form("special_order_form"):
        tanggal_input = st.date_input("Tanggal Input", value=get_now_in_jakarta())
        kategori_pesanan = st.selectbox(
            "Pilih Kategori Pesanan",
            ("RETURN", "CANCEL"),
        )
        order_ids_input = st.text_area("Order ID", height=150)
        submit_button = st.form_submit_button("Simpan Data")

        if submit_button:
            if order_ids_input:
                order_ids = [
                    oid.strip()
                    for oid in re.split(r"[\s,]+", order_ids_input)
                    if oid.strip()
                ]

                try:
                    if db_manager.insert_order_flags_batch(
                        tanggal_input, kategori_pesanan, order_ids
                    ):
                        st.success(
                            f"Data untuk kategori '{kategori_pesanan}' berhasil disimpan!"
                        )
                    else:
                        st.error(
                            "Gagal menyimpan data. Cek log server untuk detail error."
                        )
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

            else:
                st.warning("Input Order ID tidak boleh kosong.")
