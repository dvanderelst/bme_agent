import streamlit as st

st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

student = st.session_state.get("student", {})

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
