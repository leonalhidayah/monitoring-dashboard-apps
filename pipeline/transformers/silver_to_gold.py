import logging

import pandas as pd
import streamlit as st  # Kita gunakan untuk st.info di orkestrator

# Impor utilitas database Anda
import pipeline.utils.db_utils as db

# Impor semua mapping dan skema
from pipeline.config import column_mappings as maps
from pipeline.config import value_mappings as val_maps
from pipeline.config.column_mappings import (
    CUSTOMERS_MAP,
    MARKETPLACES_MAP,
    ORDER_ITEMS_MAP,
    ORDERS_MAP,
    PAYMENT_METHODS_MAP,
    PAYMENTS_MAP,
    PRODUCTS_MAP,
    SHIPMENTS_MAP,
    SHIPPING_SERVICES_MAP,
    STORES_MAP,
)
from pipeline.config.value_mappings import BRAND_MAP, MARKETPLACE_MAP
from pipeline.schemas import gold_schema as schemas


# Independent Dimmension Table Builders
def _build_dim_brands(df_silver):
    """
    Menyiapkan DataFrame dim_brands untuk di-UPSERT.
    Output: DataFrame dengan kolom ['nama_brand']
    """
    df_dim = df_silver[["SKU"]].copy()

    # Enrichment
    df_dim["sku_prefix"] = df_dim["SKU"].str.split("-", n=1).str[0]
    df_dim["nama_brand"] = df_dim["sku_prefix"].map(BRAND_MAP).fillna("Unknown")

    df_dim_final = (
        df_dim[["nama_brand"]].drop_duplicates().dropna(subset=["nama_brand"])
    )

    return df_dim_final


def _build_dim_marketplaces(df_silver):
    """
    Menyiapkan DataFrame dim_marketplaces untuk di-UPSERT.
    Output: DataFrame dengan kolom ['nama_marketplace']
    """
    df_dim = df_silver[["Marketplace"]].copy()
    df_dim = (
        df_dim.drop_duplicates(subset=["Marketplace"])
        .dropna(subset=["Marketplace"])
        .rename(columns=MARKETPLACES_MAP)
    )

    return df_dim


def _build_dim_shipping_services(df_silver):
    """
    Menyiapkan DataFrame dim_shipping_services untuk di-UPSERT.
    Output: DataFrame dengan kolom ['jasa_kirim']
    """
    df_dim = df_silver[["Jasa Kirim yang Dipilih Pembeli"]].copy()
    df_dim = (
        df_dim.drop_duplicates(subset=["Jasa Kirim yang Dipilih Pembeli"])
        .dropna(subset=["Jasa Kirim yang Dipilih Pembeli"])
        .rename(columns=SHIPPING_SERVICES_MAP)
    )

    return df_dim


def _build_dim_payment_methods(df_silver):
    """
    Menyiapkan DataFrame dim_payment_methods untuk di-UPSERT.
    Output: DataFrame dengan kolom ['metode_pembayaran']
    """
    df_dim = df_silver[["Metode Pembayaran"]].copy()
    df_dim = (
        df_dim.drop_duplicates(subset=["Metode Pembayaran"])
        .dropna(subset=["Metode Pembayaran"])
        .rename(columns=PAYMENT_METHODS_MAP)
    )

    return df_dim


def _build_dim_customers(df_silver):
    """
    Menyiapkan DataFrame dim_customers untuk di-UPSERT.
    Output: DataFrame dengan natural keys gabungan.
    """
    # Tentukan natural key gabungan
    natural_key_cols = ["Nama Pembeli", "Nomor Telepon", "Alamat Lengkap"]

    # Ambil semua kolom yang ada di mapping
    all_cols = list(CUSTOMERS_MAP.keys())

    df_dim = df_silver[all_cols].copy()

    # Deduplikasi DAN hapus baris di mana natural key-nya NULL
    df_dim = df_dim.drop_duplicates(subset=natural_key_cols).dropna(
        subset=natural_key_cols
    )

    df_dim = df_dim.rename(columns=CUSTOMERS_MAP)

    return df_dim


