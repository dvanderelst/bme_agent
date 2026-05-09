import pathlib

import streamlit as st
import yaml

from rubric_db import TOTAL_QUESTIONS, get_progress, record_answer

st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

# --- Guards ------------------------------------------------------------------
if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

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
if progress["attempt"] > attempt:
    # DB is ahead of our session (e.g. another tab submitted) — sync.
    attempt = progress["attempt"]
    st.session_state.attempt = attempt

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
    if img_path.exists():
        st.image(str(img_path))
    else:
        st.warning(f"(Image not found: {q['image']})")

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
                ok = record_answer(
                    database_url,
                    username,
                    task,
                    attempt,
                    current_question,
                    answer_text=answer.strip(),
                    note=restart_note,
                )
                if ok:
                    st.toast(f"Q{current_question} saved", icon="✅")
                    st.rerun()
                else:
                    st.error(
                        "Could not save your answer — please try again. "
                        "If this keeps happening, ask an instructor."
                    )

# --- Q5: structured wrap-up --------------------------------------------------
elif current_question == 5:
    st.markdown(
        "A few short questions about the task you just did. "
        "*(Placeholder set — these will be refined.)*"
    )

    with st.form("q5_form", clear_on_submit=True):
        used_chatbot = st.radio(
            "Did you use the chatbot for this task?",
            options=["Yes", "No"],
            horizontal=True,
            key="q5_used_chatbot",
        )
        usefulness = st.slider(
            "If yes — how useful was the chatbot? (Skip if you didn't use it.)",
            min_value=1,
            max_value=5,
            value=3,
            step=1,
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
            used_chatbot_bool = used_chatbot == "Yes"
            answer_json = {
                "used_chatbot": used_chatbot_bool,
                "usefulness": usefulness if used_chatbot_bool else None,
                "specifics": specifics.strip() or None,
                "comments": comments.strip() or None,
            }
            ok = record_answer(
                database_url,
                username,
                task,
                attempt,
                5,
                answer_json=answer_json,
                note=restart_note,
            )
            if ok:
                st.toast("Q5 saved", icon="✅")
                st.rerun()
            else:
                st.error(
                    "Could not save your answers — please try again. "
                    "If this keeps happening, ask an instructor."
                )
