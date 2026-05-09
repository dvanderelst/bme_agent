import streamlit as st

from rubric_db import TOTAL_QUESTIONS

st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

if "task" not in st.session_state:
    st.switch_page("pages/2_Tasks.py")

task = st.session_state.task
task_label = st.session_state.get("task_label", task)
progress = st.session_state.get("progress", {})

st.title(f"{task_label} — survey (stub)")
st.caption(
    "This is a placeholder. Q1–Q4 (free-text) and Q5 (structured) come in "
    "the next iteration, along with the continue/restart-with-passcode flow."
)

st.write("**Current state**")
st.json(
    {
        "task": task,
        "attempt_recorded": progress.get("attempt"),
        "last_question": progress.get("last_question"),
        "completed": progress.get("completed"),
        "note": progress.get("note"),
        "total_questions_planned": TOTAL_QUESTIONS,
    }
)

if st.button("← Back to task picker"):
    for k in ("task", "task_label", "progress"):
        st.session_state.pop(k, None)
    st.switch_page("pages/2_Tasks.py")
