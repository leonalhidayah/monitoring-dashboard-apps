import streamlit as st
import streamlit_authenticator as stauth

from database.db_connection import get_connection

# 1. Konfigurasi Halaman (Hanya sekali di paling atas)
st.set_page_config(
    page_title="AMS Dashboard", layout="wide", page_icon="assets/ams-logo-crop.PNG"
)

# 2. DEFINISI SEMUA HALAMAN APLIKASI
# ==============================================================================
home_page = st.Page(
    "views/home.py", title="Hi There!", icon=":material/home:", default=True
)

# Halaman Fungsional (Finance, Admin, Stock)
finance_pages = {
    "dashboard": st.Page(
        "views/dashboard/finance.py",
        title="Dashboard Finance",
        icon=":material/dashboard:",
    ),
    "budget_plan": st.Page(
        "views/finance/budget_plan.py",
        title="Budget Plan",
        icon=":material/finance_mode:",
    ),
    "omset": st.Page(
        "views/finance/omset.py",
        title="Omset",
        icon=":material/money_bag:",
    ),
    "budget_ads": st.Page(
        "views/finance/budget_ads.py",
        title="Budget Ads",
        icon=":material/campaign:",
    ),
    "budget_non_ads": st.Page(
        "views/finance/budget_non_ads.py",
        title="Budget Non Ads",
        icon=":material/campaign:",
    ),
    "cashflow": st.Page(
        "views/finance/cashflow.py",
        title="Cashflow",
        icon=":material/account_balance_wallet:",
    ),
    "finance_data_management": st.Page(
        "views/finance/finance_data_management.py",
        title="Data Management",
        icon=":material/database:",
    ),
}
admin_pages = {
    "marketplace": st.Page(
        "views/admin/admin_marketplace.py",
        title="Admin Marketplace",
        icon=":material/contacts_product:",
    ),
}

# --- HALAMAN BARU UNTUK JALUR REGULAR ---
regular_pages = {
    "entry_zyy_juw": st.Page(
        "views/regular/zyy_juw_regular.py",
        title="Entry ZYY x Juw",
        icon=":material/campaign:",
    ),
    "entry_enz_kdk": st.Page(
        "views/regular/enz_kdk_regular.py",
        title="Entry ENZ x KDK",
        icon=":material/campaign:",
    ),
    "return": st.Page(
        "views/regular/order_flag_reg_editor.py",
        title="Entry Return",
        icon=":material/assignment_return:",
    ),
    "dashboard": st.Page(
        "views/regular/dashboard_regular.py",
        title="Dashboard ADV & CS",
        icon=":material/dashboard:",
    ),
    "dashboard_budget": st.Page(
        "views/regular/dashboard_budgeting_reg.py",
        title="Dashboard Budgeting",
        icon=":material/dashboard:",
    ),
}

