import streamlit as st

from rubric_db import get_progress, TOTAL_QUESTIONS

st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

student = st.session_state.get("student", {})
username = student.get("username")
database_url = st.session_state.get("database_url")

TASKS = [
    ("mimic", "Mimic Color"),
    ("approach", "Approach Color"),
    ("kinesis", "Kinesis"),
    ("taxis", "Taxis"),
]


def progress_label(progress: dict) -> str:
    """Hint shown next to each task button."""
    if progress["attempt"] == 0:
        return "not started"
    if progress["completed"]:
        return f"completed (attempt {progress['attempt']})"
    return (
        f"in progress — last answered Q{progress['last_question']} "
        f"(attempt {progress['attempt']})"
    )


def enter_survey(task_key: str, task_label: str, attempt: int) -> None:
    """Stash the bits 3_Survey.py needs and route there. current_question is
    re-derived from the DB on the survey page itself."""
    st.session_state.task = task_key
    st.session_state.task_label = task_label
    st.session_state.attempt = attempt
    for k in ("selected_task", "selected_progress"):
        st.session_state.pop(k, None)
    st.switch_page("pages/3_Survey.py")


# --- Confirmation flow for an already-touched task ---------------------------
selected_task = st.session_state.get("selected_task")
if selected_task is not None:
    task_label = dict(TASKS)[selected_task]
    progress = st.session_state.get("selected_progress") or get_progress(
        database_url, username, selected_task
    )

    st.title(task_label)

    if progress["completed"]:
        st.warning(
            f"You've already completed this task (attempt {progress['attempt']})."
        )
        st.caption(
            "Restart with an instructor passcode will be added in the next "
            "iteration. For now, pick a different task."
        )
        if st.button("Back to task list"):
            for k in ("selected_task", "selected_progress"):
                st.session_state.pop(k, None)
            st.rerun()
    else:
        next_q = progress["last_question"] + 1
        st.info(
            f"You've already started this task (attempt {progress['attempt']}). "
            f"Last answered Q{progress['last_question']} of {TOTAL_QUESTIONS}."
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Continue from Q{next_q}", type="primary", use_container_width=True):
                enter_survey(selected_task, task_label, progress["attempt"])
        with col2:
            if st.button("Cancel", use_container_width=True):
                for k in ("selected_task", "selected_progress"):
                    st.session_state.pop(k, None)
                st.rerun()
    st.stop()

# --- Default view: list of tasks ---------------------------------------------
st.title("Pick the task you just completed")
st.caption(f"Logged in as **{username}**.")

for task_key, task_label in TASKS:
    progress = get_progress(database_url, username, task_key)
    col1, col2 = st.columns([2, 5])
    with col1:
        if st.button(task_label, key=f"task_{task_key}", use_container_width=True):
            if progress["attempt"] == 0:
                # Fresh start — go straight in
                enter_survey(task_key, task_label, attempt=1)
            else:
                # Already touched — show confirm UI on next rerun
                st.session_state.selected_task = task_key
                st.session_state.selected_progress = progress
                st.rerun()
    with col2:
        st.write(progress_label(progress))

st.divider()
if st.button("Log out"):
    for k in list(st.session_state.keys()):
        st.session_state.pop(k, None)
    st.switch_page("app.py")
