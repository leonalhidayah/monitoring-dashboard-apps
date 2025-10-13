import streamlit as st

from data_preprocessor.utils import fetch_data
from database.db_connection import get_connection
from views.render_pages import render_team_regular_tab

TEAM_NAME_TO_RENDER = "ZYY x JUW"

st.title(f"Data Management ADV & CS: Tim {TEAM_NAME_TO_RENDER}")

conn = get_connection()
if conn:
    if "full_df" not in st.session_state:
        st.session_state.full_df = fetch_data(conn)

    render_team_regular_tab(
        team_name=TEAM_NAME_TO_RENDER, full_df=st.session_state.full_df, conn=conn
    )

    conn.close()
