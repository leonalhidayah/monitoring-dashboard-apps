# pages/2_Input_Cash_Out.py

from datetime import date

import streamlit as st

from database import db_manager

st.set_page_config(layout="wide")
st.header("Form Input Pengeluaran (Cash Out)")


if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

form_fields = {
    "project_name": None,
    "bidang": None,
    "tipe_beban": None,
    "trans_date": date.today(),
    "nominal": 0,
    "deskripsi": "",
}
for field, default_value in form_fields.items():
    if field not in st.session_state:
        st.session_state[field] = default_value


def on_bidang_change():
    st.session_state.tipe_beban = None


def clear_form_inputs():
    """Mengosongkan semua input di form."""
    for field, default_value in form_fields.items():
        st.session_state[field] = default_value


if st.session_state.form_submitted:
    st.success(st.session_state.success_message)
    st.balloons()
    clear_form_inputs()
    st.session_state.form_submitted = False

try:
    df_projects = db_manager.get_dim_projects()
    df_categories = db_manager.get_dim_expense_categories()
except Exception as e:
    st.error(f"Gagal memuat data awal: {e}")
    st.stop()

project_list = df_projects["project_name"].tolist()
bidang_list = df_categories["bidang"].unique().tolist()

st.info("Lengkapi form berikut untuk mencatat transaksi pengeluaran.")

col1, col2, col3 = st.columns(3)
with col1:
    st.selectbox(
        "Untuk Project",
        project_list,
        key="project_name",
        placeholder="Pilih project...",
    )
with col2:
    st.selectbox(
        "Bidang Pengeluaran",
        bidang_list,
        key="bidang",
        on_change=on_bidang_change,
        placeholder="Pilih bidang...",
    )

tipe_beban_options = []
if st.session_state.bidang:
    tipe_beban_options = df_categories[
        df_categories["bidang"] == st.session_state.bidang
    ]["tipe_beban"].tolist()

with col3:
    st.selectbox(
        "Tipe Beban",
        tipe_beban_options,
        key="tipe_beban",
        disabled=not st.session_state.bidang,
        placeholder="Pilih tipe...",
    )

col4, col5 = st.columns(2)
with col4:
    st.date_input("Tanggal Transaksi", key="trans_date")
with col5:
    st.number_input(
        "Nominal (Rp)",
        min_value=0,
        step=1000,
        key="nominal",
        help="Masukkan hanya angka",
    )
    if st.session_state.nominal > 0:
        st.caption(f"↳ Pratinjau: **Rp {st.session_state.nominal:,.0f}**")

st.text_area(
    "Deskripsi / Catatan (optional)",
    key="deskripsi",
    placeholder="Contoh: Pembayaran Iklan Facebook...",
)
st.divider()

# --- LOGIKA SUBMIT ---
if st.button("💾 Simpan Transaksi", use_container_width=True, type="primary"):
    if not all(
        [
            st.session_state.project_name,
            st.session_state.bidang,
            st.session_state.tipe_beban,
            st.session_state.nominal > 0,
        ]
    ):
        st.warning("Mohon lengkapi semua field wajib (project, bidang, tipe, nominal).")
    else:
        result = db_manager.insert_cash_out(
            trans_date=st.session_state.trans_date,
            project_name=st.session_state.project_name,
            bidang=st.session_state.bidang,
            tipe_beban=st.session_state.tipe_beban,
            nominal=st.session_state.nominal,
            deskripsi=st.session_state.deskripsi,
            user_input="finance",
        )

        if result["status"] == "success":
            st.session_state.success_message = (
                f"🎉 Transaksi untuk '{st.session_state.tipe_beban}' "
                f"sebesar Rp {st.session_state.nominal:,.0f} berhasil disimpan!"
            )
            st.session_state.form_submitted = True
            st.rerun()
        else:
            st.error(f"Gagal menyimpan ke database: {result['message']}")
