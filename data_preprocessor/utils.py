import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

project_root = Path().cwd().parent

# GLOBAL VARIABLE
ZYY_STORE_LIST = [
    "SP zhi yang yao official store",
    "SP zhi yang yao",
    "SP zhi yang yao (iklan eksternal FB)",
    "SP zhi yang yao official",
    "SP zhi yang yao id",
    "SP zhi yang yao shop",
    "SP zhi yang yao indonesia",
    "SP zhi yang yao mart",
    "SP zhi yang yao store",
    "TT zhi yang yao official store",
    "LZ zhi yang yao",
    "LZ zhi yang yao id",
    "LZ zhi yang yao store makasar",
    "TP zhi yang yao official store",
    "TP zhi yang yao",
    "TP zhi yang yao store makassar",
    "TP zhi yang yao official medan",
]

JH_STORE_LIST = [
    "SP juwara herbal official store",
    "TT juwara herbal",
]

ENZ_STORE_LIST = [
    "SP enzhico",
    "SP enzhico shop",
    "SP enzhico store",
    "SP enzhico store indonesia",
    "SP enzhico shop indonesia",
    "SP enzhico indonesia",
    "SP enzhico authorize store",
    "TT enzhico authorized store",
    "LZ enzhico",
    "LZ enzhico store",
    "TP enzhico official store",
]

ERA_STORE_LIST = [
    "SP erassgo",
    "SP erassgo bandung",
    "SP erassgo official",
    "SP erassgo official store",
    "SP erassgo.co",
    "SP erassgo makassar",
    "TP erassgo",
    "LZ erassgo",
    "LZ erassgo store id",
]

TOKO_BANDUNG = ["SP zhi yang yao official", "SP erassgo bandung"]
MARKETPLACE_LIST = ["Lazada", "Shopee", "TikTok", "Tokopedia"]
BRAND_LIST = ["Zhi Yang Yao", "Enzhico", "Erassgo"]
AKUN_LIST = [
    "Zhi yang yao mall 1",
    "Zhi yang yao CPAS 03",
    "Zhi yang yao CPAS",
    "Erassgo CPAS 1",
    "Erassgo mall 1",
    "Enzhico CPAS 1",
]


