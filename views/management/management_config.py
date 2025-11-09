from datetime import datetime, timedelta

import pytz
import streamlit as st

from database.queries import dimmension_query as dim


def get_yesterday_in_jakarta():
    tz = pytz.timezone("Asia/Jakarta")
    return (datetime.now(tz) - timedelta(days=1)).date()


def get_now_in_jakarta():
    tz = pytz.timezone("Asia/Jakarta")
    return datetime.now(tz)


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
                "date_range_type": "yesterday",
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
            "pendapatan_kotor",
            "biaya_admin",
            "cash_basis",
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
                options=dim.get_nama_marketplace(),
                required=True,
            ),
            "nama_toko": st.column_config.SelectboxColumn(
                "Nama Toko",
                options=dim.get_nama_toko(),
                required=True,
            ),
            "pendapatan_kotor": st.column_config.NumberColumn(
                "Pendapatan Kotor (Rp)",
                min_value=0,
                format="accounting",
                required=True,
            ),
            "biaya_admin": st.column_config.NumberColumn(
                "Biaya Admin (Rp)",
                min_value=0,
                format="accounting",
                required=True,
            ),
            "cash_basis": st.column_config.NumberColumn(
                "Cash Basis (Rp)",
                min_value=0,
                format="accounting",
            ),
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
                "date_range_type": "yesterday",
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
                options=dim.get_nama_platform(),
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
                options=dim.get_nama_marketplace(),
                required=True,
            ),
            "nama_toko": st.column_config.SelectboxColumn(
                "Nama Toko",
                options=dim.get_nama_toko(),
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
                options=dim.get_nama_toko_cpas(),
                required=True,
            ),
            "akun": st.column_config.SelectboxColumn(
                "Akun",
                options=dim.get_nama_akun_cpas(),
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
                options=dim.get_nama_akun_topup_regular(),
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
                options=dim.get_nama_marketplace(),
                required=True,
            ),
            "nama_toko": st.column_config.SelectboxColumn(
                "Nama Toko",
                options=dim.get_nama_toko(),
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
                options=dim.get_nama_project(),
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
    "finance_transactions": {
        "display_name": "Cashflow",
        "table_name": "vw_finance_transactions",
        "primary_keys": [
            "transaction_id",
        ],
        "filters": [
            {
                "column_name": "transaction_date",
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
                "column_name": "bidang",
                "filter_type": "selectbox",
                "label": "Pilih Bidang",
                "options_source": {
                    "table": "dim_expense_categories",
                    "column": "bidang",
                },
            },
            {
                "column_name": "tipe_beban",
                "filter_type": "selectbox",
                "label": "Pilih Tipe Beban",
                "options_source": {
                    "table": "dim_expense_categories",
                    "column": "tipe_beban",
                },
            },
        ],
        "column_order": [
            "transaction_date",
            "project_name",
            "transaction_type",
            "amount",
            "bidang",
            "tipe_beban",
            "description",
        ],
        "column_config": {
            "transaction_date": st.column_config.DateColumn(
                "Tanggal",
                format="YYYY-MM-DD",
                required=True,
                default=get_now_in_jakarta(),
            ),
            "project_name": st.column_config.SelectboxColumn(
                "Nama Project",
                options=dim.get_nama_project(),
                required=True,
            ),
            "transaction_type": st.column_config.SelectboxColumn(
                "IN / OUT",
                options=["IN", "OUT"],
                required=True,
                default="OUT",
            ),
            "amount": st.column_config.NumberColumn(
                "Nominal (Rp)",
                min_value=0,
                format="accounting",
                required=True,
            ),
            "bidang": st.column_config.SelectboxColumn(
                "Bidang",
                options=dim.get_bidang(),
                required=True,
            ),
            "tipe_beban": st.column_config.SelectboxColumn(
                "Tipe Beban",
                options=dim.get_tipe_beban(),
                required=True,
            ),
            "description": st.column_config.TextColumn(
                "Keterangan",
            ),
        },
    },
    # --- TAMBAHKAN KONFIGURASI TABEL LAIN DI SINI ---
}


