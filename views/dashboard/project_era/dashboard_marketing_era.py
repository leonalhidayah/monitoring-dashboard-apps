import streamlit as st

from views.renderer.dashboard_marketing import display_marketing_dashboard

st.set_page_config(layout="wide")

PROJECT_ID = 5
PROJECT_NAME = "Erassgo"

display_marketing_dashboard(project_id=PROJECT_ID, project_name=PROJECT_NAME)