# -- ORDERS DATA
def clean_admin_marketplace_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fungsi untuk membersihkan dan memproses data pesanan admin marketplace dari BigSeller.

    Args:
        df (pd.DataFrame): DataFrame mentah dari file yang diunggah.

    Returns:
        pd.DataFrame: DataFrame yang sudah bersih dan terstandarisasi.
    """
    df = df.copy()

    columns_mapping = {
        "Nomor Pesanan": "order_id",
        "Nomor Paket": "package_id",
        "Status Pesanan": "order_status",
        "Marketplace": "nama_marketplace",
        "Toko Marketplace": "nama_toko",
        "Nama Pembeli": "nama_pembeli",
        "Nomor Telepon": "no_telepon",
        "Kode Pos": "kode_pos",
        "Negara": "negara",
        "Provinsi": "provinsi",
        "Kabupaten/Kota": "kabupaten_kota",
        "Kecamatan": "kecamatan",
        "Kelurahan": "kelurahan",
        "Alamat Lengkap": "alamat_lengkap",
        "SKU": "sku",
        "Nama Produk": "nama_produk",
        "Jumlah": "jumlah",
        "Harga Satuan": "harga_satuan",
        "Subtotal Produk": "subtotal_produk",
        "Harga Awal Produk": "harga_awal_produk",
        "Gudang Asal": "gudang_asal",
        "Jasa Kirim yang Dipilih Pembeli": "jasa_kirim",
        "Metode Pengiriman": "metode_pengiriman",
        "Nomor Resi": "no_resi",
        "Ongkos Kirim": "ongkos_kirim",
        "Diskon Ongkos Kirim Penjual": "diskon_ongkos_kirim_penjual",
        "Diskon Ongkos Kirim Marketplace": "diskon_ongkos_kirim_marketplace",
        "Total Pesanan": "total_pesanan",
        "Metode Pembayaran": "metode_pembayaran",
        "Biaya Pengelolaan": "biaya_pengelolaan",
        "Biaya Transaksi": "biaya_transaksi",
        "Diskon Penjual": "diskon_penjual",
        "Diskon Marketplace": "diskon_marketplace",
        "Voucher": "voucher",
        "Voucher Toko": "voucher_toko",
        "Waktu Pesanan Dibuat": "waktu_pesanan_dibuat",
        "Waktu Pesanan Dibayar": "waktu_pesanan_dibayar",
        "Waktu Kedaluwarsa": "waktu_kadaluwarsa",
        "Waktu Proses": "waktu_proses",
        "Waktu Cetak": "waktu_cetak",
        "Waktu Pesanan Dikirim": "waktu_pesanan_dikirim",
        "Waktu Selesai": "waktu_selesai",
        "Waktu Pembatalan": "waktu_pembatalan",
        "Pesan dari Pembeli": "pesan_dari_pembeli",
        "Yang Membatalkan": "yang_membatalkan",
    }

    # Ganti nama kolom dan ambil kolom yang relevan
    df.rename(columns=columns_mapping, inplace=True)
    df = df[list(columns_mapping.values())]

    object_cols = df.select_dtypes(["object"]).columns.to_list()
    for col in object_cols:
        df[col] = df[col].str.strip()
        df[col] = df[col].str.replace(r"\xa0", " ", regex=True)

    # Standarisasi kolom teks (mengubah ke title case dan lowercase)
    df["nama_toko"] = df["nama_toko"].str.lower()
    df["sku"] = df["sku"].str.replace(r"\r\n", " ", regex=True)

    address_cols = [
        "negara",
        "provinsi",
        "kabupaten_kota",
        "kecamatan",
        "kelurahan",
        "alamat_lengkap",
        "nama_produk",
        "nama_pembeli",
    ]
    for col in address_cols:
        df[col] = df[col].str.lower()

    marketplace_map = {
        "Shopee": "SP",
        "Lazada": "LZ",
        "Tokopedia": "TP",
        "TikTok": "TT",
    }

    df["nama_toko"] = (
        df["nama_marketplace"].map(marketplace_map) + " " + df["nama_toko"].str.lower()
    )

    # df["marketplace_toko"] = df["nama_marketplace"] + df["nama_toko"]
    # df["nama_toko_standard"] = df["marketplace_toko"].map(store_mapping)

    # Konversi kolom tanggal dan waktu ke tipe datetime
    month_mapping = {
        "Jan": "Jan",
        "Feb": "Feb",
        "Mar": "Mar",
        "Apr": "Apr",
        "Mei": "May",
        "Jun": "Jun",
        "Jul": "Jul",
        "Agu": "Aug",
        "Sep": "Sep",
        "Okt": "Oct",
        "Nov": "Nov",
        "Des": "Dec",
    }

    # compile regex untuk ganti bulan (lebih cepat daripada loop biasa)
    pattern = re.compile(r"\b(" + "|".join(month_mapping.keys()) + r")\b")

    def replace_months(series: pd.Series) -> pd.Series:
        """Ganti bulan Indonesia ke format Inggris + parsing datetime."""
        replaced = series.astype(str).str.replace(
            pattern, lambda m: month_mapping.get(m.group()), regex=True
        )

        return pd.to_datetime(replaced, errors="coerce")

    datetime_cols = [
        "waktu_pesanan_dibuat",
        "waktu_pesanan_dibayar",
        "waktu_kadaluwarsa",
        "waktu_proses",
        "waktu_cetak",
        "waktu_pesanan_dikirim",
        "waktu_selesai",
        "waktu_pembatalan",
    ]

    df[datetime_cols] = df[datetime_cols].apply(replace_months)

    # Konversi kolom numerik
    currency_cols = [
        "harga_satuan",
        "subtotal_produk",
        "harga_awal_produk",
        "ongkos_kirim",
        "diskon_ongkos_kirim_penjual",
        "diskon_ongkos_kirim_marketplace",
        "total_pesanan",
        "biaya_pengelolaan",
        "biaya_transaksi",
        "diskon_penjual",
        "diskon_marketplace",
        "voucher",
        "voucher_toko",
    ]
    for col in currency_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Standarisasi kolom numerik yang mungkin perlu konversi ke float
    # df["ongkos_kirim"] = df["ongkos_kirim"].astype(float)

    # df.drop(columns="marketplace_toko", inplace=True)

    return df


def add_new_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fungsi untuk menambahkan kolom-kolom baru berdasarkan logika bisnis.

    Args:
        df (pd.DataFrame): DataFrame yang sudah bersih.

    Returns:
        pd.DataFrame: DataFrame dengan kolom-kolom baru.
    """
    df = df.copy()

    # Tambah kolom baru
    df["is_fake_order"] = np.where(
        df["pesan_dari_pembeli"].str.contains("FO", na=False), True, False
    )

    df["gudang_asal"] = np.where(
        df["nama_toko"].isin(TOKO_BANDUNG), "Bandung", "Jakarta"
    )

    brand_map = {
        "ZYY": "Zhi Yang Yao",
        "ERA": "Erassgo",
        "ENZ": "Enzhico",
        "KDK": "Kudaku",
        "JOY": "Joymens",
        "GLU": "Glumevit",
        "GOD": "Godfather",
        "BTN": "Bycetin",
        "BIO": "Bio Antanam",
        "DOU": "Doui",
    }

    # ambil prefix SKU sebelum tanda '-'
    df["nama_brand"] = df["sku"].str.split("-", n=1).str[0].map(brand_map)
    df["nama_brand"].fillna("Unknown", inplace=True)

    return df