# PETA HALAMAN PER PROYEK (Marketplace)
PROJECT_PAGE_MAP = {
    "Zhi Yang Yao": {
        "entry_adv": st.Page(
            "views/advertiser/zyy_advertiser.py",
            title="Entry Advertiser",
            icon=":material/campaign:",
        ),
        "dash_budget": st.Page(
            "views/dashboard/project_zyy/dashboard_budgeting_zyy.py",
            title="Dashboard Budgeting",
            icon=":material/money_bag:",
        ),
        "dash_adv": st.Page(
            "views/dashboard/project_zyy/dashboard_advertiser_zyy.py",
            title="Dashboard Advertiser",
            icon=":material/ad_group:",
        ),
        "dash_admin": st.Page(
            "views/dashboard/project_zyy/dashboard_admin_zyy.py",
            title="Dashboard Admin",
            icon=":material/credit_card_heart:",
        ),
    },
    "Juwara Herbal": {
        "entry_adv": st.Page(
            "views/advertiser/juw_advertiser.py",
            title="Entry Advertiser",
            icon=":material/campaign:",
        ),
        "dash_budget": st.Page(
            "views/dashboard/project_juw/dashboard_budgeting_juw.py",
            title="Dashboard Budgeting",
            icon=":material/money_bag:",
        ),
        "dash_adv": st.Page(
            "views/dashboard/project_juw/dashboard_advertiser_juw.py",
            title="Dashboard Advertiser",
            icon=":material/ad_group:",
        ),
        "dash_admin": st.Page(
            "views/dashboard/project_juw/dashboard_admin_juw.py",
            title="Dashboard Admin",
            icon=":material/credit_card_heart:",
        ),
    },
    "Enzhico": {
        "entry_adv": st.Page(
            "views/advertiser/enz_advertiser.py",
            title="Entry Advertiser",
            icon=":material/campaign:",
        ),
        "dash_budget": st.Page(
            "views/dashboard/project_enz/dashboard_budgeting_enz.py",
            title="Dashboard Budgeting",
            icon=":material/money_bag:",
        ),
        "dash_adv": st.Page(
            "views/dashboard/project_enz/dashboard_advertiser_enz.py",
            title="Dashboard Advertiser",
            icon=":material/ad_group:",
        ),
        "dash_admin": st.Page(
            "views/dashboard/project_enz/dashboard_admin_enz.py",
            title="Dashboard Admin",
            icon=":material/credit_card_heart:",
        ),
    },
    "Kudaku": {
        "entry_adv": st.Page(
            "views/advertiser/kdk_advertiser.py",
            title="Entry Advertiser",
            icon=":material/campaign:",
        ),
        "dash_budget": st.Page(
            "views/dashboard/project_kdk/dashboard_budgeting_kdk.py",
            title="Dashboard Budgeting",
            icon=":material/money_bag:",
        ),
        "dash_adv": st.Page(
            "views/dashboard/project_kdk/dashboard_advertiser_kdk.py",
            title="Dashboard Advertiser",
            icon=":material/ad_group:",
        ),
        "dash_admin": st.Page(
            "views/dashboard/project_kdk/dashboard_admin_kdk.py",
            title="Dashboard Admin",
            icon=":material/credit_card_heart:",
        ),
    },
    "Erassgo": {
        "entry_adv": st.Page(
            "views/advertiser/era_advertiser.py",
            title="Entry Advertiser",
            icon=":material/campaign:",
        ),
        "dash_budget": st.Page(
            "views/dashboard/project_era/dashboard_budgeting_era.py",
            title="Dashboard Budgeting",
            icon=":material/money_bag:",
        ),
        "dash_adv": st.Page(
            "views/dashboard/project_era/dashboard_advertiser_era.py",
            title="Dashboard Advertiser",
            icon=":material/ad_group:",
        ),
        "dash_admin": st.Page(
            "views/dashboard/project_era/dashboard_admin_era.py",
            title="Dashboard Admin",
            icon=":material/credit_card_heart:",
        ),
    },
    "HPI": {
        "entry_adv": st.Page(
            "views/advertiser/hpi_advertiser.py",
            title="Entry Advertiser",
            icon=":material/campaign:",
        ),
        "dash_budget": st.Page(
            "views/dashboard/project_hpi/dashboard_budgeting_hpi.py",
            title="Dashboard Budgeting",
            icon=":material/money_bag:",
        ),
        "dash_adv": st.Page(
            "views/dashboard/project_hpi/dashboard_advertiser_hpi.py",
            title="Dashboard Advertiser",
            icon=":material/ad_group:",
        ),
        "dash_admin": st.Page(
            "views/dashboard/project_hpi/dashboard_admin_hpi.py",
            title="Dashboard Admin",
            icon=":material/credit_card_heart:",
        ),
    },
}


