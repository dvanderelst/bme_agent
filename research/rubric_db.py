"""
Rubric storage for the survey app.

Single table, idempotent CREATE on startup. One row per (student, task,
attempt, question) — multiple attempts per (student, task) are allowed
and preserved; the analysis layer decides how to aggregate.

Q1–Q4 are free-text answers (stored in answer_text). Q5 is a structured
wrap-up question whose answers are serialized as a JSON blob (stored in
answer_json) so analysis can query individual fields directly.
"""

import logging
from typing import Optional, Dict, Any

import psycopg2
from psycopg2.extras import Json, RealDictCursor


VALID_TASKS = ("mimic", "approach", "kinesis", "taxis")
TOTAL_QUESTIONS = 5  # Q1–Q4 free-text, Q5 structured wrap-up

CREATE_RUBRIC_RESPONSES_SQL = """
CREATE TABLE IF NOT EXISTS rubric_responses (
    id            SERIAL PRIMARY KEY,
    username      TEXT NOT NULL,
    task          TEXT NOT NULL CHECK (task IN ('mimic', 'approach', 'kinesis', 'taxis')),
    attempt       INT NOT NULL DEFAULT 1,
    question_no   INT NOT NULL CHECK (question_no BETWEEN 1 AND 5),
    answer_text   TEXT,
    answer_json   JSONB,
    submitted_at  TIMESTAMPTZ DEFAULT NOW(),
    note          TEXT,
    UNIQUE (username, task, attempt, question_no),
    CHECK (answer_text IS NOT NULL OR answer_json IS NOT NULL)
);
"""

CREATE_RUBRIC_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_rubric_responses_user_task
ON rubric_responses (username, task, attempt);
"""

# Records each restart authorization: one row per (username, task, attempt)
# created at the moment the passcode form is submitted, before Q1 of the new
# attempt is answered. Persists the instructor note durably so that if the
# student closes the tab between authorization and Q1 (where session_state
# carrying the note would be lost), the note can still be reattached on
# resume. rubric_responses still denormalizes the note on every row of an
# attempt; this table is the authoritative source the response rows fall
# back to.
CREATE_RUBRIC_ATTEMPTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS rubric_attempts (
    id         SERIAL PRIMARY KEY,
    username   TEXT NOT NULL,
    task       TEXT NOT NULL CHECK (task IN ('mimic', 'approach', 'kinesis', 'taxis')),
    attempt    INT NOT NULL,
    note       TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (username, task, attempt)
);
"""


def ensure_rubric_table(database_url: str) -> None:
    """Create the rubric_responses and rubric_attempts tables (and the
    rubric_responses index) if any are missing."""
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_RUBRIC_RESPONSES_SQL)
            cur.execute(CREATE_RUBRIC_INDEX_SQL)
            cur.execute(CREATE_RUBRIC_ATTEMPTS_TABLE_SQL)


def get_progress(database_url: str, username: str, task: str) -> Dict[str, Any]:
    """
    Return progress on the most recent attempt for (username, task).

    No rows yet → {"attempt": 0, "last_question": 0, "completed": False, "note": None}.
    Otherwise the latest attempt's state is returned.

    Notes:
        - `completed` is True only when the count of answered questions equals
          TOTAL_QUESTIONS. Using COUNT(*) rather than MAX(question_no) means a
          gap in the row set (e.g. {1, 3, 5}) doesn't get reported as completed.
        - `note` is read from the question_no = 1 row of the latest attempt.
          The schema currently denormalizes the same note onto every row of
          an attempt, but FILTER (WHERE question_no = 1) means a future change
          that writes per-question notes won't silently pick an arbitrary one.
    """
    with psycopg2.connect(database_url) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    attempt,
                    MAX(question_no)                            AS last_question,
                    COUNT(*)                                    AS answered_count,
                    MAX(note) FILTER (WHERE question_no = 1)    AS note
                FROM rubric_responses
                WHERE username = %s AND task = %s
                GROUP BY attempt
                ORDER BY attempt DESC
                LIMIT 1
                """,
                (username, task),
            )
            row = cur.fetchone()

    if row is None:
        return {"attempt": 0, "last_question": 0, "completed": False, "note": None}

    return {
        "attempt": row["attempt"],
        "last_question": row["last_question"],
        "completed": row["answered_count"] == TOTAL_QUESTIONS,
        "note": row["note"],
    }


def next_attempt_number(database_url: str, username: str, task: str) -> int:
    """Return the next attempt number to use when restarting (existing max + 1, or 1).

    Considers both rubric_responses (answered rows) and rubric_attempts
    (authorizations without responses yet) so an in-flight restart that hasn't
    saved Q1 yet still consumes its number rather than colliding on a retry.
    """
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(MAX(attempt), 0) AS max_attempt FROM (
                    SELECT attempt FROM rubric_responses WHERE username = %s AND task = %s
                    UNION ALL
                    SELECT attempt FROM rubric_attempts  WHERE username = %s AND task = %s
                ) AS combined
                """,
                (username, task, username, task),
            )
            (max_attempt,) = cur.fetchone()
    return (max_attempt or 0) + 1


