import streamlit as st

from database.db_connection import get_connection
from views.render_pages import render_order_flag_editor

conn = get_connection()
if conn:
    render_order_flag_editor(conn=conn)
    conn.close()
else:
    st.error("Tidak dapat terhubung ke database.")
