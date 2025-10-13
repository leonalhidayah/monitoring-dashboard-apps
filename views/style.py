import streamlit as st


def load_css():
    st.markdown(
        """
        <style>
        button[data-baseweb="tab"] {
            font-size: 18px;
            width: 100%;
            justify-content: center !important;
            text-align: center !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_rupiah(x):
    return f"Rp {x:,.0f}"


def format_percent(x):
    return f"{x * 100:.2f}%"
