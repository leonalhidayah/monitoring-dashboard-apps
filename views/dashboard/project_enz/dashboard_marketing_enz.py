import streamlit as st

from views.render_pages import display_marketing_dashboard

st.set_page_config(layout="wide")

PROJECT_ID = 3
PROJECT_NAME = "Enzhico"

display_marketing_dashboard(project_id=PROJECT_ID, project_name=PROJECT_NAME)
