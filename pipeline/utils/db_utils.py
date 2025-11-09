# File: pipeline/db_utils.py

import io
import logging

import pandas as pd
import pandas.io.sql as pd_sql
from psycopg2 import sql

from database.db_connection import get_connection


def bulk_upsert(df: pd.DataFrame, table_name: str, conflict_cols: list):
    """
    Melakukan bulk "UPSERT" (INSERT ... ON CONFLICT DO UPDATE) secara generik.
    Bisa digunakan untuk tabel dimensi (menggunakan natural key)
    dan tabel fakta (menggunakan primary key).

    Args:
        df: DataFrame yang akan di-load.
        table_name: Nama tabel target.
        conflict_cols: Daftar kolom yang menjadi "UNIQUE constraint" atau "Primary Key".
    """
    if df.empty:
        logging.info(f"Skipping upsert for {table_name}, DataFrame is empty.")
        return

    if isinstance(conflict_cols, str):
        conflict_cols = [conflict_cols]

    conflict_keys_str = ", ".join(conflict_cols)
    all_cols = list(df.columns)

    # Kolom untuk di-update adalah semua kolom yg BUKAN bagian dari conflict key
    non_conflict_cols = [col for col in all_cols if col not in conflict_cols]

    temp_table = f"temp_{table_name}_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S%f')}"

    with get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # 1. Buat temporary table berdasarkan skema DataFrame (df)
                create_temp_sql = pd_sql.get_schema(df, temp_table, con=conn)
                create_temp_sql = create_temp_sql.replace(
                    "CREATE TABLE", "CREATE TEMPORARY TABLE"
                )
                cursor.execute(create_temp_sql)

                # 2. COPY data dari DataFrame ke temporary table
                s_buf = io.StringIO()
                df.to_csv(s_buf, index=False, header=False, sep="\t")
                s_buf.seek(0)

                cursor.copy_expert(
                    f"COPY {temp_table} ({', '.join(all_cols)}) FROM STDIN WITH (FORMAT CSV, DELIMITER E'\\t')",
                    s_buf,
                )

                # 3. Buat query "Upsert"
                all_cols_str = ", ".join(all_cols)

                insert_query = f"""
                    INSERT INTO {table_name} ({all_cols_str})
                    SELECT {all_cols_str} FROM {temp_table}
                    ON CONFLICT ({conflict_keys_str})
                """

                if not non_conflict_cols:
                    # Jika tidak ada kolom non-key, jangan lakukan apa-apa
                    insert_query += " DO NOTHING;"
                else:
                    # Buat klausa SET secara dinamis
                    set_clause = ", ".join(
                        [f"{col} = EXCLUDED.{col}" for col in non_conflict_cols]
                    )
                    insert_query += f" DO UPDATE SET {set_clause};"

                # 4. Eksekusi query Upsert
                cursor.execute(insert_query)

                # 5. Commit
                conn.commit()
                logging.info(f"Bulk upsert successful for {table_name}.")

            except Exception as e:
                conn.rollback()
                raise Exception(f"Failed to bulk upsert {table_name}: {e}")
            finally:
                cursor.execute(f"DROP TABLE IF EXISTS {temp_table}")


