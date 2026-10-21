"""Table formatting shared by the views."""
import streamlit as st

from app.metrics import DATE_COLUMNS

MONEY_COLUMNS = ('Amount', 'Pending', 'Running pending')


def column_config() -> dict:
    """Two-decimal amounts and ISO dates (a missing date shows blank)."""
    cfg = {c: st.column_config.NumberColumn(format='%.2f') for c in MONEY_COLUMNS}
    cfg.update({c: st.column_config.DateColumn(format='YYYY-MM-DD') for c in DATE_COLUMNS})
    return cfg
