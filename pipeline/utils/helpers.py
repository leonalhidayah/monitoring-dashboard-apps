import re
import warnings
from typing import List

import numpy as np
import pandas as pd

_MONTH_MAPPING = {
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
_MONTH_PATTERN = re.compile(
    rf"\b({'|'.join(_MONTH_MAPPING.keys())})\b", flags=re.IGNORECASE
)


def clean_datetime_columns(df: pd.DataFrame, datetime_cols: List[str]) -> pd.DataFrame:
    def _normalize_months(series: pd.Series) -> pd.Series:
        if series.isna().all():
            return pd.to_datetime(series, errors="coerce")

        cleaned = series.astype(str).str.strip()
        replaced = cleaned.str.replace(
            _MONTH_PATTERN,
            lambda m: _MONTH_MAPPING.get(m.group(1).capitalize(), m.group(1)),
            regex=True,
        )

        parsed = pd.to_datetime(replaced, errors="coerce", dayfirst=True)
        mask_na = parsed.isna()
        if mask_na.any():
            parsed.loc[mask_na] = pd.to_datetime(
                replaced[mask_na],
                errors="coerce",
                dayfirst=True,  # tetap gunakan dayfirst agar tidak memicu warning
            )
        return parsed

    for col in datetime_cols:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            if col in df.columns:
                df[col] = _normalize_months(df[col])
    return df


def clean_currency_columns(
    df: pd.DataFrame, currency_columns: list[str]
) -> pd.DataFrame:
    """
    Membersihkan kolom currency campuran dari berbagai format
    (ribuan dengan koma/titik dan desimal dengan koma).
    """

    def _detect_and_fix(val):
        if pd.isna(val):
            return np.nan
        s = str(val).strip()

        # Pola ribuan dengan koma (6,000 atau 3,000.50)
        if re.match(r"^\d{1,3}(,\d{3})+(\.\d+)?$", s):
            s = s.replace(",", "")
            return float(s)

        # Pola desimal koma (9856,5)
        if re.match(r"^\d+,\d+$", s):
            s = s.replace(",", ".")
            return float(s)

        # Pola ribuan Eropa (12.345,67)
        if re.match(r"^\d{1,3}(\.\d{3})+(,\d+)?$", s):
            s = s.replace(".", "").replace(",", ".")
            return float(s)

        # Pola angka biasa (5000 atau 1234.56)
        if re.match(r"^\d+(\.\d+)?$", s):
            return float(s)

        return np.nan

    for col in currency_columns:
        if col in df.columns:
            df[col] = df[col].apply(_detect_and_fix)

    return df


def fix_misconverted_currency(series, threshold=100):
    s = pd.to_numeric(series, errors="coerce")
    mask = (s > 0) & (s < threshold)
    s[mask] = s[mask] * 1000
    return s


# def clean_object_columns(df: pd.DataFrame, object_columns: list[str]) -> pd.DataFrame:
#     """
#     Membersihkan kolom bertipe teks (object/string) agar konsisten dan bebas karakter aneh.

#     Best Practice Data Engineering:
#     - Aman untuk data campuran (NaN, angka, tipe lain)
#     - Hindari inplace operation
#     - Gunakan regex yang efisien
#     """
#     # --- Validasi awal ---
#     if df.empty or not object_columns:
#         return df

#     df = df.copy()
#     cleaned_cols = []

#     for col in object_columns:
#         if col not in df.columns:
#             continue

#         # Pastikan kolom string agar tidak error saat apply string method
#         df[col] = df[col].astype(str)

#         # Normalisasi whitespace dan karakter non-ASCII umum
#         df[col] = (
#             df[col]
#             .str.replace(r"\xa0", " ", regex=True)  # Non-breaking space
#             .str.replace(r"[\r\n\t]+", " ", regex=True)  # Newline/tab
#             .str.replace(r"\s+", " ", regex=True)  # Multi-space → single space
#             .str.strip()  # Leading/trailing spaces
#         )

#         # Ganti string 'nan' hasil dari cast
#         df[col] = df[col].replace("nan", np.nan)
#         cleaned_cols.append(col)

#     return df


def clean_object_columns(
    df: pd.DataFrame, object_columns: list[str], case: str = None
) -> pd.DataFrame:
    """
    Membersihkan kolom teks, menangani NaN secara robust, dan mengonversi case.

    Args:
        df: DataFrame yang akan dimodifikasi.
        object_columns: Daftar nama kolom yang akan dibersihkan.
        case: Opsional. Bisa 'lower' atau 'upper' untuk konversi case.
    """
    # --- Validasi awal ---
    if df.empty or not object_columns:
        return df

    df = df.copy()

    for col in object_columns:
        if col not in df.columns:
            continue

        series = df[col].fillna("")
        series = series.astype(str)

        # 3. Normalisasi whitespace
        series = (
            series.str.replace(r"\xa0", " ", regex=True)  # Non-breaking space
            .str.replace(r"[\r\n\t]+", " ", regex=True)  # Newline/tab
            .str.replace(r"\s+", " ", regex=True)  # Multi-space -> single space
            .str.strip()  # Leading/trailing spaces
        )

        # 4. Terapkan konversi 'case'
        if case == "lower":
            series = series.str.lower()
        elif case == "upper":
            series = series.str.upper()

        series = series.replace("", np.nan)

        df[col] = series

    return df


def standardize_mapping_column(df, column_name, mapping_dict, inplace=False):
    """
    Menstandarkan nilai pada kolom DataFrame berdasarkan mapping yang diberikan.

    Params
    -------
    df : pd.DataFrame
        DataFrame target
    column_name : str
        Nama kolom yang ingin distandardisasi
    mapping_dict : dict
        Kamus mapping {nilai_asli: nilai_standard}
    inplace : bool, default=False
        Jika True, menimpa kolom aslinya di df

    Returns
    -------
    pd.Series atau pd.DataFrame:
        - Jika inplace=False → return Series hasil standarisasi
        - Jika inplace=True → return df (kolom sudah ditimpa)
    """
    if column_name not in df.columns:
        raise KeyError(f"Kolom '{column_name}' tidak ditemukan di DataFrame")

    standardized_series = df[column_name].apply(
        lambda x: mapping_dict.get(str(x).strip(), x) if pd.notna(x) else x
    )

    if inplace:
        df[column_name] = standardized_series
        return df
    else:
        return standardized_series


def load_dataframe(file):
    """Memuat file (Excel atau CSV) ke DataFrame pandas."""
    if file.name.endswith(".xlsx"):
        return pd.read_excel(file, dtype=str)
    elif file.name.endswith(".csv"):
        return pd.read_csv(file, dtype=str)
    else:
        raise ValueError("Format file tidak didukung. Harap upload .xlsx atau .csv")


def fillna_currency_with_rules(
    df,
    fill_col="Total Pesanan",
    reference_col="SKU",
    jumlah_col="Jumlah",
):
    """
    Mengisi nilai kosong di kolom total pesanan berdasarkan aturan bisnis:
    - Rata-rata (Total Pesanan / Jumlah) per SKU digunakan untuk imputasi.
    - Jika SKU tidak punya referensi valid (semua NaN), fallback ke median global Total Pesanan.

    Args:
        df (pd.DataFrame): Data input (misal data raw marketplace).
        fill_col (str): Nama kolom total pesanan.
        reference_col (str): Nama kolom SKU.
        jumlah_col (str): Nama kolom jumlah item.
        log (bool): Jika True, tampilkan informasi di log.

    Returns:
        pd.DataFrame: DataFrame dengan kolom total pesanan yang sudah diisi.
    """

    df = df.copy()

    if "Jumlah" in df.columns:
        df[jumlah_col] = pd.to_numeric(df[jumlah_col], errors="coerce")

    valid_mask = df[fill_col].notna() & df[jumlah_col].notna()
    df_valid = df.loc[valid_mask, [reference_col, fill_col, jumlah_col]].copy()
    df_valid["avg_per_item"] = df_valid[fill_col] / df_valid[jumlah_col]

    df_avg = (
        df_valid.groupby(reference_col, as_index=False)["avg_per_item"]
        .mean()
        .rename(columns={"avg_per_item": "avg_per_item_sku"})
    )

    df_merged = df.merge(df_avg, on=reference_col, how="left")

    global_median = df_valid[fill_col].median() / df_valid[jumlah_col].median()

    na_mask = df_merged[fill_col].isna()

    df_merged.loc[na_mask, fill_col] = (
        df_merged.loc[na_mask, "avg_per_item_sku"].fillna(global_median)
        * df_merged.loc[na_mask, jumlah_col]
    )

    df_merged.drop(columns=["avg_per_item_sku"], inplace=True)

    return df_merged


def fillna_by_other_column(df, fill_col, reference_col):
    df[fill_col] = df[fill_col].fillna(df[reference_col])
    return df
