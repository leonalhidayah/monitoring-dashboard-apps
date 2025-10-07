import streamlit as st

from views.render_pages import (
    display_advertiser_dashboard,
)

st.set_page_config(layout="wide")
PROJECT_NAME = "Juwara Herbal"

st.header(f"Dashboard Advertiser Marketplace {PROJECT_NAME}")

# load_css()
st.divider()
# mp_tab, cpas_tab = st.tabs(["Marketplace", "CPAS"])

# with mp_tab:
display_advertiser_dashboard(project_name=PROJECT_NAME)

# with cpas_tab:
#     display_advertiser_cpas_dashboard(project_name=PROJECT_NAME)
