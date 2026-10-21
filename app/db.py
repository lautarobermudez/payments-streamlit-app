"""Database access. Every connection is read-only, so the app cannot change data even by mistake."""
import os

import pandas as pd
import psycopg
import streamlit as st

DEFAULT_DSN = 'postgresql://payments:payments@localhost:5432/payments'   # matches the Docker setup of payments-data-platform


def dsn() -> str:
    return os.environ.get('DATABASE_URL', DEFAULT_DSN)


def connect() -> psycopg.Connection:
    """Open a connection whose transactions are read-only: PostgreSQL itself rejects any write."""
    con = psycopg.connect(dsn())
    con.read_only = True
    return con


@st.cache_data(ttl=60, show_spinner=False)
def query(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Run a SELECT and return a DataFrame. Results are cached for 60 seconds."""
    with connect() as con, con.cursor() as cur:
        cur.execute(sql, params or {})
        return pd.DataFrame(cur.fetchall(), columns=[c.name for c in cur.description])
