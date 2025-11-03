import streamlit as st

from views.config import ADV_CPAS_MAP_PROJECT, ADV_MP_MAP_PROJECT
from views.render_pages import render_cpas_page, render_marketplace_page
from views.style import load_css

load_css()

project_name = "HPI"

tab1, tab2 = st.tabs(["Marketplace", "CPAS"])

with tab1:
    render_marketplace_page(project_name, ADV_MP_MAP_PROJECT[project_name])

with tab2:
    render_cpas_page(project_name, ADV_CPAS_MAP_PROJECT[project_name])