def get_keys_for_batch(
    table_name: str, key_cols: list[str], batch_keys_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Mengambil key map (DataFrame) HANYA untuk natural keys di batch ini.
    Ini adalah perbaikan untuk key gabungan, menggunakan 'temp table join'.

    Args:
        table_name: Nama tabel dimensi (cth: 'dim_customers')
        key_cols: Daftar kolom (cth: ['customer_id', 'nama_pembeli', 'no_telepon'])
        batch_keys_df: DataFrame yang HANYA berisi natural keys dari batch
    """
    if batch_keys_df.empty:
        return pd.DataFrame(columns=key_cols)

    natural_key_cols = key_cols[1:]

    # Buat nama tabel temporer yang unik
    temp_table = f"temp_keys_{table_name}_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"

    with get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # 1. Buat Tabel Temporer
                create_temp_sql = pd.io.sql.get_schema(
                    batch_keys_df, temp_table, con=conn
                )
                cursor.execute(create_temp_sql)

                # 2. Bulk Load natural keys ke Tabel Temporer
                s_buf = io.StringIO()
                batch_keys_df.to_csv(s_buf, index=False, header=False, sep="\t")
                s_buf.seek(0)
                cursor.copy_expert(
                    f"COPY {temp_table} FROM STDIN WITH (FORMAT CSV, DELIMITER E'\\t')",
                    s_buf,
                )

                # 3. Buat join condition untuk SEMUA natural keys
                join_condition = " AND ".join(
                    [f"main.{nk} = tmp.{nk}" for nk in natural_key_cols]
                )

                # 4. Query untuk SELECT keys dengan JOIN
                prefixed_cols = [f"main.{col}" for col in key_cols]

                # Gabungkan daftar baru tersebut dengan koma
                # Hasil: "main.customer_id, main.nama_pembeli, main.nomor_pesanan"
                select_clause = ", ".join(prefixed_cols)

                # Masukkan ke query utama
                query = f"""
                            SELECT {select_clause}
                            FROM {table_name} AS main
                            JOIN {temp_table} AS tmp ON {join_condition}
                        """

                cursor.execute(query)
                rows = cursor.fetchall()

                # 5. Ambil hasil sebagai DataFrame
                cols = [desc[0] for desc in cursor.description]
                return pd.DataFrame(rows, columns=cols)

            except Exception as e:
                conn.rollback()
                raise Exception(f"Failed to get keys for {table_name}: {e}")
            finally:
                cursor.execute(f"DROP TABLE IF EXISTS {temp_table}")


def select_from_db(
    conn, table_name, columns="*", filters=None, limit=None, order_by=None
):
    """
    Fungsi generik untuk melakukan SELECT dari PostgreSQL dengan filter dinamis dan aman.

    Parameters:
    ----------
    conn : psycopg2.connection
        Koneksi aktif ke database PostgreSQL.
    table_name : str
        Nama tabel yang ingin di-query.
    columns : list[str] | str, optional
        Daftar kolom yang ingin diambil. Default '*'.
    filters : dict, optional
        Filter dalam bentuk {kolom: nilai}, misal {"tim": "zyy x juw", "nama_produk": "Bycetin 20 Gr"}.
    limit : int, optional
        Batas jumlah data yang diambil.
    order_by : str | tuple, optional
        Kolom untuk pengurutan. Bisa string ('created_at DESC') atau tuple ('created_at', 'DESC').

    Returns:
    --------
    list[dict]
        Daftar hasil query dalam bentuk dictionary.
    """
    try:
        with conn.cursor() as cur:
            # kolom yang akan diambil
            if isinstance(columns, list):
                col_clause = sql.SQL(", ").join(map(sql.Identifier, columns))
            else:
                col_clause = sql.SQL(columns)  # jika '*'

            # query dasar
            query = sql.SQL("SELECT {fields} FROM {table}").format(
                fields=col_clause, table=sql.Identifier(table_name)
            )

            # WHERE
            values = []
            if filters:
                conditions = []
                for col, val in filters.items():
                    conditions.append(sql.SQL("{} = %s").format(sql.Identifier(col)))
                    values.append(val)
                where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions)
                query += where_clause

            # ORDER BY
            if order_by:
                if isinstance(order_by, tuple):
                    query += sql.SQL(" ORDER BY {} {}").format(
                        sql.Identifier(order_by[0]), sql.SQL(order_by[1])
                    )
                else:
                    query += sql.SQL(" ORDER BY ") + sql.SQL(order_by)

            # LIMIT
            if limit:
                query += sql.SQL(" LIMIT %s")
                values.append(limit)

            cur.execute(query, values)

            # Ambil hasil dan ubah ke dict
            colnames = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            results = [dict(zip(colnames, row)) for row in rows]

            return results

    except Exception as e:
        print(f"[ERROR] Gagal mengeksekusi query: {e}")
        return []
