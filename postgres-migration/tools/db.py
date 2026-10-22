# tools/db.py
# One place for the Postgres connection.
# Reads DATABASE_URL from Streamlit secrets (cloud) or .env (local).

import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    try:
        import streamlit as st
        return st.secrets["DATABASE_URL"]
    except Exception:
        url = os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError(
                "DATABASE_URL is not set. Add it to "
                ".env (local) or Streamlit secrets (cloud)."
            )
        return url


@contextmanager
def get_conn():
    """Open a connection, commit on success, roll back on error."""
    conn = psycopg.connect(
        get_database_url(),
        row_factory=dict_row,
        connect_timeout=10,
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
