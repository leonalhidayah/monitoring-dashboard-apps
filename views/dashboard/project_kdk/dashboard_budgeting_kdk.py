import streamlit as st

from views.render_pages import display_budgeting_dashboard

st.set_page_config(layout="wide")

PROJECT_ID = 4
PROJECT_NAME = "Kudaku"

display_budgeting_dashboard(project_id=PROJECT_ID, project_name=PROJECT_NAME)
