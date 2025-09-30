import datetime
import warnings

import pandas as pd
import pytz
import streamlit as st

from data_preprocessor import utils
from database import db_manager

warnings.filterwarnings("ignore")

st.set_page_config(layout="wide")
st.title("Data Entry Harian Admin")


st.markdown(
    """
    <style>
    button[data-baseweb="tab"] {
        font-size: 18px;
        width: 100%;
        justify-content: center !important;  /* Pusatkan teks */
        text-align: center !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

(
    admin_marketplace_tab,
    admin_regular_tab,
    admin_mp_return_tab,
    admin_reg_return_tab,
) = st.tabs(["Marketplace", "Regular", "Return MP", "Return REG"])

with admin_marketplace_tab:
    st.subheader("Unggah Data Admin Marketplace")
    st.markdown("""
        **Cara Ekspor Data dari BigSeller:**
        1. Pastikan Jenis Ekspor: Ekspor Berdasarkan SKU Toko
        2. Pastikan Jenis Template: Template Standar
    """)

    uploaded_file = st.file_uploader(
        "Upload file CSV atau Excel dari BigSeller", type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_raw = pd.read_csv(uploaded_file, dtype=str)
            else:
                df_raw = pd.read_excel(uploaded_file, dtype=str)

            st.info("File berhasil diunggah. Silakan lengkapi data di bawah ini.")

            # Pilihan tanggal dan waktu input
            jakarta_tz = pytz.timezone("Asia/Jakarta")
            now_in_jakarta = datetime.datetime.now(jakarta_tz)

            # Simpan default ke session_state hanya sekali
            if "selected_date" not in st.session_state:
                st.session_state.selected_date = now_in_jakarta.date()

            if "selected_time" not in st.session_state:
                st.session_state.selected_time = now_in_jakarta.time()

            selected_date = st.date_input(
                "Pilih tanggal input",
                # value=st.session_state.selected_date,
                key="selected_date",
            )

            selected_time = st.time_input(
                "Pilih waktu input",
                # value=st.session_state.selected_time,
                key="selected_time",
            )

            # Tombol untuk memproses dan menyimpan data
            if st.button("Proses & Simpan Data"):
                st.info("Memproses data, mohon tunggu...")

                # Panggil fungsi pembersihan dari utils
                df_clean = utils.clean_admin_marketplace_data(df_raw)

                # Panggil fungsi penambahan kolom baru
                df_with_new_cols = utils.add_new_columns(df_clean)

                # Tambahkan timestamp dan sesi
                timestamp_input = datetime.datetime.combine(
                    selected_date, selected_time
                )
                df_final = utils.add_timestamp_and_sesi_columns(
                    df_with_new_cols, timestamp_input
                )

                st.markdown("""---""")

                st.subheader("Data Hasil Pembersihan")
                st.dataframe(df_final.head())

                # df_final = utils.convert_datetime_to_str(df_final)
                df_final.replace({pd.NaT: None}, inplace=True)

                def insert_and_notify(
                    df, table_name, columns, conflict_cols, update_cols=None
                ):
                    """
                    Fungsi untuk memasukkan data ke tabel dan memberikan notifikasi di UI Streamlit.

                    Args:
                        st: Objek streamlit.
                        db_manager: Objek database manager Anda.
                        df (pd.DataFrame): DataFrame yang berisi data.
                        table_name (str): Nama tabel tujuan.
                        columns (list): Daftar kolom yang akan dimasukkan.
                        conflict_cols (list): Daftar kolom untuk penanganan konflik (ON CONFLICT).
                    """
                    result = db_manager.insert_orders_to_normalized_table(
                        df,
                        table_name,
                        columns,
                        drop_duplicates_row=True,
                        dropna=True,
                        conflict_cols=conflict_cols,
                        update_cols=update_cols,
                    )

                    if result["status"] == "success":
                        st.success(result["message"])
                    else:
                        st.error(
                            f"Gagal menyimpan data ke '{table_name}': {result['message']}"
                        )

                    # Mengembalikan status untuk penanganan lebih lanjut jika diperlukan
                    # return result["status"] == "success"

                # PROSES DIMENSI SEDERHANA (tanpa join/mapping)
                dimension_tables = {
                    "dim_brands": ["nama_brand"],
                    "dim_marketplaces": ["nama_marketplace"],
                    "dim_shipping_services": ["jasa_kirim"],
                    "dim_payment_methods": ["metode_pembayaran"],
                }

                st.info("Memproses tabel dimensi dasar...")
                for table_name, cols in dimension_tables.items():
                    insert_and_notify(
                        df_final,
                        table_name,
                        columns=cols,
                        conflict_cols=cols,
                    )

                # PROSES DIM_STORES (dengan mapping)
                st.info("Memproses tabel dim_stores...")
                # Lakukan mapping ID terlebih dahulu
                dim_marketplaces = db_manager.get_dim_marketplaces()
                marketplace_mapping = dict(
                    zip(
                        dim_marketplaces["nama_marketplace"],
                        dim_marketplaces["marketplace_id"],
                    )
                )
                df_final["marketplace_id"] = df_final["nama_marketplace"].map(
                    marketplace_mapping
                )

                store_cols = ["nama_toko", "marketplace_id"]
                insert_and_notify(
                    df_final,
                    "dim_stores",
                    columns=store_cols,
                    conflict_cols=["nama_toko"],
                )

                # PROSES CUSTOMERS
                st.info("Memproses tabel customers...")
                customers_cols = [
                    "nama_pembeli",
                    "no_telepon",
                    "alamat_lengkap",
                    "kecamatan",
                    "kelurahan",
                    "kabupaten_kota",
                    "provinsi",
                    "negara",
                    "kode_pos",
                ]
                customers_conflict_cols = [
                    "nama_pembeli",
                    "no_telepon",
                    "alamat_lengkap",
                ]
                insert_and_notify(
                    df_final,
                    "customers",
                    columns=customers_cols,
                    conflict_cols=customers_conflict_cols,
                )

                # PROSES PRODUCTS (dengan mapping)
                st.info("Memproses tabel products...")
                # Lakukan mapping ID terlebih dahulu
                dim_brands = db_manager.get_dim_brands()
                brand_mapping = dict(
                    zip(dim_brands["nama_brand"], dim_brands["brand_id"])
                )
                df_final["brand_id"] = df_final["nama_brand"].map(brand_mapping)

                products_cols = ["sku", "nama_produk", "brand_id", "harga_awal_produk"]
                insert_and_notify(
                    df_final,
                    "products",
                    columns=products_cols,
                    conflict_cols=["sku"],
                )

                # PROSES ORDERS (dengan mapping customer_id)
                st.info("Memproses tabel orders...")
                df_unique_customers_raw = (
                    df_final[customers_conflict_cols].drop_duplicates().dropna()
                )

                df_customer_map = db_manager.get_customers()

                df_final_with_customer_id = pd.merge(
                    df_final, df_customer_map, on=customers_conflict_cols, how="left"
                )

                if df_final_with_customer_id["customer_id"].isnull().any():
                    st.warning(
                        "Ditemukan customer yang tidak terpetakan, akan di-mapping ke ID 999 (Unknown)."
                    )

                    df_final_with_customer_id["customer_id"].fillna(999, inplace=True)

                    df_final_with_customer_id["customer_id"] = (
                        df_final_with_customer_id["customer_id"].astype(int)
                    )

                    st.success("Berhasil memetakan customer kosong ke ID 999.")

                if not df_final_with_customer_id["customer_id"].isnull().any():
                    st.success(
                        "Verifikasi berhasil! Semua baris pesanan kini memiliki customer_id yang valid."
                    )

                order_level_columns = {
                    "customer_id": "first",
                    "order_status": "first",
                    "is_fake_order": "first",
                    "waktu_pesanan_dibuat": "first",
                    "waktu_pesanan_dibayar": "first",
                    "waktu_kadaluwarsa": "first",
                    "waktu_proses": "first",
                    "waktu_selesai": "first",
                    "waktu_pembatalan": "first",
                    "yang_membatalkan": "first",
                    "pesan_dari_pembeli": "first",
                    "timestamp_input_data": "first",
                }

                df_orders_normalized = (
                    df_final_with_customer_id.groupby("order_id")
                    .agg(order_level_columns)
                    .reset_index()
                )

                df_orders_normalized.replace({pd.NaT: None}, inplace=True)
                df_orders_normalized = df_orders_normalized.astype(object)

                orders_columns = [
                    "order_id",
                    "customer_id",
                    "order_status",
                    "is_fake_order",
                    "waktu_pesanan_dibuat",
                    "waktu_pesanan_dibayar",
                    "waktu_kadaluwarsa",
                    "waktu_proses",
                    "waktu_selesai",
                    "waktu_pembatalan",
                    "yang_membatalkan",
                    "pesan_dari_pembeli",
                    "timestamp_input_data",
                ]

                cols_to_update = [
                    "order_status",
                    "is_fake_order",
                    "waktu_proses",
                    "waktu_selesai",
                    "waktu_pembatalan",
                    "yang_membatalkan",
                    "pesan_dari_pembeli",
                ]

                insert_and_notify(
                    df_orders_normalized,
                    "orders",
                    columns=orders_columns,
                    conflict_cols=["order_id"],
                    update_cols=cols_to_update,
                )

                st.info("Memproses tabel order_items...")

                df_products_map = db_manager.get_products()[["sku", "product_id"]]
                df_stores_map = db_manager.get_dim_stores()[["nama_toko", "store_id"]]

                df_mapped = pd.merge(df_final, df_products_map, on="sku", how="left")

                df_mapped = pd.merge(
                    df_mapped, df_stores_map, on="nama_toko", how="left"
                )

                if df_mapped[["product_id", "store_id"]].isnull().any().any():
                    st.warning(
                        "Ditemukan data yang gagal di-mapping. Baris ini akan dilewati."
                    )
                    df_mapped.dropna(subset=["product_id", "store_id"], inplace=True)

                df_mapped["product_id"] = df_mapped["product_id"].astype(int)
                df_mapped["store_id"] = df_mapped["store_id"].astype(int)

                st.success("Semua foreign keys berhasil di-mapping.")

                final_columns = [
                    "order_id",
                    "product_id",
                    "store_id",
                    "jumlah",
                    "harga_satuan",
                    "subtotal_produk",
                    "diskon_penjual",
                    "voucher",
                    "voucher_toko",
                ]

                df_order_items_final = df_mapped[final_columns]

                oi_conflict_cols = ["order_id", "product_id", "store_id"]

                insert_and_notify(
                    df_order_items_final,
                    "order_items",
                    columns=final_columns,
                    conflict_cols=oi_conflict_cols,
                )

                # TODO: PROSES SHIPMENTS
                st.info("Memproses tabel shipments...")
                df_shipping_map = db_manager.get_dim_shipping_services()

                df_mapped = pd.merge(
                    df_final,
                    df_shipping_map,
                    left_on="jasa_kirim",
                    right_on="jasa_kirim",
                    how="left",
                )

                if df_mapped["service_id"].isnull().any():
                    st.warning(
                        "Ditemukan jasa kirim yang tidak terpetakan, akan di-mapping ke ID 999 (Unknown)."
                    )

                    df_mapped["service_id"].fillna(999, inplace=True)

                df_mapped["service_id"] = df_mapped["service_id"].astype(int)

                df_shipments_normalized = (
                    df_mapped.groupby("no_resi")
                    .agg(
                        order_id=("order_id", "first"),
                        service_id=("service_id", "first"),
                        gudang_asal=("gudang_asal", "first"),
                        sesi=("sesi", "first"),
                        ongkos_kirim=("ongkos_kirim", "first"),
                        diskon_ongkos_kirim_penjual=(
                            "diskon_ongkos_kirim_penjual",
                            "first",
                        ),
                        diskon_ongkos_kirim_marketplace=(
                            "diskon_ongkos_kirim_marketplace",
                            "first",
                        ),
                        waktu_cetak=("waktu_cetak", "first"),
                        waktu_pesanan_dikirim=("waktu_pesanan_dikirim", "first"),
                    )
                    .reset_index()
                )

                st.success("Berhasil mengagregasi data ke level shipment!")

                shipments_columns = [
                    "order_id",
                    "no_resi",
                    "service_id",
                    "gudang_asal",
                    "sesi",
                    "ongkos_kirim",
                    "diskon_ongkos_kirim_penjual",
                    "diskon_ongkos_kirim_marketplace",
                    "waktu_cetak",
                    "waktu_pesanan_dikirim",
                ]

                df_shipments_final = df_shipments_normalized[shipments_columns]

                conflict_cols = ["no_resi"]

                update_cols = ["waktu_pesanan_dikirim", "waktu_cetak"]

                insert_and_notify(
                    df_shipments_final,
                    "shipments",
                    columns=shipments_columns,
                    conflict_cols=conflict_cols,
                    update_cols=update_cols,
                )

                # PROSES PAYMENTS
                st.info("Memproses tabel payments...")
                df_methods_map = db_manager.get_dim_payment_methods()

                # 1. Mapping method_id dari metode_pembayaran
                df_mapped = pd.merge(
                    df_final,
                    df_methods_map,
                    left_on="metode_pembayaran",
                    right_on="metode_pembayaran",
                    how="left",
                )

                # 2. Tangani metode pembayaran yang tidak ditemukan
                if df_mapped["method_id"].isnull().any():
                    st.warning(
                        "Ditemukan metode pembayaran yang tidak terpetakan, akan di-mapping ke ID 999 (Unknown)."
                    )

                    # Ganti semua NaN di kolom method_id dengan 999
                    df_mapped["method_id"].fillna(999, inplace=True)

                df_mapped["method_id"] = df_mapped["method_id"].astype(int)

                df_payments_normalized = (
                    df_mapped[
                        [
                            "order_id",
                            "method_id",
                            "total_pesanan",
                            "biaya_pengelolaan",
                            "biaya_transaksi",
                        ]
                    ]
                    .drop_duplicates()
                    .groupby(by=["order_id"])
                    .agg(
                        {
                            "method_id": "first",
                            "total_pesanan": "sum",
                            "biaya_pengelolaan": "sum",
                            "biaya_transaksi": "sum",
                        }
                    )
                    .reset_index()
                )

                st.success("Berhasil mengagregasi data ke level payment!")

                payments_columns = [
                    "order_id",
                    "method_id",
                    "total_pesanan",
                    "biaya_pengelolaan",
                    "biaya_transaksi",
                ]

                df_payments_final = df_payments_normalized[payments_columns]

                conflict_cols = ["order_id"]

                update_cols = ["biaya_pengelolaan", "biaya_transaksi"]

                insert_and_notify(
                    df_payments_final,
                    "payments",
                    columns=payments_columns,
                    conflict_cols=conflict_cols,
                    update_cols=update_cols,
                )

                # Tampilkan balon hanya sekali di akhir jika semua proses berhasil
                st.balloons()

        except Exception as e:
            st.error(f"Terjadi error saat memproses file: {e}")
            st.warning("Pastikan format file sesuai dengan template BigSeller.")

with admin_regular_tab:
    st.subheader("Unggah Data Admin Regular")
    st.info("Fitur ini akan diimplementasikan di kemudian hari.")
    # TODO: Logika untuk admin regular akan ditambahkan di sini.

with admin_mp_return_tab:
    st.subheader("Input Data Retur")
    with st.form("retur_form"):
        tanggal_retur = st.date_input("Tanggal Retur")
        st.markdown(
            "Masukkan Order ID yang diretur, pisahkan dengan koma atau baris baru."
        )
        order_ids_input = st.text_area("Order ID", height=150)

        submit_retur_button = st.form_submit_button("Simpan Data Retur")

        if submit_retur_button:
            if order_ids_input:
                # Memproses input teks menjadi list of strings
                order_ids = [
                    oid.strip() for oid in order_ids_input.split() if oid.strip()
                ]

                if db_manager.insert_returns_batch(tanggal_retur, order_ids):
                    st.success(f"✅ {len(order_ids)} data retur berhasil disimpan!")
                else:
                    st.error("❌ Gagal menyimpan data retur.")
            else:
                st.warning("Order ID tidak boleh kosong.")
