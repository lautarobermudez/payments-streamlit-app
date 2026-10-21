import streamlit as st

from app import metrics, queries
from app.filters import Filters


def render(f: Filters) -> None:
    st.header('Supplier statement')
    names = queries.suppliers(f.company, f.text)
    if not names:
        st.info('No suppliers match the filters.')
        return
    supplier = st.selectbox('Supplier', names, help='The list follows the company and the text in the sidebar.')
    stm = queries.statement(supplier, f.company)
    k = metrics.statement_kpis(stm)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Orders', k['orders'])
    c2.metric('Total (without cancelled)', metrics.money(k['total']))
    c3.metric('Paid', metrics.money(k['paid']))
    c4.metric('Pending', metrics.money(k['pending']))
    st.dataframe(metrics.label_columns(stm), width='stretch', hide_index=True, height=420,
                 column_config={c: st.column_config.NumberColumn(format='%.2f')
                                for c in ('Amount', 'Pending', 'Running pending')})
