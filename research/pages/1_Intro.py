import streamlit as st

from shared_lib.auth import lookup_student

st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

# Re-verify the student is still active. session_state.authenticated is set
# at login and otherwise never re-checked, so disabling a student in the DB
# would only take effect on next login without this guard.
fresh_student = lookup_student(
    st.session_state.get("database_url"), st.session_state.get("student_id")
)
if fresh_student is None or not fresh_student.get("enabled", True):
    for k in list(st.session_state.keys()):
        st.session_state.pop(k, None)
    st.error("Your account is no longer active. Please contact an instructor.")
    st.stop()
st.session_state.student = fresh_student
student = fresh_student

st.title("Bme Survey")
st.write(f"Logged in as **{student.get('username', '?')}**.")

st.markdown(
    """
    ---

    *Placeholder text — full instructions and a reminder of how the data
    will be used will live here. For now this page exists so the navigation
    flow can be tested.*

    On the next page you'll pick the task you just completed, then answer
    five short questions about it. Your written answers cannot be revisited
    once submitted, so take a moment with each one.

    ---
    """
)

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Continue", type="primary"):
        st.switch_page("pages/2_Tasks.py")
with col2:
    if st.button("Log out"):
        for k in list(st.session_state.keys()):
            st.session_state.pop(k, None)
        st.switch_page("app.py")
