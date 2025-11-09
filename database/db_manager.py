import logging
import warnings
from datetime import date
from typing import List

import numpy as np
import pandas as pd
import psycopg2
import streamlit as st
from psycopg2 import extras
from psycopg2.extensions import AsIs, register_adapter

from database.db_connection import get_connection

# Konfigurasi dasar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


warnings.filterwarnings("ignore")


# Adapter untuk tipe data NumPy
def adapt_numpy_types(numpy_type):
    return AsIs(numpy_type)


# Mendaftarkan adapter untuk semua tipe numerik umum
register_adapter(np.int64, adapt_numpy_types)
register_adapter(np.float64, adapt_numpy_types)


def get_table_columns(table_name):
    """
    Mengambil daftar nama kolom dari sebuah tabel di database PostgreSQL.

    Args:
        table_name (str): Nama tabel yang ingin diperiksa.

    Returns:
        list: Daftar nama kolom dalam bentuk string.
    """
    conn = None
    try:
        conn = get_connection()  # Menggunakan fungsi koneksi Anda yang sudah ada
        cursor = conn.cursor()

        # Query ini mengambil nama kolom dari katalog informasi standar database
        query = """
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s;
        """

        cursor.execute(query, (table_name,))

        # Mengubah hasil query (list of tuples) menjadi list of strings
        columns = [row[0] for row in cursor.fetchall()]

        return columns
    except Exception as e:
        print(f"Error saat mengambil kolom untuk tabel {table_name}: {e}")
        return []  # Mengembalikan list kosong jika terjadi error
    finally:
        if conn:
            conn.close()


# --- DIm TABLE
def get_table_data(table_name: str, order_by_column: str = None) -> pd.DataFrame:
    """
    Mengambil semua data dari tabel yang ditentukan secara generik.

    Args:
        table_name (str): Nama tabel yang akan diambil datanya.
        order_by_column (str, optional): Nama kolom untuk mengurutkan data. Default None.

    Returns:
        pd.DataFrame: DataFrame berisi data tabel, atau DataFrame kosong jika error.
    """
    conn = None
    try:
        conn = get_connection()

        # Query dasar
        query = f"SELECT * FROM {table_name}"

        # Tambahkan ORDER BY jika kolom disediakan
        if order_by_column:
            query += f" ORDER BY {order_by_column} ASC"

        df = pd.read_sql(query, conn)
        logging.info(f"Berhasil mengambil {len(df)} records dari tabel {table_name}.")
        return df

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(
            f"Error saat mengambil data dari {table_name}: {error}", exc_info=True
        )
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()
            logging.info(f"Koneksi database untuk mengambil data {table_name} ditutup.")


def get_dim_marketplaces():
    """Mengambil semua data dari tabel dim_marketplaces."""
    return get_table_data(
        table_name="dim_marketplaces", order_by_column="marketplace_id"
    )


def get_dim_reg_products():
    """Mengambil semua data dari tabel dim_reg_products."""
    return get_table_data(table_name="dim_reg_products")


def get_dim_platforms():
    """Mengambil semua data dari tabel dim_platforms."""
    return get_table_data(table_name="dim_platforms", order_by_column="platform_id")


def get_dim_topup_account_regular():
    """Mengambil semua data dari tabel dim_topup_account_regular."""
    return get_table_data(
        table_name="dim_topup_account_regular", order_by_column="account_id"
    )


def get_dim_cpas_accounts():
    """Mengambil semua data dari tabel vw_cpas_account_with_store_name."""
    return get_table_data(
        table_name="vw_cpas_account_with_store_name", order_by_column="cpas_id"
    )


def get_dim_brands():
    """Mengambil semua data dari tabel dim_brands."""
    return get_table_data(table_name="dim_brands", order_by_column="nama_brand")


def get_dim_stores():
    """Mengambil semua data dari tabel dim_stores."""
    return get_table_data(table_name="dim_stores", order_by_column="store_id")


def get_customers():
    """Mengambil semua data dari tabel customers."""
    return get_table_data(table_name="customers", order_by_column="customer_id")


def get_products():
    """Mengambil semua data dari tabel products."""
    return get_table_data(table_name="products", order_by_column="product_id")


def get_dim_shipping_services():
    """Mengambil semua data dari tabel dim_shipping_services."""
    return get_table_data(
        table_name="dim_shipping_services", order_by_column="service_id"
    )