# Dependent Dimension Table Builders
def _build_dim_stores(df_silver, marketplace_key_map: dict):
    """
    Menyiapkan DataFrame dim_stores (dependen).
    Menerima key map (dict), bukan DataFrame.
    """
    df_dim = df_silver[list(STORES_MAP.keys())].copy()

    # Deduplikasi berdasarkan natural key
    df_dim = df_dim.drop_duplicates(subset=["Marketplace", "Toko Marketplace"]).dropna(
        subset=["Toko Marketplace"]
    )

    df_dim = df_dim.rename(columns=STORES_MAP)

    # Enrichment
    df_dim["nama_toko"] = (
        df_dim["nama_marketplace"].map(MARKETPLACE_MAP) + " " + df_dim["nama_toko_raw"]
    )

    df_dim["marketplace_id"] = df_dim["nama_marketplace"].map(marketplace_key_map)

    if df_dim["marketplace_id"].isnull().any():
        logging.warning("Marketplace ID tidak ditemukan, diisi dengan 9999 (Unknown).")
        df_dim["marketplace_id"] = df_dim["marketplace_id"].fillna(9999).astype(int)

    return schemas.dim_stores_schema.validate(df_dim)


def _build_dim_products(df_silver, brand_key_map: dict):
    """
    Menyiapkan DataFrame dim_products (dependen).
    Menerima key map (dict), bukan DataFrame.
    """
    df_dim = df_silver[list(PRODUCTS_MAP.keys())].copy()

    # Deduplikasi berdasarkan natural key
    df_dim = df_dim.drop_duplicates(subset=["SKU"]).dropna(subset=["SKU"])
    df_dim = df_dim.rename(columns=PRODUCTS_MAP)

    # Enrichment (string-based)
    df_dim["sku_prefix"] = df_dim["sku"].str.split("-", n=1).str[0]
    df_dim["nama_brand"] = df_dim["sku_prefix"].map(BRAND_MAP).fillna("Unknown")

    df_dim["brand_id"] = df_dim["nama_brand"].map(brand_key_map)

    if df_dim["brand_id"].isnull().any():
        logging.warning("Brand ID tidak ditemukan, diisi dengan 9999 (Unknown).")
        df_dim["brand_id"] = df_dim["brand_id"].fillna(9999).astype(int)

    return schemas.dim_products_schema.validate(df_dim)


# Fact Table Builder with Linking and Aggregation
def _build_fact_orders(df_clean_silver: pd.DataFrame, key_maps: dict) -> pd.DataFrame:
    """
    Menyiapkan DataFrame fact_orders yang tertaut dengan Foreign Keys.
    Menerima 'key_maps' (dict berisi DataFrame kecil) dari orkestrator.
    """

    natural_key_cols_silver = ["Nama Pembeli", "Nomor Telepon", "Alamat Lengkap"]
    natural_key_cols_gold = ["nama_pembeli", "no_telepon", "alamat_lengkap"]
    timestamp_source_col = "Tanggal Gudang"

    # 1. Validasi Key Map
    customer_id_map_df = key_maps.get("customers")
    if customer_id_map_df is None:
        raise ValueError("Customer key map (DataFrame) tidak ditemukan di key_maps.")

    # 2. Siapkan Data Fakta
    fact_cols_silver = list(ORDERS_MAP.keys())

    # Strict Check 1
    if timestamp_source_col not in df_clean_silver.columns:
        raise ValueError(
            f"CRITICAL ERROR: Kolom wajib '{timestamp_source_col}' tidak ditemukan di file input! "
            "Mohon pastikan tim gudang menggunakan template terbaru."
        )

    #    Copy data
    df_fact = df_clean_silver[fact_cols_silver + natural_key_cols_silver].copy()

    # 3. Validasi Data Kosong (Strict Check 2)
    if df_fact[timestamp_source_col].isnull().any():
        missing_count = df_fact[timestamp_source_col].isnull().sum()
        sample_missing = (
            df_fact[df_fact[timestamp_source_col].isnull()]["Nomor Pesanan"]
            .head(3)
            .tolist()
        )

        raise ValueError(
            f"VALIDASI GAGAL: Ditemukan {missing_count} pesanan dengan '{timestamp_source_col}' KOSONG. "
            f"Kolom ini wajib diisi. Contoh Pesanan: {sample_missing}"
        )

    # 4. Konversi Date -> Timestamp (PostgreSQL Compatible)
    try:
        df_fact[timestamp_source_col] = pd.to_datetime(df_fact[timestamp_source_col])
    except Exception as e:
        raise ValueError(
            f"Gagal mengonversi '{timestamp_source_col}' ke format Timestamp: {e}"
        )

    # 5. Deduplikasi & Rename
    df_fact = df_fact.drop_duplicates(subset=["Nomor Pesanan"])

    df_fact = df_fact.rename(columns=ORDERS_MAP)
    df_fact = df_fact.rename(columns=CUSTOMERS_MAP)

    # 6. Linking (Merge dengan Customer Map)
    df_fact_linked = pd.merge(
        df_fact,
        customer_id_map_df,
        on=natural_key_cols_gold,
        how="left",
    )

    # 7. Handle Missing Customer IDs
    if df_fact_linked["customer_id"].isnull().any():
        missing_count = df_fact_linked["customer_id"].isnull().sum()
        logging.warning(
            f"{missing_count} baris customer_id tidak ditemukan di fact_orders, "
            f"diisi dengan 9999 (Unknown)."
        )
        df_fact_linked["customer_id"] = (
            df_fact_linked["customer_id"].fillna(9999).astype(int)
        )

    # 8. Validasi Skema
    return schemas.orders_schema.validate(df_fact_linked)


