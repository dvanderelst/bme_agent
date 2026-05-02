"""
Postgres logging module for BME agent interactions.
Logs user/agent conversations and student feedback to a Postgres database.
"""

import logging
import psycopg2
from typing import Optional

from shared_lib.auth import (
    CREATE_STUDENTS_TABLE_SQL,
    ADD_ENABLED_COLUMN_SQL,
    ADD_BACKEND_COLUMN_SQL,
)


CREATE_INTERACTIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS interactions (
    id              SERIAL PRIMARY KEY,
    timestamp       TIMESTAMPTZ DEFAULT NOW(),
    conversation_id TEXT,
    user_id         TEXT,
    user_message    TEXT,
    agent_response  TEXT,
    llm             TEXT
);
"""

CREATE_FEEDBACK_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS feedback (
    id              SERIAL PRIMARY KEY,
    timestamp       TIMESTAMPTZ DEFAULT NOW(),
    conversation_id TEXT,
    user_id         TEXT,
    sentiment       SMALLINT,
    note            TEXT
);
"""


def get_postgres_client(database_url: str) -> str:
    """
    Validate the database URL and ensure all tables exist.

    Args:
        database_url: Postgres connection URL

    Returns:
        The validated database URL

    Raises:
        ValueError: If database_url is empty
    """
    if not database_url:
        raise ValueError("Database URL must not be empty")

    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_INTERACTIONS_TABLE_SQL)
            cur.execute(CREATE_FEEDBACK_TABLE_SQL)
            cur.execute(CREATE_STUDENTS_TABLE_SQL)
            cur.execute(ADD_ENABLED_COLUMN_SQL)
            cur.execute(ADD_BACKEND_COLUMN_SQL)

    return database_url


def log_interaction(
    client_config: str,
    conversation_id: str,
    user_message: str,
    agent_response: str,
    user_id: Optional[str] = None,
    llm: Optional[str] = None,
) -> bool:
    """
    Log a single user/agent exchange to the interactions table.

    Returns:
        True if logging succeeded, False if failed
    """
    try:
        with psycopg2.connect(client_config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO interactions
                        (conversation_id, user_id, user_message, agent_response, llm)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (conversation_id, user_id, user_message, agent_response, llm),
                )
        return True

    except psycopg2.Error as e:
        logging.error("Postgres error: %s", e)
        return False
    except Exception as e:
        logging.error("Unexpected error logging to Postgres: %s", e)
        return False


def log_feedback(
    client_config: str,
    conversation_id: Optional[str],
    sentiment: int,
    note: Optional[str] = None,
    user_id: Optional[str] = None,
) -> bool:
    """
    Log a student feedback submission to the feedback table.

    Args:
        client_config: Postgres connection URL
        conversation_id: Current conversation ID
        sentiment: 1 = thumbs up, 0 = thumbs down
        note: Optional free-text note from the student
        user_id: Optional student identifier

    Returns:
        True if logging succeeded, False if failed
    """
    try:
        with psycopg2.connect(client_config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO feedback
                        (conversation_id, user_id, sentiment, note)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (conversation_id, user_id, sentiment, note or None),
                )
        return True

    except psycopg2.Error as e:
        logging.error("Postgres error logging feedback: %s", e)
        return False
    except Exception as e:
        logging.error("Unexpected error logging feedback: %s", e)
        return False
