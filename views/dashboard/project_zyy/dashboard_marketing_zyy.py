import streamlit as st

from views.render_pages import display_marketing_dashboard

st.set_page_config(layout="wide")

PROJECT_ID = 1
PROJECT_NAME = "Zhi Yang Yao"

display_marketing_dashboard(project_id=PROJECT_ID, project_name=PROJECT_NAME)
