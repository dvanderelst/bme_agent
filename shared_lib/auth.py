"""
Student authentication for the BME agent.

The students table stores one row per enrolled student. New columns can be
added at any time (via ALTER TABLE or the management script); authenticate()
returns every column except password_hash, so app code automatically sees
new fields in st.session_state["student"].

This module also owns a small login_failures table used by both the chatbot
and the survey to throttle login attempts.
"""

import logging
from datetime import timedelta
from typing import Optional, Dict, Any, Tuple

import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor


# Login throttle. Five failed attempts in a five-minute rolling window
# block further attempts for that username until enough failures roll out
# of the window. Lockout is by username only — Railway's proxy means we
# don't have reliable per-IP info on the chat side.
LOCKOUT_THRESHOLD = 5
LOCKOUT_WINDOW_MINUTES = 5


CREATE_STUDENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS students (
    username      TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    enabled       BOOLEAN NOT NULL DEFAULT TRUE,
    backend       TEXT,
    full_name     TEXT,
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

CREATE_LOGIN_FAILURES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS login_failures (
    id            SERIAL PRIMARY KEY,
    username      TEXT NOT NULL,
    attempted_at  TIMESTAMPTZ DEFAULT NOW()
);
"""

CREATE_LOGIN_FAILURES_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_login_failures_user_time
ON login_failures (username, attempted_at);
"""


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


# Strings that count as "false" when the enabled column arrives as TEXT.
# Anything else non-empty is treated as enabled (fail-open: a typo in the
# spreadsheet keeps a student in rather than silently locking them out).
_FALSE_STRINGS = {"false", "no", "0", "n", "f", "off"}


def _coerce_enabled(value: Any) -> bool:
    """Normalise the `enabled` flag to a real bool.

    The students table column is BOOLEAN, but a re-sync from the .ods roster
    can land it as TEXT ('true'/'FALSE'/...) depending on how Calc saved the
    cell. Both apps gate access on `enabled`, and `not "false"` is False — a
    truthy non-empty string — so without this coercion a disabled student
    would still be let in. Empty/None defaults to True (enabled)."""
    if value is None:
        return True
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() not in _FALSE_STRINGS


def _build_student(row: Dict[str, Any]) -> Dict[str, Any]:
    """Strip password_hash and normalise the enabled flag for a DB row."""
    student = dict(row)
    student.pop("password_hash", None)
    if "enabled" in student:
        student["enabled"] = _coerce_enabled(student["enabled"])
    return student


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

    return _build_student(row)


def lookup_student(database_url: str, username: str) -> Optional[Dict[str, Any]]:
    """Fetch the student row by username. Returns the row (minus
    password_hash) or None if not found. No password verification.

    Used by app pages to re-verify "is this account still active?" on
    every render, so disabling a student in the DB takes effect
    immediately rather than on next login.
    """
    if not username:
        return None

    lookup = username.strip().lower()

    try:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM students WHERE username = %s", (lookup,))
                row = cur.fetchone()
    except psycopg2.Error as e:
        logging.error("Postgres error during student lookup: %s", e)
        return None

    if row is None:
        return None

    return _build_student(row)


def check_login_lockout(database_url: str, username: str) -> Tuple[bool, int]:
    """Check whether the username is currently rate-limited.

    Returns (locked, seconds_until_unlock). When locked, the caller should
    refuse the login attempt without running bcrypt. The lockout lifts
    when enough recent failures roll out of the window.

    Fails open on DB error — better to let students log in during a DB
    blip than to lock the whole class out.
    """
    if not username:
        return False, 0

    lookup = username.strip().lower()
    window = timedelta(minutes=LOCKOUT_WINDOW_MINUTES)

    try:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT attempted_at
                    FROM login_failures
                    WHERE username = %s
                      AND attempted_at > NOW() - %s
                    ORDER BY attempted_at DESC
                    LIMIT %s
                    """,
                    (lookup, window, LOCKOUT_THRESHOLD),
                )
                rows = cur.fetchall()
                if len(rows) < LOCKOUT_THRESHOLD:
                    return False, 0
                # The lockout lifts when the OLDEST of the threshold-most-recent
                # failures rolls out of the window. rows are sorted DESC, so
                # the oldest of the top-K is the last one.
                cur.execute("SELECT NOW()")
                now = cur.fetchone()[0]
        oldest_relevant = rows[-1][0]
        unlock_at = oldest_relevant + window
        seconds_remaining = max(0, int((unlock_at - now).total_seconds()))
        return True, seconds_remaining
    except psycopg2.Error as e:
        logging.error("Postgres error checking login lockout: %s", e)
        return False, 0


def record_login_failure(database_url: str, username: str) -> None:
    """Record one failed login attempt. Errors are logged, not raised —
    a DB blip during login shouldn't compound into a hard failure on
    top of the wrong-password failure the user already saw.
    """
    if not username:
        return

    lookup = username.strip().lower()

    try:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO login_failures (username) VALUES (%s)",
                    (lookup,),
                )
    except psycopg2.Error as e:
        logging.error("Postgres error recording login failure: %s", e)
