import logging

import numpy as np
import pandera.dtypes as pa_dtypes
import pandera.pandas as pa

from pipeline.config.value_mappings import (
    PAYMENT_METHOD_MAP,
    PROVINCE_MAPPING,
    SHIPPING_PROVIDER_MAP,
)
from pipeline.schemas.bigseller_schema import bigseller_schema
from pipeline.utils.helpers import (
    clean_currency_columns,
    clean_datetime_columns,
    clean_object_columns,
    fillna_by_other_column,
    fillna_currency_with_rules,
    fix_misconverted_currency,
    standardize_mapping_column,
)


# Main Function
def standardize_silver_data(df):
    """
    Membersihkan DataFrame (format BigSeller) yang kotor.
    TIDAK melakukan rename atau enrichment.
    HANYA membersihkan agar patuh pada bigseller_schema.
    """

    df.columns = df.columns.str.strip()

    # Tentukan tipe kolom untuk cleaning
    currency_cols = [
        k
        for k, v in bigseller_schema.columns.items()
        if isinstance(v.dtype, pa_dtypes.Float)
    ]

    datetime_cols = [
        k
        for k, v in bigseller_schema.columns.items()
        if isinstance(v.dtype, pa_dtypes.DateTime)
    ]

    object_cols = [
        k
        for k, v in bigseller_schema.columns.items()
        if isinstance(v.dtype, pa_dtypes.String)
    ]

    # Clean Teks (lakukan pertama)
    df = clean_object_columns(df, object_cols)

    lowercase_cols = [
        "Toko Marketplace",
        "Negara",
        "Provinsi",
        "Kabupaten/Kota",
        "Kecamatan",
        "Kelurahan",
        "Alamat Lengkap",
        "Nama Produk",
        "Nama Pembeli",
    ]

    upper_cols = ["Gudang", "Sesi Pengiriman", "Jenis Resi", "Status Pesanan"]

    df = clean_object_columns(df, lowercase_cols, case="lower")
    df = clean_object_columns(df, upper_cols, case="upper")

    # Clean Tipe Data Spesifik
    df = clean_currency_columns(df, currency_cols)

    df["Diskon Ongkos Kirim Marketplace"] = fix_misconverted_currency(
        df["Diskon Ongkos Kirim Marketplace"]
    )

    target_cols_zero_to_nan = [
        "Total Pesanan",
        "Subtotal Produk",
    ]  # Tambahkan kolom lain jika ada logic serupa

    for col in target_cols_zero_to_nan:
        if col in df.columns:
            df[col] = df[col].replace(0, np.nan)

    df = fillna_currency_with_rules(df)
    df = fillna_currency_with_rules(df, fill_col="Subtotal Produk")
    df["Harga Satuan"] = df["Harga Satuan"].fillna(df["Subtotal Produk"] / df["Jumlah"])
    df = fillna_by_other_column(
        df, fill_col="Harga Awal Produk", reference_col="Harga Satuan"
    )
    df = fillna_by_other_column(
        df, fill_col="Nama Pembeli", reference_col="Nama Penerima"
    )

    df = clean_datetime_columns(df, datetime_cols)

    # Mapping value ke standard
    df["Jasa Kirim yang Dipilih Pembeli"] = standardize_mapping_column(
        df, "Jasa Kirim yang Dipilih Pembeli", SHIPPING_PROVIDER_MAP
    )

    df["Metode Pembayaran"] = standardize_mapping_column(
        df, "Metode Pembayaran", PAYMENT_METHOD_MAP
    )

    df["Provinsi"] = standardize_mapping_column(df, "Provinsi", PROVINCE_MAPPING)

    # Validasi terhadap skema Silver
    try:
        logging.info("Memvalidasi skema data silver...")
        validated_df = bigseller_schema.validate(df)
        logging.info("Validasi Silver sukses.")
        return validated_df

    except pa.errors.SchemaError as e:
        logging.error("--- GAGAL VALIDASI SILVER STANDARDIZATION ---")
        logging.error(e.failure_cases)
        raise Exception(f"Data campuran tidak lolos standardisasi: \n{e}")
