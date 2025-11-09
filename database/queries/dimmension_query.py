from database.db_connection import get_engine
from database.db_generic_crud import fetch_distinct_options

engine = get_engine()


def get_nama_marketplace():
    return fetch_distinct_options(
        engine, table_name="dim_marketplaces", column_name="nama_marketplace"
    )


def get_bidang():
    return fetch_distinct_options(
        engine, table_name="dim_expense_categories", column_name="bidang"
    )


def get_tipe_beban():
    return fetch_distinct_options(
        engine, table_name="dim_expense_categories", column_name="tipe_beban"
    )


def get_nama_project():
    """Mengambil semua data dari tabel dim_projects."""
    return fetch_distinct_options(
        engine, table_name="dim_projects", column_name="project_name"
    )


def get_nama_produk_regular():
    """Mengambil semua data dari tabel dim_reg_products."""
    return fetch_distinct_options(
        engine, table_name="dim_reg_products", column_name="nama_produk"
    )


def get_nama_platform():
    """Mengambil semua data dari tabel dim_platforms."""
    return fetch_distinct_options(
        engine, table_name="dim_platforms", column_name="nama_platform"
    )


def get_nama_akun_topup_regular():
    """Mengambil semua data dari tabel dim_topup_account_regular."""
    return fetch_distinct_options(
        engine, table_name="dim_topup_account_regular", column_name="nama_akun"
    )


def get_nama_akun_cpas():
    """Mengambil semua data dari tabel vw_cpas_account_with_store_name."""
    return fetch_distinct_options(
        engine,
        table_name="vw_cpas_account_with_store_name",
        column_name="nama_akun_cpas",
    )


def get_nama_toko_cpas():
    """Mengambil semua data dari tabel vw_cpas_account_with_store_name."""
    return fetch_distinct_options(
        engine,
        table_name="vw_cpas_account_with_store_name",
        column_name="nama_toko",
    )


def get_nama_brand():
    """Mengambil semua data dari tabel dim_brands."""
    return fetch_distinct_options(
        engine, table_name="dim_brands", column_name="nama_brand"
    )


def get_nama_toko():
    """Mengambil semua data dari tabel dim_stores."""
    return fetch_distinct_options(
        engine, table_name="dim_stores", column_name="nama_toko"
    )


# def get_customers():
#     """Mengambil semua data dari tabel customers."""
#     return fetch_distinct_options(engine, table_name="customers")


# def get_products():
#     """Mengambil semua data dari tabel products."""
#     return fetch_distinct_options(engine, table_name="products")


# def get_dim_shipping_services():
#     """Mengambil semua data dari tabel dim_shipping_services."""
#     return fetch_distinct_options(engine, table_name="dim_shipping_services")
