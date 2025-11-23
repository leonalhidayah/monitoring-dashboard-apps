import streamlit as st

from views.renderer.dashboard_marketing import display_marketing_dashboard

st.set_page_config(layout="wide")

PROJECT_ID = 6
PROJECT_NAME = "HPI"

display_marketing_dashboard(project_id=PROJECT_ID, project_name=PROJECT_NAME)
