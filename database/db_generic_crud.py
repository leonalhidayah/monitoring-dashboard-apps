import logging

import numpy as np
import pandas as pd
import streamlit as st
from sqlalchemy import Engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

# @st.cache_data(ttl=300, show_spinner=False)
# def fetch_filtered_data(
#     _engine: Engine, table_name: str, active_filters: dict
# ) -> pd.DataFrame:
#     """
#     Mengambil data dari database dengan menerapkan filter pada level SQL Query.
#     """
#     # Base Query
#     sql = f"SELECT * FROM {table_name}"
#     where_conditions = []
#     params = {}

#     # Membangun WHERE clause dinamis
#     for col, val in active_filters.items():
#         if val is None or val == "Semua Kategori" or val == "":
#             continue

#         # Handle Date Range (Tuple: (start_date, end_date))
#         if isinstance(val, tuple) and len(val) == 2:
#             start, end = val
#             if start and end:  # Pastikan kedua tanggal ada
#                 where_conditions.append(f"{col} BETWEEN :start_{col} AND :end_{col}")
#                 params[f"start_{col}"] = start
#                 params[f"end_{col}"] = end

#         # Handle Multi-Select (List)
#         elif isinstance(val, list) and len(val) > 0:
#             # Menggunakan tuple untuk parameter IN clause agar aman di SQLAlchemy
#             where_conditions.append(f"{col} IN :list_{col}")
#             params[f"list_{col}"] = tuple(val)

#         # Handle Single Value (Exact Match)
#         elif isinstance(val, (str, int, float)):
#             where_conditions.append(f"{col} = :val_{col}")
#             params[f"val_{col}"] = val

#     # Menggabungkan WHERE clause jika ada filter aktif
#     if where_conditions:
#         sql += " WHERE " + " AND ".join(where_conditions)

#     try:
#         insp = inspect(_engine)
#         columns = [col["name"] for col in insp.get_columns(table_name)]

#         date_col = next((col for col in columns if col == "created_at"), None)
#         if not date_col:
#             date_col = next(
#                 (
#                     col
#                     for col in columns
#                     if "tanggal" in col.lower() or col.lower().endswith("_date")
#                 ),
#                 None,
#             )

#         if date_col:
#             sql += f" ORDER BY {date_col} DESC"
#         else:
#             sql += " ORDER BY 1 DESC"

#     except Exception as e:
#         logging.warning(f"Gagal inspect kolom untuk auto-order di {table_name}: {e}")
#         sql += " ORDER BY 1 DESC"

#     try:
#         with _engine.connect() as conn:
#             # Menggunakan text() untuk query dan passing params dengan aman
#             df = pd.read_sql(text(sql), conn, params=params)