def _build_fact_order_items(
    df_clean_silver: pd.DataFrame, key_maps: dict
) -> pd.DataFrame:
    """
    Menyiapkan DataFrame fact_order_items, tertaut, dan teragregasi.
    Menerima 'key_maps' (dict berisi DataFrame kecil) dari orkestrator.
    """

    product_natural_key_gold = "sku"
    store_link_keys_silver = ["Toko Marketplace", "Marketplace"]

    product_id_map_df = key_maps.get("products")
    store_id_map_df = key_maps.get("stores")

    if product_id_map_df is None or store_id_map_df is None:
        raise ValueError(
            "Product atau Store ID map (DataFrame) tidak ditemukan di key_maps."
        )

    fact_cols_silver = list(ORDER_ITEMS_MAP.keys())

    df_fact = df_clean_silver[fact_cols_silver + store_link_keys_silver].copy()

    df_fact = df_fact.rename(columns=ORDER_ITEMS_MAP)
    df_fact = df_fact.rename(columns=PRODUCTS_MAP)
    df_fact = df_fact.rename(columns=STORES_MAP)
    df_fact = df_fact.rename(columns=MARKETPLACES_MAP)

    # ENRICHMENT: Buat 'nama_toko' untuk linking
    df_fact["nama_toko"] = (
        df_fact["nama_marketplace"].map(MARKETPLACE_MAP)
        + " "
        + df_fact["nama_toko_raw"]
    )

    # LINKING (Tautkan Foreign Keys)
    df_linked = pd.merge(
        df_fact,
        product_id_map_df,
        on=product_natural_key_gold,
        how="left",
    )

    df_linked = pd.merge(
        df_linked,
        store_id_map_df,
        on="nama_toko",
        how="left",
    )

    if df_linked[["product_id", "store_id"]].isnull().any().any():
        missing_count = df_linked[["product_id", "store_id"]].isnull().any(axis=1).sum()
        logging.warning(
            f"{missing_count} baris di order_items gagal di-mapping "
            f"(product_id atau store_id tidak ditemukan). Baris ini akan DIHAPUS."
        )
        df_linked.dropna(subset=["product_id", "store_id"], inplace=True)

    grouping_keys = ["order_id", "product_id", "store_id"]

    agg_rules = {
        "jumlah": "sum",
        "harga_satuan": "mean",
        "subtotal_produk": "sum",
        "diskon_penjual": "sum",
        "voucher": "sum",
        "voucher_toko": "sum",
    }

    cols_to_agg = {k: v for k, v in agg_rules.items() if k in df_linked.columns}

    df_fact_agg = df_linked.groupby(grouping_keys).agg(cols_to_agg).reset_index()

    df_fact_agg["product_id"] = df_fact_agg["product_id"].astype(int)
    df_fact_agg["store_id"] = df_fact_agg["store_id"].astype(int)

    return schemas.order_items_schema.validate(df_fact_agg)