# 3. FUNGSI DINAMIS UNTUK MEMBANGUN NAVIGASI
# ==============================================================================
def build_navigation_for_role(role, project_names=[]):
    """Membangun dictionary navigasi berdasarkan peran dan proyek yang diakses."""
    pages = {"Home": [home_page]}

    # --- PERAN BARU UNTUK JALUR REGULAR ---
    if role == "adv_cs_regular":
        pages["Menu Regular"] = [
            regular_pages["entry_zyy_juw"],
            regular_pages["entry_enz_kdk"],
            regular_pages["dashboard"],
        ]
        return pages

    if role == "project_manager_reg":
        pages["Menu Regular"] = list(regular_pages.values())
        return pages
    # --- AKHIR PENAMBAHAN PERAN BARU ---

    # Peran-peran spesifik lainnya
    if role == "finance":
        pages["Finance"] = list(finance_pages.values())
        for proj_name, proj_pages in PROJECT_PAGE_MAP.items():
            pages[f"Budgeting {proj_name}"] = [proj_pages["dash_budget"]]
        return pages

    if role == "admin_marketplace":
        pages["Entry Data"] = [admin_pages["marketplace"]]
        for proj_name in project_names:
            if proj_name in PROJECT_PAGE_MAP:
                pages[f"Dashboard {proj_name}"] = [
                    PROJECT_PAGE_MAP[proj_name]["dash_admin"]
                ]
        return pages

    if role == "advertiser_marketplace":
        for proj_name in project_names:
            if proj_name in PROJECT_PAGE_MAP:
                pages[f"Project {proj_name}"] = [
                    PROJECT_PAGE_MAP[proj_name]["entry_adv"],
                    PROJECT_PAGE_MAP[proj_name]["dash_adv"],
                ]
        return pages

    if role == "project_manager":
        for proj_name in project_names:
            if proj_name in PROJECT_PAGE_MAP:
                pages[f"Project {proj_name}"] = [
                    PROJECT_PAGE_MAP[proj_name]["entry_adv"],
                    PROJECT_PAGE_MAP[proj_name]["dash_adv"],
                    PROJECT_PAGE_MAP[proj_name]["dash_budget"],
                    PROJECT_PAGE_MAP[proj_name]["dash_admin"],
                ]
        return pages

    # Peran dengan akses luas
    all_project_pages = {
        f"Project {name}": list(pages.values())
        for name, pages in PROJECT_PAGE_MAP.items()
    }

    if role == "total_project_manager":
        pages["Admin"] = list(admin_pages.values())
        pages["Project Regular"] = list(regular_pages.values())
        pages.update(all_project_pages)
        return pages

    if role in ["owner", "superuser"]:
        pages["Finance"] = list(finance_pages.values())
        pages["Admin"] = list(admin_pages.values())
        pages["Project Regular"] = list(regular_pages.values())
        pages.update(all_project_pages)
        return pages

    return pages  # Default (hanya home) untuk peran yang tidak dikenal


# 4. FUNGSI DATABASE & AUTENTIKASI
# (Tidak ada perubahan di bagian ini)
# ==============================================================================
@st.cache_data(ttl=3600)
def fetch_users_for_auth():
    """Mengambil data pengguna untuk streamlit-authenticator."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT username, full_name, password_hash FROM users"
        cursor.execute(query)
        users = cursor.fetchall()
        credentials = {"usernames": {}}
        for user in users:
            username, name, password_hash = user
            credentials["usernames"][username] = {
                "name": name,
                "password": password_hash,
            }
        return credentials
    except Exception as e:
        st.error(f"Gagal memuat data pengguna: {e}")
        return {"usernames": {}}
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()


@st.cache_data(ttl=3600)
def get_user_details(username):
    """Mengambil role dan daftar proyek yang diakses oleh pengguna."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT r.name as role_name, p.project_name as project_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            LEFT JOIN user_projects up ON u.id = up.user_id
            LEFT JOIN dim_projects p ON up.project_id = p.project_id
            WHERE LOWER(u.username) = LOWER(%s)
        """
        cursor.execute(query, (username,))
        results = cursor.fetchall()
        if not results:
            return None, []
        user_role = results[0][0].strip().lower()
        accessible_projects = sorted(
            list({res[1] for res in results if res[1] is not None})
        )
        return user_role, accessible_projects
    except Exception as e:
        st.error(f"Gagal mengambil detail hak akses: {e}")
        return None, []
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()


# 5. LOGIKA UTAMA APLIKASI
# (Tidak ada perubahan di bagian ini)
# ==============================================================================
credentials = fetch_users_for_auth()
authenticator = stauth.Authenticate(
    credentials,
    cookie_name=st.secrets["cookie"]["name"],
    key=st.secrets["cookie"]["key"],
    cookie_expiry_days=st.secrets["cookie"]["expiry"],
)

_, col, _ = st.columns([1, 1.5, 1])
with col:
    authenticator.login()

if st.session_state["authentication_status"]:
    user_role, accessible_projects = get_user_details(st.session_state["username"])
    if user_role:
        st.session_state["role"] = user_role
        st.session_state["accessible_projects"] = accessible_projects
        nav_pages = build_navigation_for_role(user_role, accessible_projects)
        st.logo("assets/ams-logo-white-crop.PNG")
        with st.sidebar:
            st.text("Made with ❤️ by AMS Corp.")
            authenticator.logout("Logout", "sidebar")
        pg = st.navigation(nav_pages)
        pg.run()
    else:
        st.error("Gagal mendapatkan peran (role) untuk pengguna ini. Hubungi admin.")
        authenticator.logout("Logout", "main")
elif st.session_state["authentication_status"] is False:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.error("Username atau password salah!")
elif st.session_state["authentication_status"] is None:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.info("Silakan masukkan username dan password Anda")
