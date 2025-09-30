import psycopg2
import streamlit as st


def get_connection():
    """Membuat dan mengembalikan objek koneksi ke database."""
    return psycopg2.connect(**st.secrets["database"])
