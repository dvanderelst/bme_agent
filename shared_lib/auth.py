"""
Student authentication for the BME agent.

The students table stores one row per enrolled student. New columns can be
added at any time (via ALTER TABLE or the management script); authenticate()
returns every column except password_hash, so app code automatically sees
new fields in st.session_state["student"].
"""

import logging
from typing import Optional, Dict, Any

import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor


CREATE_STUDENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS students (
    username      TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    enabled       BOOLEAN NOT NULL DEFAULT TRUE,
    backend       TEXT,
    full_name     TEXT,
    challenge     TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
"""

# Idempotent migrations so deployments that predate these columns pick them
# up automatically on startup.
ADD_ENABLED_COLUMN_SQL = (
    "ALTER TABLE students ADD COLUMN IF NOT EXISTS enabled "
    "BOOLEAN NOT NULL DEFAULT TRUE;"
)
ADD_BACKEND_COLUMN_SQL = (
    "ALTER TABLE students ADD COLUMN IF NOT EXISTS backend TEXT;"
)


def ensure_students_table(database_url: str) -> None:
    """Create the students table if it doesn't already exist."""
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_STUDENTS_TABLE_SQL)
            cur.execute(ADD_ENABLED_COLUMN_SQL)
            cur.execute(ADD_BACKEND_COLUMN_SQL)


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# Pre-computed throwaway hash used to equalise the cost of authenticating an
# unknown username vs. a wrong password. Without this, response-time
# differences would let attackers enumerate valid usernames.
_DUMMY_HASH = bcrypt.hashpw(b"dummy", bcrypt.gensalt())


def authenticate(
    database_url: str, username: str, password: str
) -> Optional[Dict[str, Any]]:
    """
    Verify credentials and return the full student row (minus password_hash).

    Username matching is case-insensitive — usernames are stored lowercased
    and the lookup lowercases the input as well.

    Returns:
        Dict of all student columns except password_hash on success.
        None if the username is unknown or the password doesn't match.
    """
    if not username or not password:
        return None

    lookup = username.strip().lower()

    try:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM students WHERE username = %s", (lookup,))
                row = cur.fetchone()
    except psycopg2.Error as e:
        logging.error("Postgres error during authentication: %s", e)
        return None

    if row is None:
        # Run bcrypt against a dummy hash so the response time matches the
        # wrong-password path — avoids leaking which usernames exist.
        bcrypt.checkpw(password.encode("utf-8"), _DUMMY_HASH)
        return None

    stored_hash = row.get("password_hash")
    if not stored_hash:
        return None

    try:
        ok = bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
    except ValueError:
        # Malformed hash in the DB — treat as auth failure rather than crashing.
        logging.error("Malformed password hash for user %s", lookup)
        return None

    if not ok:
        return None

    student = dict(row)
    student.pop("password_hash", None)
    return student
