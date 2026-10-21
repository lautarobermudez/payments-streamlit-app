import datetime as dt

import streamlit as st

from app import metrics, queries, ui
from app.filters import Filters


def render(f: Filters) -> None:
    st.header('Orders')
    ops = queries.orders(f.company, f.statuses, f.text)
    if ops.empty:
        st.info('No payment orders match the filters.')
        return
    k = metrics.order_kpis(ops, dt.date.today())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Orders', f"{k['orders']:,}")
    c2.metric('Total', metrics.money(k['total']))
    c3.metric('Pending', metrics.money(k['pending']))
    c4.metric('Overdue', metrics.money(k['overdue']))

    left, right = st.columns([3, 2])
    with left:
        st.subheader('Payment orders')
        st.dataframe(metrics.label_columns(ops), width='stretch', hide_index=True, height=420,
                     column_config=ui.column_config())
    with right:
        st.subheader('Amount by month')
        st.bar_chart(metrics.monthly_totals(ops))
        st.subheader('Top suppliers')
        st.bar_chart(metrics.top_suppliers(ops), horizontal=True)
