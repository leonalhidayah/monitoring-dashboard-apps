import datetime
import re
import warnings

import pandas as pd
import streamlit as st

# Asumsikan fungsi-fungsi ini ada di file lain
from data_preprocessor.utils import add_new_columns, clean_admin_marketplace_data
from database import db_manager
from views.config import get_now_in_jakarta
from views.style import load_css

warnings.filterwarnings("ignore")
load_css()

# =============================================================================
# DEFINISI KONSTANTA & FUNGSI HELPER
# Memusatkan daftar kolom dan logika berulang
# =============================================================================

# Definisikan daftar kolom sebagai konstanta agar mudah dirawat
CUSTOMER_KEY_COLS = ["nama_pembeli", "no_telepon", "alamat_lengkap"]
ORDER_ITEMS_FINAL_COLS = [
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
NUMERIC_COLS_FOR_AGG = [
    "jumlah",
    "harga_satuan",
    "subtotal_produk",
    "diskon_penjual",
    "voucher",
    "voucher_toko",
]


def load_data_from_uploader(uploaded_file):
    """Membaca file yang diunggah dan mengembalikannya sebagai DataFrame."""
    try:
        if uploaded_file.name.endswith(".csv"):
            # Biarkan pandas mendeteksi tipe data, lalu kita perbaiki nanti
            return pd.read_csv(uploaded_file, dtype=str)
        else:
            return pd.read_excel(uploaded_file, dtype=str)
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return None


def insert_and_notify(df, table_name, columns, conflict_cols, update_cols=None):
    """Fungsi pembungkus untuk insert data dan notifikasi UI (dipindah ke luar)."""
    result = db_manager.insert_orders_to_normalized_table(
        df,
        table_name,
        columns,
        conflict_cols=conflict_cols,
        update_cols=update_cols,
        # Default-nya tidak lagi drop duplicates di level ini
        drop_duplicates_row=False,
    )
    if result and result.get("status") == "success":
        st.success(result["message"])
    else:
        st.error(
            f"Gagal menyimpan data ke '{table_name}': {result.get('message', 'Error tidak diketahui')}"
        )


def run_etl_pipeline(df_raw, selected_date, selected_time, selected_sesi):
    """Fungsi utama yang menjalankan seluruh proses ETL."""

    # 1. TRANSFORMASI AWAL
    st.info("Membersihkan dan memperkaya data mentah...")
    df_clean = clean_admin_marketplace_data(df_raw)
    df_enriched = add_new_columns(df_clean)

    timestamp_input = datetime.datetime.combine(selected_date, selected_time)
    df_enriched["timestamp_input_data"] = timestamp_input
    df_enriched["sesi"] = selected_sesi
    df_enriched.replace({pd.NaT: None}, inplace=True)
    st.success("Data mentah berhasil diproses.")

    # 2. LOAD DIMENSI DASAR
    st.info("Memproses tabel dimensi dasar (brand, marketplace, dll)...")
    dimension_tables = {
        "dim_brands": ["nama_brand"],
        "dim_marketplaces": ["nama_marketplace"],
        "dim_shipping_services": ["jasa_kirim"],
        "dim_payment_methods": ["metode_pembayaran"],
    }
    for table_name, cols in dimension_tables.items():
        df_dim = df_enriched[cols].drop_duplicates().dropna()
        insert_and_notify(df_dim, table_name, columns=cols, conflict_cols=cols)

    # 3. MAPPING & ENRICHMENT LANJUTAN
    st.info("Mengambil data mapping dari database...")
    df_products_map = db_manager.get_products()[["sku", "product_id"]]
    df_stores_map = db_manager.get_dim_stores()[["nama_toko", "store_id"]]
    df_customer_map = db_manager.get_customers()

    df_mapped = pd.merge(df_enriched, df_products_map, on="sku", how="left")
    df_mapped = pd.merge(df_mapped, df_stores_map, on="nama_toko", how="left")
    df_mapped = pd.merge(df_mapped, df_customer_map, on=CUSTOMER_KEY_COLS, how="left")

    # Handle unmapped data
    df_mapped.dropna(subset=["product_id"], inplace=True)
    df_mapped["customer_id"].fillna(9999, inplace=True)
    df_mapped[["product_id", "customer_id"]] = df_mapped[
        ["product_id", "customer_id"]
    ].astype(int)
    st.success("Mapping ID produk dan customer selesai.")

    # 4. LOAD TABEL FAKTA & DIMENSI KOMPLEKS
    # PROSES CUSTOMERS
    df_customers = df_mapped[CUSTOMER_KEY_COLS].drop_duplicates().dropna()
    insert_and_notify(
        df_customers,
        "customers",
        columns=CUSTOMER_KEY_COLS,
        conflict_cols=CUSTOMER_KEY_COLS,
    )

    # PROSES ORDERS
    df_orders = df_mapped.groupby("order_id").first().reset_index()
    orders_cols = [
        col
        for col in df_orders.columns
        if col in db_manager.get_table_columns("orders")
    ]
    insert_and_notify(
        df_orders, "orders", columns=orders_cols, conflict_cols=["order_id"]
    )

    # PROSES ORDER_ITEMS (Bagian Paling Kritis)
    st.info("Memproses tabel order_items dengan agregasi varian...")
    df_order_items = df_mapped[ORDER_ITEMS_FINAL_COLS].copy()

    # Konversi tipe data ke numerik SEBELUM agregasi
    for col in NUMERIC_COLS_FOR_AGG:
        df_order_items[col] = pd.to_numeric(
            df_order_items[col], errors="coerce"
        ).fillna(0)

    # Agregasi untuk menangani produk varian
    grouping_keys = ["order_id", "product_id", "store_id"]
    agg_rules = {
        "jumlah": "sum",
        "harga_satuan": "mean",
        "subtotal_produk": "sum",
        "diskon_penjual": "sum",
        "voucher": "sum",
        "voucher_toko": "sum",
    }
    df_oi_agg = df_order_items.groupby(grouping_keys).agg(agg_rules).reset_index()

    conflict_cols_oi = ["order_id", "product_id", "store_id"]
    insert_and_notify(
        df_oi_agg,
        "order_items",
        columns=ORDER_ITEMS_FINAL_COLS,
        conflict_cols=conflict_cols_oi,
    )

    st.success("✅ Semua data berhasil diproses dan disimpan ke database!")
    st.balloons()


# =============================================================================
# UI STREAMLIT
# =============================================================================

st.header("Data Entry Harian Admin Marketplace")
admin_marketplace_tab, pesanan_khusus_marketplace_page = st.tabs(
    ["Marketplace", "Pesanan Khusus"]
)

with admin_marketplace_tab:
    st.subheader("Unggah Data Admin Marketplace")
    uploaded_file = st.file_uploader(
        "Upload file CSV atau Excel dari BigSeller", type=["csv", "xlsx"]
    )

    if uploaded_file:
        df_raw = load_data_from_uploader(uploaded_file)

        if df_raw is not None:
            st.info("File berhasil diunggah. Silakan lengkapi data di bawah ini.")
            if "selected_date" not in st.session_state:
                st.session_state.selected_date = get_now_in_jakarta().date()

            if "selected_time" not in st.session_state:
                st.session_state.selected_time = get_now_in_jakarta().time()

            selected_date = st.date_input(
                "Pilih tanggal input",
                key="selected_date",
            )

            selected_time = st.time_input(
                "Pilih waktu input",
                key="selected_time",
            )
            selected_sesi = st.selectbox(
                "Pilih Sesi", options=["SESI 1", "SESI 2", "SESI 3", "SESI 4"]
            )

            if st.button("Proses & Simpan Data"):
                with st.spinner(
                    "Memproses file dan menyimpan ke database... Ini mungkin memakan waktu beberapa saat."
                ):
                    run_etl_pipeline(
                        df_raw, selected_date, selected_time, selected_sesi
                    )


with pesanan_khusus_marketplace_page:
    st.subheader("Input Manual Pesanan Khusus")

    with st.form("special_order_form"):
        tanggal_input = st.date_input("Tanggal Input", value=get_now_in_jakarta())
        kategori_pesanan = st.selectbox(
            "Pilih Kategori Pesanan",
            ("RETURN", "FIKTIF_ORDER", "AFFILIATE", "CANCEL", "LAINNYA"),
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
