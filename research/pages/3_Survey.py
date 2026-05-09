import logging
import pathlib

import streamlit as st
import yaml

from shared_lib.auth import lookup_student
from rubric_db import TOTAL_QUESTIONS, get_progress, record_answer

st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

# --- Guards ------------------------------------------------------------------
if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

# Re-verify the student is still active (see 1_Intro.py for rationale).
fresh_student = lookup_student(
    st.session_state.get("database_url"), st.session_state.get("student_id")
)
if fresh_student is None or not fresh_student.get("enabled", True):
    for k in list(st.session_state.keys()):
        st.session_state.pop(k, None)
    st.error("Your account is no longer active. Please contact an instructor.")
    st.stop()
st.session_state.student = fresh_student

required_keys = ("task", "task_label", "attempt")
if not all(k in st.session_state for k in required_keys):
    st.switch_page("pages/2_Tasks.py")

task = st.session_state.task
task_label = st.session_state.task_label
attempt = st.session_state.attempt
username = st.session_state.student["username"]
database_url = st.session_state.database_url

# --- Question source ---------------------------------------------------------
QUESTIONS_DIR = pathlib.Path(__file__).resolve().parent.parent / "questions"
with open(QUESTIONS_DIR / f"{task}.yaml") as f:
    task_data = yaml.safe_load(f)

# --- Derive current question from the DB ------------------------------------
# The DB is the source of truth; session state only carries (task, attempt).
# Refreshing the page or coming back from a tab close still works.
progress = get_progress(database_url, username, task)

# If the DB is ahead of the attempt we have in session state, this tab is
# stale — most likely another tab (or the instructor on a shared screen)
# restarted the same task with the passcode. Refuse to render the form
# rather than silently rewriting the attempt number on submit, which would
# park the typed text under the wrong (attempt, question_no) row.
if progress["attempt"] > attempt:
    st.warning(
        "This task was advanced in another tab or window — possibly a "
        "restart with the instructor passcode. Reload to pick up where "
        "it stands now. Anything you started typing here will not be saved."
    )
    if st.button("Reload", type="primary"):
        for k in ("task", "task_label", "attempt", "restart_note"):
            st.session_state.pop(k, None)
        st.switch_page("pages/2_Tasks.py")
    st.stop()

if progress["attempt"] < attempt:
    current_question = 1  # No rows for this attempt yet
else:
    current_question = progress["last_question"] + 1

# A restart writes the same instructor note onto every row of the new
# attempt. Prefer the value carried in session state (set by 2_Tasks.py
# when restart was authorized); fall back to whatever's on disk so a
# refresh mid-attempt doesn't drop the note.
restart_note = st.session_state.get("restart_note")
if not restart_note and attempt > 1:
    restart_note = progress.get("note")

# --- Completion screen -------------------------------------------------------
if current_question > TOTAL_QUESTIONS:
    st.title("Thank you")
    st.success(
        f"You've completed the **{task_label}** survey (attempt {attempt})."
    )
    st.caption("Your answers are saved.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to tasks", use_container_width=True):
            for k in ("task", "task_label", "attempt", "restart_note"):
                st.session_state.pop(k, None)
            st.switch_page("pages/2_Tasks.py")
    with col2:
        if st.button("Log out", use_container_width=True):
            for k in list(st.session_state.keys()):
                st.session_state.pop(k, None)
            st.switch_page("app.py")
    st.stop()

# --- Header ------------------------------------------------------------------
st.progress(
    current_question / TOTAL_QUESTIONS,
    text=f"Question {current_question} of {TOTAL_QUESTIONS}",
)
st.title(task_label)
st.caption(
    "Answer each question as best you can. Once submitted, you can't return "
    "to a previous question."
)

