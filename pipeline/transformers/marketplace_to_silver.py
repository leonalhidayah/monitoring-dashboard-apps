import pandas as pd
import pandera as pa

# Impor dari modul Anda sendiri
from pipeline.config.column_mappings import SHOPEE_MAP, TIKTOK_MAP  # , TOKOPEDIA_MAP
from pipeline.config.value_mappings import PAYMENT_METHOD_MAP, SHIPPING_PROVIDER_MAP
from pipeline.schemas.bigseller_schema import bigseller_schema
from pipeline.utils.helpers import (
    clean_currency_columns,
    clean_datetime_columns,
    load_dataframe,
    standardize_mapping_column,
)

# --- LOGIKA TRANSFORMASI SPESIFIK SUMBER ---


def _transform_shopee(df):
    """Logika transformasi spesifik untuk Shopee."""

    # 1. Rename kolom
    df = df.rename(columns=SHOPEE_MAP)

    # 2. Pengayaan & Pengisian Default
    df["Marketplace"] = "Shopee"
    df["Toko Marketplace"] = (
        "herba pusat indonesia"  # Bisa dipindah ke config jika perlu
    )
    df["Negara"] = df.get("Negara", "indonesia")
    df["Kode Pos"] = df.get("Kode Pos", None)
    df["Kecamatan"] = df.get("Kecamatan", None)
    df["Kelurahan"] = df.get("Kelurahan", None)
    df["Gudang Asal"] = df.get("Gudang Asal", "Default Warehouse")

    # Kolom opsional yg mungkin tidak ada di file
    optional_datetime_cols = ["Waktu Proses", "Waktu Cetak", "Waktu Pembatalan"]
    for col in optional_datetime_cols:
        df[col] = df.get(col, None)  # Isi None jika tidak ada

    df["Yang Membatalkan"] = df.get("Yang Membatalkan", None)

    # Kolom finansial yg mungkin tidak ada
    optional_finance_cols = [
        "Diskon Ongkos Kirim Penjual",
        "Biaya Pengelolaan",
        "Biaya Transaksi",
    ]
    for col in optional_finance_cols:
        df[col] = df.get(col, 0.0)

    # 3. Pembersihan Tipe Data
    currency_columns = [
        "Harga Satuan",
        "Subtotal Produk",
        "Harga Awal Produk",
        "Ongkos Kirim",
        "Diskon Ongkos Kirim Penjual",
        "Diskon Ongkos Kirim Marketplace",
        "Total Pesanan",
        "Biaya Pengelolaan",
        "Biaya Transaksi",
        "Diskon Penjual",
        "Diskon Marketplace",
        "Voucher",
        "Voucher Toko",
    ]
    df = clean_currency_columns(df, currency_columns)

    datetime_columns = [
        "Waktu Pesanan Dibuat",
        "Waktu Pesanan Dibayar",
        "Waktu Kedaluwarsa",
        "Waktu Proses",
        "Waktu Cetak",
        "Waktu Pesanan Dikirim",
        "Waktu Selesai",
        "Waktu Pembatalan",
    ]
    df = clean_datetime_columns(df, datetime_columns)

    # 4. Mapping Metode Pengiriman & Metode Pembayaran
    df["Jasa Kirim yang Dipilih Pembeli"] = standardize_mapping_column(
        df, "Jasa Kirim yang Dipilih Pembeli", SHIPPING_PROVIDER_MAP
    )

    df["Metode Pembayaran"] = standardize_mapping_column(
        df, "Metode Pembayaran", PAYMENT_METHOD_MAP
    )

    return df


