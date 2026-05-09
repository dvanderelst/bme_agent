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


def ensure_rubric_table(database_url: str) -> None:
    """Create the rubric_responses table and its index if missing."""
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_RUBRIC_RESPONSES_SQL)
            cur.execute(CREATE_RUBRIC_INDEX_SQL)


def get_progress(database_url: str, username: str, task: str) -> Dict[str, Any]:
    """
    Return progress on the most recent attempt for (username, task).

    No rows yet → {"attempt": 0, "last_question": 0, "completed": False, "note": None}.
    Otherwise the latest attempt's state is returned. "completed" is True when
    the latest attempt has all four questions answered.
    """
    with psycopg2.connect(database_url) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    attempt,
                    MAX(question_no) AS last_question,
                    MAX(note)        AS note
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
        "completed": row["last_question"] >= TOTAL_QUESTIONS,
        "note": row["note"],
    }


def next_attempt_number(database_url: str, username: str, task: str) -> int:
    """Return the next attempt number to use when restarting (existing max + 1, or 1)."""
    progress = get_progress(database_url, username, task)
    return (progress["attempt"] or 0) + 1


def record_answer(
    database_url: str,
    username: str,
    task: str,
    attempt: int,
    question_no: int,
    answer_text: Optional[str] = None,
    answer_json: Optional[Dict[str, Any]] = None,
    note: Optional[str] = None,
) -> bool:
    """
    Insert one answer row. Returns True on success.

    Provide answer_text for Q1–Q4 (free text) and answer_json for Q5
    (structured wrap-up). At least one of the two must be supplied.
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
        return True
    except psycopg2.Error as e:
        logging.error("Postgres error recording rubric answer: %s", e)
        return False
