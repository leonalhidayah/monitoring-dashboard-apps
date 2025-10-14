import logging

import pandas as pd

# =============================================================================
# MESIN DATABASE GENERIK
# =============================================================================
# Modul ini berisi fungsi-fungsi "otot" yang berinteraksi dengan database.
# Didesain untuk menjadi generik, artinya bisa bekerja untuk tabel apa pun
# selama diberi "blueprint" (konfigurasi) yang benar.
# =============================================================================


def fetch_table_data(conn, source_view: str) -> pd.DataFrame:
    """
    Mengambil data dari tabel ATAU view yang ditentukan.

    Args:
        conn: Koneksi database yang aktif.
        source_view (str): Nama tabel yang akan diambil datanya.

    Returns:
        pd.DataFrame: DataFrame berisi data dari tabel.
    """
    logging.info(f"Fetching data from table: {source_view}...")
    try:
        # Menggunakan ORDER BY 1 DESC sebagai default yang aman, biasanya PK atau tanggal.
        query = f"SELECT * FROM {source_view} ORDER BY 1 DESC;"
        df = pd.read_sql(query, conn)

        # Konversi otomatis kolom-kolom yang mengandung 'tanggal' atau '_date'
        # agar sesuai dengan format yang dibutuhkan Streamlit.
        for col in df.columns:
            if "tanggal" in col or "_date" in col:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = pd.to_datetime(df[col]).dt.date

        logging.info(f"Successfully fetched {len(df)} rows from {source_view}.")
        return df
    except Exception as e:
        logging.error(f"Failed to fetch data from {source_view}: {e}")
        return pd.DataFrame()  # Kembalikan DataFrame kosong jika gagal


def process_generic_changes(
    conn, config: dict, original_df: pd.DataFrame, changes: dict
):
    """
    Memproses perubahan CRUD. Cerdas membaca 'target_table' dari config.
    Memproses semua perubahan (tambah, edit, hapus) dari st.data_editor.
    Fungsi ini cerdas dan bisa menangani Primary Key tunggal maupun ganda (composite).

    Args:
        conn: Koneksi database yang aktif.
        config (dict): Blueprint/konfigurasi untuk tabel yang sedang diproses.
        original_df (pd.DataFrame): DataFrame asli sebelum diedit oleh pengguna.
        changes (dict): Dictionary perubahan yang dihasilkan oleh st.data_editor.
    """
    cursor = conn.cursor()
    target_table = config.get("target_table", config.get("table_name"))
    # Tentukan primary key, baik tunggal ('id_column') maupun ganda ('primary_keys')
    primary_keys = config.get("primary_keys", [config.get("id_column")])

    logging.info(
        f"Processing changes for table: {target_table} with PKs: {primary_keys}"
    )

    try:
        # --- 1. PROSES PENGHAPUSAN ---
        if "deleted_rows" in changes and changes["deleted_rows"]:
            for index in changes["deleted_rows"]:
                row_to_delete = original_df.iloc[index]
                where_clauses = [f"{key} = %s" for key in primary_keys]
                where_sql = " AND ".join(where_clauses)

                # Ambil nilai PK dan konversi tipe data jika perlu (misal: dari numpy.int64)
                pk_values = tuple(row_to_delete[key] for key in primary_keys)

                logging.debug(
                    f"Deleting from {target_table} where {where_sql} with values {pk_values}"
                )
                cursor.execute(
                    f"DELETE FROM {target_table} WHERE {where_sql}", pk_values
                )

        # --- 2. PROSES PENAMBAHAN ---
        if "added_rows" in changes and changes["added_rows"]:
            for new_row in changes["added_rows"]:
                # Hanya ambil kolom yang benar-benar ada di tabel dan tidak kosong
                columns = [
                    col
                    for col in new_row.keys()
                    if col in original_df.columns and new_row[col] is not None
                ]
                if not columns:
                    continue  # Lewati jika baris tambahan kosong

                placeholders = ", ".join(["%s"] * len(columns))
                column_names = ", ".join(columns)
                values = tuple(new_row[col] for col in columns)

                query = f"INSERT INTO {target_table} ({column_names}) VALUES ({placeholders})"
                logging.debug(
                    f"Inserting into {target_table} with query: {query} and values {values}"
                )
                cursor.execute(query, values)

        # --- 3. PROSES PENGEDITAN ---
        if "edited_rows" in changes and changes["edited_rows"]:
            for index, updates in changes["edited_rows"].items():
                original_row = original_df.iloc[int(index)]

                # Buat klausa SET secara dinamis
                set_clauses = [f"{key} = %s" for key in updates.keys()]
                set_sql = ", ".join(set_clauses)

                # Buat klausa WHERE secara dinamis
                where_clauses = [f"{key} = %s" for key in primary_keys]
                where_sql = " AND ".join(where_clauses)

                # Gabungkan nilai untuk SET dan WHERE
                update_values = list(updates.values())
                pk_values = [original_row[key] for key in primary_keys]

                query = f"UPDATE {target_table} SET {set_sql} WHERE {where_sql}"
                params = tuple(update_values + pk_values)

                logging.debug(
                    f"Updating {target_table} with query: {query} and params {params}"
                )
                cursor.execute(query, params)

        conn.commit()
        logging.info(f"Successfully committed changes to {target_table}.")

    except Exception as e:
        conn.rollback()  # Batalkan semua perubahan jika terjadi error
        logging.error(
            f"Error processing changes for {target_table}. Transaction rolled back. Error: {e}"
        )
        raise e  # Lemparkan error agar bisa ditangkap oleh UI
    finally:
        cursor.close()