def _build_fact_shipments(
    df_clean_silver: pd.DataFrame, key_maps: dict
) -> pd.DataFrame:
    """
    Menyiapkan DataFrame fact_shipments, tertaut, dan teragregasi per no_resi.
    Menerima 'key_maps' (dict berisi DataFrame kecil) dari orkestrator.
    """

    shipping_natural_key_silver = "Jasa Kirim yang Dipilih Pembeli"
    shipping_natural_key_gold = "jasa_kirim"

    shipping_id_map_df = key_maps.get("shipping_services")
    if shipping_id_map_df is None:
        raise ValueError(
            "Shipping services ID map (DataFrame) tidak ditemukan di key_maps."
        )

    fact_cols_silver = list(SHIPMENTS_MAP.keys())

    df_fact = df_clean_silver[fact_cols_silver + [shipping_natural_key_silver]].copy()

    df_fact = df_fact.rename(columns=SHIPMENTS_MAP)
    df_fact = df_fact.rename(columns=SHIPPING_SERVICES_MAP)  # Me-rename natural key

    df_linked = pd.merge(
        df_fact,
        shipping_id_map_df,
        on=shipping_natural_key_gold,
        how="left",
    )

    if df_linked["service_id"].isnull().any():
        missing_count = df_linked["service_id"].isnull().sum()
        logging.warning(
            f"{missing_count} baris di fact_shipments gagal di-mapping "
            f"(service_id tidak ditemukan). Diisi dengan 9999 (Unknown)."
        )
        df_linked["service_id"].fillna(9999, inplace=True)

    df_linked["service_id"] = df_linked["service_id"].astype(int)

    df_linked.dropna(subset=["no_resi"], inplace=True)

    cols_in_df = set(df_linked.columns)

    agg_spec = {
        "order_id": ("order_id", "first"),
        "service_id": ("service_id", "first"),
        "gudang_asal": ("gudang_asal", "first"),
        "sesi": ("sesi", "first"),
        "ongkos_kirim": ("ongkos_kirim", "first"),
        "diskon_ongkos_kirim_penjual": ("diskon_ongkos_kirim_penjual", "first"),
        "diskon_ongkos_kirim_marketplace": ("diskon_ongkos_kirim_marketplace", "first"),
        "waktu_cetak": ("waktu_cetak", "first"),
        "waktu_pesanan_dikirim": ("waktu_pesanan_dikirim", "first"),
    }

    valid_agg_spec = {
        col: spec for col, spec in agg_spec.items() if spec[0] in cols_in_df
    }

    df_fact_agg = df_linked.groupby("no_resi").agg(**valid_agg_spec).reset_index()

    return schemas.shipments_schema.validate(df_fact_agg)


