"""Entry point: page configuration and navigation. Each page is a thin script in pages/ that draws the shared
sidebar filters and calls a view from app/views.

    streamlit run streamlit_app.py
"""
import streamlit as st

st.set_page_config(page_title='Payment orders', layout='wide')
st.title('Payment orders')
st.caption('Read-only explorer on synthetic data. The database refuses any write.')

st.navigation([
    st.Page('pages/orders.py', title='Orders', url_path='orders', default=True),
    st.Page('pages/statement.py', title='Supplier statement', url_path='statement'),
    st.Page('pages/due.py', title='Due dates', url_path='due'),
]).run()