def add_timestamp_and_sesi_columns(
    df: pd.DataFrame, timestamp_input_data: datetime
) -> pd.DataFrame:
    """
    Fungsi untuk menambahkan kolom timestamp_input_data dan sesi ke DataFrame.

    Args:
        df (pd.DataFrame): DataFrame yang sudah dibersihkan.
        timestamp_input_data (datetime): Objek datetime yang berisi tanggal dan waktu input data.

    Returns:
        pd.DataFrame: DataFrame dengan kolom tambahan.
    """
    df["timestamp_input_data"] = timestamp_input_data

    hours = timestamp_input_data.hour
    conditions = [
        (hours >= 7) & (hours < 12),
        (hours >= 12) & (hours < 14),
        (hours >= 14) & (hours < 16),
    ]
    choices = ["SESI 1", "SESI 2", "SESI 3"]
    df["sesi"] = np.select(conditions, choices, default="SESI 4")

    return df


# FINANCE DATA
def initialize_omset_data_session(brand_name, marketplace_list, store_list):
    """
    Menginisialisasi DataFrame di st.session_state untuk brand tertentu jika belum ada.

    Args:
        brand_name (str): Nama brand untuk kunci di session_state.
        marketplace__list (list): Daftar nama marketplace yang akan diisi ke DataFrame.
        store_list (list): Daftar nama toko yang akan diisi ke DataFrame.
    """
    session_key = f"df_{brand_name}_omset"

    if session_key not in st.session_state:
        # Buat DataFrame default dengan kolom yang dibutuhkan
        data = {
            "Tanggal": pd.Series(
                pd.Timestamp.today().date(), index=range(len(store_list))
            ),
            "Marketplace": marketplace_list,
            "Nama Toko": store_list,
            "Akrual Basis": [0.0] * len(store_list),
            "Cash Basis": [0.0] * len(store_list),
            "Bukti": [None] * len(store_list),
            "Akun Bank": [None] * len(store_list),
        }
        st.session_state[session_key] = pd.DataFrame(data)


