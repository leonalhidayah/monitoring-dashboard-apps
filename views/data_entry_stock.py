from datetime import datetime

import pandas as pd
import streamlit as st

st.title("Data Entry Harian Gudang")

# --- Data produk (dummy awal, bisa load dari DB) ---
produk_list = ["Madu A", "Madu B", "Madu C", "Madu D", "Madu E"]
df_input = pd.DataFrame(
    {
        "Produk": produk_list,
        "Stok Gudang": [0] * len(produk_list),
        "Pesanan Hari Ini": [0] * len(produk_list),
        "Tanggal": [datetime.today().strftime("%Y-%m-%d")] * len(produk_list),
    }
)

# --- Input editable ---
edited_df = st.data_editor(
    df_input,
    num_rows="dynamic",  # bisa tambah baris kalau perlu
    use_container_width=True,
    key="editor_input",
)

# --- Tombol Simpan ---
if st.button("💾 Simpan Data Harian"):
    st.success("✅ Data berhasil disimpan!")
    st.dataframe(edited_df)  # sementara tampilkan hasil
    # TODO: Simpan ke DB/Postgres/BigQuery/CSV
