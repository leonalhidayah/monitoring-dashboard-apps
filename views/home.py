import streamlit as st

st.set_page_config(layout="centered", page_icon="assets/ams-icon-crop.png")

display_name = st.session_state.get("name", "Guest")

st.title(f"Hi, {display_name}! 👋")
st.markdown("---")

st.header("Selamat Datang di Dashboard AMS Corp.")
st.write(
    "Ini adalah halaman utama Anda. Silakan pilih menu di sidebar kiri untuk memulai."
)

# Anda bisa menambahkan konten lainnya di sini
st.balloons()