def get_omset_column_config(brand):
    """
    Mengembalikan konfigurasi kolom yang konsisten untuk st.data_editor.
    """
    if brand == "Zhi Yang Yao":
        store_list = ZYY_STORE_LIST
    elif brand == "Enzhico":
        store_list = ENZ_STORE_LIST
    elif brand == "Erassgo":
        store_list = ERA_STORE_LIST

    return {
        "Tanggal": st.column_config.DateColumn(
            "Tanggal",
            min_value=pd.Timestamp(2023, 1, 1),
            format="YYYY-MM-DD",
            required=True,
        ),
        "Marketplace": st.column_config.SelectboxColumn(
            "Marketplace",
            options=MARKETPLACE_LIST,
            required=True,
        ),
        "Nama Toko": st.column_config.SelectboxColumn(
            "Nama Toko",
            options=store_list,
            required=True,
        ),
        "Akrual Basis": st.column_config.NumberColumn(
            "Akrual Basis (Rp)",
            min_value=0.0,
            format="accounting",
            required=True,
        ),
        "Cash Basis": st.column_config.NumberColumn(
            "Cash Basis (Rp)",
            min_value=0.0,
            format="accounting",
        ),
        "Bukti": st.column_config.TextColumn("Bukti"),
        "Akun Bank": st.column_config.TextColumn("Akun Bank"),
    }


def initialize_ads_data_session(brand_name, marketplace_list, store_list):
    """
    Menginisialisasi DataFrame di st.session_state untuk brand tertentu jika belum ada.

    Args:
        brand_name (str): Nama brand untuk kunci di session_state.
        marketplace__list (list): Daftar nama marketplace yang akan diisi ke DataFrame.
        store_list (list): Daftar nama toko yang akan diisi ke DataFrame.
    """
    session_key = f"df_{brand_name}_ads"

    if session_key not in st.session_state:
        # Buat DataFrame default dengan kolom yang dibutuhkan
        data = {
            "Tanggal": pd.Series(
                pd.Timestamp.today().date(), index=range(len(store_list))
            ),
            "Marketplace": marketplace_list,
            "Nama Toko": store_list,
            "Nominal Budget Ads": [0.0] * len(store_list),
            "Nominal Aktual Ads": None,
        }
        st.session_state[session_key] = pd.DataFrame(data)


def get_ads_column_config(brand):
    """
    Mengembalikan konfigurasi kolom yang konsisten untuk st.data_editor.
    """
    if brand == "Zhi Yang Yao":
        store_list = ZYY_STORE_LIST
    elif brand == "Enzhico":
        store_list = ENZ_STORE_LIST
    elif brand == "Erassgo":
        store_list = ERA_STORE_LIST

    return {
        "Tanggal": st.column_config.DateColumn(
            "Tanggal",
            min_value=pd.Timestamp(2023, 1, 1),
            format="YYYY-MM-DD",
            required=True,
        ),
        "Marketplace": st.column_config.SelectboxColumn(
            "Marketplace",
            options=MARKETPLACE_LIST,
            required=True,
        ),
        "Nama Toko": st.column_config.SelectboxColumn(
            "Nama Toko",
            options=store_list,
            required=True,
        ),
        "Nominal Budget Ads": st.column_config.NumberColumn(
            "Nominal Budget Ads (Rp)",
            min_value=0.0,
            format="accounting",
            required=True,
        ),
        "Nominal Aktual Ads": st.column_config.NumberColumn(
            "Nominal Aktual Ads (Rp)",
            min_value=0.0,
            format="accounting",
        ),
    }


def initialize_stock_data_session():
    """
    Menginisialisasi DataFrame di st.session_state untuk brand tertentu jika belum ada.

    """
    session_key = "df_stock"

    if session_key not in st.session_state:
        # Buat DataFrame default dengan kolom yang dibutuhkan
        data = {
            "Tanggal": pd.Series(pd.Timestamp.today().date(), index=range(5)),
            "Marketplace": None,
            "Nama Toko": None,
            "Nominal Budget Ads": [0.0] * 5,
            "Nominal Aktual Ads": None,
        }
        st.session_state[session_key] = pd.DataFrame(data)


