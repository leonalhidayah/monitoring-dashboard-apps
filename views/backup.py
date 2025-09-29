import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")
st.title("Form Data Entry Harian Advertiser")
st.subheader("Masukkan data iklan harian Anda di bawah ini")

# Buat DataFrame kosong dengan kolom yang dibutuhkan
data = {
    "Tanggal": pd.Series(pd.Timestamp.today().date(), index=range(10)),
    "Campaign ID": [""] * 10,
    "Nama Campaign": [""] * 10,
    "Platform": ["Facebook Ads", "Google Ads", "TikTok Ads", "X Ads", "Lainnya"] * 2,
    "Budget (Rp)": [0.0] * 10,
    "Spend (Rp)": [0.0] * 10,
    "Leads": [0] * 10,
    "Revenue (Rp)": [0.0] * 10,
    "Catatan": [""] * 10,
}
df = pd.DataFrame(data)

# Tampilkan data editor
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    width="stretch",
    column_config={
        "Tanggal": st.column_config.DateColumn(
            "Tanggal",
            min_value=pd.Timestamp(2023, 1, 1),
            max_value=pd.Timestamp(2026, 1, 1),
            format="YYYY-MM-DD",
            step=1,
        ),
        "Platform": st.column_config.SelectboxColumn(
            "Platform",
            options=["Facebook Ads", "Google Ads", "TikTok Ads", "X Ads", "Lainnya"],
            required=True,
        ),
        "Budget (Rp)": st.column_config.NumberColumn(
            "Budget (Rp)",
            min_value=0,
            format="Rp %d",
        ),
        "Spend (Rp)": st.column_config.NumberColumn(
            "Spend (Rp)",
            min_value=0,
            format="Rp %d",
        ),
        "Leads": st.column_config.NumberColumn(
            "Leads",
            min_value=0,
            step=1,
            format="%d",
        ),
        "Revenue (Rp)": st.column_config.NumberColumn(
            "Revenue (Rp)",
            min_value=0,
            format="Rp %d",
        ),
    },
)

# Tombol untuk menyimpan data
if st.button("Simpan Data"):
    # Hapus baris yang kosong atau tidak diedit
    cleaned_df = edited_df.dropna(how="all")
    st.write("Data yang disimpan:")
    st.dataframe(cleaned_df)
    # Di sini Anda bisa menambahkan logika untuk menyimpan data ke database atau file CSV
    # Contoh: cleaned_df.to_csv("data_ads.csv", mode='a', header=not os.path.exists("data_ads.csv"), index=False)
    st.success("Data berhasil disimpan!")