#         return df
#     except SQLAlchemyError as e:
#         logging.error(f"Error in fetch_filtered_data: {e}")
#         st.error("Terjadi kesalahan saat mengambil data. Silakan coba lagi.")
#         return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_filtered_data(
    _engine: Engine,
    table_name: str,
    active_filters: dict,
    base_filter: dict = None,
) -> pd.DataFrame:
    """
    Mengambil data dari database dengan menerapkan filter UI (active_filters)
    dan filter kontekstual (base_filter).
    """
    # Base Query
    sql = f"SELECT * FROM {table_name}"
    where_conditions = []
    params = {}

    all_filters = {}
    if base_filter:
        all_filters.update(base_filter)
    if active_filters:
        all_filters.update(active_filters)

    for col, val in all_filters.items():  # <-- Diubah ke all_filters
        if val is None or val == "Semua Kategori" or val == "":
            continue

        if isinstance(val, tuple) and len(val) == 2:
            start, end = val
            if start and end:
                where_conditions.append(f"{col} BETWEEN :start_{col} AND :end_{col}")
                params[f"start_{col}"] = start
                params[f"end_{col}"] = end

        elif isinstance(val, list) and len(val) > 0:
            where_conditions.append(f"{col} IN :list_{col}")
            params[f"list_{col}"] = tuple(val)

        elif isinstance(val, (str, int, float)):
            where_conditions.append(f"{col} = :val_{col}")
            params[f"val_{col}"] = val

    if where_conditions:
        sql += " WHERE " + " AND ".join(where_conditions)

    try:
        insp = inspect(_engine)
        columns = [col["name"] for col in insp.get_columns(table_name)]

        date_col = next((col for col in columns if col == "created_at"), None)
        if not date_col:
            date_col = next(
                (
                    col
                    for col in columns
                    if "tanggal" in col.lower() or col.lower().endswith("_date")
                ),
                None,
            )

        if date_col:
            sql += f" ORDER BY {date_col} DESC"
        else:
            sql += " ORDER BY 1 DESC"

    except Exception as e:
        logging.warning(f"Gagal inspect kolom untuk auto-order di {table_name}: {e}")
        sql += " ORDER BY 1 DESC"

    try:
        with _engine.connect() as conn:
            df = pd.read_sql(text(sql), conn, params=params)
        return df
    except SQLAlchemyError as e:
        logging.error(f"Error in fetch_filtered_data: {e}")
        st.error("Terjadi kesalahan saat mengambil data. Silakan coba lagi.")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_distinct_options(
    _engine: Engine,
    table_name: str,
    column_name: str,
    project_context: str = None,
) -> list:
    """
    Helper function untuk mengambil opsi unik.
    Sekarang bisa memfilter berdasarkan project_context jika diperlukan.
    """
    params = {}

    if project_context and table_name == "dim_stores":
        query_str = f"""
            SELECT DISTINCT ds."{column_name}" 
            FROM dim_stores ds
            JOIN map_project_stores mps ON ds.store_id = mps.store_id
            JOIN dim_projects dp ON mps.project_id = dp.project_id
            WHERE dp.project_name = :project_name
            ORDER BY 1
        """
        params["project_name"] = project_context
        query = text(query_str)

    elif project_context and table_name == "dim_cpas_accounts":
        query_str = f"""
            SELECT DISTINCT dca."{column_name}" 
            FROM dim_cpas_accounts dca
            JOIN map_project_stores mps ON dca.store_id = mps.store_id
            JOIN dim_projects dp ON mps.project_id = dp.project_id
            WHERE dp.project_name = :project_name
            ORDER BY 1
        """
        params["project_name"] = project_context
        query = text(query_str)

    else:
        query = text(f'SELECT DISTINCT "{column_name}" FROM {table_name} ORDER BY 1')

    try:
        with _engine.connect() as conn:
            df = pd.read_sql(query, conn, params=params)  # <-- Tambahkan params
        return df[column_name].tolist()
    except Exception as e:
        logging.warning(f"Gagal fetch distinct options: {e}")
        return []


def process_generic_changes(
    _engine: Engine, config: dict, original_df: pd.DataFrame, changes: dict
):
    """
    Memproses perubahan CRUD menggunakan SQLAlchemy dengan transaksi aman.
    Menerima Engine, dan mengelola koneksi serta transaksi secara internal.
    """
    target_table = config.get("target_table", config.get("table_name"))
    primary_keys = config.get("primary_keys", [config.get("id_column")])

    logging.info(
        f"Processing changes for table: {target_table} with PKs: {primary_keys}"
    )

    # Helper function untuk memastikan nilai bukan tipe numpy agar kompatibel dengan DB driver
    def to_native(val):
        return val.item() if isinstance(val, np.generic) else val

    try:
        with _engine.begin() as conn:
            # --- 1. DELETE ---
            if "deleted_rows" in changes and changes["deleted_rows"]:
                for index in changes["deleted_rows"]:
                    row_to_delete = original_df.iloc[index]

                    where_clauses = [
                        f"{pk} = :pk_{i}" for i, pk in enumerate(primary_keys)
                    ]
                    where_sql = " AND ".join(where_clauses)

                    params = {
                        f"pk_{i}": to_native(row_to_delete[pk])
                        for i, pk in enumerate(primary_keys)
                    }

                    stmt = text(f"DELETE FROM {target_table} WHERE {where_sql}")
                    conn.execute(stmt, params)

            # --- 2. INSERT ---
            if "added_rows" in changes and changes["added_rows"]:
                for new_row in changes["added_rows"]:
                    valid_cols = [
                        col
                        for col in new_row.keys()
                        if col in original_df.columns and new_row[col] is not None
                    ]
                    if not valid_cols:
                        continue

                    cols_sql = ", ".join(valid_cols)
                    placeholders = ", ".join([f":{col}" for col in valid_cols])

                    params = {col: to_native(new_row[col]) for col in valid_cols}

                    stmt = text(
                        f"INSERT INTO {target_table} ({cols_sql}) VALUES ({placeholders})"
                    )
                    conn.execute(stmt, params)

            # --- 3. UPDATE ---
            if "edited_rows" in changes and changes["edited_rows"]:
                for index, updates in changes["edited_rows"].items():
                    original_row = original_df.iloc[int(index)]

                    set_clauses = []
                    params = {}

                    for col, val in updates.items():
                        set_clauses.append(f"{col} = :val_{col}")
                        params[f"val_{col}"] = to_native(val)

                    set_sql = ", ".join(set_clauses)

                    where_clauses = []
                    for i, pk in enumerate(primary_keys):
                        where_clauses.append(f"{pk} = :pk_{i}")
                        params[f"pk_{i}"] = to_native(original_row[pk])

                    where_sql = " AND ".join(where_clauses)

                    stmt = text(
                        f"UPDATE {target_table} SET {set_sql} WHERE {where_sql}"
                    )
                    conn.execute(stmt, params)

        logging.info(f"Successfully committed all changes to {target_table}.")

    except SQLAlchemyError as e:
        logging.error(f"SQLAlchemy Error processing changes for {target_table}: {e}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected Error processing changes for {target_table}: {e}")
        raise e


