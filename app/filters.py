"""Sidebar filters shared by every page. The widget keys keep the values when the user changes page."""
from dataclasses import dataclass

import streamlit as st

from app import queries
from app.metrics import STATUS_LABELS


@dataclass(frozen=True)
class Filters:
    company: str
    statuses: list[str]
    text: str


def sidebar() -> Filters:
    st.sidebar.header('Filters')
    company = st.sidebar.selectbox('Company', [queries.ALL] + queries.companies(), key='company')
    statuses = st.sidebar.multiselect('Status', list(STATUS_LABELS), default=['pendiente', 'pagada'],
                                      format_func=STATUS_LABELS.get, help='Applies to the Orders page.', key='statuses')
    text = st.sidebar.text_input('Supplier contains', placeholder='e.g. Sierra', key='text')
    return Filters(company, statuses or ['pendiente'], text)