# --- Q1–Q4: free-text answer ------------------------------------------------
if 1 <= current_question <= 4:
    q = task_data["questions"][current_question - 1]

    img_path = (QUESTIONS_DIR.parent / q["image"]).resolve()
    if not img_path.exists():
        # The student can't meaningfully answer a figure-grounded question
        # without seeing the figure. Halt with an instructor-actionable
        # message rather than letting them submit blind.
        logging.error(
            "Survey image missing for %s Q%d: %s",
            task, current_question, img_path,
        )
        st.error(
            "The image for this question is missing. Please ask an "
            "instructor to look at the deployment."
        )
        st.stop()
    st.image(str(img_path))

    st.markdown(q["text"])

    with st.form(f"q{current_question}_form", clear_on_submit=True):
        answer = st.text_area(
            "Your answer",
            height=200,
            key=f"answer_q{current_question}",
            placeholder="Type your answer here...",
        )
        submitted = st.form_submit_button("Submit and continue", type="primary")
        if submitted:
            if not answer.strip():
                st.error("Please write an answer before submitting.")
            else:
                # Re-check progress at submit time. Closes the race window
                # between page render and form submit — if another tab moved
                # this task forward between the render and now, the form's
                # captured (attempt, current_question) is stale and we
                # mustn't write under those keys.
                live = get_progress(database_url, username, task)
                if live["attempt"] > attempt:
                    expected_q = None  # stale tab
                elif live["attempt"] == attempt:
                    expected_q = live["last_question"] + 1
                else:
                    expected_q = 1  # fresh attempt; no rows yet
                if expected_q != current_question:
                    st.error(
                        "This task changed in another tab while you were "
                        "answering. Reload the page to continue."
                    )
                else:
                    result = record_answer(
                        database_url,
                        username,
                        task,
                        attempt,
                        current_question,
                        answer_text=answer.strip(),
                        note=restart_note,
                    )
                    if result["ok"]:
                        st.toast(f"Q{current_question} saved", icon="✅")
                        st.rerun()
                    elif result.get("reason") == "duplicate":
                        st.error(
                            "Looks like this answer was already saved "
                            "(probably from another tab). Reload the page "
                            "to continue."
                        )
                    else:
                        st.error(
                            "Could not save your answer — please try again. "
                            "If this keeps happening, ask an instructor."
                        )

# --- Q5: structured wrap-up --------------------------------------------------
#
# DESIGN PRINCIPLE for every Q5 widget — read this before adding or
# replacing fields below.
#
# Each input must distinguish a real answer from "didn't touch". A
# student who clicks straight through Q5 must not look in the data like
# they actively answered with whatever value was the widget's default.
#
# Concrete rules:
#   - st.radio / st.selectbox: pass `index=None` so nothing is preselected;
#     reject the submit if the value is still None and the question is
#     required.
#   - Avoid st.slider for ordinal ratings — sliders default to a midpoint
#     that looks indistinguishable from a deliberate neutral answer. Use
#     a horizontal `st.radio` over a small integer range instead. If a
#     slider really is needed, pair it with a separate "didn't rate"
#     checkbox.
#   - Free-text (st.text_area / st.text_input): an empty string IS the
#     "didn't touch" answer — store it as None on submit so that's explicit.
#
# The widgets below are placeholders; the actual Q5 questions are TBD.
# Whatever they end up being, they must follow these same rules so the
# analysis layer can tell skipped questions from neutral answers.
#
elif current_question == 5:
    st.markdown(
        "A few short questions about the task you just did. "
        "*(Placeholder set — these will be refined.)*"
    )

    with st.form("q5_form", clear_on_submit=True):
        used_chatbot = st.radio(
            "Did you use the chatbot for this task?",
            options=["Yes", "No"],
            index=None,
            horizontal=True,
            key="q5_used_chatbot",
        )
        usefulness = st.radio(
            "If yes — how useful was the chatbot? "
            "(1 = not useful, 5 = very useful. Leave blank if you didn't use it.)",
            options=[1, 2, 3, 4, 5],
            index=None,
            horizontal=True,
            key="q5_usefulness",
        )
        specifics = st.text_area(
            "If yes — anything specific that helped or didn't?",
            height=100,
            key="q5_specifics",
        )
        comments = st.text_area(
            "Any other comments about the task?",
            height=100,
            key="q5_comments",
        )
        submitted = st.form_submit_button("Submit and finish", type="primary")
        if submitted:
            if used_chatbot is None:
                st.error(
                    "Please answer whether you used the chatbot for this task."
                )
            elif used_chatbot == "Yes" and usefulness is None:
                st.error(
                    "You said you used the chatbot — please rate how useful it was."
                )
            else:
                # Re-check progress at submit time (same race-protection
                # logic as the Q1–Q4 path).
                live = get_progress(database_url, username, task)
                if live["attempt"] > attempt:
                    expected_q = None
                elif live["attempt"] == attempt:
                    expected_q = live["last_question"] + 1
                else:
                    expected_q = 1
                if expected_q != 5:
                    st.error(
                        "This task changed in another tab while you were "
                        "answering. Reload the page to continue."
                    )
                else:
                    used_chatbot_bool = used_chatbot == "Yes"
                    answer_json = {
                        "used_chatbot": used_chatbot_bool,
                        "usefulness": usefulness if used_chatbot_bool else None,
                        "specifics": specifics.strip() or None,
                        "comments": comments.strip() or None,
                    }
                    result = record_answer(
                        database_url,
                        username,
                        task,
                        attempt,
                        5,
                        answer_json=answer_json,
                        note=restart_note,
                    )
                    if result["ok"]:
                        st.toast("Q5 saved", icon="✅")
                        st.rerun()
                    elif result.get("reason") == "duplicate":
                        st.error(
                            "Looks like Q5 was already saved (probably from "
                            "another tab). Reload the page to continue."
                        )
                    else:
                        st.error(
                            "Could not save your answers — please try again. "
                            "If this keeps happening, ask an instructor."
                        )
