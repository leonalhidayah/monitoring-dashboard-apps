from datetime import datetime, timedelta

import pytz
import streamlit as st

from database.db_manager import (
    get_dim_cpas_accounts,
    get_dim_marketplaces,
    get_dim_platforms,
    get_dim_projects,
    get_dim_stores,
    get_dim_topup_account_regular,
)


def get_yesterday_in_jakarta():
    tz = pytz.timezone("Asia/Jakarta")
    return (datetime.now(tz) - timedelta(days=1)).date()


def get_now_in_jakarta():
    tz = pytz.timezone("Asia/Jakarta")
    return datetime.now(tz)


MARKETPLACE_LIST = set(get_dim_marketplaces()["nama_marketplace"].tolist())
STORE_LIST = set(get_dim_stores()["nama_toko"].tolist())
PLARFORM_REGULAR = set(get_dim_platforms()["nama_platform"].tolist())
TOPUP_AKUN_REGULAR = set(get_dim_topup_account_regular()["nama_akun"].tolist())
AKUN_CPAS_LIST = set(get_dim_cpas_accounts()["nama_akun_cpas"].tolist())
STORE_WITH_CPAS_LIST = set(get_dim_cpas_accounts()["nama_toko"].tolist())
PROJECT_LIST = set(get_dim_projects()["project_name"].tolist())


# =============================================================================
# KONFIGURASI PUSAT UNTUK SEMUA TABEL DATA MANAGEMENT
# =============================================================================
# Setiap entri di sini akan secara otomatis membuat halaman editor datanya sendiri.
#
# Struktur Konfigurasi:
#   "nama_tabel_unik": {
#       "display_name": Judul yang akan tampil di UI.
#       "table_name": Nama tabel sebenarnya di database.
#       "id_column": Nama kolom Primary Key (untuk proses UPDATE/DELETE).
#       "filters": List yang berisi definisi filter untuk tabel ini.
#           - "column_name": Kolom di database yang akan difilter.
#           - "filter_type": Jenis widget filter ('date_range' atau 'selectbox').
#           - "label": Label yang tampil di atas widget.
#           - "options": (Hanya untuk selectbox) List pilihan yang tersedia.
#       "column_order": Urutan kolom yang akan ditampilkan di data editor.
#       "column_config": Konfigurasi detail untuk setiap kolom di data editor.
#   }
# =============================================================================

