import logging

import psycopg2
import streamlit as st
from sqlalchemy import create_engine


def get_connection():
    """Membuat dan mengembalikan objek koneksi ke database."""
    return psycopg2.connect(**st.secrets["database"])


@st.cache_resource(show_spinner=False)
def get_engine():
    """
    Membuat SQLAlchemy Engine hanya sekali dengan koneksi ke Supabase Pooler.
    Pooler memastikan koneksi efisien di Streamlit & notebook.
    """
    try:
        db = st.secrets["database"]
        user = db["user"]
        password = db["password"]
        host = db["host"]
        port = db.get("port", 6543)
        dbname = db["dbname"]

        db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

        engine = create_engine(
            db_url, pool_pre_ping=True, pool_size=5, max_overflow=2, pool_recycle=1800
        )
        logging.info("✅ SQLAlchemy engine berhasil dibuat.")
        return engine

    except Exception as e:
        logging.error(f"❌ Gagal membuat engine: {e}", exc_info=True)
        raise