def get_stock_column_config(brand):
    """
    Mengembalikan konfigurasi kolom yang konsisten untuk st.data_editor.
    """
    if brand == "Zhi Yang Yao":
        store_list = ZYY_STORE_LIST
    elif brand == "Enzhico":
        store_list = ENZ_STORE_LIST
    elif brand == "Erassgo":
        store_list = ERA_STORE_LIST

    return {
        "Tanggal": st.column_config.DateColumn(
            "Tanggal",
            min_value=pd.Timestamp(2023, 1, 1),
            format="YYYY-MM-DD",
            required=True,
        ),
        "Marketplace": st.column_config.SelectboxColumn(
            "Marketplace",
            options=MARKETPLACE_LIST,
            required=True,
        ),
        "Nama Toko": st.column_config.SelectboxColumn(
            "Nama Toko",
            options=store_list,
            required=True,
        ),
        "Nominal Budget Ads": st.column_config.NumberColumn(
            "Nominal Budget Ads (Rp)",
            min_value=0.0,
            format="accounting",
            required=True,
        ),
        "Nominal Aktual Ads": st.column_config.NumberColumn(
            "Nominal Aktual Ads (Rp)",
            min_value=0.0,
            format="accounting",
        ),
    }


def initialize_non_ads_data_session(branch_name):
    """
    Menginisialisasi DataFrame di st.session_state untuk brand tertentu jika belum ada.

    Args:
        brand_name (str): Nama brand untuk kunci di session_state.
        marketplace__list (list): Daftar nama marketplace yang akan diisi ke DataFrame.
        store_list (list): Daftar nama toko yang akan diisi ke DataFrame.
    """
    session_key = f"df_{branch_name}_non_ads"

    if session_key not in st.session_state:
        # Buat DataFrame default dengan kolom yang dibutuhkan
        data = {
            "Tanggal": pd.Series(pd.Timestamp.today().date(), index=range(5)),
            "Nominal Budget Non Ads": [0.0] * 5,
            "Nominal Aktual Non Ads": None,
            "Keterangan": None,
        }
        st.session_state[session_key] = pd.DataFrame(data)


def get_non_ads_column_config():
    """
    Mengembalikan konfigurasi kolom yang konsisten untuk st.data_editor.
    """
    return {
        "Tanggal": st.column_config.DateColumn(
            "Tanggal",
            min_value=pd.Timestamp(2023, 1, 1),
            format="YYYY-MM-DD",
            required=True,
        ),
        "Nominal Budget Non Ads": st.column_config.NumberColumn(
            "Nominal Budget Non Ads (Rp)",
            min_value=0.0,
            format="accounting",
            required=True,
        ),
        "Nominal Aktual Non Ads": st.column_config.NumberColumn(
            "Nominal Aktual Non Ads (Rp)",
            min_value=0.0,
            format="accounting",
        ),
        "Keterangan": st.column_config.TextColumn(
            "Keterangan",
        ),
    }


# ADVERTISER DATA
def initialize_marketplace_data_session(brand_name, marketplace_list, store_list):
    """
    Menginisialisasi DataFrame di st.session_state untuk brand tertentu jika belum ada.

    Args:
        brand_name (str): Nama brand untuk kunci di session_state.
        marketplace__list (list): Daftar nama marketplace yang akan diisi ke DataFrame.
        store_list (list): Daftar nama toko yang akan diisi ke DataFrame.
    """
    session_key = f"df_{brand_name}_marketplace"

    if session_key not in st.session_state:
        # Buat DataFrame default dengan kolom yang dibutuhkan
        data = {
            "Tanggal": pd.Series(
                pd.Timestamp.today().date(), index=range(len(store_list))
            ),
            "Marketplace": marketplace_list,
            "Nama Toko": store_list,
            "Spend": [0.0] * len(store_list),
            "Konversi": [0] * len(store_list),
            "Produk Terjual": [0] * len(store_list),
            "Gross Revenue": [0.0] * len(store_list),
            "CTR": [0.0] * len(store_list),
        }
        st.session_state[session_key] = pd.DataFrame(data)