FINANCE_TABLE_CONFIGS = {
    "finance_omset": {
        "display_name": "Omset Marketplace",
        "source_view": "vw_finance_omset_with_project",
        "target_table": "finance_omset",
        "primary_keys": [
            "tanggal",
            "nama_toko",
        ],
        "filters": [
            {
                "column_name": "tanggal",
                "filter_type": "date_range",
                "label": "Pilih Rentang Tanggal",
            },
            {
                "column_name": "project_name",
                "filter_type": "selectbox",
                "label": "Pilih Project",
                "options_source": {
                    "table": "dim_projects",
                    "column": "project_name",
                },
            },
            {
                "column_name": "marketplace",
                "filter_type": "selectbox",
                "label": "Pilih Marketplace",
                "options_source": {
                    "table": "dim_marketplaces",
                    "column": "nama_marketplace",
                },
            },
            {
                "column_name": "nama_toko",
                "filter_type": "selectbox",
                "label": "Pilih Toko",
                "options_source": {
                    "table": "dim_stores",
                    "column": "nama_toko",
                },
            },
        ],
        "column_order": [
            "tanggal",
            "marketplace",
            "nama_toko",
            "akrual_basis",
            "cash_basis",
            "bukti",
            "akun_bank",
        ],
        "column_config": {
            "tanggal": st.column_config.DateColumn(
                "Tanggal",
                format="YYYY-MM-DD",
                required=True,
                default=get_yesterday_in_jakarta(),
            ),
            "marketplace": st.column_config.SelectboxColumn(
                "Marketplace",
                options=MARKETPLACE_LIST,
                required=True,
            ),
            "nama_toko": st.column_config.SelectboxColumn(
                "Nama Toko",
                options=STORE_LIST,
                required=True,
            ),
            "akrual_basis": st.column_config.NumberColumn(
                "Akrual Basis (Rp)",
                min_value=0,
                format="accounting",
                required=True,
            ),
            "cash_basis": st.column_config.NumberColumn(
                "Cash Basis (Rp)",
                min_value=0,
                format="accounting",
            ),
            "bukti": st.column_config.TextColumn("Bukti (Link)"),
            "akun_bank": st.column_config.TextColumn("Akun Bank"),
        },
    },
    "finance_omset_reg": {
        "display_name": "Omset Regular",
        "table_name": "finance_omset_reg",
        "primary_keys": [
            "tanggal",
            "platform",
        ],
        "filters": [
            {
                "column_name": "tanggal",
                "filter_type": "date_range",
                "label": "Pilih Rentang Tanggal",
            },
            {
                "column_name": "platform",
                "filter_type": "selectbox",
                "label": "Pilih Plarform",
                "options_source": {
                    "table": "dim_platforms",
                    "column": "nama_platform",
                },
            },
        ],
        "column_order": [
            "tanggal",
            "platform",
            "akrual_basis",
            "cash_basis",
            "bukti",
            "akun_bank",
        ],
        "column_config": {
            "tanggal": st.column_config.DateColumn(
                "Tanggal",
                format="YYYY-MM-DD",
                required=True,
                default=get_yesterday_in_jakarta(),
            ),
            "platform": st.column_config.SelectboxColumn(
                "Platform",
                options=PLARFORM_REGULAR,
                required=True,
            ),
            "akrual_basis": st.column_config.NumberColumn(
                "Akrual Basis (Rp)",
                min_value=0,
                format="accounting",
                required=True,
            ),
            "cash_basis": st.column_config.NumberColumn(
                "Cash Basis (Rp)",
                min_value=0,
                format="accounting",
            ),
            "bukti": st.column_config.TextColumn("Bukti (Link)"),
            "akun_bank": st.column_config.TextColumn("Akun Bank"),
        },
    },
    "finance_budget_ads": {
        "display_name": "Budget Ads Marketplace",
        "source_view": "vw_finance_budget_ads_with_project",
        "target_table": "finance_budget_ads",
        "primary_keys": [
            "tanggal",
            "nama_toko",
        ],
        "filters": [
            {
                "column_name": "tanggal",
                "filter_type": "date_range",
                "label": "Pilih Rentang Tanggal",
            },
            {
                "column_name": "project_name",
                "filter_type": "selectbox",
                "label": "Pilih Project",
                "options_source": {
                    "table": "dim_projects",
                    "column": "project_name",
                },
            },
            {
                "column_name": "marketplace",
                "filter_type": "selectbox",
                "label": "Pilih Marketplace",
                "options_source": {
                    "table": "dim_marketplaces",
                    "column": "nama_marketplace",
                },
            },
            {
                "column_name": "nama_toko",
                "filter_type": "selectbox",
                "label": "Pilih Toko",
                "options_source": {
                    "table": "dim_stores",
                    "column": "nama_toko",
                },
            },
        ],
        "column_order": [
            "tanggal",
            "marketplace",
            "nama_toko",
            "nominal_aktual_ads",
        ],
        "column_config": {
            "tanggal": st.column_config.DateColumn(
                "Tanggal",
                format="YYYY-MM-DD",
                required=True,
                default=get_yesterday_in_jakarta(),
            ),
            "marketplace": st.column_config.SelectboxColumn(
                "Marketplace",
                options=MARKETPLACE_LIST,
                required=True,
            ),
            "nama_toko": st.column_config.SelectboxColumn(
                "Nama Toko",
                options=STORE_LIST,
                required=True,
            ),
            "nominal_aktual_ads": st.column_config.NumberColumn(
                "Nominal Aktual Ads (Rp)",
                min_value=0,
                format="accounting",
                required=True,
            ),
        },
    },
    "finance_budget_ads_cpas": {
        "display_name": "Budget Ads CPAS",
        "source_view": "vw_finance_budget_ads_cpas_with_project",
        "target_table": "finance_budget_ads_cpas",
        "primary_keys": [
            "tanggal",
            "akun",
        ],
        "filters": [
            {
                "column_name": "tanggal",
                "filter_type": "date_range",
                "label": "Pilih Rentang Tanggal",
            },
            {
                "column_name": "project_name",
                "filter_type": "selectbox",
                "label": "Pilih Project",
                "options_source": {
                    "table": "dim_projects",
                    "column": "project_name",
                },
            },
            {
                "column_name": "nama_toko",
                "filter_type": "selectbox",
                "label": "Pilih Toko",
                "options_source": {
                    "table": "dim_stores",
                    "column": "nama_toko",
                },
            },
            {
                "column_name": "akun",
                "filter_type": "selectbox",
                "label": "Pilih Akun CPAS",
                "options_source": {
                    "table": "dim_cpas_accounts",
                    "column": "nama_akun_cpas",
                },
            },
        ],
        "column_order": [
            "tanggal",
            "nama_toko",
            "akun",
            "nominal_aktual_ads",
        ],
        "column_config": {
            "tanggal": st.column_config.DateColumn(
                "Tanggal",
                format="YYYY-MM-DD",
                required=True,
                default=get_yesterday_in_jakarta(),
            ),
            "nama_toko": st.column_config.SelectboxColumn(
                "Nama Toko",
                options=STORE_WITH_CPAS_LIST,
                required=True,
            ),
            "akun": st.column_config.SelectboxColumn(
                "Akun",
                options=AKUN_CPAS_LIST,
                required=True,
            ),
            "nominal_aktual_ads": st.column_config.NumberColumn(
                "Nominal Aktual Ads (Rp)",
                min_value=0,
                format="accounting",
                required=True,
            ),
        },
    },
    "finance_budget_ads_reg": {
        "display_name": "Budget Ads Regular",
        "table_name": "finance_budget_ads_reg",
        "primary_keys": [
            "tanggal",
            "akun",
        ],
        "filters": [
            {
                "column_name": "tanggal",
                "filter_type": "date_range",
                "label": "Pilih Rentang Tanggal",
            },
            {
                "column_name": "akun",
                "filter_type": "selectbox",
                "label": "Pilih Akun Top Up",
                "options_source": {
                    "table": "dim_topup_account_regular",
                    "column": "nama_akun",
                },
            },
        ],
        "column_order": [
            "tanggal",
            "akun",
            "nominal_aktual_ads",
        ],
        "column_config": {
            "tanggal": st.column_config.DateColumn(
                "Tanggal",
                format="YYYY-MM-DD",
                required=True,
                default=get_yesterday_in_jakarta(),
            ),
            "akun": st.column_config.SelectboxColumn(
                "Akun",
                options=TOPUP_AKUN_REGULAR,
                required=True,
            ),
            "nominal_aktual_ads": st.column_config.NumberColumn(
                "Nominal Aktual Ads (Rp)",
                min_value=0,
                format="accounting",
                required=True,
            ),
        },
    },
    "finance_budget_non_ads_fo": {
        "display_name": "Budget Non Ads FO",
        "source_view": "vw_finance_budget_fo",
        "target_table": "finance_budget_non_ads_fo",
        "primary_keys": [
            "tanggal",
            "nama_toko",
        ],
        "filters": [
            {
                "column_name": "tanggal",
                "filter_type": "date_range",
                "label": "Pilih Rentang Tanggal",
            },
            {
                "column_name": "project_name",
                "filter_type": "selectbox",
                "label": "Pilih Project",
                "options_source": {
                    "table": "dim_projects",
                    "column": "project_name",
                },
            },
            {
                "column_name": "marketplace",
                "filter_type": "selectbox",
                "label": "Pilih Marketplace",
                "options_source": {
                    "table": "dim_marketplaces",
                    "column": "nama_marketplace",
                },
            },
            {
                "column_name": "nama_toko",
                "filter_type": "selectbox",
                "label": "Pilih Toko",
                "options_source": {
                    "table": "dim_stores",
                    "column": "nama_toko",
                },
            },
        ],
        "column_order": [
            "tanggal",
            "marketplace",
            "nama_toko",
            "nominal_aktual_non_ads",
        ],
        "column_config": {
            "tanggal": st.column_config.DateColumn(
                "Tanggal",
                format="YYYY-MM-DD",
                required=True,
                default=get_yesterday_in_jakarta(),
            ),
            "marketplace": st.column_config.SelectboxColumn(
                "Marketplace",
                options=MARKETPLACE_LIST,
                required=True,
            ),
            "nama_toko": st.column_config.SelectboxColumn(
                "Nama Toko",
                options=STORE_LIST,
                required=True,
            ),
            "nominal_aktual_non_ads": st.column_config.NumberColumn(
                "Nominal Aktual Non Ads (Rp)",
                min_value=0,
                format="accounting",
                required=True,
            ),
        },
    },
    "finance_budget_non_ads_lainnya": {
        "display_name": "Budget Non Ads Lainnya",
        "table_name": "finance_budget_non_ads_lainnya",
        "primary_keys": [
            "tanggal",
            "nama_project",
            "keterangan",
        ],
        "filters": [
            {
                "column_name": "tanggal",
                "filter_type": "date_range",
                "label": "Pilih Rentang Tanggal",
            },
            {
                "column_name": "nama_project",
                "filter_type": "selectbox",
                "label": "Pilih Project",
                "options_source": {
                    "table": "dim_projects",
                    "column": "project_name",
                },
            },
        ],
        "column_order": [
            "tanggal",
            "nama_project",
            "keterangan",
            "nominal_aktual_non_ads",
        ],
        "column_config": {
            "tanggal": st.column_config.DateColumn(
                "Tanggal",
                format="YYYY-MM-DD",
                required=True,
                default=get_yesterday_in_jakarta(),
            ),
            "nama_project": st.column_config.SelectboxColumn(
                "Nama Project",
                options=PROJECT_LIST,
                required=True,
            ),
            "keterangan": st.column_config.TextColumn(
                "Keterangan",
            ),
            "nominal_aktual_non_ads": st.column_config.NumberColumn(
                "Nominal Aktual Non Ads (Rp)",
                min_value=0,
                format="accounting",
                required=True,
            ),
        },
    },
    # --- TAMBAHKAN KONFIGURASI TABEL LAIN DI SINI ---
}