# def fetch_table_data(conn, source_view: str) -> pd.DataFrame:
#     """
#     Mengambil data dari tabel ATAU view yang ditentukan.

#     Args:
#         conn: Koneksi database yang aktif.
#         source_view (str): Nama tabel yang akan diambil datanya.

#     Returns:
#         pd.DataFrame: DataFrame berisi data dari tabel.
#     """
#     logging.info(f"Fetching data from table: {source_view}...")
#     try:
#         query = f"SELECT * FROM {source_view} ORDER BY 1 DESC;"
#         df = pd.read_sql(query, conn)

#         for col in df.columns:
#             if "tanggal" in col or "_date" in col:
#                 if pd.api.types.is_datetime64_any_dtype(df[col]):
#                     df[col] = pd.to_datetime(df[col]).dt.date

#         logging.info(f"Successfully fetched {len(df)} rows from {source_view}.")
#         return df
#     except Exception as e:
#         logging.error(f"Failed to fetch data from {source_view}: {e}")
#         return pd.DataFrame()


# def process_generic_changes(
#     conn, config: dict, original_df: pd.DataFrame, changes: dict
# ):
#     """
#     Memproses perubahan CRUD. Cerdas membaca 'target_table' dari config.
#     Memproses semua perubahan (tambah, edit, hapus) dari st.data_editor.
#     Fungsi ini cerdas dan bisa menangani Primary Key tunggal maupun ganda (composite).

#     Args:
#         conn: Koneksi database yang aktif.
#         config (dict): Blueprint/konfigurasi untuk tabel yang sedang diproses.
#         original_df (pd.DataFrame): DataFrame asli sebelum diedit oleh pengguna.
#         changes (dict): Dictionary perubahan yang dihasilkan oleh st.data_editor.
#     """
#     cursor = conn.cursor()
#     target_table = config.get("target_table", config.get("table_name"))
#     primary_keys = config.get("primary_keys", [config.get("id_column")])

#     logging.info(
#         f"Processing changes for table: {target_table} with PKs: {primary_keys}"
#     )

#     try:
#         if "deleted_rows" in changes and changes["deleted_rows"]:
#             for index in changes["deleted_rows"]:
#                 row_to_delete = original_df.iloc[index]
#                 where_clauses = [f"{key} = %s" for key in primary_keys]
#                 where_sql = " AND ".join(where_clauses)

#                 pk_values = tuple(row_to_delete[key] for key in primary_keys)

#                 logging.debug(
#                     f"Deleting from {target_table} where {where_sql} with values {pk_values}"
#                 )
#                 cursor.execute(
#                     f"DELETE FROM {target_table} WHERE {where_sql}", pk_values
#                 )

#         if "added_rows" in changes and changes["added_rows"]:
#             for new_row in changes["added_rows"]:
#                 columns = [
#                     col
#                     for col in new_row.keys()
#                     if col in original_df.columns and new_row[col] is not None
#                 ]
#                 if not columns:
#                     continue

#                 placeholders = ", ".join(["%s"] * len(columns))
#                 column_names = ", ".join(columns)
#                 values = tuple(new_row[col] for col in columns)

#                 query = f"INSERT INTO {target_table} ({column_names}) VALUES ({placeholders})"
#                 logging.debug(
#                     f"Inserting into {target_table} with query: {query} and values {values}"
#                 )
#                 cursor.execute(query, values)

#         if "edited_rows" in changes and changes["edited_rows"]:
#             for index, updates in changes["edited_rows"].items():
#                 original_row = original_df.iloc[int(index)]

