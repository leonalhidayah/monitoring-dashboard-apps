import bcrypt
import streamlit as st

from database.db_connection import get_connection

# 1. Konfigurasi Halaman (Hanya sekali di paling atas)
st.set_page_config(
    page_title="AMS Dashboard", layout="wide", page_icon="assets/ams-logo-crop.PNG"
)

# --- DATA & MAPPING ---
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

# --- DEFINISI HALAMAN ---
home_page = st.Page(
    "views/home.py", title="Hi There!", icon=":material/home:", default=True
)
advertiser_dashboard_page = st.Page(
    "views/dashboard_advertiser.py",
    title="Advertiser Dashboard",
    icon=":material/analytics:",
)
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
    "admin": {"Home": [home_page], "Menu": [entry_admin_page]},
    "finance": {"Home": [home_page], "Menu": [entry_finance_page]},
    "advertiser": {
        "Home": [home_page],
        "Dashboard": [advertiser_dashboard_page],
        "Menu": [entry_advertiser_page],
    },
    "stock": {"Home": [home_page], "Menu": [entry_stock_page]},
    "owner": {"Home": [home_page], "Dashboard": [advertiser_dashboard_page]},
}

SUPERUSER_PAGES = {
    "Home": [home_page],
    "Dashboards": [advertiser_dashboard_page],
    "Data Entry": [
        entry_admin_page,
        entry_finance_page,
        entry_advertiser_page,
        entry_stock_page,
    ],
}


# --- FUNGSI LOGIN ---
# --- FUNGSI LOGIN ---
def show_login_form():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.title("🗝️ Login")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input(
                "Password", type="password", placeholder="Masukkan password"
            )
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                conn = None
                cursor = None
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    query = "SELECT u.username, u.password_hash, r.name FROM users u JOIN roles r ON u.role_id = r.id WHERE u.username = %s"
                    cursor.execute(query, (username,))
                    user_record = cursor.fetchone()

                    if user_record and bcrypt.checkpw(
                        password.encode("utf-8"), user_record[1].encode("utf-8")
                    ):
                        db_username, _, db_role = user_record
                        st.session_state["logged_in"] = True
                        st.session_state["role"] = db_role
                        st.session_state["username"] = db_username
                        st.session_state["name"] = DISPLAY_NAMES.get(db_role)

                        st.rerun()
                    else:
                        st.error("Username atau password salah!")
                except Exception as e:
                    st.error(f"Terjadi kesalahan koneksi: {e}")
                finally:
                    if cursor:
                        cursor.close()
                    if conn:
                        conn.close()


# --- LOGIKA UTAMA APLIKASI ---
# Inisialisasi semua kunci session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.name = None

# Tampilkan halaman berdasarkan status login
if not st.session_state.logged_in:
    show_login_form()
else:
    user_role = st.session_state.role

    # KUNCI UTAMA: Mengambil nama dari session_state untuk ditampilkan
    display_name = st.session_state.name

    if user_role == "superuser":
        accessible_pages = SUPERUSER_PAGES
    else:
        accessible_pages = PAGE_MAPPING.get(user_role, {})

    if not accessible_pages:
        st.error("Peran Anda tidak memiliki akses ke halaman manapun.")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
    else:
        st.logo("assets/ams-logo-white-crop.PNG")
        pg = st.navigation(accessible_pages)

        with st.sidebar:
            st.text("Made with ❤️ by AMS Corp.")
            if st.button("Logout", use_container_width=True, type="primary"):
                st.session_state.clear()
                st.rerun()

        pg.run()
