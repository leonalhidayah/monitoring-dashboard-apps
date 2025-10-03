import io
import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

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
    "TT juwaraherbal",
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

KDK_STORE_LIST = [
    "SP kudaku",
    "SP kudaku store",
    "SP kudaku official store",
    "SP kudaku id",
    "SP kudaku indonesia",
    "TT kudaku milk",
    "LZ kudaku",
]

TOKO_BANDUNG = [
    "SP zhi yang yao official",
    "SP erassgo bandung",
    "SP juwara herbal official store",
    "TT juwara herbal",
]
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


def get_store_list_by_project(project_name):
    if project_name == "Zhi Yang Yao":
        return ZYY_STORE_LIST
    elif project_name == "Enzhico":
        return ENZ_STORE_LIST
    elif project_name == "Erassgo":
        return ERA_STORE_LIST
    elif project_name == "Kudaku":
        return KDK_STORE_LIST
    elif project_name == "Juwara Herbal":
        return JH_STORE_LIST
    else:
        return None


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
def initialize_omset_data_session(project_name, marketplace_list, store_list):
    """
    Menginisialisasi DataFrame di st.session_state untuk brand tertentu jika belum ada.

    Args:
        project_name (str): Nama project untuk kunci di session_state.
        marketplace__list (list): Daftar nama marketplace yang akan diisi ke DataFrame.
        store_list (list): Daftar nama toko yang akan diisi ke DataFrame.
    """
    session_key = f"df_{project_name}_omset"

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


def get_omset_column_config(project_name):
    """
    Mengembalikan konfigurasi kolom yang konsisten untuk st.data_editor.
    """
    store_list = get_store_list_by_project(project_name)

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


def initialize_ads_data_session(project_name, marketplace_list, store_list):
    """
    Menginisialisasi DataFrame di st.session_state untuk project tertentu jika belum ada.

    Args:
        project_name (str): Nama project untuk kunci di session_state.
        marketplace__list (list): Daftar nama marketplace yang akan diisi ke DataFrame.
        store_list (list): Daftar nama toko yang akan diisi ke DataFrame.
    """
    session_key = f"df_{project_name}_ads"

    if session_key not in st.session_state:
        # Buat DataFrame default dengan kolom yang dibutuhkan
        data = {
            "Tanggal": pd.Series(
                pd.Timestamp.today().date(), index=range(len(store_list))
            ),
            "Marketplace": marketplace_list,
            "Nama Toko": store_list,
            # "Nominal Budget Ads": [0.0] * len(store_list),
            "Nominal Aktual Ads": None,
        }
        st.session_state[session_key] = pd.DataFrame(data)


def get_ads_column_config(project_name):
    """
    Mengembalikan konfigurasi kolom yang konsisten untuk st.data_editor.
    """
    store_list = get_store_list_by_project(project_name)

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
        # "Nominal Budget Ads": st.column_config.NumberColumn(
        #     "Nominal Budget Ads (Rp)",
        #     min_value=0.0,
        #     format="accounting",
        #     required=True,
        # ),
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


