from datetime import datetime

import pandas as pd
import streamlit as st

from data_preprocessor.utils import get_quarter_months
from database import db_manager
from views.style import load_css

st.set_page_config(layout="wide")

load_css()

st.header("🎯 Generator Budget Plan Kuartalan (Multi-Project)")

# --- 1. PILIH PERIODE ---
now = datetime.now()
months, q = get_quarter_months(now.month)
tahun = now.year
st.info(
    f"Anda sedang membuat budget plan untuk Kuartal {q} {tahun} ({', '.join(months)})."
)

# --- Ambil Daftar Project dari Database ---
try:
    projects_df = db_manager.get_dim_projects()
    project_list = projects_df["project_name"].tolist()
except Exception as e:
    st.error(f"Gagal memuat daftar project dari database: {e}")
    project_list = []

if not project_list:
    st.warning(
        "Tidak ada data project yang ditemukan. Mohon tambahkan project terlebih dahulu."
    )
    st.stop()

# --- 2. BUAT TABS UNTUK SETIAP PROJECT ---
project_tabs = st.tabs(project_list)
all_project_configs = {}

for i, project_name in enumerate(project_list):
    with project_tabs[i]:
        st.subheader(f"Konfigurasi untuk: {project_name}")
        config = {"ratios": {}}

        # --- MODIFIKASI 1: PRATINJAU REAL-TIME ---
        target_val = st.number_input(
            "Target Omset Kuartalan (Rp)",
            min_value=0,
            step=1_000_000,
            key=f"target_{project_name}",
        )
        config["target_quarter"] = target_val
        if target_val > 0:
            st.caption(f"↳ Pratinjau: Rp {target_val:,.0f}")
        # --- AKHIR MODIFIKASI 1 ---

        st.markdown("---")
        st.markdown("**Alokasi Rasio Budget (%)**")

        c1, c2 = st.columns(2)
        with c1:
            config["ratios"]["HPP"] = st.number_input(
                "HPP (%)", value=20.0, step=1.0, key=f"hpp_{project_name}"
            )
            config["ratios"]["Biaya Admin"] = st.number_input(
                "Biaya Admin (%)", value=20.0, step=1.0, key=f"admin_{project_name}"
            )
            config["ratios"]["Biaya Marketing (Ads)"] = st.number_input(
                "Biaya Marketing (Ads) (%)",
                value=25.0,
                step=1.0,
                key=f"ads_{project_name}",
            )
            config["ratios"]["Biaya Marketing (Non Ads)"] = st.number_input(
                "Biaya Marketing (Non Ads) (%)",
                value=5.0,
                step=1.0,
                key=f"nonads_{project_name}",
            )
        with c2:
            config["ratios"]["Personal Expense"] = st.number_input(
                "Personal Expense (%)",
                value=10.0,
                step=1.0,
                key=f"personal_{project_name}",
            )
            config["ratios"]["Administrasi dan Umum"] = st.number_input(
                "Administrasi dan Umum (%)",
                value=5.0,
                step=1.0,
                key=f"umum_{project_name}",
            )
            config["ratios"]["Estimasi Ebit/Net Profit"] = st.number_input(
                "Estimasi Ebit/Net Profit (%)",
                value=15.0,
                step=1.0,
                key=f"ebit_{project_name}",
            )

        total_ratio = sum(config["ratios"].values())
        if total_ratio != 100:
            st.error(
                f"Total Rasio untuk {project_name} harus 100% (Saat ini: {total_ratio:.2f}%)"
            )
        else:
            st.success(f"Total Rasio untuk {project_name}: {total_ratio:.2f}%")

        all_project_configs[project_name] = config

# --- 3. TOMBOL SUBMIT DI LUAR TABS ---
st.divider()

if st.button(
    "🚀 Generate & Simpan Semua Budget Plan", use_container_width=True, type="primary"
):
    all_data_to_save = []
    is_valid = True

    for project_name, config in all_project_configs.items():
        total_ratio = sum(config["ratios"].values())
        if total_ratio != 100:
            st.error(
                f"Gagal: Total Rasio untuk project **{project_name}** bukan 100%. Mohon perbaiki di Tab-nya."
            )
            is_valid = False
            break

        target_quarter = config["target_quarter"]
        if target_quarter > 0:
            target_monthly = target_quarter / 3
            all_data_to_save.append(
                [project_name, "Target Omset", 0, target_quarter] + [target_monthly] * 3
            )
            for param, ratio in config["ratios"].items():
                row = [project_name, param, ratio, target_quarter * (ratio / 100)] + [
                    target_monthly * (ratio / 100)
                ] * 3
                all_data_to_save.append(row)

    if is_valid and all_data_to_save:
        df = pd.DataFrame(
            all_data_to_save,
            columns=["Project", "Parameter", "Target Rasio", "Target Kuartal"] + months,
        )
        df["Tahun"] = tahun
        df["Kuartal"] = q

        df_long = df.melt(
            id_vars=[
                "Project",
                "Parameter",
                "Target Rasio",
                "Target Kuartal",
                "Tahun",
                "Kuartal",
            ],
            var_name="Bulan",
            value_name="Target Bulanan",
        )

        st.subheader("📊 Pratinjau Budget Plan Gabungan")

        # --- MODIFIKASI 2: FORMAT TABEL ---
        formatters = {"Target Rasio": "{:.2f}%", "Target Kuartal": "Rp {:,.0f}"}
        for month in months:
            formatters[month] = "Rp {:,.0f}"

        st.dataframe(df.style.format(formatters, na_rep="-"), width="stretch")
        result = db_manager.insert_budget_plan(df_long)
        if result["status"] == "success":
            st.success("✅ Semua budget plan berhasil disimpan!")
        else:
            st.error(f"Gagal menyimpan: {result['message']}")
        st.balloons()
    elif is_valid and not all_data_to_save:
        st.warning("Tidak ada target omset yang diisi. Tidak ada data untuk disimpan.")