def record_attempt_start(
    database_url: str, username: str, task: str, note: str
) -> Optional[int]:
    """Atomically allocate the next attempt number and record the note in
    rubric_attempts. Returns the allocated number, or None on error.

    Retries up to 5 times if a race against another tab causes a UNIQUE
    collision on the chosen attempt number.
    """
    if not note:
        return None
    for _ in range(5):
        attempt = next_attempt_number(database_url, username, task)
        try:
            with psycopg2.connect(database_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO rubric_attempts (username, task, attempt, note)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (username, task, attempt, note),
                    )
            return attempt
        except psycopg2.errors.UniqueViolation:
            continue  # another tab took our number; retry with the next one
        except psycopg2.Error as e:
            logging.error("Postgres error recording attempt start: %s", e)
            return None
    logging.error("Could not allocate an attempt number after 5 retries")
    return None


def get_attempt_note(
    database_url: str, username: str, task: str, attempt: int
) -> Optional[str]:
    """Look up the note recorded for an attempt in rubric_attempts. Used as
    the recovery fallback when session_state.restart_note is gone and no
    rubric_responses row for the attempt has been written yet (so
    get_progress can't see the denormalized note either)."""
    try:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT note FROM rubric_attempts
                    WHERE username = %s AND task = %s AND attempt = %s
                    """,
                    (username, task, attempt),
                )
                row = cur.fetchone()
    except psycopg2.Error as e:
        logging.error("Postgres error looking up attempt note: %s", e)
        return None
    return row[0] if row else None


def record_answer(
    database_url: str,
    username: str,
    task: str,
    attempt: int,
    question_no: int,
    answer_text: Optional[str] = None,
    answer_json: Optional[Dict[str, Any]] = None,
    note: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Insert one answer row.

    Provide answer_text for Q1–Q4 (free text) and answer_json for Q5
    (structured wrap-up). At least one of the two must be supplied.

    Returns:
        {"ok": True}                            — row was inserted.
        {"ok": False, "reason": "duplicate"}    — UNIQUE constraint violation.
                                                  In normal flow our submit-time
                                                  re-check should catch this
                                                  case first, but the explicit
                                                  branch lets the caller surface
                                                  a clearer message if a race
                                                  ever slips through.
        {"ok": False, "reason": "error"}        — any other DB error.
    """
    if answer_text is None and answer_json is None:
        raise ValueError("Either answer_text or answer_json must be provided")
    try:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO rubric_responses
                        (username, task, attempt, question_no,
                         answer_text, answer_json, note)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        username,
                        task,
                        attempt,
                        question_no,
                        answer_text,
                        Json(answer_json) if answer_json is not None else None,
                        note,
                    ),
                )
        return {"ok": True}
    except psycopg2.errors.UniqueViolation as e:
        logging.warning("Duplicate rubric_responses row: %s", e)
        return {"ok": False, "reason": "duplicate"}
    except psycopg2.Error as e:
        logging.error("Postgres error recording rubric answer: %s", e)
        return {"ok": False, "reason": "error"}
