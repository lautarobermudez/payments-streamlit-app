import streamlit as st

from app import metrics, queries, ui
from app.filters import Filters


def render(f: Filters) -> None:
    st.header('Due dates')
    days = st.slider('Show payables due within the next (days)', 7, 60, 15)
    buckets = metrics.due_buckets(queries.payables(f.company, f.text), days)
    spec = [('overdue', 'Overdue'), ('soon', f'Due in the next {days} days'), ('no_date', 'No due date loaded')]
    for col, (key, title) in zip(st.columns(3), spec):
        col.metric(f'{title} ({len(buckets[key])})', metrics.money(buckets[key].importe_total.sum()))
    for key, title in spec:
        st.subheader(title)
        if buckets[key].empty:
            st.caption('None.')
        else:
            st.dataframe(metrics.label_columns(buckets[key].drop(columns=['situacion'])), width='stretch', hide_index=True,
                         column_config=ui.column_config())
