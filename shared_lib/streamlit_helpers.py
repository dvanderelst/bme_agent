"""
Streamlit-specific wrappers shared between the chatbot and survey apps.

Kept separate from shared_lib.postgres_logger so that module stays
framework-agnostic — anything that imports streamlit lives here.
"""

import streamlit as st

from shared_lib.postgres_logger import get_postgres_client


@st.cache_resource
def setup_postgres(database_url: str) -> str:
    """Cached wrapper around get_postgres_client.

    get_postgres_client runs CREATE TABLE IF NOT EXISTS / ALTER TABLE on
    every call — idempotent, but firing the DDL on every page render
    (especially every chat-input rerun) adds latency and DB churn for no
    benefit. cache_resource keys by the database_url, so the DDL runs
    once per (app process, URL) and the cached URL is returned thereafter.
    """
    return get_postgres_client(database_url)
