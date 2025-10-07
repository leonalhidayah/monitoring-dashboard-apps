import streamlit as st

from views.render_pages import display_admin_dashboard

st.set_page_config(layout="wide")

PROJECT_NAME = "Zhi Yang Yao"

display_admin_dashboard(project_name=PROJECT_NAME)
