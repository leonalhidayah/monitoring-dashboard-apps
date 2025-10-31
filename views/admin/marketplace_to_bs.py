import streamlit as st

from pipeline.transformers.marketplace_to_silver import transform_to_bigseller_format

st.set_page_config(layout="wide")
st.title("Data Pipeline: Marketplace to BigSeller")
st.info("Upload file mentah marketplace untuk diubah ke format standar BigSeller.")

st.divider()

# --- Bagian Upload ---
source_marketplace = st.selectbox(
    "Pilih Marketplace:",
    ["Shopee", "TikTok"],  # "Lainnya"
    key="marketplace_source",
)

st.divider()

uploaded_file = st.file_uploader(
    "Upload file mentah (.xlsx atau .csv)",
    type=["xlsx", "csv"],
    key="file_uploader",
)

# --- Bagian Transformasi & Download ---
if uploaded_file:
    st.divider()

    if st.button(
        f"Proses File {source_marketplace}", type="primary", use_container_width=True
    ):
        try:
            with st.spinner(f"Mentransformasi data {source_marketplace}..."):
                # Panggil fungsi modular Anda
                df_silver, clean_filename = transform_to_bigseller_format(
                    file=uploaded_file, source=source_marketplace
                )

            st.success("Berhasil! Data telah ditransformasi ke format BigSeller.")

            st.subheader("Data Bersih (Format BigSeller)")
            st.dataframe(df_silver.head(10))  # Tampilkan 10 baris pertama

            # Simpan hasil di session_state agar tombol download bisa akses
            st.session_state["df_silver"] = df_silver
            st.session_state["clean_filename"] = clean_filename

        except Exception as e:
            st.error(f"Gagal memproses file: {e}")
            st.error(
                "Jika ini error validasi, cek log di terminal/konsol Anda untuk detail data yang gagal."
            )

# --- Bagian Download (di luar tombol proses) ---
# Ini akan muncul SETELAH 'df_silver' tersimpan di session_state
if "df_silver" in st.session_state:
    df_to_download = st.session_state["df_silver"]

    # Konversi ke CSV untuk download
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    csv_data = convert_df_to_csv(df_to_download)

    st.download_button(
        label="✅ Download File Bersih (Silver CSV)",
        data=csv_data,
        file_name=st.session_state["clean_filename"],
        mime="text/csv",
        use_container_width=True,
    )