def get_finance_budget_plan_by_project(
    project_name: str, start_date: date, end_date: date
) -> pd.DataFrame:
    """
    Mengambil data mentah finance_budget_plan dari database berdasarkan
    project_name dan rentang tanggal.
    """
    conn = None
    # Query ini mengambil semua kolom yang dibutuhkan untuk transformasi
    query = """
        SELECT 
            fbp.*, 
            dp.project_name 
        FROM 
            finance_budget_plan fbp
        INNER JOIN 
            dim_projects dp ON dp.project_id = fbp.project_id
        WHERE
            dp.project_name = %(project_name)s
            -- PERBAIKAN DI SINI:
            -- Kita membandingkan tanggal 1 dari database dengan tanggal 1 dari filter.
            AND TO_DATE(fbp.bulan || ' ' || fbp.tahun, 'FMMonth YYYY') 
                BETWEEN DATE_TRUNC('month', %(start_date)s::date) 
                    AND DATE_TRUNC('month', %(end_date)s::date)
        ORDER BY
            fbp.tahun, 
            TO_DATE(fbp.bulan, 'FMMonth');
    """
    try:
        conn = get_connection()
        if not conn:
            return pd.DataFrame()

        params = {
            "project_name": project_name,
            "start_date": start_date,
            "end_date": end_date,
        }
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except (Exception, psycopg2.Error) as e:
        logging.error(f"Gagal mengambil data budget plan: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


def get_dim_payment_methods():
    """Mengambil semua data dari tabel dim_payment_methods."""
    return get_table_data(table_name="dim_payment_methods")


def get_shipments():
    """Mengambil semua data dari tabel shipments."""
    return get_table_data(table_name="shipments")


def get_orders():
    """Mengambil semua data dari tabel orders."""
    return get_table_data(table_name="orders")


def get_order_items():
    """Mengambil semua data dari tabel order_items."""
    return get_table_data(table_name="order_items")


def get_vw_admin_shipments():
    """Mengambil semua data dari tabel vw_admin_shipments."""
    return get_table_data(table_name="vw_admin_shipments")


def get_vw_shipments_delivery():
    """Mengambil semua data dari tabel vw_shipments_delivery."""
    return get_table_data(table_name="vw_shipments_delivery")


def get_vw_admin_shipments_delivery():
    """Mengambil semua data dari tabel vw_admin_shipments_delivery."""
    return get_table_data(table_name="vw_admin_shipments_delivery")


def get_target_ads_ratio(project_id: int, year: int, quarter: int) -> float | None:
    """
    Mengambil target rasio ads/omset dari budget plan untuk kuartal tertentu.

    Args:
        project_id (int): ID project.
        year (int): Tahun budget.
        quarter (int): Kuartal budget (1-4).

    Returns:
        float | None: Nilai target rasio dalam persen, atau None jika tidak ditemukan.
    """
    query = """
    SELECT 
        target_rasio_persen 
    FROM 
        finance_budget_plan
    WHERE 
        project_id = %(project_id)s
        AND parameter_name = 'Biaya Marketing (Ads)'
        AND tahun = %(year)s
        AND kuartal = %(quarter)s
    LIMIT 1; -- Ambil satu baris saja karena nilainya sama untuk satu kuartal
    """
    conn = None
    try:
        conn = get_connection()
        # Menggunakan read_sql untuk kemudahan, lalu ambil nilainya
        df = pd.read_sql(
            query,
            conn,
            params={"project_id": project_id, "year": year, "quarter": quarter},
        )
        if not df.empty:
            return df["target_rasio_persen"].iloc[0]
        else:
            logging.warning(
                f"Target rasio tidak ditemukan untuk project {project_id}, Q{quarter} {year}."
            )
            return None  # Kembalikan None jika tidak ada target
    except Exception as e:
        logging.error(f"Gagal mengambil target rasio: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_finance_omset():
    return get_table_data(table_name="finance_omset")


def get_finance_budget_ads():
    return get_table_data(table_name="finance_budget_ads")


def get_finance_budget_non_ads():
    return get_table_data(table_name="finance_budget_non_ads")


# def get_vw_budget_ads_monitoring():
#     """Mengambil semua data dari tabel vw_budget_ads_monitoring."""
#     return get_table_data(table_name="vw_budget_ads_monitoring")


def get_vw_ads_performance_summary(
    project_name: str, start_date: date, end_date: date
) -> pd.DataFrame:
    """
    Mengambil data dari view vw_ads_performance_summary berdasarkan filter.

    Args:
        project_name (str): Nama project yang akan difilter.
        start_date (date): Tanggal mulai periode.
        end_date (date): Tanggal akhir periode.

    Returns:
        pd.DataFrame: DataFrame berisi detail performa.
                      Mengembalikan DataFrame kosong jika tidak ada data atau terjadi error.
    """
    query = """
    SELECT
        *
    FROM
        vw_ads_performance_summary
    WHERE
        project_name = %(project_name)s
        AND tanggal BETWEEN %(start_date)s AND %(end_date)s
    ORDER BY
        tanggal DESC, nama_toko ASC;
    """
    conn = None
    try:
        conn = get_connection()
        df = pd.read_sql(
            query,
            conn,
            params={
                "project_name": project_name,
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        logging.info(f"Successfully fetched {len(df)} rows for project {project_name}.")
        return df
    except Exception as e:
        logging.error(f"Failed to fetch data from vw_ads_performance_summary: {e}")
        return pd.DataFrame()  # Kembalikan dataframe kosong jika error
    finally:
        if conn:
            conn.close()


def get_payments():
    """Mengambil semua data dari tabel payments."""
    return get_table_data(table_name="payments")


def get_dim_projects():
    """Mengambil semua data dari tabel dim_projects."""
    return get_table_data(table_name="dim_projects")


def get_dim_expense_categories():
    """Mengambil semua data dari tabel dim_expense_categories ."""
    return get_table_data(table_name="dim_expense_categories ")


def get_map_project_stores():
    """Mengambil semua data dari tabel map_project_stores ."""
    return get_table_data(table_name="map_project_stores ")


def get_total_sales_target(project_id: int, start_date: str, end_date: str):
    """
    Menghitung total TARGET OMSET untuk sebuah project dalam rentang tanggal.
    """
    conn = None
    query = """
        SELECT
            SUM(target_bulanan_rp) AS total_target
        FROM
            finance_budget_plan
        WHERE
            project_id = %(project_id)s
            AND parameter_name = 'Target Omset'
            AND to_date(tahun || '-' || bulan, 'YYYY-Month') BETWEEN %(start_date)s AND %(end_date)s;
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            query,
            {"project_id": project_id, "start_date": start_date, "end_date": end_date},
        )
        result = cur.fetchone()
        return result[0] if result and result[0] is not None else 0
    except psycopg2.Error as e:
        logging.error(f"Gagal mengambil total target omset: {e}")
        return 0
    finally:
        if conn:
            conn.close()


def get_vw_monitoring_cashflow(
    project_name: str, start_date: date, end_date: date
) -> pd.DataFrame:
    """
    Mengambil detail laporan monitoring dari view dan mengembalikannya sebagai Pandas DataFrame.
    Fungsi ini ideal untuk digunakan langsung di UI seperti Streamlit.
    """
    conn = None
    query = """
        SELECT 
            project_name AS "Project",
            report_year AS "Tahun",
            report_month_name AS "Bulan",
            parameter_name AS "Parameter Budget",
            maksimal_budget AS "Maksimal Budget (Plan)",
            total_realisasi AS "Total Realisasi (Actual)",
            sisa_budget AS "Sisa Budget",
            persentase_terpakai AS "Persentase Terpakai",
            status AS "Status"
        FROM 
            vw_monitoring_cashflow
        WHERE
            project_name = %(project_name)s
            AND TO_DATE(report_month_name || ' ' || report_year, 'FMMonth YYYY') 
                BETWEEN DATE_TRUNC('month', %(start_date)s::date) 
                    AND DATE_TRUNC('month', %(end_date)s::date)
        ORDER BY
            report_year, 
            TO_DATE(report_month_name, 'FMMonth');
    """
    try:
        conn = get_connection()
        # Jika koneksi gagal, kembalikan DataFrame kosong
        if not conn:
            return pd.DataFrame()

        params = {
            "project_name": project_name,
            "start_date": start_date,
            "end_date": end_date,
        }

        # pd.read_sql_query adalah cara paling efisien untuk mendapatkan DataFrame
        df = pd.read_sql_query(query, conn, params=params)
        return df

    except (Exception, psycopg2.Error) as e:
        logging.error(f"Gagal mengambil data monitoring report: {e}")
        # Kembalikan DataFrame kosong jika terjadi error saat query
        return pd.DataFrame()

    finally:
        if conn:
            conn.close()


def get_marketing_ads_ratio(project_name, start_date, end_date):
    query = """
        SELECT 
            fbp.project_id,
            dp.project_name,
            fbp.tahun,
            fbp.kuartal,
            fbp.bulan,
            fbp.parameter_name,
            fbp.target_rasio_persen
        FROM 
            finance_budget_plan fbp
        JOIN 
            dim_projects dp ON fbp.project_id = dp.project_id
        WHERE 
            dp.project_name = %(project_name)s
            AND fbp.parameter_name = 'Biaya Marketing (Ads)'
            -- PERUBAIKAN: Logika perbandingan diubah untuk membandingkan bulan, bukan hari.
            AND TO_DATE(fbp.bulan || ' ' || fbp.tahun, 'Month YYYY') 
                BETWEEN DATE_TRUNC('month', %(start_date)s::date) 
                    AND DATE_TRUNC('month', %(end_date)s::date)
    """
    conn = get_connection()
    df = pd.read_sql(
        query,
        conn,
        params={
            "project_name": project_name,
            "start_date": start_date,
            "end_date": end_date,
        },
    )
    conn.close()
    return df


def insert_new_stores(df_new_stores: pd.DataFrame):
    """
    Memasukkan data toko baru dari DataFrame ke tabel dim_stores.
    """
    if df_new_stores.empty:
        return {
            "status": "success",
            "count": 0,
            "message": "Tidak ada toko baru untuk dimasukkan.",
        }

    conn = None
    query = """
        INSERT INTO dim_stores (nama_toko, marketplace_id)
        VALUES %s
        ON CONFLICT (nama_toko) DO NOTHING;
    """

    try:
        conn = get_connection()
        cur = conn.cursor()

        data_tuples = [
            tuple(row)
            for row in df_new_stores[["nama_toko", "marketplace_id"]].to_numpy()
        ]

        extras.execute_values(cur, query, data_tuples)

        inserted_rows = cur.rowcount
        conn.commit()

        logging.info(
            f"Berhasil memasukkan/memperbarui {inserted_rows} toko di dim_stores."
        )
        return {"status": "success", "count": inserted_rows}

    except psycopg2.Error as e:
        logging.error(f"Gagal memasukkan data ke dim_stores: {e}")
        if conn:
            conn.rollback()
        return {"status": "error", "message": str(e)}

    finally:
        if conn:
            conn.close()


def insert_project_store_mapping(df_mapping: pd.DataFrame):
    """
    Memasukkan data pemetaan project ke toko dari DataFrame.
    """
    if df_mapping.empty:
        return {
            "status": "success",
            "count": 0,
            "message": "Tidak ada data mapping untuk dimasukkan.",
        }

    conn = None
    query = """
        INSERT INTO map_project_stores (project_id, store_id)
        VALUES %s
        ON CONFLICT (project_id, store_id) DO NOTHING;
    """

    try:
        conn = get_connection()
        cur = conn.cursor()

        data_tuples = [
            tuple(map(int, row))
            for row in df_mapping[["project_id", "store_id"]].to_numpy()
        ]

        extras.execute_values(cur, query, data_tuples)

        inserted_rows = cur.rowcount
        conn.commit()

        logging.info(
            f"Berhasil memasukkan {inserted_rows} baris pemetaan project-toko."
        )
        return {"status": "success", "count": inserted_rows}

    except psycopg2.Error as e:
        logging.error(f"Gagal memasukkan data mapping: {e}")
        if conn:
            conn.rollback()
        return {"status": "error", "message": str(e)}

    finally:
        if conn:
            conn.close()


def get_financial_summary(project_id: int, start_date: str, end_date: str):
    """
    Query yang diperbarui untuk mencocokkan budget plan 'parameter_name'
    dengan 'bidang' dari kategori pengeluaran.
    """
    conn = None
    query = """
    WITH 
    date_series AS (
        SELECT generate_series(%(start_date)s::date, %(end_date)s::date, '1 day'::interval) AS tanggal
    ),
    budget_with_categories AS (
        SELECT 
            fbp.parameter_name,
            dec.id AS category_id, -- <-- Kunci: Mengambil category_id
            dec.tipe_beban,      -- <-- Mengambil tipe beban spesifik
            fbp.target_bulanan_rp,
            to_date(fbp.tahun || '-' || fbp.bulan || '-01', 'YYYY-Month-DD') AS month_start
        FROM finance_budget_plan fbp
        -- Join berdasarkan parameter_name = bidang
        JOIN dim_expense_categories dec ON fbp.parameter_name = dec.bidang
        WHERE fbp.project_id = %(project_id)s AND fbp.parameter_name != 'Target Omset'
    ),
    -- 2. Scaffold sekarang berisi baris untuk setiap 'tipe_beban' yang spesifik
    scaffold AS (
        SELECT
            d.tanggal,
            bwc.parameter_name, -- Ini adalah 'bidang' (misal: HPP)
            bwc.tipe_beban,     -- Ini adalah kategori spesifik (misal: Beban Gudang)
            bwc.category_id,    -- ID untuk join
            -- Alokasi budget harian dibagi rata ke semua tipe_beban dalam satu bidang
            (bwc.target_bulanan_rp / EXTRACT(DAY FROM (bwc.month_start + interval '1 month - 1 day'))::integer) 
                / COUNT(*) OVER(PARTITION BY bwc.month_start, bwc.parameter_name) AS budget_harian_rp
        FROM date_series d
        CROSS JOIN budget_with_categories bwc
        WHERE date_trunc('month', d.tanggal) = bwc.month_start
    ),
    daily_sales AS (
        SELECT
            fo.tanggal,
            SUM(fo.akrual_basis) AS total_omset_akrual
        FROM finance_omset fo
        JOIN dim_stores ds ON fo.nama_toko = ds.nama_toko
        JOIN map_project_stores mps ON ds.store_id = mps.store_id
        WHERE mps.project_id = %(project_id)s
        GROUP BY fo.tanggal
    ),
    -- 3. Agregasi cash out berdasarkan category_id
    daily_cash_out AS (
        SELECT
            ft.transaction_date,
            ft.category_id,
            SUM(ft.amount) AS total_cash_out
        FROM finance_transactions ft
        WHERE ft.project_id = %(project_id)s AND ft.transaction_type = 'OUT'
        GROUP BY ft.transaction_date, ft.category_id
    )
    -- FINAL SELECT: Menggabungkan semuanya berdasarkan category_id
    SELECT
        sc.tanggal,
        sc.tipe_beban AS parameter_name, -- Tampilkan nama yang lebih detail (tipe_beban)
        0 AS target_rasio_persen, -- Kolom ini mungkin perlu penyesuaian logika
        sc.budget_harian_rp,
        COALESCE(ds.total_omset_akrual, 0) AS omset_akrual,
        COALESCE(dco.total_cash_out, 0) AS total_cash_out
    FROM scaffold sc
    LEFT JOIN daily_sales ds ON sc.tanggal = ds.tanggal
    -- Join final menggunakan category_id
    LEFT JOIN daily_cash_out dco ON sc.tanggal = dco.transaction_date AND sc.category_id = dco.category_id
    WHERE 
        sc.tanggal BETWEEN %(start_date)s AND %(end_date)s
    ORDER BY sc.tanggal, sc.parameter_name;
    """
    try:
        conn = get_connection()
        df = pd.read_sql(
            query,
            conn,
            params={
                "project_id": project_id,
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        logging.info(
            f"Berhasil mengambil {len(df)} baris data summary keuangan (dengan scaffold)."
        )
        return df
    except psycopg2.Error as e:
        logging.error(f"Gagal mengambil financial summary (dengan scaffold): {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


def insert_budget_plan(df_long: pd.DataFrame):
    """
    Memasukkan atau memperbarui data budget plan dari DataFrame.

    Menggunakan klausa ON CONFLICT (project_id, tahun, bulan, parameter_name) DO UPDATE
    untuk menangani entri budget yang sudah ada, memungkinkan revisi.

    Args:
        df_long (pd.DataFrame): DataFrame dalam format panjang (long) yang berisi data budget.

    Returns:
        dict: Berisi status dan pesan hasil operasi.
    """
    if df_long.empty:
        return {"status": "success", "message": "Tidak ada data untuk dimasukkan."}

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Langkah 1: Dapatkan pemetaan project_name ke project_id dari database
        cur.execute("SELECT project_name, project_id FROM dim_projects;")
        project_map = {name: pid for name, pid in cur.fetchall()}

        # Langkah 2: Ganti kolom 'Project' dengan 'project_id' di DataFrame
        df_long["project_id"] = df_long["Project"].map(project_map)

        # Validasi jika ada project yang tidak terpetakan
        if df_long["project_id"].isnull().any():
            unmapped_projects = df_long[df_long["project_id"].isnull()][
                "Project"
            ].unique()
            return {
                "status": "error",
                "message": f"Project tidak ditemukan: {', '.join(unmapped_projects)}",
            }

        # Langkah 3: Siapkan data untuk bulk insert/update
        # Ubah nama kolom DataFrame agar sesuai dengan nama kolom di tabel DB
        df_to_insert = df_long.rename(
            columns={
                "Tahun": "tahun",
                "Kuartal": "kuartal",
                "Bulan": "bulan",
                "Parameter": "parameter_name",
                "Target Rasio": "target_rasio_persen",
                "Target Bulanan": "target_bulanan_rp",
            }
        )

        # Pilih kolom yang relevan dan siapkan tuples
        cols = [
            "project_id",
            "tahun",
            "kuartal",
            "bulan",
            "parameter_name",
            "target_rasio_persen",
            "target_bulanan_rp",
        ]
        data_tuples = [tuple(x) for x in df_to_insert[cols].to_numpy()]

        # Langkah 4: Buat query dengan ON CONFLICT DO UPDATE
        query = f"""
            INSERT INTO finance_budget_plan ({", ".join(cols)})
            VALUES %s
            ON CONFLICT (project_id, tahun, bulan, parameter_name) DO UPDATE SET
                target_rasio_persen = EXCLUDED.target_rasio_persen,
                target_bulanan_rp = EXCLUDED.target_bulanan_rp;
        """

        extras.execute_values(cur, query, data_tuples)
        conn.commit()

        logging.info(
            f"Berhasil memasukkan/memperbarui {len(data_tuples)} baris budget plan."
        )
        return {"status": "success"}

    except psycopg2.Error as e:
        logging.error(f"Gagal memasukkan budget plan: {e}")
        if conn:
            conn.rollback()
        return {"status": "error", "message": str(e)}

    finally:
        if conn:
            conn.close()


def insert_cash_out(
    trans_date,
    project_name,
    bidang,
    tipe_beban,
    nominal,
    deskripsi,
    user_input="system",
):
    """
    Menyimpan satu transaksi pengeluaran (cash out) ke database.

    Fungsi ini melakukan lookup untuk mendapatkan project_id and category_id
    sebelum memasukkan data ke tabel finance_transactions.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT project_id FROM dim_projects WHERE project_name = %s;",
            (project_name,),
        )
        project_result = cur.fetchone()
        if not project_result:
            return {
                "status": "error",
                "message": f"Project '{project_name}' tidak ditemukan.",
            }
        project_id = project_result[0]

        cur.execute(
            "SELECT id FROM dim_expense_categories WHERE bidang = %s AND tipe_beban = %s;",
            (bidang, tipe_beban),
        )
        category_result = cur.fetchone()
        if not category_result:
            return {
                "status": "error",
                "message": f"Kategori '{bidang} - {tipe_beban}' tidak ditemukan.",
            }
        category_id = category_result[0]

        query = """
            INSERT INTO finance_transactions (
                transaction_date, project_id, transaction_type, amount, 
                category_id, description, user_input
            ) VALUES (%s, %s, 'OUT', %s, %s, %s, %s);
        """
        cur.execute(
            query,
            (
                trans_date,
                project_id,
                nominal,
                category_id,
                deskripsi,
                user_input,
            ),
        )

        conn.commit()
        logging.info(f"Berhasil menyimpan transaksi cash out sebesar {nominal}.")
        return {"status": "success"}

    except psycopg2.Error as e:
        logging.error(f"Gagal menyimpan transaksi cash out: {e}")
        if conn:
            conn.rollback()
        return {"status": "error", "message": str(e)}

    finally:
        if conn:
            conn.close()


# --- ADVERTISER DATA ---
# --- marketplace
def insert_advertiser_marketplace_data(data: pd.DataFrame):
    """
    Menyimpan atau memperbarui data dari DataFrame ke database.
    Menggunakan transaksi untuk memastikan operasi berjalan atomic.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        data = data.dropna(
            subset=["Spend", "Konversi", "Produk Terjual", "Gross Revenue", "CTR"],
            how="all",
        )

        query = """
            INSERT INTO advertiser_marketplace (
                tanggal, marketplace, nama_toko, spend, konversi,
                produk_terjual, gross_revenue, ctr
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (tanggal, nama_toko) DO UPDATE SET
                marketplace = EXCLUDED.marketplace,
                spend = EXCLUDED.spend,
                konversi = EXCLUDED.konversi,
                produk_terjual = EXCLUDED.produk_terjual,
                gross_revenue = EXCLUDED.gross_revenue,
                ctr = EXCLUDED.ctr;
        """

        records = [
            tuple(row)
            for row in data[
                [
                    "Tanggal",
                    "Marketplace",
                    "Nama Toko",
                    "Spend",
                    "Konversi",
                    "Produk Terjual",
                    "Gross Revenue",
                    "CTR",
                ]
            ].to_numpy()
        ]

        cur.executemany(query, records)
        conn.commit()
        logging.info(
            f"Berhasil menyimpan/memperbarui {len(records)} records advertiser_marketplace ke database."
        )
        return {
            "status": "success",
            "message": f"{len(records)} records advertiser_marketplace berhasil disimpan atau diperbarui.",
        }

    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()
        logging.error(f"Error saat menyimpan data: {error}", exc_info=True)
        return {"status": "error", "message": str(error)}
    finally:
        if conn:
            cur.close()
            conn.close()
            logging.info("Koneksi database ditutup.")


def get_advertiser_marketplace_data():
    """
    Mengambil semua data dari tabel advertiser_marketplace.
    """
    conn = None
    try:
        conn = get_connection()
        query = """
            SELECT
                *
            FROM
                advertiser_marketplace
            ORDER BY
                tanggal DESC, nama_toko ASC;
        """
        df = pd.read_sql(query, conn)
        logging.info(f"Berhasil mengambil {len(df)} records dari database.")
        return df
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"Error saat mengambil data: {error}", exc_info=True)
        return pd.DataFrame()  # Mengembalikan DataFrame kosong jika ada error
    finally:
        if conn:
            conn.close()
            logging.info("Koneksi database ditutup.")


# --- cpas
def insert_advertiser_cpas_data(data: pd.DataFrame):
    """
    Memasukkan atau memperbarui data CPAS dari DataFrame ke dalam tabel advertiser_cpas.
    Menggunakan ON CONFLICT DO UPDATE untuk menangani entri ganda secara efisien.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        data = data.dropna(
            subset=["Spend", "Konversi", "Gross Revenue"],
            how="all",
        )

        query = """
            INSERT INTO advertiser_cpas (tanggal, nama_toko, akun, spend, konversi, gross_revenue)
            VALUES (
                %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (tanggal, akun) DO UPDATE
            SET
                nama_toko = EXCLUDED.nama_toko,
                spend = EXCLUDED.spend,
                konversi = EXCLUDED.konversi,
                gross_revenue = EXCLUDED.gross_revenue;
        """
        records = [
            tuple(row)
            for row in data[
                [
                    "Tanggal",
                    "Nama Toko",
                    "Akun",
                    "Spend",
                    "Konversi",
                    "Gross Revenue",
                ]
            ].to_numpy()
        ]

        cur.executemany(query, records)
        conn.commit()

        logging.info(
            f"Berhasil menyimpan/memperbarui {len(records)} records advertiser_cpas ke database."
        )
        return {
            "status": "success",
            "message": f"{len(records)} records advertiser_cpas berhasil disimpan atau diperbarui.",
        }

    except psycopg2.Error as e:
        logging.error(f"Gagal memasukkan data ke database: {e}")
        conn.rollback()  # Batalkan transaksi jika terjadi kesalahan
        return False

    finally:
        if conn:
            conn.close()


def get_advertiser_cpas_data():
    """
    engambil semua data dari tabel advertiser_cpas.
    """
    conn = None
    try:
        conn = get_connection()
        query = """
            SELECT
                *
            FROM
                advertiser_cpas
            ORDER BY
                tanggal DESC, nama_toko ASC;
        """
        df = pd.read_sql(query, conn)
        logging.info(f"Berhasil mengambil {len(df)} records dari database.")
        return df
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"Error saat mengambil data: {error}", exc_info=True)
        return pd.DataFrame()  # Mengembalikan DataFrame kosong jika ada error
    finally:
        if conn:
            conn.close()
            logging.info("Koneksi database ditutup.")


# --- ORDERS DATA ---
def insert_orders_batch_data(df):
    """
    Insert batch data orders ke dalam tabel orders.
    Args:
        df (pd.DataFrame): DataFrame hasil cleaning dengan kolom sesuai schema.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Kolom schema sesuai urutan yang diminta
        columns = [
            "order_id",
            "package_id",
            "no_resi",
            "order_status",
            "waktu_pesanan_dibuat",
            "waktu_pesanan_dibayar",
            "waktu_selesai",
            "waktu_pembatalan",
            "yang_membatalkan",
            "nama_pembeli",
            "no_telepon",
            "alamat_lengkap",
            "kecamatan",
            "kelurahan",
            "kabupaten_kota",
            "provinsi",
            "negara",
            "kode_pos",
            "sku",
            "nama_produk",
            "jumlah",
            "harga_satuan",
            "subtotal_produk",
            "harga_awal_produk",
            "ongkos_kirim",
            "diskon_ongkos_kirim_penjual",
            "diskon_ongkos_kirim_marketplace",
            "diskon_penjual",
            "diskon_marketplace",
            "total_pesanan",
            "biaya_pengelolaan",
            "biaya_transaksi",
            "voucher",
            "voucher_toko",
            "nama_marketplace",
            "nama_toko",
            "id_brand",
            "gudang_asal",
            "jasa_kirim",
            "metode_pengiriman",
            "metode_pembayaran",
            "pesan_dari_pembeli",
            "sesi",
            "is_fake_order",
            "timestamp_input_data",
        ]

        # Konversi DataFrame ke list of tuples sesuai urutan kolom
        values = [
            tuple(row[col] if col in row else None for col in columns)
            for _, row in df.iterrows()
        ]

        # SQL template
        insert_sql = f"""
            INSERT INTO orders ({", ".join(columns)})
            VALUES %s
            ON CONFLICT (order_id) DO NOTHING
        """
        # {", ".join([f"{col}=EXCLUDED.{col}" for col in columns if col != "order_id"])};

        extras.execute_values(cursor, insert_sql, values)
        conn.commit()

        logging.info(
            f"Berhasil menyimpan/memperbarui {len(values)} records orders ke database."
        )
        return {
            "status": "success",
            "message": f"{len(values)} records orders berhasil disimpan atau diperbarui.",
        }

    except Exception as e:
        st.error(f"Gagal insert batch orders: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def insert_orders_to_normalized_table(
    df,
    table_name,
    columns,
    conflict_cols=None,
    update_cols=None,
    drop_duplicates_row=None,
    dropna=None,
):
    """
    Insert dataframe ke tabel PostgreSQL dengan psycopg2.

    Params
    ------
    conn : psycopg2 connection
    df : pandas DataFrame
    table_name : str, nama tabel target
    columns : list[str], nama kolom sesuai schema di PostgreSQL
    conflict_cols : list[str] atau None
        Kolom unik/PK untuk ON CONFLICT.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if isinstance(conflict_cols, str):
        conflict_cols = [conflict_cols]

    df = df[columns].copy()

    if drop_duplicates_row and dropna:
        df = df.drop_duplicates(subset=conflict_cols, keep="first")
        df = df.dropna(subset=conflict_cols, how="any")
    elif drop_duplicates_row:
        df = df.drop_duplicates(subset=conflict_cols, keep="first")
    elif dropna:
        df = df.dropna(subset=conflict_cols, how="any")
    # else:
    #     df = df[columns].copy()

    # convert dataframe ke list of tuples
    values = df.to_numpy().tolist()

    # build query insert
    colnames = ", ".join(columns)
    placeholders = "(" + ", ".join(["%s"] * len(columns)) + ")"

    if conflict_cols and update_cols:
        update_statement = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_cols])
        conflict_clause = (
            f"ON CONFLICT ({', '.join(conflict_cols)}) DO UPDATE SET {update_statement}"
        )
    elif conflict_cols:
        conflict_clause = f"ON CONFLICT ({', '.join(conflict_cols)}) DO NOTHING"
    else:
        conflict_clause = ""

    query = f"""
        INSERT INTO {table_name} ({colnames})
        VALUES %s
        {conflict_clause}
    """

    try:
        extras.execute_values(
            cursor, query, values, template=placeholders, page_size=1000
        )
        conn.commit()
        logging.info(
            f"Berhasil menyimpan/memperbarui {len(values)} records {table_name} ke database."
        )
        return {
            "status": "success",
            "message": f"{len(values)} records {table_name} berhasil disimpan atau diperbarui.",
        }

    except Exception as e:
        st.error(f"Gagal insert batch {table_name}: {e}")
        conn.rollback()
        return False

    finally:
        if conn:
            conn.close()


# --- FINANCE DATA
def insert_omset_data(data: pd.DataFrame):
    """
    Menyimpan atau memperbarui data omset dari DataFrame ke database.
    Menggunakan transaksi untuk memastikan operasi berjalan atomic.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            INSERT INTO finance_omset (
                tanggal, marketplace, nama_toko, akrual_basis,
                cash_basis, bukti, akun_bank, pendapatan_kotor, biaya_admin 
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (tanggal, nama_toko) DO UPDATE SET
                marketplace = EXCLUDED.marketplace,
                akrual_basis = EXCLUDED.akrual_basis,
                cash_basis = EXCLUDED.cash_basis,
                bukti = EXCLUDED.bukti,
                akun_bank = EXCLUDED.akun_bank,
                pendapatan_kotor = EXCLUDED.pendapatan_kotor,
                biaya_admin = EXCLUDED.biaya_admin;
        """

        records = [
            tuple(row)
            for row in data[
                [
                    "Tanggal",
                    "Marketplace",
                    "Nama Toko",
                    "Akrual Basis",
                    "Cash Basis",
                    "Bukti",
                    "Akun Bank",
                    "Pendapatan Kotor",
                    "Biaya Admin",
                ]
            ].to_numpy()
        ]

        cur.executemany(query, records)
        conn.commit()
        logging.info(
            f"Berhasil menyimpan/memperbarui {len(records)} records finance_omset ke database."
        )
        return {
            "status": "success",
            "message": f"{len(records)} records finance_omset berhasil disimpan atau diperbarui.",
        }

    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()
        logging.error(f"Error saat menyimpan data: {error}", exc_info=True)
        return {"status": "error", "message": str(error)}
    finally:
        if conn:
            cur.close()
            conn.close()
            logging.info("Koneksi database ditutup.")


def insert_omset_reg_data(data: pd.DataFrame):
    """
    Menyimpan atau memperbarui data omset reguler dari DataFrame ke database.
    Menggunakan transaksi untuk memastikan operasi berjalan atomic.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            INSERT INTO finance_omset_reg (
                tanggal, platform, akrual_basis, cash_basis, bukti, akun_bank
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (tanggal, platform) DO UPDATE SET
                akrual_basis = EXCLUDED.akrual_basis,
                cash_basis = EXCLUDED.cash_basis,
                bukti = EXCLUDED.bukti,
                akun_bank = EXCLUDED.akun_bank;
        """

        # Pastikan urutan kolom sesuai query
        records = [
            tuple(row)
            for row in data[
                [
                    "Tanggal",
                    "Platform",
                    "Akrual Basis",
                    "Cash Basis",
                    "Bukti",
                    "Akun Bank",
                ]
            ].to_numpy()
        ]

        cur.executemany(query, records)
        conn.commit()

        logging.info(
            f"Berhasil menyimpan/memperbarui {len(records)} records finance_omset_reg ke database."
        )
        return {
            "status": "success",
            "message": f"{len(records)} records finance_omset_reg berhasil disimpan atau diperbarui.",
        }

    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()
        logging.error(
            f"Error saat menyimpan data finance_omset_reg: {error}", exc_info=True
        )
        return {"status": "error", "message": str(error)}

    finally:
        if conn:
            cur.close()
            conn.close()
            logging.info("Koneksi database ditutup.")


def insert_budget_ads_data(data: pd.DataFrame):
    """
    Menyimpan atau memperbarui data budget ads dari DataFrame ke database.
    Menggunakan transaksi untuk memastikan operasi berjalan atomic.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            INSERT INTO finance_budget_ads (
                tanggal, marketplace, nama_toko,
                nominal_aktual_ads
            ) VALUES (
                %s, %s, %s, %s
            )
            ON CONFLICT (tanggal, nama_toko) DO UPDATE SET
                marketplace = EXCLUDED.marketplace,
                nominal_aktual_ads = EXCLUDED.nominal_aktual_ads;
        """

        records = [
            tuple(row)
            for row in data[
                [
                    "Tanggal",
                    "Marketplace",
                    "Nama Toko",
                    "Nominal Aktual Ads",
                ]
            ].to_numpy()
        ]

        cur.executemany(query, records)
        conn.commit()
        logging.info(
            f"Berhasil menyimpan/memperbarui {len(records)} records finance_budget_ads ke database."
        )
        return {
            "status": "success",
            "message": f"{len(records)} records finance_omset berhasil disimpan atau diperbarui.",
        }

    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()
        logging.error(f"Error saat menyimpan data: {error}", exc_info=True)
        return {"status": "error", "message": str(error)}
    finally:
        if conn:
            cur.close()
            conn.close()
            logging.info("Koneksi database ditutup.")


def insert_finance_cpas_data(data: pd.DataFrame):
    """
    Memasukkan atau memperbarui data CPAS dari DataFrame ke dalam tabel finance_budget_ads_cpas.
    Menggunakan ON CONFLICT DO UPDATE untuk menangani entri ganda secara efisien.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            INSERT INTO finance_budget_ads_cpas (tanggal, nama_toko, akun, nominal_aktual_ads)
            VALUES (
                %s, %s, %s, %s
            )
            ON CONFLICT (tanggal, akun) DO UPDATE
            SET
                nama_toko = EXCLUDED.nama_toko,
                nominal_aktual_ads = EXCLUDED.nominal_aktual_ads
        """
        records = [
            tuple(row)
            for row in data[
                [
                    "Tanggal",
                    "Nama Toko",
                    "Akun",
                    "Nominal Aktual Ads",
                ]
            ].to_numpy()
        ]

        cur.executemany(query, records)
        conn.commit()

        logging.info(
            f"Berhasil menyimpan/memperbarui {len(records)} records finance_budget_ads_cpas ke database."
        )
        return {
            "status": "success",
            "message": f"{len(records)} records finance_budget_ads_cpas berhasil disimpan atau diperbarui.",
        }

    except psycopg2.Error as e:
        logging.error(f"Gagal memasukkan data ke database: {e}")
        conn.rollback()  # Batalkan transaksi jika terjadi kesalahan
        return False

    finally:
        if conn:
            conn.close()


def insert_budget_reg_ads_data(data: pd.DataFrame):
    """
    Menyimpan atau memperbarui data budget reg ads dari DataFrame ke database.
    Menggunakan transaksi untuk memastikan operasi berjalan atomic.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            INSERT INTO finance_budget_ads_reg (
                tanggal, akun, nominal_aktual_ads
            ) VALUES (
                %s, %s, %s
            )
            ON CONFLICT (tanggal, akun) DO UPDATE SET
                nominal_aktual_ads = EXCLUDED.nominal_aktual_ads;
        """

        records = [
            tuple(row)
            for row in data[
                [
                    "Tanggal",
                    "Akun",
                    "Nominal Aktual Ads",
                ]
            ].to_numpy()
        ]

        cur.executemany(query, records)
        conn.commit()
        logging.info(
            f"Berhasil menyimpan/memperbarui {len(records)} records finance_budget_ads_reg ke database."
        )
        return {
            "status": "success",
            "message": f"{len(records)} records finance_omset berhasil disimpan atau diperbarui.",
        }

    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()
        logging.error(f"Error saat menyimpan data: {error}", exc_info=True)
        return {"status": "error", "message": str(error)}
    finally:
        if conn:
            cur.close()
            conn.close()
            logging.info("Koneksi database ditutup.")


# def insert_budget_non_ads_data(data: pd.DataFrame):
#     """
#     Menyimpan atau memperbarui data budget ads dari DataFrame ke database.
#     Menggunakan transaksi untuk memastikan operasi berjalan atomic.
#     """
#     conn = None
#     try:
#         conn = get_connection()
#         cur = conn.cursor()

#         query = """
#             INSERT INTO finance_budget_non_ads (
#                 tanggal, nominal_aktual_non_ads, keterangan
#             ) VALUES (
#                 %s, %s, %s
#             );
#         """

#         records = [
#             tuple(row)
#             for row in data[
#                 [
#                     "Tanggal",
#                     "Nominal Aktual Non Ads",
#                     "Keterangan",
#                 ]
#             ].to_numpy()
#         ]

#         cur.executemany(query, records)
#         conn.commit()
#         logging.info(
#             f"Berhasil menyimpan/memperbarui {len(records)} records finance_budget_non_ads ke database."
#         )
#         return {
#             "status": "success",
#             "message": f"{len(records)} records finance_omset berhasil disimpan atau diperbarui.",
#         }

#     except (Exception, psycopg2.DatabaseError) as error:
#         if conn:
#             conn.rollback()
#         logging.error(f"Error saat menyimpan data: {error}", exc_info=True)
#         return {"status": "error", "message": str(error)}
#     finally:
#         if conn:
#             cur.close()
#             conn.close()
#             logging.info("Koneksi database ditutup.")


def insert_budget_non_ads_fo_data(data: pd.DataFrame):
    """
    Menyimpan atau memperbarui data budget ads dari DataFrame ke database.
    Menggunakan transaksi untuk memastikan operasi berjalan atomic.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            INSERT INTO finance_budget_non_ads_fo (
                tanggal, marketplace, nama_toko, nominal_aktual_non_ads
            ) VALUES (
                %s, %s, %s, %s
            ) 
            ON CONFLICT (tanggal, nama_toko) DO UPDATE SET
                nominal_aktual_non_ads = EXCLUDED.nominal_aktual_non_ads;
        """

        records = [
            tuple(row)
            for row in data[
                [
                    "Tanggal",
                    "Marketplace",
                    "Nama Toko",
                    "Nominal Aktual Non Ads",
                ]
            ].to_numpy()
        ]

        cur.executemany(query, records)
        conn.commit()
        logging.info(
            f"Berhasil menyimpan/memperbarui {len(records)} records finance_budget_non_ads ke database."
        )
        return {
            "status": "success",
            "message": f"{len(records)} records finance_budget_non_ads_fo berhasil disimpan atau diperbarui.",
        }

    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()
        logging.error(f"Error saat menyimpan data: {error}", exc_info=True)
        return {"status": "error", "message": str(error)}
    finally:
        if conn:
            cur.close()
            conn.close()
            logging.info("Koneksi database ditutup.")


def insert_budget_non_ads_lainnya_data(data: pd.DataFrame):
    """
    Menyimpan atau memperbarui data budget ads dari DataFrame ke database.
    Menggunakan transaksi untuk memastikan operasi berjalan atomic.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            INSERT INTO finance_budget_non_ads_lainnya (
                tanggal, nama_project, keterangan, nominal_aktual_non_ads
            ) VALUES (
                %s, %s, %s, %s
            )
            ON CONFLICT (tanggal, nama_project, keterangan) DO UPDATE SET
                nominal_aktual_non_ads = EXCLUDED.nominal_aktual_non_ads;
        """

        records = [
            tuple(row)
            for row in data[
                [
                    "Tanggal",
                    "Nama Project",
                    "Keterangan",
                    "Nominal Aktual Non Ads",
                ]
            ].to_numpy()
        ]

        cur.executemany(query, records)
        conn.commit()
        logging.info(
            f"Berhasil menyimpan/memperbarui {len(records)} records finance_budget_non_ads ke database."
        )
        return {
            "status": "success",
            "message": f"{len(records)} records finance_omset berhasil disimpan atau diperbarui.",
        }

    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()
        logging.error(f"Error saat menyimpan data: {error}", exc_info=True)
        return {"status": "error", "message": str(error)}
    finally:
        if conn:
            cur.close()
            conn.close()
            logging.info("Koneksi database ditutup.")


# --- RETURNS DATA ---
def insert_returns_data(tanggal, order_id):
    """Menyimpan data retur ke dalam database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO returns (tanggal, order_id)
            VALUES (%s, %s)
            ON CONFLICT (order_id) DO NOTHING;
            """,
            (tanggal, order_id),
        )
        conn.commit()
        st.success(f"Data retur untuk order ID {order_id} berhasil disimpan.")
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan data retur: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_returns_data():
    """Mengambil semua data retur dari database."""
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM returns ORDER BY tanggal ASC", conn)
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data retur: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def insert_returns_data_batch(tanggal, order_ids):
    """
    Menyimpan data retur dalam batch ke dalam tabel returns.
    order_ids adalah list dari order ID.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Membuat list of tuples (tanggal, order_id) untuk executemany
        data_to_insert = [(tanggal, oid) for oid in order_ids]

        insert_query = """
        INSERT INTO returns (tanggal, order_id)
        VALUES (%s, %s)
        ON CONFLICT (order_id) DO NOTHING;
        """
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()
        st.success(f"✅ {len(order_ids)} data retur berhasil disimpan atau diperbarui.")
        return True
    except Exception as e:
        st.error(f"❌ Gagal menyimpan data retur dalam batch: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()


# --- ORDER KHUSUS ---
def insert_order_flags_batch(tanggal_input, kategori, order_ids) -> bool:
    """
    Menyisipkan beberapa baris data ke tabel order_flags secara efisien (batch).

    Args:
        tanggal_input (date): Tanggal yang dipilih dari form.
        kategori (str): Kategori yang dipilih dari form.
        order_ids (List[str]): Daftar order_id yang akan diinput.

    Returns:
        bool: True jika berhasil, False jika terjadi error.
    """
    conn = get_connection()

    # SQL Query dengan placeholder untuk keamanan
    query = """
        INSERT INTO order_flags (order_id, kategori, tanggal_input)
        VALUES (%s, %s, %s);
    """

    # Mempersiapkan data dalam format yang dibutuhkan (list of tuples)
    data_to_insert = [(oid, kategori, tanggal_input) for oid in order_ids]

    try:
        # Menggunakan koneksi yang sudah ada
        with conn.cursor() as cur:
            # Eksekusi query untuk semua data sekaligus
            cur.executemany(query, data_to_insert)

        # Commit transaksi untuk menyimpan perubahan
        conn.commit()
        print(f"Successfully inserted {len(data_to_insert)} rows into order_flags.")
        return True

    except psycopg2.Error as e:
        # Jika terjadi error, batalkan semua perubahan (rollback)
        print(f"Database error, rolling back: {e}")
        conn.rollback()
        return False


def update_table(table_name, data_list, pk_cols):
    """
    Upsert (insert or update) records ke PostgreSQL secara aman
    berdasarkan primary key.
    """
    if not data_list:
        return

    conn = get_connection()
    cur = conn.cursor()

    # ambil semua kolom dari dict pertama
    cols = list(data_list[0].keys())
    col_names = ", ".join(cols)

    # bagian UPDATE untuk kolom selain PK
    update_clause = ", ".join(
        [f"{col} = EXCLUDED.{col}" for col in cols if col not in pk_cols]
    )

    # buat query template
    query = f"""
        INSERT INTO {table_name} ({col_names})
        VALUES %s
        ON CONFLICT ({", ".join(pk_cols)})
        DO UPDATE SET {update_clause};
    """

    # ambil nilai sebagai tuple dari setiap dict
    values = [tuple(row[col] for col in cols) for row in data_list]

    # ini kunci penting: execute_values akan handle tipe data dengan benar
    extras.execute_values(cur, query, values)

    conn.commit()
    cur.close()
    conn.close()


def get_budget_ads_summary_by_project(project_name, start_date=None, end_date=None):
    """
    Mengambil data summary budget ads dari view vw_budget_ads_summary.

    Args:
        db_params (Dict[str, str]): Parameter koneksi database.
        project_name (str): Nama project yang ingin difilter.
        start_date (Optional[date]): Tanggal mulai untuk filter (inklusif).
        end_date (Optional[date]): Tanggal akhir untuk filter (inklusif).

    Returns:
        Optional[pd.DataFrame]: DataFrame berisi hasil query, atau None jika error.
    """
    conn = None
    try:
        # Membuat koneksi ke database PostgreSQL
        conn = get_connection()

        # Membangun query secara dinamis dan aman
        params = {"p_name": project_name}
        where_clauses: List[str] = ["project_name = %(p_name)s"]

        if start_date:
            where_clauses.append("tanggal >= %(s_date)s")
            params["s_date"] = start_date

        if end_date:
            where_clauses.append("tanggal <= %(e_date)s")
            params["e_date"] = end_date

        where_sql = " AND ".join(where_clauses)

        sql_query = f"""
            SELECT *
            FROM vw_budget_ads_summary
            WHERE {where_sql}
            ORDER BY tanggal;
        """

        # Menjalankan query dan mengambil data ke DataFrame
        print(f"Executing query for project '{project_name}'...")
        df = pd.read_sql(sql_query, conn, params=params)

        return df

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return None

    finally:
        # Memastikan koneksi selalu ditutup
        if conn is not None:
            conn.close()
            print("Database connection closed.")


def fetch_all_flags_reg(conn):
    """Mengambil semua data dari order_flag_reg dan mengonversi tipe data."""
    query = "SELECT * FROM order_flag_reg ORDER BY tanggal_input DESC, id_flag DESC;"
    df = pd.read_sql(query, conn)
    # Konversi tipe data yang penting untuk data editor
    df["tanggal_input"] = pd.to_datetime(df["tanggal_input"]).dt.date
    df["nominal_adjustment"] = df["nominal_adjustment"].astype(float)
    return df


def process_flag_changes_reg(conn, original_df, changes):
    """
    Memproses semua perubahan (tambah, edit, hapus) dari data editor
    dan menerapkannya ke database.
    """
    cursor = conn.cursor()

    # 1. Proses Penghapusan Data
    if "deleted_rows" in changes and changes["deleted_rows"]:
        indices_to_delete = changes["deleted_rows"]
        ids_to_delete = original_df.iloc[indices_to_delete]["id_flag"].tolist()
        for flag_id in ids_to_delete:
            # PERBAIKAN: Ubah numpy.int64 menjadi int standar Python
            cursor.execute(
                "DELETE FROM order_flag_reg WHERE id_flag = %s", (int(flag_id),)
            )

    # 2. Proses Penambahan Data
    if "added_rows" in changes and changes["added_rows"]:
        for new_row in changes["added_rows"]:
            cursor.execute(
                """
                INSERT INTO order_flag_reg (tanggal_input, nominal_adjustment, kategori, keterangan)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    new_row.get("tanggal_input", date.today()),
                    new_row.get("nominal_adjustment", 0.0),
                    new_row.get("kategori", "RETURN"),
                    new_row.get("keterangan", None),
                ),
            )

    # 3. Proses Pengeditan Data
    if "edited_rows" in changes and changes["edited_rows"]:
        for index, updates in changes["edited_rows"].items():
            flag_id = original_df.iloc[int(index)]["id_flag"]

            set_clauses = [f"{key} = %s" for key in updates.keys()]
            query = (
                f"UPDATE order_flag_reg SET {', '.join(set_clauses)} WHERE id_flag = %s"
            )

            # PERBAIKAN: Ubah numpy.int64 menjadi int standar Python untuk ID
            values = list(updates.values()) + [int(flag_id)]
            cursor.execute(query, tuple(values))

    conn.commit()
    cursor.close()


