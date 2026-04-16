"""
Postgres logging module for BME agent interactions.
Logs user/agent conversations to a Postgres database.
"""

import logging
import psycopg2
from psycopg2.extras import execute_values
from typing import Optional


CREATE_TABLE_SQL = """
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


def get_postgres_client(database_url: str) -> str:
    """
    Validate the database URL and ensure the interactions table exists.

    Args:
        database_url: Postgres connection URL

    Returns:
        The validated database URL

    Raises:
        ValueError: If database_url is empty
    """
    if not database_url:
        raise ValueError("Database URL must not be empty")

    # Create table if it doesn't exist
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)

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
    Log a single user/agent exchange to the Postgres interactions table.

    Args:
        client_config: Postgres connection URL (returned by get_postgres_client)
        conversation_id: Conversation ID
        user_message: The message sent by the user
        agent_response: The response returned by the agent
        user_id: Optional identifier for the user
        llm: Name of the LLM backend used (e.g. "mistral", "anthropic")

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
