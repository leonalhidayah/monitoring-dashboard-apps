import logging
from datetime import date
from typing import List, Optional

import pandas as pd
import streamlit as st
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError


@st.cache_data(ttl=3600, show_spinner=False)
def get_mart_budget_plan(
    _engine: Engine, project_names: list[str], start_date: date, end_date: date
) -> pd.DataFrame:
    """
    Mengambil data Budget Plan yang SUDAH DIPIVOT (matang) dari Data Mart.
    """
    if not project_names:
        return pd.DataFrame()

    query = """
        SELECT 
            project_name AS "Project", -- Alias agar konsisten
            parameter_name AS "Parameter",
            target_rasio_persen AS "Target Rasio",
            "Target Kuartal",
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
            tahun AS "Tahun",
            kuartal AS "Kuartal"
        FROM 
            mart_finance_budget_plan
        WHERE 
            project_name IN :project_names
            AND "report_date" BETWEEN DATE_TRUNC('month', :start_date ::date) 
                        AND DATE_TRUNC('month', :end_date ::date)
        ORDER BY
            project_name,
            parameter_name;
    """
    try:
        params = {
            "project_names": tuple(project_names),
            "start_date": start_date,
            "end_date": end_date,
        }
        with _engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        return df

    except SQLAlchemyError as e:
        logging.error(f"Gagal mengambil data budget plan dari MART: {e}")
        st.error(f"Database error (Mart Budget Plan): {e}")
        return pd.DataFrame()


# --- FUNGSI MART UNTUK CASHFLOW MONITORING ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_mart_monitoring_cashflow(
    _engine: Engine, project_names: list[str], start_date: date, end_date: date
) -> pd.DataFrame:
    """
    Mengambil data monitoring cashflow dari Data Mart (Materialized View).
    """
    if not project_names:
        return pd.DataFrame()

    query = """
        SELECT 
            "Project", 
            "Tahun", 
            "Bulan",
            "Kuartal",
            "Parameter Budget",
            "Maksimal Budget (Plan)",
            "Total Realisasi (Actual)",
            "Sisa Budget",
            "Persentase Terpakai",
            "Status"
        FROM mart_monitoring_cashflow
        WHERE 
            "Project" IN :project_names
            AND "report_date" BETWEEN DATE_TRUNC('month', :start_date ::date) 
                        AND DATE_TRUNC('month', :end_date ::date)
        ORDER BY
            "Tahun", 
            TO_DATE("Bulan", 'FMMonth'),
            "Parameter Budget";
    """
    try:
        params = {
            "project_names": tuple(project_names),
            "start_date": start_date,
            "end_date": end_date,
        }
        with _engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        return df

    except SQLAlchemyError as e:
        logging.error(f"Gagal mengambil data monitoring report dari MART: {e}")
        st.error(f"Database error (Mart Cashflow): {e}")
        return pd.DataFrame()


# --- FUNGSI MART UNTUK ADS SUMMARY ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_mart_budget_ads_summary(
    _engine: Engine,
    project_names: list[str],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> pd.DataFrame:
    """
    Mengambil data summary budget ads dari Data Mart (Materialized View).
    """
    if not project_names:
        return pd.DataFrame()

    try:
        params = {}
        where_clauses = ["project_name IN :p_names"]
        params["p_names"] = tuple(project_names)

        if start_date:
            where_clauses.append("tanggal >= :s_date")
            params["s_date"] = start_date

        if end_date:
            where_clauses.append("tanggal <= :e_date")
            params["e_date"] = end_date

        where_sql = " AND ".join(where_clauses)

        sql_query = f"SELECT * FROM mart_budget_ads_summary WHERE {where_sql} ORDER BY tanggal DESC;"

        with _engine.connect() as conn:
            df = pd.read_sql(text(sql_query), conn, params=params)
        return df

    except SQLAlchemyError as error:
        logging.error(f"Error fetching ads summary from MART: {error}")
        st.error(f"Database error (Mart Ads Summary): {error}")
        return pd.DataFrame()


# --- FUNGSI MART UNTUK ADS RATIO ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_mart_marketing_ads_ratio(
    _engine: Engine, project_names: List[str], start_date: date, end_date: date
) -> pd.DataFrame:
    """
    Mengambil data target rasio 'Biaya Marketing (Ads)' dari
    MART mart_monitoring_cashflow (yang sudah di-upgrade).
    """
    if not project_names:
        return pd.DataFrame()

    query = """
        SELECT 
            "Project" as project_name,
            "Tahun" as tahun,
            "Bulan" as bulan,
            "Kuartal" as kuartal,
            "Parameter Budget" as parameter_name,
            "Target Rasio (%)" as target_rasio_persen
        FROM 
            mart_monitoring_cashflow
        WHERE 
            "Project" IN :project_names
            AND "Parameter Budget" = 'Biaya Marketing (Ads)'
            AND "report_date" BETWEEN DATE_TRUNC('month', :start_date ::date) 
                        AND DATE_TRUNC('month', :end_date ::date)
    """
    try:
        params = {
            "project_names": tuple(project_names),
            "start_date": start_date,
            "end_date": end_date,
        }
        with _engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)
        return df

    except SQLAlchemyError as e:
        logging.error(f"Error fetching marketing ads ratio from MART: {e}")
        st.error(f"Database error (Mart Ads Ratio): {e}")
        return pd.DataFrame()