#                 # Buat klausa SET secara dinamis
#                 set_clauses = [f"{key} = %s" for key in updates.keys()]
#                 set_sql = ", ".join(set_clauses)

#                 # Buat klausa WHERE secara dinamis
#                 where_clauses = [f"{key} = %s" for key in primary_keys]
#                 where_sql = " AND ".join(where_clauses)

#                 # Gabungkan nilai untuk SET dan WHERE
#                 update_values = list(updates.values())
#                 pk_values = [original_row[key] for key in primary_keys]

#                 query = f"UPDATE {target_table} SET {set_sql} WHERE {where_sql}"
#                 params = tuple(update_values + pk_values)

#                 logging.debug(
#                     f"Updating {target_table} with query: {query} and params {params}"
#                 )
#                 cursor.execute(query, params)

#         conn.commit()
#         logging.info(f"Successfully committed changes to {target_table}.")

#     except Exception as e:
#         conn.rollback()  # Batalkan semua perubahan jika terjadi error
#         logging.error(
#             f"Error processing changes for {target_table}. Transaction rolled back. Error: {e}"
#         )
#         raise e  # Lemparkan error agar bisa ditangkap oleh UI
#     finally:
#         cursor.close()


# def process_generic_changes(
#     conn,
#     config: dict,
#     original_df: pd.DataFrame,
#     changes: dict,
# ):
#     """
#     Memproses perubahan CRUD menggunakan st.connection (SQLAlchemy).
#     ... (Docstring lainnya sama) ...
#     """
#     target_table = config.get("target_table", config.get("table_name"))
#     primary_keys = config.get("primary_keys", [config.get("id_column")])

#     logging.info(
#         f"Processing changes for table: {target_table} with PKs: {primary_keys}"
#     )

#     with conn.session as s:
#         try:
#             # --- DELETE ---
#             if "deleted_rows" in changes and changes["deleted_rows"]:
#                 for index in changes["deleted_rows"]:
#                     row_to_delete = original_df.iloc[index]

#                     where_clauses = [f"{key} = :pk_{key}" for key in primary_keys]
#                     where_sql = " AND ".join(where_clauses)

#                     pk_dict = {f"pk_{key}": row_to_delete[key] for key in primary_keys}

#                     logging.debug(
#                         f"Deleting from {target_table} where {where_sql} with values {pk_dict}"
#                     )
#                     s.execute(
#                         text(f"DELETE FROM {target_table} WHERE {where_sql}"), pk_dict
#                     )

#             # --- ADD (INSERT) ---
#             if "added_rows" in changes and changes["added_rows"]:
#                 for new_row in changes["added_rows"]:
#                     filtered_row = {
#                         col: val
#                         for col, val in new_row.items()
#                         if col in original_df.columns and val is not None
#                     }
#                     if not filtered_row:
#                         continue

#                     column_names = ", ".join(filtered_row.keys())
#                     placeholders = ", ".join([f":{col}" for col in filtered_row.keys()])

#                     query = f"INSERT INTO {target_table} ({column_names}) VALUES ({placeholders})"
#                     logging.debug(
#                         f"Inserting into {target_table} with query: {query} and values {filtered_row}"
#                     )

#                     s.execute(text(query), filtered_row)

#             # --- EDIT (UPDATE) ---
#             if "edited_rows" in changes and changes["edited_rows"]:
#                 for index, updates in changes["edited_rows"].items():
#                     original_row = original_df.iloc[int(index)]

#                     set_clauses = [f"{key} = :set_{key}" for key in updates.keys()]
#                     set_sql = ", ".join(set_clauses)

#                     where_clauses = [f"{key} = :pk_{key}" for key in primary_keys]
#                     where_sql = " AND ".join(where_clauses)

#                     set_dict = {f"set_{key}": val for key, val in updates.items()}
#                     pk_dict = {f"pk_{key}": original_row[key] for key in primary_keys}
#                     params_dict = {**set_dict, **pk_dict}

#                     query = f"UPDATE {target_table} SET {set_sql} WHERE {where_sql}"
#                     logging.debug(
#                         f"Updating {target_table} with query: {query} and params {params_dict}"
#                     )
#                     s.execute(text(query), params_dict)

#             s.commit()
#             logging.info(f"Successfully committed changes to {target_table}.")

#         except Exception as e:
#             # 6. Rollback jika ada error
#             s.rollback()
#             logging.error(
#                 f"Error processing changes for {target_table}. Transaction rolled back. Error: {e}"
#             )
#             raise e
