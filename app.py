import streamlit as st
import streamlit_authenticator as stauth

from database.db_connection import get_connection

st.set_page_config(
    page_title="AMS Dashboard", layout="wide", page_icon="assets/ams-logo-crop.PNG"
)
DISPLAY_NAMES = {
    "admin": "Ademin",
    "finance": "Teh Karinnn",
    "advertiser": "A Adnan dkk",
    "stock": "Pak Herrr!",
    "superuser": "Brooow",
    "owner": "Pak Faiz",
    "manager": "Mas Junn",
    "hrd": "Pak Yoggs",
}


home_page = st.Page(
    "views/home.py", title="Hi There!", icon=":material/home:", default=True
)

# DASHBOARD
advertiser_dashboard_page = st.Page(
    "views/dashboard_advertiser.py",
    title="Advertiser Dashboard",
    icon=":material/analytics:",
)

admin_dashboard_page = st.Page(
    "views/dashboard_admin.py",
    title="Admin Dashboard",
    icon=":material/analytics:",
)

# MENU
entry_advertiser_page = st.Page(
    "views/data_entry_advertiser.py", title="Advertiser", icon=":material/campaign:"
)
entry_admin_page = st.Page(
    "views/data_entry_admin.py", title="Admin", icon=":material/manage_accounts:"
)
entry_finance_page = st.Page(
    "views/data_entry_finance.py", title="Finance", icon=":material/finance_chip:"
)
entry_stock_page = st.Page(
    "views/data_entry_stock.py", title="Stock", icon=":material/package_2:"
)

PAGE_MAPPING = {
    "admin": {
        "Home": [home_page],
        "Dashboard": [admin_dashboard_page],
        "Menu": [entry_admin_page],
    },
    "finance": {"Home": [home_page], "Menu": [entry_finance_page]},
    "advertiser": {
        "Home": [home_page],
        "Dashboard": [advertiser_dashboard_page],
        "Menu": [entry_advertiser_page],
    },
    "stock": {"Home": [home_page], "Menu": [entry_stock_page]},
    "owner": {
        "Home": [home_page],
        "Dashboard": [advertiser_dashboard_page, admin_dashboard_page],
    },
}

SUPERUSER_PAGES = {
    "Home": [home_page],
    "Dashboards": [advertiser_dashboard_page, admin_dashboard_page],
    "Data Entry": [
        entry_admin_page,
        entry_finance_page,
        entry_advertiser_page,
        entry_stock_page,
    ],
}


def fetch_users_from_db():
    """
    Mengambil data pengguna dari database dan mengubahnya menjadi format
    yang dibutuhkan oleh streamlit-authenticator.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT u.username, u.password_hash, r.name FROM users u JOIN roles r ON u.role_id = r.id"
        cursor.execute(query)
        users = cursor.fetchall()

        credentials = {"usernames": {}}
        for user in users:
            username, password_hash, role_name = user
            user_display_name = DISPLAY_NAMES.get(role_name, username)

            credentials["usernames"][username] = {
                "name": user_display_name,
                "password": password_hash,
            }

        return credentials
    except Exception as e:
        st.error(f"Gagal terhubung ke database: {e}")
        return {"usernames": {}}
    finally:
        if "cursor" in locals() and cursor is not None:
            cursor.close()
        if "conn" in locals() and conn is not None:
            conn.close()


def get_user_role(username):
    """Mendapatkan role dari user yang berhasil login (case-insensitive)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT r.name FROM roles r JOIN users u ON r.id = u.role_id WHERE LOWER(u.username) = %s"

        cursor.execute(query, (username.lower(),))

        result = cursor.fetchone()

        if result:
            return result[0].strip().lower()
        return None

    finally:
        if "cursor" in locals() and cursor:
            cursor.close()
        if "conn" in locals() and conn:
            conn.close()


credentials = fetch_users_from_db()

# 2. Inisialisasi authenticator
# Ganti 'some_random_string' dengan secret key Anda sendiri!
authenticator = stauth.Authenticate(
    credentials,
    cookie_name=st.secrets["cookie"]["name"],
    key=st.secrets["cookie"]["key"],
    cookie_expiry_days=st.secrets["cookie"]["expiry"],
)

_, col, _ = st.columns([1, 1.5, 1])
with col:
    authenticator.login()

# 4. Logika setelah login
if st.session_state["authentication_status"]:
    user_role = get_user_role(st.session_state["username"])

    if user_role == "superuser":
        accessible_pages = SUPERUSER_PAGES
    else:
        accessible_pages = PAGE_MAPPING.get(user_role, {})

    if not accessible_pages:
        st.error("Peran Anda tidak memiliki akses ke halaman manapun.")
        with st.sidebar:
            authenticator.logout("Logout", "sidebar")
    else:
        st.logo("assets/ams-logo-white-crop.PNG")

        with st.sidebar:
            st.text("Made with ❤️ by AMS Corp.")
            authenticator.logout("Logout", "sidebar", key="unique_logout_button")
            # st.divider()

        pg = st.navigation(accessible_pages)
        pg.run()

elif st.session_state["authentication_status"] is False:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.error("Username atau password salah!")

elif st.session_state["authentication_status"] is None:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.info("Silakan masukkan username dan password Anda")
