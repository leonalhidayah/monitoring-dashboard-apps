import streamlit as st

from database import db_manager

st.title("Hello, Welcome!")


dim_marketplaces = db_manager.get_dim_marketplaces()
st.dataframe(dim_marketplaces)

dim_stores = db_manager.get_dim_stores()
st.dataframe(dim_stores)

dim_brands = db_manager.get_dim_brands()
st.dataframe(dim_brands)

customers = db_manager.get_customers()
st.dataframe(customers.head(20))

products = db_manager.get_products()[["sku", "product_id"]]
st.dataframe(products.head(20))

dim_shipping_services = db_manager.get_dim_shipping_services()
st.dataframe(dim_shipping_services)

dim_payment_methods = db_manager.get_dim_payment_methods()
st.dataframe(dim_payment_methods)