def get_budget_regular_summary_by_project(
    start_date=None, end_date=None
) -> pd.DataFrame:
    """
    Mengambil data summary budget dari view vw_budget_regular_summary.
    Data hanya difilter berdasarkan rentang tanggal.

    Args:
        start_date (Optional[date]): Tanggal mulai untuk filter (inklusif).
        end_date (Optional[date]): Tanggal akhir untuk filter (inklusif).

    Returns:
        Optional[pd.DataFrame]: DataFrame berisi hasil query, atau None jika error.
    """
    conn = None
    try:
        conn = get_connection()

        # Memulai dengan parameter dan klausa WHERE yang kosong
        params = {}
        where_clauses = []

        # Menambahkan filter tanggal secara dinamis jika disediakan
        if start_date:
            where_clauses.append("tanggal >= %(s_date)s")
            params["s_date"] = start_date

        if end_date:
            where_clauses.append("tanggal <= %(e_date)s")
            params["e_date"] = end_date

        # Membangun klausa WHERE hanya jika ada filter yang diterapkan
        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        sql_query = f"""
            SELECT *
            FROM vw_budget_regular_summary
            {where_sql}
            ORDER BY tanggal;
        """

        print("Executing query for regular budget summary...")
        df = pd.read_sql(sql_query, conn, params=params)

        return df

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return None

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")


