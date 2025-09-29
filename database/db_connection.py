import socket

import psycopg2
import streamlit as st


def get_connection():
    """Membuat koneksi ke database Supabase via Connection Pooler (IPv4 + SSL)."""

    # Paksa resolusi DNS ke IPv4 (hindari error IPv6)
    orig_getaddrinfo = socket.getaddrinfo

    def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
        return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

    socket.getaddrinfo = getaddrinfo_ipv4

    try:
        conn = psycopg2.connect(
            **st.secrets["database"], connect_timeout=10, sslmode="require"
        )
        return conn
    except Exception as e:
        st.error(f"Gagal koneksi ke database Supabase Pooler: {e}")
        return None
