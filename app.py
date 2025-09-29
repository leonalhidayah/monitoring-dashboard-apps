import streamlit as st

# --- PAGE SETUP ---
# HOME PAGE
home_page = st.Page(
    page="views/home.py",
    title="Hi There!",
    icon=":material/home:",
    default=True,
)

# DASHBOARD PAGE
monitoring_dashboard_page = st.Page(
    page="views/monitoring.py",
    title="Monitoring Dashboard",
    icon=":material/analytics:",
)

advertiser_dashboard_page = st.Page(
    page="views/dashboard_advertiser.py",
    title="Advertiser Dashboard",
    icon=":material/analytics:",
)

# DATA ENTRY PAGE
entry_advertiser_page = st.Page(
    page="views/data_entry_advertiser.py",
    title="Advertiser",
    icon=":material/campaign:",
)

entry_admin_page = st.Page(
    page="views/data_entry_admin.py",
    title="Admin",
    icon=":material/manage_accounts:",
)

entry_finance_page = st.Page(
    page="views/data_entry_finance.py",
    title="Finance",
    icon=":material/finance_chip:",
)

entry_stock_page = st.Page(
    page="views/data_entry_stock.py",
    title="Stock",
    icon=":material/package_2:",
)


# # --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[home_page, dashboard_page])

# --- NAVIGATION SETUP [WITH SECTIONS] ---
pg = st.navigation(
    {
        "Home": [home_page],
        "Dashboard": [advertiser_dashboard_page],
        "Menu": [
            entry_advertiser_page,
            entry_admin_page,
            entry_stock_page,
            entry_finance_page,
        ],
    }
)

# --- SHARED ON ALL PAGES
# st.logo("path to your logo") # logo perusahaan di sidebar
st.sidebar.text("Made with ❤️ by AMS Corp")

# -- RUN NAVIGATION ---
pg.run()
