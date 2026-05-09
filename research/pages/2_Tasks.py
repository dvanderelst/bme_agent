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
    """Render a per-task progress hint shown next to each button."""
    if progress["attempt"] == 0:
        return "not started"
    if progress["completed"]:
        return f"completed (attempt {progress['attempt']})"
    return f"in progress — last answered Q{progress['last_question']} (attempt {progress['attempt']})"


st.title("Pick the task you just completed")
st.caption(f"Logged in as **{username}**.")

for task_key, task_label in TASKS:
    progress = get_progress(database_url, username, task_key)
    col1, col2 = st.columns([2, 5])
    with col1:
        if st.button(task_label, key=f"task_{task_key}", use_container_width=True):
            # Stash what the survey page needs and route into the flow.
            st.session_state.task = task_key
            st.session_state.task_label = task_label
            st.session_state.progress = progress
            st.switch_page("pages/3_Survey.py")
    with col2:
        st.write(progress_label(progress))

st.divider()
if st.button("Log out"):
    for k in list(st.session_state.keys()):
        st.session_state.pop(k, None)
    st.switch_page("app.py")