def _build_fact_payments(df_clean_silver: pd.DataFrame, key_maps: dict) -> pd.DataFrame:
    """
    Menyiapkan DataFrame fact_payments, tertaut, dan teragregasi per order_id.
    Menerima 'key_maps' (dict berisi DataFrame kecil) dari orkestrator.
    """

    payment_natural_key_gold = "metode_pembayaran"

    payment_id_map_df = key_maps.get("payment_methods")
    if payment_id_map_df is None:
        raise ValueError(
            "Payment methods ID map (DataFrame) tidak ditemukan di key_maps."
        )

    fact_cols_silver = list(PAYMENTS_MAP.keys())
    df_fact = df_clean_silver[fact_cols_silver].copy()

    df_fact = df_fact.rename(columns=PAYMENTS_MAP)

    df_linked = pd.merge(
        df_fact,
        payment_id_map_df,
        on=payment_natural_key_gold,  # 'metode_pembayaran'
        how="left",
    )

    if df_linked["method_id"].isnull().any():
        missing_count = df_linked["method_id"].isnull().sum()
        logging.warning(
            f"{missing_count} baris di fact_payments gagal di-mapping "
            f"(method_id tidak ditemukan). Diisi dengan 9999 (Unknown)."
        )
        df_linked["method_id"].fillna(9999, inplace=True)

    df_linked["method_id"] = df_linked["method_id"].astype(int)

    agg_columns = [
        "order_id",
        "method_id",
        "total_pesanan",
        "biaya_pengelolaan",
        "biaya_transaksi",
    ]

    valid_agg_columns = [col for col in agg_columns if col in df_linked.columns]

    df_fact_agg = (
        df_linked[valid_agg_columns]
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

    return schemas.payments_schema.validate(df_fact_agg)


# ORCHESTRATOR UTILITIES
def process_silver_to_gold(df_clean_silver: pd.DataFrame):
    """
    Orkestrator pipeline Silver -> Gold (Metode Serial yang Dioptimalkan).

    Args:
        df_clean_silver: DataFrame bersih dari silver_standardizer.
    """

    st.info("Memulai pipeline Silver-to-Gold...")

    try:
        # === TAHAP 1: SIAPKAN & UPSERT DIMENSI INDEPENDEN ===
        st.info("1/5: Memproses dimensi independen (Customers, Brands, etc.)...")

        # 1A. Siapkan DataFrame (T1 - Transform)
        df_dim_brands = _build_dim_brands(df_clean_silver)
        df_dim_marketplaces = _build_dim_marketplaces(df_clean_silver)
        df_dim_shipping_services = _build_dim_shipping_services(df_clean_silver)
        df_dim_payment_methods = _build_dim_payment_methods(df_clean_silver)
        df_dim_customers = _build_dim_customers(df_clean_silver)

        # 1B. Load ke Database (L1 - Load)
        db.bulk_upsert(df_dim_brands, "dim_brands", ["nama_brand"])
        db.bulk_upsert(df_dim_marketplaces, "dim_marketplaces", ["nama_marketplace"])
        db.bulk_upsert(
            df_dim_shipping_services, "dim_shipping_services", ["jasa_kirim"]
        )
        db.bulk_upsert(
            df_dim_payment_methods, "dim_payment_methods", ["metode_pembayaran"]
        )
        db.bulk_upsert(
            df_dim_customers,
            "customers",
            ["nama_pembeli", "no_telepon", "alamat_lengkap"],
        )

        # === TAHAP 2: AMBIL KEY MAPS UNTUK DIMENSI DEPENDEN ===
        st.info("2/5: Mengambil key maps untuk dimensi dependen...")

        # 2A. Siapkan batch natural keys (dari data yg baru disiapkan)
        brand_keys_df = df_dim_brands[["nama_brand"]]
        marketplace_keys_df = df_dim_marketplaces[["nama_marketplace"]]

        # 2B. Ambil key maps dari DB (T2 - Transform)
        brand_key_map_df = db.get_keys_for_batch(
            "dim_brands", ["brand_id", "nama_brand"], brand_keys_df
        )
        marketplace_key_map_df = db.get_keys_for_batch(
            "dim_marketplaces",
            ["marketplace_id", "nama_marketplace"],
            marketplace_keys_df,
        )

        # 2C. Konversi ke DICT (sesuai kebutuhan _build_dim_dependen)
        brand_key_map_dict = dict(
            zip(brand_key_map_df["nama_brand"], brand_key_map_df["brand_id"])
        )
        marketplace_key_map_dict = dict(
            zip(
                marketplace_key_map_df["nama_marketplace"],
                marketplace_key_map_df["marketplace_id"],
            )
        )

        # === TAHAP 3: SIAPKAN & UPSERT DIMENSI DEPENDEN ===
        st.info("3/5: Memproses dimensi dependen (Products, Stores)...")

        # 3A. Siapkan DataFrame (T3 - Transform)
        df_dim_products = _build_dim_products(df_clean_silver, brand_key_map_dict)
        df_dim_stores = _build_dim_stores(df_clean_silver, marketplace_key_map_dict)

        # 3B. Load ke Database (L2 - Load)
        db.bulk_upsert(df_dim_products, "products", ["sku"])
        db.bulk_upsert(df_dim_stores, "dim_stores", ["nama_toko"])

        # === TAHAP 4: AMBIL SEMUA KEY MAPS UNTUK FAKTA ===
        st.info("4/5: Mengambil semua key maps untuk tabel fakta...")

        # 4A. Siapkan DataFrame batch keys (dari df_clean_silver)

        # Customer (Key Gabungan)
        cust_keys_df = df_clean_silver[
            list(maps.CUSTOMERS_MAP.keys())
        ].drop_duplicates()
        cust_keys_df = cust_keys_df.rename(columns=maps.CUSTOMERS_MAP)

        # Product (Key Tunggal)
        prod_keys_df = (
            df_clean_silver[["SKU"]].drop_duplicates().rename(columns=maps.PRODUCTS_MAP)
        )

        # Store (Key Tunggal, tapi perlu di-build)
        store_keys_df = df_clean_silver[
            ["Toko Marketplace", "Marketplace"]
        ].drop_duplicates()
        store_keys_df = store_keys_df.rename(columns=maps.STORES_MAP)
        store_keys_df = store_keys_df.rename(columns=maps.MARKETPLACES_MAP)
        store_keys_df["nama_toko"] = (
            store_keys_df["nama_marketplace"].map(val_maps.MARKETPLACE_MAP)
            + " "
            + store_keys_df["nama_toko_raw"]
        )

        # Shipping (Key Tunggal)
        ship_keys_df = (
            df_clean_silver[["Jasa Kirim yang Dipilih Pembeli"]]
            .drop_duplicates()
            .rename(columns=maps.SHIPPING_SERVICES_MAP)
        )

        # Payment (Key Tunggal)
        pay_keys_df = (
            df_clean_silver[["Metode Pembayaran"]]
            .drop_duplicates()
            .rename(columns=maps.PAYMENT_METHODS_MAP)
        )

        # 4B. Ambil semua key maps dari DB (T4 - Transform)
        key_maps = {
            "customers": db.get_keys_for_batch(
                "customers",
                ["customer_id", "nama_pembeli", "no_telepon", "alamat_lengkap"],
                cust_keys_df,
            ),
            "products": db.get_keys_for_batch(
                "products", ["product_id", "sku"], prod_keys_df
            ),
            "stores": db.get_keys_for_batch(
                "dim_stores", ["store_id", "nama_toko"], store_keys_df[["nama_toko"]]
            ),
            "shipping_services": db.get_keys_for_batch(
                "dim_shipping_services", ["service_id", "jasa_kirim"], ship_keys_df
            ),
            "payment_methods": db.get_keys_for_batch(
                "dim_payment_methods", ["method_id", "metode_pembayaran"], pay_keys_df
            ),
        }

        # === TAHAP 5: BANGUN TABEL FAKTA ===
        st.info("5/5: Membangun tabel fakta (linking)...")

        # 5A. Bangun DataFrame (T5 - Transform)
        fact_orders = _build_fact_orders(df_clean_silver, key_maps)

        fact_order_items = _build_fact_order_items(df_clean_silver, key_maps)
        fact_shipments = _build_fact_shipments(df_clean_silver, key_maps)
        fact_payments = _build_fact_payments(df_clean_silver, key_maps)

        # === TAHAP 6: LOAD TABEL FAKTA ===
        st.info("6/6: Me-load tabel fakta ke database...")

        # 6A. Load ke Database (L3 - Load)
        db.bulk_upsert(fact_orders, "orders", ["order_id"])

        db.bulk_upsert(
            fact_order_items, "order_items", ["order_id", "product_id", "store_id"]
        )

        db.bulk_upsert(fact_shipments, "shipments", ["no_resi"])
        db.bulk_upsert(fact_payments, "payments", ["order_id"])

        st.success("🎉 Pipeline Silver-to-Gold Selesai!")
        return True

    except Exception as e:
        logging.exception("Gagal total di pipeline Silver-to-Gold.")
        st.error(f"Gagal total di pipeline Silver-to-Gold: {e}")
        raise e