def get_stock_column_config(project_name):
    """
    Mengembalikan konfigurasi kolom yang konsisten untuk st.data_editor.
    """
    store_list = get_store_list_by_project(project_name)

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
        project_name (str): Nama brand untuk kunci di session_state.
        marketplace__list (list): Daftar nama marketplace yang akan diisi ke DataFrame.
        store_list (list): Daftar nama toko yang akan diisi ke DataFrame.
    """
    session_key = f"df_{branch_name}_non_ads"

    if session_key not in st.session_state:
        # Buat DataFrame default dengan kolom yang dibutuhkan
        data = {
            "Tanggal": pd.Series(pd.Timestamp.today().date(), index=range(5)),
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
def initialize_marketplace_data_session(project_name, marketplace_list, store_list):
    """
    Menginisialisasi DataFrame di st.session_state untuk brand tertentu jika belum ada.

    Args:
        project_name (str): Nama brand untuk kunci di session_state.
        marketplace__list (list): Daftar nama marketplace yang akan diisi ke DataFrame.
        store_list (list): Daftar nama toko yang akan diisi ke DataFrame.
    """
    session_key = f"df_{project_name}_marketplace"

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


def get_marketplace_column_config(project_name):
    """
    Mengembalikan konfigurasi kolom yang konsisten untuk st.data_editor.
    """
    store_list = get_store_list_by_project(project_name)

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


# DASHBOARD ADMIN
def generate_excel_bytes(df, group_cols, value_col, aggfunc="sum"):
    """
    Membuat report Excel dari hasil groupby dan mengembalikannya sebagai
    objek bytes untuk di-download.
    """
    if not group_cols:
        raise ValueError("Parameter 'group_cols' tidak boleh kosong.")

    brand_col = group_cols[0]
    grouped = (
        df.groupby(group_cols, as_index=False)[value_col]
        .agg(aggfunc)
        .sort_values(by=brand_col)
    )
    grand_total = grouped[value_col].sum()

    wb = Workbook()
    ws = wb.active
    ws.title = "Report"

    header = group_cols + [value_col.capitalize()]
    ws.append(header)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    current_row_idx = 2
    for brand_name, brand_df in grouped.groupby(brand_col):
        start_merge_row = current_row_idx
        for _, data_row in brand_df.iterrows():
            ws.append(list(data_row))
            current_row_idx += 1

        subtotal_value = brand_df[value_col].sum()
        subtotal_row_data = (
            [f"Subtotal {brand_name}"] + [""] * (len(group_cols) - 1) + [subtotal_value]
        )
        ws.append(subtotal_row_data)
        for cell in ws[current_row_idx]:
            cell.font = Font(bold=True)
        current_row_idx += 1

        end_merge_row = current_row_idx - 2
        if start_merge_row < end_merge_row:
            ws.merge_cells(
                start_row=start_merge_row,
                start_column=1,
                end_row=end_merge_row,
                end_column=1,
            )
            ws.cell(start_merge_row, 1).alignment = Alignment(
                horizontal="left", vertical="center"
            )

    grand_total_row_data = (
        ["Grand Total"] + [""] * (len(group_cols) - 1) + [grand_total]
    )
    ws.append(grand_total_row_data)
    for cell in ws[ws.max_row]:
        cell.font = Font(bold=True, size=12)

    for col_idx, column_cells in enumerate(ws.columns, 1):
        max_length = 0
        column_letter = get_column_letter(col_idx)
        for cell in column_cells:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[column_letter].width = adjusted_width

    # --- PERUBAHAN UTAMA ADA DI SINI ---
    # Simpan workbook ke dalam buffer memori
    buffer = io.BytesIO()
    wb.save(buffer)
    # Pindahkan "cursor" buffer ke awal
    buffer.seek(0)
    return buffer


def expand_sku(sku: str):
    """
    Expand SKU bundling sesuai aturan:
    - Jika tidak ada "_", return [sku]
    - Jika ada "_", pecah jadi beberapa produk
    """
    if "_" not in sku:
        return [sku]

    parts = sku.split("_")
    prefix = parts[0].split("-")[0]  # ambil brand prefix (3 huruf pertama sebelum '-')

    expanded = [parts[0]]  # produk pertama utuh
    for p in parts[1:]:
        expanded.append(prefix + "-" + p)

    return expanded


def create_visual_report(report_df, original_df):
    """
    Membuat laporan Excel yang lebih mudah dibaca secara visual
    dengan warna, border, subtotal, dan grand total.
    """
    if report_df.empty:
        wb = Workbook()
        ws = wb.active
        ws.title = "Laporan Marketplace"
        ws["A1"] = "Tidak ada data untuk ditampilkan."
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    # Urutkan data
    df_sorted = report_df.sort_values(
        by=["nama_marketplace", "nama_toko", "sku"]
    ).reset_index(drop=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "Laporan Marketplace"

    # --- Styles ---
    bold_font = Font(bold=True)
    italic_bold_font = Font(bold=True, italic=True)
    center_align = Alignment(horizontal="center", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")

    header_fill = PatternFill(
        start_color="BDD7EE", end_color="BDD7EE", fill_type="solid"
    )
    subtotal_fill = PatternFill(
        start_color="FFF2CC", end_color="FFF2CC", fill_type="solid"
    )
    marketplace_fill = PatternFill(
        start_color="FCE4D6", end_color="FCE4D6", fill_type="solid"
    )
    total_fill = PatternFill(
        start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"
    )

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    # --- Header ---
    headers = [
        "Marketplace",
        "Nama Toko",
        "SKU",
        "Jumlah PCS",
        "Total Resi Unik Marketplace",
    ]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = bold_font
        cell.alignment = center_align
        cell.fill = header_fill
        cell.border = thin_border

    # --- Variabel Pelacak ---
    marketplace_start_row, toko_start_row = 2, 2
    marketplace_pcs_subtotal, toko_pcs_subtotal = 0, 0
    prev_marketplace, prev_toko = None, None

    # --- Iterasi Data ---
    for idx, row in df_sorted.iterrows():
        current_row_num = ws.max_row + 1
        if prev_marketplace is None:
            prev_marketplace = row["nama_marketplace"]
            prev_toko = row["nama_toko"]

        # Marketplace berubah
        if row["nama_marketplace"] != prev_marketplace:
            # Subtotal toko terakhir
            ws.append(["", f"Subtotal {prev_toko}", "", toko_pcs_subtotal, ""])
            for cell in ws[ws.max_row]:
                cell.font = italic_bold_font
                cell.fill = subtotal_fill
                cell.border = thin_border

            # Subtotal marketplace
            ws.append(
                [
                    "",
                    f"SUBTOTAL {prev_marketplace}",
                    "",
                    marketplace_pcs_subtotal,
                    df_sorted.loc[idx - 1, "jumlah_resi_unik"],
                ]
            )
            for cell in ws[ws.max_row]:
                cell.font = bold_font
                cell.fill = marketplace_fill
                cell.border = thin_border

            ws.append([])  # baris kosong

            # Reset
            marketplace_pcs_subtotal, toko_pcs_subtotal = 0, 0
            prev_marketplace, prev_toko = row["nama_marketplace"], row["nama_toko"]

        # Toko berubah
        elif row["nama_toko"] != prev_toko:
            ws.append(["", f"Subtotal {prev_toko}", "", toko_pcs_subtotal, ""])
            for cell in ws[ws.max_row]:
                cell.font = italic_bold_font
                cell.fill = subtotal_fill
                cell.border = thin_border

            ws.append([])  # baris kosong antar toko

            toko_pcs_subtotal = 0
            prev_toko = row["nama_toko"]

        # Tulis data SKU
        ws.append(
            [
                row["nama_marketplace"],
                row["nama_toko"],
                row["sku"],
                row["jumlah_pcs"],
                "",
            ]
        )
        for cell in ws[ws.max_row]:
            cell.border = thin_border
        ws[ws.max_row][3].alignment = right_align

        marketplace_pcs_subtotal += row["jumlah_pcs"]
        toko_pcs_subtotal += row["jumlah_pcs"]

    # --- Akhiri dengan subtotal terakhir ---
    ws.append(["", f"Subtotal {prev_toko}", "", toko_pcs_subtotal, ""])
    for cell in ws[ws.max_row]:
        cell.font = italic_bold_font
        cell.fill = subtotal_fill
        cell.border = thin_border

    ws.append(
        [
            "",
            f"SUBTOTAL {prev_marketplace}",
            "",
            marketplace_pcs_subtotal,
            df_sorted.iloc[-1]["jumlah_resi_unik"],
        ]
    )
    for cell in ws[ws.max_row]:
        cell.font = bold_font
        cell.fill = marketplace_fill
        cell.border = thin_border

    ws.append([])

    # --- Grand Total ---
    grand_total_pcs = df_sorted["jumlah_pcs"].sum()
    grand_total_resi_unik = original_df["no_resi"].nunique()
    ws.append(["GRAND TOTAL", "", "", grand_total_pcs, grand_total_resi_unik])
    for cell in ws[ws.max_row]:
        cell.font = bold_font
        cell.fill = total_fill
        cell.border = thin_border

    ws.merge_cells(
        start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=2
    )

    # --- Auto Width Columns ---
    for col in ws.columns:
        max_length = 0
        column_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[column_letter].width = max_length + 2

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()
