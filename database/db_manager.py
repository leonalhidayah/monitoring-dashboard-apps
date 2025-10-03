import logging
import warnings

import pandas as pd
import psycopg2
import streamlit as st
from psycopg2 import extras

from database.db_connection import get_connection

# Konfigurasi dasar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


warnings.filterwarnings("ignore")


# --- DIM_STORE
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


def get_admin_shipments():
    """Mengambil semua data dari tabel admin_shipments."""
    return get_table_data(table_name="admin_shipments")


def get_finance_omset():
    return get_table_data(table_name="finance_omset")


def get_finance_budget_ads():
    return get_table_data(table_name="finance_budget_ads")


def get_finance_budget_non_ads():
    return get_table_data(table_name="finance_budget_non_ads")


def get_vw_budget_ads_monitoring():
    """Mengambil semua data dari tabel vw_budget_ads_monitoring."""
    return get_table_data(table_name="vw_budget_ads_monitoring")


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

        query = """
            INSERT INTO advertiser_cpas (tanggal, nama_brand, akun, spend, konversi, gross_revenue)
            VALUES (
                %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (tanggal, akun) DO UPDATE
            SET
                nama_brand = EXCLUDED.nama_brand,
                spend = EXCLUDED.spend,
                konversi = EXCLUDED.konversi,
                gross_revenue = EXCLUDED.gross_revenue;
        """
        records = [
            tuple(row)
            for row in data[
                [
                    "Tanggal",
                    "Brand",
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

    if conflict_cols:
        conflict_clause = f"ON CONFLICT ({', '.join(conflict_cols)}) DO NOTHING"
    elif conflict_clause and update_cols:
        conflict_clause = (
            f"ON CONFLICT ({', '.join(conflict_cols)}) DO UPDATE SET "
            + ", ".join([f"{col} = EXCLUDED.{col}" for col in update_cols])
        )
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


# def insert_orders_normalized(df: pd.DataFrame, update_cols: list) -> dict:
#     """
#     Insert batch data yang sudah dinormalisasi ke dalam tabel orders.
#     Menggunakan mekanisme ON CONFLICT DO UPDATE (Upsert).

#     Args:
#         df (pd.DataFrame): DataFrame yang sudah diagregasi per order_id.
#         update_cols (list): Daftar nama kolom yang akan diperbarui jika terjadi konflik.

#     Returns:
#         dict: Berisi status keberhasilan dan pesan.
#     """
#     # 1. Sesuaikan daftar kolom dengan skema tabel 'orders' di database
#     table_columns = [
#         "order_id",
#         "customer_id",
#         "order_status",
#         "is_fake_order",
#         "waktu_pesanan_dibuat",
#         "waktu_pesanan_dibayar",
#         "waktu_kadaluwarsa",
#         "waktu_proses",
#         "waktu_selesai",
#         "waktu_pembatalan",
#         "yang_membatalkan",
#         "pesan_dari_pembeli",
#         # 'timestamp_input_data' akan di-handle oleh database
#     ]

#     # Pastikan DataFrame input memiliki semua kolom yang diperlukan
#     df_insert = df[table_columns]

#     conn = None
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()

#         # 2. Buat bagian SET untuk klausa DO UPDATE secara dinamis
#         update_set_clause = ", ".join(
#             [f"{col} = EXCLUDED.{col}" for col in update_cols]
#         )
#         # Selalu update timestamp terakhir diubah
#         update_set_clause += ", timestamp_input_data = CURRENT_TIMESTAMP"

#         # 3. SQL Template yang lebih aman dan presisi
#         insert_sql = f"""
#             INSERT INTO orders ({", ".join(table_columns)})
#             VALUES %s
#             ON CONFLICT (order_id) DO UPDATE SET
#               {update_set_clause};
#         """

#         # 4. Konversi DataFrame ke list of tuples
#         # Cara ini lebih aman dan memastikan urutan kolom benar
#         values = list(df_insert.to_records(index=False))

#         # Eksekusi query menggunakan execute_values untuk efisiensi
#         extras.execute_values(cursor, insert_sql, values, page_size=1000)
#         conn.commit()

#         logging.info(
#             f"Berhasil melakukan upsert {len(df_insert)} records ke tabel orders."
#         )
#         return {
#             "status": "success",
#             "message": f"Berhasil memproses {len(df_insert)} data pesanan.",
#         }

#     except (Exception, psycopg2.Error) as e:
#         if conn:
#             conn.rollback()
#         logging.error(f"Gagal insert batch orders: {e}", exc_info=True)
#         return {"status": "error", "message": str(e)}

#     finally:
#         if conn:
#             conn.close()


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
                cash_basis, bukti, akun_bank 
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (tanggal, nama_toko) DO UPDATE SET
                marketplace = EXCLUDED.marketplace,
                akrual_basis = EXCLUDED.akrual_basis,
                cash_basis = EXCLUDED.cash_basis,
                bukti = EXCLUDED.bukti,
                akun_bank = EXCLUDED.akun_bank;
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


def insert_budget_non_ads_data(data: pd.DataFrame):
    """
    Menyimpan atau memperbarui data budget ads dari DataFrame ke database.
    Menggunakan transaksi untuk memastikan operasi berjalan atomic.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            INSERT INTO finance_budget_non_ads (
                tanggal, nominal_aktual_non_ads, keterangan
            ) VALUES (
                %s, %s, %s
            );
        """

        records = [
            tuple(row)
            for row in data[
                [
                    "Tanggal",
                    "Nominal Aktual Non Ads",
                    "Keterangan",
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


# def insert_cashflow_data(tanggal, jenis_transaksi, keterangan, nominal):
#     """Menyimpan data cashflow ke dalam database."""
#     conn = get_connection()
#     try:
#         cursor = conn.cursor()
#         cursor.execute(
#             """
#             INSERT INTO finance_cashflow (tanggal, jenis_transaksi, keterangan, nominal)
#             VALUES (%s, %s, %s, %s);
#             """,
#             (tanggal, jenis_transaksi, keterangan, nominal),
#         )
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Gagal menyimpan data cashflow: {e}")
#         conn.rollback()
#         return False
#     finally:
#         conn.close()


def insert_budget_plan_long(df_long: pd.DataFrame):
    """
    Insert data budget plan (long format) ke database Postgres.
    Jika data dengan (parameter, tahun, kuartal, bulan) sudah ada, maka update.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO finance_budget_plan (
            parameter, target_ratio, target_quarter, tahun, kuartal, bulan, target_bulanan, created_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (parameter, tahun, kuartal, bulan)
        DO UPDATE SET
            target_ratio = EXCLUDED.target_ratio,
            target_quarter = EXCLUDED.target_quarter,
            target_bulanan = EXCLUDED.target_bulanan,
            updated_at = NOW();
    """

    data = [
        (
            row["Parameter"],
            float(str(row["Target Rasio"]).replace("%", "")),  # ambil angka rasio
            float(row["Target Kuartal"]),
            int(row["Tahun"]),
            int(row["Kuartal"]),
            row["Bulan"],
            float(row["Target Bulanan"]),
        )
        for _, row in df_long.iterrows()
    ]

    try:
        extras.execute_batch(cursor, query, data)
        conn.commit()
        st.success(
            f"✅ {len(data)} baris budget plan berhasil disimpan/diupdate ke database."
        )
    except Exception as e:
        conn.rollback()
        st.error(f"❌ Gagal menyimpan data: {e}")
    finally:
        # cursor.close()
        conn.close()


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