ADVERTISER_TABLE_CONFIGS = {
    "advertiser_marketplace": {
        "display_name": "Advertiser Marketplace",
        "source_view": "vw_advertiser_mp",
        "target_table": "advertiser_marketplace",
        "primary_keys": [
            "tanggal",
            "nama_toko",
        ],
        "filters": [
            {
                "column_name": "tanggal",
                "filter_type": "date_range",
                "label": "Pilih Rentang Tanggal",
                "date_range_type": "yesterday",
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
                    "needs_project_context": True,
                },
            },
        ],
        "column_order": [
            "tanggal",
            "marketplace",
            "nama_toko",
            "spend",
            "konversi",
            "produk_terjual",
            "gross_revenue",
            "ctr",
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
                options=dim.get_nama_marketplace(),
                required=True,
            ),
            "nama_toko": st.column_config.SelectboxColumn(
                "Nama Toko",
                options=[],
                required=True,
            ),
            "spend": st.column_config.NumberColumn(
                "Spend (Rp)",
                min_value=0,
                format="accounting",
                required=True,
            ),
            "konversi": st.column_config.NumberColumn(
                "Konversi", min_value=0, format="%d"
            ),
            "produk_terjual": st.column_config.NumberColumn(
                "Produk Terjual", min_value=0, format="%d"
            ),
            "gross_revenue": st.column_config.NumberColumn(
                "Gross Revenue (Rp)",
                min_value=0,
                format="accounting",
            ),
            "ctr": st.column_config.NumberColumn(
                "CTR",
                max_value=10.0,
                min_value=0.0,
            ),
        },
    },
    "advertiser_cpas": {
        "display_name": "Advertiser CPAS",
        "source_view": "vw_advertiser_cpas",
        "target_table": "advertiser_cpas",
        "primary_keys": [
            "tanggal",
            "akun",
        ],
        "filters": [
            {
                "column_name": "tanggal",
                "filter_type": "date_range",
                "label": "Pilih Rentang Tanggal",
                "date_range_type": "yesterday",
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
                    "needs_project_context": True,
                },
            },
            {
                "column_name": "akun",
                "filter_type": "selectbox",
                "label": "Pilih Akun CPAS",
                "options_source": {
                    "table": "dim_cpas_accounts",
                    "column": "nama_akun_cpas",
                    "needs_project_context": True,
                },
            },
        ],
        "column_order": [
            "tanggal",
            "nama_toko",
            "akun",
            "spend",
            "konversi",
            "gross_revenue",
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
                options=[],
                required=True,
            ),
            "akun": st.column_config.SelectboxColumn(
                "Akun",
                options=[],
                required=True,
            ),
            "spend": st.column_config.NumberColumn(
                "Spend (Rp)",
                min_value=0,
                format="accounting",
                required=True,
            ),
            "konversi": st.column_config.NumberColumn(
                "Konversi", min_value=0, format="%d"
            ),
            "gross_revenue": st.column_config.NumberColumn(
                "Gross Revenue (Rp)",
                min_value=0,
                format="accounting",
            ),
        },
    },
}


REGULAR_TABLE_CONFIGS = {
    "order_flag_reg": {
        "display_name": "Order Flag Regular",
        "table_name": "order_flag_reg",
        "primary_keys": ["tanggal", "order_id"],
        "filters": [
            {
                "column_name": "tanggal",
                "filter_type": "date_range",
                "label": "Pilih Rentang Tanggal",
                "date_range_type": "today",
            },
            {
                "column_name": "kategori",
                "filter_type": "selectbox",
                "label": "Pilih Kategori",
                "options_source": {
                    "table": "order_flag_reg",
                    "column": "kategori",
                },
            },
        ],
        "column_order": [
            "tanggal",
            "order_id",
            "kategori",
            "nominal",
            "keterangan",
        ],
        "column_config": {
            "tanggal": st.column_config.DateColumn(
                "Tanggal",
                format="YYYY-MM-DD",
                required=True,
                default=get_now_in_jakarta(),
            ),
            "order_id": st.column_config.TextColumn("Order ID"),
            "kategori": st.column_config.SelectboxColumn(
                "Kategori",
                options=["RETURN", "CANCEL"],
                required=True,
            ),
            "nominal": st.column_config.NumberColumn(
                "Nominal Adjustment (Rp)",
                min_value=0,
                format="accounting",
                required=True,
            ),
            "keterangan": st.column_config.TextColumn("Keterangan"),
        },
    },
}