def get_marketplace_column_config(brand):
    """
    Mengembalikan konfigurasi kolom yang konsisten untuk st.data_editor.
    """
    if brand == "Zhi Yang Yao":
        store_list = ZYY_STORE_LIST
    elif brand == "Enzhico":
        store_list = ENZ_STORE_LIST
    elif brand == "Enzhico":
        store_list = ENZ_STORE_LIST
    elif brand == "Erassgo":
        store_list = ERA_STORE_LIST

    return {
        "Tanggal": st.column_config.DateColumn(
            "Tanggal",
            min_value=pd.Timestamp(2023, 1, 1),
            format="YYYY-MM-DD",
            required=True,
        ),
        "Marketplace": st.column_config.SelectboxColumn(
            "Marketplace",
            options=MARKETPLACE_LIST,
            required=True,
        ),
        "Nama Toko": st.column_config.SelectboxColumn(
            "Nama Toko",
            options=store_list,
            required=True,
        ),
        "Spend": st.column_config.NumberColumn(
            "Spend (Rp)", min_value=None, format="accounting"
        ),
        "Konversi": st.column_config.NumberColumn(
            "Konversi", min_value=None, step=1, format="%d"
        ),
        "Produk Terjual": st.column_config.NumberColumn(
            "Produk Terjual",
            min_value=None,
            step=1,
            format="%d",
        ),
        "Gross Revenue": st.column_config.NumberColumn(
            "Gross Revenue (Rp)",
            min_value=None,
            format="accounting",
        ),
        "CTR": st.column_config.NumberColumn(
            "CTR",
            min_value=None,
            format="%.2f",
        ),
    }


def initialize_cpas_data_session(branch_name, brand, akun):
    """
    Menginisialisasi DataFrame di st.session_state untuk brand tertentu jika belum ada.

    Args:
        branch_name (str): Nama brand untuk kunci di session_state.
        marketplace__list (list): Daftar nama marketplace yang akan diisi ke DataFrame.
        akun (list): Daftar nama toko yang akan diisi ke DataFrame.
    """
    session_key = f"df_{branch_name}_cpas"

    if session_key not in st.session_state:
        # Buat DataFrame default dengan kolom yang dibutuhkan
        data = {
            "Tanggal": pd.Series(pd.Timestamp.today().date(), index=range(len(akun))),
            "Brand": brand,
            "Akun": akun,
            "Spend": [0.0] * len(akun),
            "Konversi": [0] * len(akun),
            "Gross Revenue": [0.0] * len(akun),
        }
        st.session_state[session_key] = pd.DataFrame(data)


def get_cpas_column_config():
    """
    Mengembalikan konfigurasi kolom yang konsisten untuk st.data_editor.
    """

    return {
        "Tanggal": st.column_config.DateColumn(
            "Tanggal",
            min_value=pd.Timestamp(2023, 1, 1),
            format="YYYY-MM-DD",
            required=True,
        ),
        "Brand": st.column_config.SelectboxColumn(
            "Brand",
            options=BRAND_LIST,
            required=True,
        ),
        "Akun": st.column_config.SelectboxColumn(
            "Akun",
            options=AKUN_LIST,
            required=True,
        ),
        "Spend": st.column_config.NumberColumn(
            "Spend (Rp)", min_value=None, format="accounting"
        ),
        "Konversi": st.column_config.NumberColumn(
            "Konversi", min_value=None, step=1, format="%d"
        ),
        "Gross Revenue": st.column_config.NumberColumn(
            "Gross Revenue (Rp)",
            min_value=None,
            format="accounting",
        ),
    }