# TODO: TRANSFORM TIKTOK
def _transform_tiktok(df):
    """Logika transformasi spesifik untuk TikTok."""

    # 1. Rename kolom
    df = df.rename(columns=TIKTOK_MAP)

    # 2. Pengayaan & Pengisian Default
    df["Marketplace"] = "TikTok"
    df["Toko Marketplace"] = (
        "herba pusat indonesia"  # Bisa dipindah ke config jika perlu
    )
    df["Negara"] = df.get("Negara", "indonesia")
    df["Kode Pos"] = df.get("Kode Pos", None)
    df["Kecamatan"] = df.get("Kecamatan", None)
    df["Kelurahan"] = df.get("Kelurahan", None)
    df["Gudang Asal"] = df.get("Gudang Asal", "Default Warehouse")

    # Kolom opsional yg mungkin tidak ada di file
    optional_datetime_cols = [
        "Waktu Proses",
        "Waktu Cetak",
        "Waktu Pembatalan",
        "Waktu Kedaluwarsa",
    ]
    for col in optional_datetime_cols:
        df[col] = df.get(col, None)  # Isi None jika tidak ada

    df["Yang Membatalkan"] = df.get("Yang Membatalkan", None)

    # Kolom finansial yg mungkin tidak ada
    optional_finance_cols = [
        "Diskon Ongkos Kirim Penjual",
        "Biaya Pengelolaan",
        "Biaya Transaksi",
        "Voucher Toko",
    ]
    for col in optional_finance_cols:
        df[col] = df.get(col, 0.0)

    # # 3. Pembersihan Tipe Data
    currency_columns = [
        "Subtotal Produk",
        "Harga Awal Produk",
        "Ongkos Kirim",
        "Diskon Ongkos Kirim Penjual",
        "Diskon Ongkos Kirim Marketplace",
        "Total Pesanan",
        "Biaya Pengelolaan",
        "Biaya Transaksi",
        "Diskon Penjual",
        "Diskon Marketplace",
        "Voucher",
        "Voucher Toko",
    ]
    df = clean_currency_columns(df, currency_columns)

    df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce")
    df["Harga Satuan"] = df["Subtotal Produk"] / df["Jumlah"]

    datetime_columns = [
        "Waktu Pesanan Dibuat",
        "Waktu Pesanan Dibayar",
        "Waktu Kedaluwarsa",
        "Waktu Proses",
        "Waktu Cetak",
        "Waktu Pesanan Dikirim",
        "Waktu Selesai",
        "Waktu Pembatalan",
    ]
    df = clean_datetime_columns(df, datetime_columns)

    # 4. Mapping Metode Pengiriman
    df["Metode Pembayaran"] = standardize_mapping_column(
        df, "Metode Pembayaran", PAYMENT_METHOD_MAP
    )

    return df


# --- FUNGSI UTAMA ---


def transform_to_bigseller_format(file, source):
    """
    Fungsi utama pipeline Bronze -> Silver.
    Menerima file upload dan sumbernya, mengembalikan DataFrame bersih.
    """

    # 1. EXTRACT (E) - Membaca data mentah
    df = load_dataframe(file)

    # 2. TRANSFORM (T) - Memilih transformasi yang tepat
    if source == "Shopee":
        df_transformed = _transform_shopee(df)
    elif source == "TikTok":
        df_transformed = _transform_tiktok(df)
    else:
        raise ValueError(f"Sumber data {source} tidak didukung.")

    # 3. VALIDATE - Memvalidasi output terhadap kontrak skema
    try:
        # Skema akan otomatis:
        # 1. (coerce=True) Memaksa tipe data (str ke int/float/datetime)
        # 2. (strict="filter") Menghapus kolom ekstra yg tidak ada di skema
        validated_df = bigseller_schema.validate(df_transformed)

    except pa.errors.SchemaError as e:
        print("--- Gagal Validasi Skema ---")
        print(e.failure_cases)  # Menampilkan data yang gagal
        print("------------------------------")
        raise Exception(f"Data tidak sesuai format BigSeller. Cek detail error: \n{e}")

    # Buat nama file yang bersih untuk di-download
    clean_filename = f"silver_bigseller_format_{source.lower()}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv"

    return validated_df, clean_filename