def get_vw_ragular_performance_summary(
    start_date: date, end_date: date
) -> pd.DataFrame:
    """
    Mengambil data dari view vw_regular_performance_summary berdasarkan filter tanggal.

    Args:
        start_date (date): Tanggal mulai periode.
        end_date (date): Tanggal akhir periode.

    Returns:
        pd.DataFrame: DataFrame berisi detail performa.
                      Mengembalikan DataFrame kosong jika tidak ada data atau terjadi error.
    """
    # Query disederhanakan: Hapus filter project_name dan ORDER BY nama_toko
    query = """
        SELECT
            *
        FROM
            vw_regular_performance_summary
        WHERE
            tanggal BETWEEN %(start_date)s AND %(end_date)s
        ORDER BY
            tanggal DESC;
    """
    conn = None
    try:
        conn = get_connection()
        df = pd.read_sql(
            query,
            conn,
            # Params disederhanakan: Hapus project_name
            params={
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        logging.info(
            f"Successfully fetched {len(df)} rows from vw_regular_performance_summary."
        )
        return df
    except (Exception, psycopg2.DatabaseError) as e:
        # Log error yang lebih spesifik
        logging.error(f"Failed to fetch data from vw_regular_performance_summary: {e}")
        return pd.DataFrame()  # Kembalikan dataframe kosong jika error
    finally:
        if conn:
            conn.close()
